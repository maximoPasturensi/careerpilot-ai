from google import genai
from google.genai import types
from app.config import GEMINI_MODEL
from app.models import CVProfile, JobDescription, MatchResult, CoverLetter
from app.cache import cache_set, cache_get
from app.retry_utils import llm_retry

client = genai.Client()

COVER_LETTER_SYSTEM_PROMPT = """Sos un experto en redaccion de cartas de presentacion para
procesos de seleccion tecnicos. Tu tarea es escribir una carta de presentacion breve (3
parrafos) para un candidato, basandote UNICAMENTE en su experiencia real y en los
requerimientos de una oferta laboral especifica.

REGLAS ESTRICTAS:
1. NUNCA inventes anecdotas, proyectos, logros o motivaciones personales que no esten
respaldados por el CV real del candidato. Podes inferir entusiasmo genuino a partir de la
experiencia existente, pero no fabricar historias.
2. No prometas habilidades que el candidato no tiene (revisa los missing_keywords antes de
escribir) - si el puesto pide Airflow y el candidato no lo tiene, NO digas que "esta
femiliarizado" con Airflow ni insinues experiencia que no tiene
3. Adapta el tono segun el nombre y estilo de la empresa: si suena una startup joven, tono mas
cercano; si suena corporativo/enterprise, tono mas formal. Si no hay señales claras, usa el
tono profesional neutro.
4. Evita chicles genericos tipo "soy un apasionado de los datos" sin sustento - ancla cada
afirmacion a algo concreto de la experiencia real del candidato.
5. Maximo 250 palabras en total entre los 3 parrafos - una carta larga no se lee en procesos
de seleccion reales."""

@llm_retry
def _call_gemini_cover_letter(prompt: str):
    return client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CoverLetter,
            max_output_tokens=2000,
        ),
    )

def generate_cover_letter(cv: CVProfile, job: JobDescription, match: MatchResult) -> CoverLetter:
    prompt = f"""{COVER_LETTER_SYSTEM_PROMPT}

--- PERFIL DEL CANDIDATO (JSON) ---
{cv.model_dump_json(indent=2)}

--- OFERTA LABORAL (JSON) ---
{job.model_dump_json(indent=2)}

--- ANALISIS DE GAPS ---
Keywords que el candidato NO tiene (NO las menciones ni insinues que las tiene):
{match.missing_keywords}

Score actual de compatibilidad: {match.overall_score}%

Escribi la carta de presentacion siguiendo todas las reglas del system prompt."""

    cached = cache_get("cover_letter", GEMINI_MODEL, prompt)
    if cached:
        return CoverLetter.model_validate_json(cached)

    response = _call_gemini_cover_letter(prompt)
    cache_set("cover_letter", GEMINI_MODEL, prompt, value=response.text)
    return response.parsed