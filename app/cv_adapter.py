from google import genai
from google.genai import types
from app.config import GEMINI_MODEL
from app.models import CVProfile, JobDescription, MatchResult, AdaptedCV
from app.cache import cache_get, cache_set
from app.retry_utils import llm_retry

client = genai.Client()

CV_ADAPTER_SYSTEM_PROMPT = """Sos un experto en redaccion de CVs y reclutamiento tecnico
Tu tarea es reescribir los bullets de experiencia de un candidato usando el metodo STAR
(Situacion, Tarea, Accion, Resultado), alineandolos con los requerimientos de una oferta
laboral especifica.

REGLAS ESTRICTAS:
1. Nunca inventes logros, tecnologias, metricas o responsabilidades que no esten implicitas
en el bullet original. Podes reformular y resaltar, pero no fabricar informacion nueva.
2. Si el bullet original no tiene un resultado medible, no investes una cifra falsa - mejora
la redaccion sin agregar numeros que el candidato no proporciono.
3. Prioriza usar terminologia exacta de la oferta laboral cuando el candidato ya tenga esa
experiencia real, para pasar filtros ATS (Applicant Tracking Systems).
4. El summary y headline deben reflejar honestamente el perfil del candidato, orientado hacia
el puesto, sin exagerar seniority o experiencia que no tiene.
5. highlighted_skills debe reordenar (no inventar) los skills existentes del candidat,
priorizando lo que matchean con la oferta."""

@llm_retry
def _call_gemini_adapter(prompt: str):
    return client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AdaptedCV,
            max_output_tokens=4096,
        ),
    )

def adapt_cv(cv: CVProfile, job: JobDescription, match: MatchResult) -> AdaptedCV:
    prompt = f"""{CV_ADAPTER_SYSTEM_PROMPT}

--- PERFIL DEL CANDIDATO (JSON) ---
{cv.model_dump_json(indent=2)}

--- OFERTA LABORAL (JSON) ---
{job.model_dump_json(indent=2)}

--- ANALISIS DE GAPS ---
Keywords que el candidato NO tiene (no las inventes, no las agregues al CV):
{match.missing_keywords}

Score actual de compatibilidad: {match.overall_score}%

Reescribi el CV del candidato optimizandolo para esta oferta especifica, siguien todas las
reglas del system prompt."""

    cached = cache_get("cv_adapter", GEMINI_MODEL, prompt)
    if cached:
        return AdaptedCV.model_validate_json(cached)

    response = _call_gemini_adapter(prompt)
    cache_set("cv_adapter", GEMINI_MODEL, prompt, value=response.text)
    return response.parsed