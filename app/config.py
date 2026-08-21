from dotenv import load_dotenv
import logging
import os
import streamlit as st

if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

logging.getLogger("google_genai").setLevel(logging.ERROR)

load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash-lite"

GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"