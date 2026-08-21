# tests/test_job_extractor.py
from app.job_extractor import parse_job_to_description

DUMMY_JOB_TEXT = """
Data Engineer Semi-Senior - TechCorp SA

Buscamos Data Engineer con 3+ años de experiencia para sumarse a nuestro equipo
de Analytics. Modalidad híbrida, oficinas en Buenos Aires. Rango salarial:
USD 2000-2800.

Responsabilidades:
- Diseñar y mantener pipelines de datos en Python y SQL
- Trabajar con Airflow y dbt para orquestación de ETLs
- Colaborar con el equipo de Data Science en la preparación de datasets

Requisitos:
- Python, SQL, Airflow, dbt, AWS (hard skills)
- Buena comunicación y trabajo en equipo (soft skills)
"""

if __name__ == "__main__":
    result = parse_job_to_description(DUMMY_JOB_TEXT)
    print(result.model_dump_json(indent=2))