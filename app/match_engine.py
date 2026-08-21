from dotenv import load_dotenv
from google import genai
from google.genai import types
import numpy as np
from rapidfuzz import fuzz
from app.config import GEMINI_EMBEDDING_MODEL, GEMINI_MODEL
from app.models import GapAnalysisJudgment, CVProfile, JobDescription, MatchResult
from app.cache import cache_set, cache_get
from app.retry_utils import llm_retry

client = genai.Client()

HARD_SKILLS_WEIGHT = 0.70
SOFT_SKILLS_WEIGHT = 0.30

def get_embedding(text: str, task_type: str = "SEMANTIC_SIMILARITY") -> list[float]:
    """Genera el vector de embedding para un texto dado."""
    result = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type),
    )

    return result.embeddings[0].values

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calcula la similitud coseno entre dos vectores de embedding."""

    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def _skill_to_context(skill: str) -> str:
    """Envuelve el skill en una frase con contexto para mejorar la separacion semantica."""
    return f"Habilidad tecnica o herramienta profesional: {skill}"

def compare_skill_lists(job_skills: list[str], cv_skills: list[str]) -> list[dict]:
    results = []
    remaining = []

    # Paso 1: fuzzy match (instantáneo, gratis)
    for job_skill in job_skills:
        match = fuzzy_match_skill(job_skill, cv_skills)
        if match:
            results.append({
                "required_skill": job_skill,
                "best_match_in_cv": match,
                "similarity": None,
                "is_gap": False,
                "reasoning": "Coincidencia directa (fuzzy match)",
            })
        else:
            remaining.append(job_skill)

    # Paso 2: LLM-judge para lo que no resolvió el fuzzy match (1 sola llamada)
    results.extend(llm_judge_skills(remaining, cv_skills))

    return results

def fuzzy_match_skill(skill: str, cv_skills: list[str], threshold: int = 85) -> str | None:
    """ Busca coincidencia casi-exacta (typos, orden de palabras, plurales)."""
    best_match = None
    best_score = 0
    for cv_skill in cv_skills:
        score = fuzz.token_sort_ratio(skill.lower(), cv_skill.lower())
        if score > best_score:
            best_score = score
            best_match = cv_skill
    return best_match if best_score >= threshold else None

JUDGE_SYSTEM_PROMPT = """Sos un evaluador tecnico de reclutamiento. Vas a recibir una lista de
skills requeridos por una oferta laboral y la lista de skills que tiene un candidato.
Para cada skill requerido, decidi si el candidato lo cubre -directamente o con una herramienta/
tecnologia funcionalmente equivalente-. Se estricto: herramientas de proposito general (ej. '
Google Cloud Platform') NO cubren automaticamente herramientas especificas (ej. 'Airflow', que
es orquestacion de datos particular). Si no hay equivalencia real, marca is_match=false.
Justifica cada decision en una frase breve."""

@llm_retry
def _call_gemini_judge(prompt: str):
    return client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GapAnalysisJudgment,
        ),
    )

def llm_judge_skills(remaining_job_skills: list[str], cv_skills: list[str]) -> list[dict]:
    """Evalua con LLM los skills que el fuzzy match no pudo resolver."""
    if not remaining_job_skills:
        return[]

    prompt = f"""{JUDGE_SYSTEM_PROMPT}

Skills requeridos a evaluar: {remaining_job_skills}
Skills del candidato (CV): {cv_skills}"""

    cached = cache_get("llm_judge", GEMINI_MODEL, prompt)
    if cached:
        parsed = GapAnalysisJudgment.model_validate_json(cached)
    else:
        response = _call_gemini_judge(prompt)
        cache_set("llm_judge", GEMINI_MODEL, prompt, value=response.text)
        parsed= response.parsed

    return [
        {
            "required_skill": j.required_skill,
            "best_match_in_cv": j.matched_cv_skill,
            "similarity": None,
            "is_gap": not j.is_match,
            "reasoning": j.reasoning,
        }
        for j in parsed.judgments
    ]

def _score_from_results(results: list[dict]) -> float:
    """% de skills que NO son gap, sobre el total requerido."""
    if not results:
        return 100.0
    matches = sum(1 for r in results if not r["is_gap"])
    return round((matches / len(results)) * 100, 1)

def compute_match_result(cv: CVProfile, job: JobDescription) -> MatchResult:
    cv_skill_names = [s.name for s in cv.skills]

    hard_results = compare_skill_lists(job.required_hard_skills, cv_skill_names)
    soft_results = compare_skill_lists(job.required_soft_skills, cv_skill_names)

    hard_score = _score_from_results(hard_results)
    soft_score = _score_from_results(soft_results)

    overall = round(
        hard_score * HARD_SKILLS_WEIGHT + soft_score * SOFT_SKILLS_WEIGHT, 1
    )

    missing = [r["required_skill"] for r in hard_results + soft_results if r["is_gap"]]

    return MatchResult(
        overall_score=overall,
        hard_skills_score=hard_score,
        soft_skills_score=soft_score,
        hard_skills_detail=hard_results,
        soft_skills_detail=soft_results,
        missing_keywords=missing,
    )