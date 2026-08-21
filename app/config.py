from dotenv import load_dotenv
import logging

logging.getLogger("google_genai").setLevel(logging.ERROR)

load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash-lite"

GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"