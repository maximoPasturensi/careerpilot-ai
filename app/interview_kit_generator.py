from google import genai
from google.genai import types
from app.config import GEMINI_MODEL
from app.models import CVProfile, JobDescription, MatchResult, InterviewKit
from app.cache import cache_get, cache_set
from app.retry_utils import llm_retry

client = genai.Client()

INTERVIEW_KIT_SYSTEM_PROMPT = """Sos un coach de entrevistas tecnicas especializado en
preparar candidatos para procesos de seleccion. Tu tarea es generar 5 preguntas probables
de entrevista (mezclando tecnicas y complementales) junto con respuesta sugeridas en
primera persona, basadas en el CV real del candidato y la oferta laboral.

REGLAS ESTRICTAS
1. Usa exclusivamente las empresas, roles y proyectos listados en el CV para armar el relato
de cada respuesta. NUNCA investes nombres de empresas, proyectos, cifras o situaciones que no
esten en el CV real del candidato.
2. Si la pregunta indaga sobre un skill que el candidato NO tiene (ver missing_keyword), la
respuesta sugerida debe abordar honestamente como el candidato planea aprenderle o como su
experiencia cercana le da una base para adquirirlo rapido - NUNCA inventar un proyecto
pasado usando esa tecnologia que el candidato no tiene.
3. Las respuestas deben sonar naturales y habladas (primera persona, tono conversacional), no
como un resumen de CV leido en voz alta.
4. Prioriza 3 preguntas tecnicas ancladas en los requisitos de la oferta (algunas sobre
fortalezas del candidato, al menos una sobre un gap real) y 2 comportamentales ancladas
en situaciones reales de su experiencia.
5. El tip de cada pregunta debe ser un consejo practico y breve (ej. "Menciona una metrica
si la tenes" o "Mantene la respuesta bajo 90 segundos")."""

@llm_retry
def _call_gemini_interview_kit(prompt: str):
    return client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InterviewKit,
            max_output_tokens=4096,
        ),
    )

def generate_interview_kit(cv: CVProfile, job: JobDescription, match: MatchResult) -> InterviewKit:
    prompt = f"""{INTERVIEW_KIT_SYSTEM_PROMPT}

--- PERFIL DEL CANDIDATO (JSON) ---
{cv.model_dump_json(indent=2)}

--- OFERTA LABORAL (JSON) ---
{job.model_dump_json(indent=2)}

--- ANALISIS DE GAPS ---
Keywords que el candidato NO tiene (para preguntas sobre estos gaps, aplica la regla 2
del system prompt - no inventar experiencia, si mostrar como cerraria la brecha):
{match.missing_keywords}

Score actual de compatibilidad: {match.overall_score}%

Genera el kit de entrevista siguiendo todas las reglas del system prompt."""

    cached = cache_get("interview_kit", GEMINI_MODEL, prompt)
    if cached:
        return InterviewKit.model_validate_json(cached)

    response = _call_gemini_interview_kit(prompt)
    cache_set("interview_kit", GEMINI_MODEL, prompt, value=response.text)
    return response.parsed