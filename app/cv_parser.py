# app/cv_parser.py
from pathlib import Path
import pdfplumber
from google import genai
from google.genai import types
from app.config import GEMINI_MODEL
from app.cache import cache_get, cache_set
from app.retry_utils import llm_retry
from app.models import CVProfile

client = genai.Client()  # toma GEMINI_API_KEY del entorno automáticamente

CV_PARSER_SYSTEM_PROMPT = """Sos un extractor de datos de CVs. Tu única tarea es leer
el texto crudo de un currículum y devolver la información estructurada. No inventes
datos que no estén en el texto: si un campo no aparece, dejalo vacío o null."""


def extract_raw_text(file_path: str) -> str:
    """Extrae texto plano de un CV en PDF o Markdown."""
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        text_chunks = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")
        return "\n".join(text_chunks)
    elif path.suffix.lower() in (".md", ".txt"):
        return path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Formato no soportado: {path.suffix}")


@llm_retry
def _call_gemini_cv(prompt: str):
    return client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CVProfile,
            max_output_tokens=4096,
        ),
    )

def parse_cv_to_profile(raw_text: str) -> CVProfile:
    prompt = f"{CV_PARSER_SYSTEM_PROMPT}\n\nTexto del CV:\n{raw_text}"

    cached = cache_get("cv_parser", GEMINI_MODEL, prompt)
    if cached:
        return CVProfile.model_validate_json(cached)

    responsed = _call_gemini_cv(prompt)
    cache_set("cv_parser", GEMINI_MODEL, prompt, value=responsed.text)
    return responsed.parsed
