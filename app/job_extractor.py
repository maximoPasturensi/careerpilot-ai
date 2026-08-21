# app/job_extractor.py
from google import genai
from google.genai import types
from app.models import JobDescription
from dotenv import load_dotenv
from app.config import GEMINI_MODEL
from app.cache import cache_get, cache_set
from app.retry_utils import llm_retry

client = genai.Client()

JOB_EXTRACTOR_SYSTEM_PROMPT = """Sos un extractor de datos de ofertas laborales. Tu única
tarea es leer el texto de una publicación de empleo y devolver la información estructurada
usando la herramienta 'extract_job_description'. No inventes datos que no estén en el texto:
si un campo no aparece (ej. salario o modalidad remota), dejalo null.

CRITERIO DE CLASIFICACIÓN DE SKILLS (muy importante, aplicalo estrictamente):
- required_hard_skills: TODA herramienta, software, plataforma, lenguaje de programación,
  framework, metodología técnica o certificación específica. Ejemplos: SAP, Data-Sphere,
  Power BI, Python, SQL, Business Intelligence, Excel, AWS, Docker, Scrum.
- required_soft_skills: ÚNICAMENTE habilidades interpersonales o de comportamiento, sin
  ninguna herramienta o tecnología de por medio. Ejemplos: comunicación efectiva, trabajo
  en equipo, liderazgo, proactividad, capacidad de negociación, orientación a resultados.

Si tenés dudas sobre un ítem (ej. 'Business Intelligence' podría sonar a concepto), preguntate:
¿esto se aprende con un curso técnico o una certificación? Si sí, es hard skill. ¿Esto describe
cómo la persona se relaciona con otros o gestiona su trabajo? Si sí, es soft skill."""

@llm_retry
def _call_gemini_job(prompt: str):
    return client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=JobDescription,
            max_output_tokens=4096,
        ),
    )


def parse_job_to_description(raw_text: str) -> JobDescription:
    prompt = f"{JOB_EXTRACTOR_SYSTEM_PROMPT}\n\nTexto de la oferta:\n{raw_text}"

    cached = cache_get("job_extractor", GEMINI_MODEL, prompt)
    if cached:
        return JobDescription.model_validate_json(cached)

    response = _call_gemini_job(prompt)
    cache_set("job_extractor", GEMINI_MODEL, prompt, value=response.text)
    return response.parsed