from app.cv_parser import parse_cv_to_profile
from app.job_extractor import parse_job_to_description
from app.match_engine import compute_match_result

DUMMY_CV_TEXT = """
Juan Perez
Data Analyst con 3 años de experiencia en análisis de datos y BI.

Experiencia:
- Analista de Datos en RetailCo (Ene 2022 - Actual)
  - Desarrollo de dashboards en Power BI para el área comercial
  - Consultas SQL complejas sobre PostgreSQL para reporting semanal
  - Automatización de reportes con Python (pandas)
  
Educación:
- Licenciatura en Sistemas, Universidad de Buenos Aires (2021)

Habilidades:
- Python, SQL, PostgreSQL, Power BI, Excel
- Trabajo en equipo, comunicación efectiva
"""

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

def test_full_pipeline():
    print("1/3 - Parseando CV...")
    cv_profile = parse_cv_to_profile(DUMMY_CV_TEXT)
    print(f"    OK: {cv_profile.full_name}, {len(cv_profile.skills)} skills detectados\n")

    print("2/3 - Parseando oferta laboral...")
    job = parse_job_to_description(DUMMY_JOB_TEXT)
    print(f"    OK: {job.job_title} en {job.company_name}\n")

    print("3/3 - Calculando match...")
    result = compute_match_result(cv_profile, job)

    print("\n=== RESULTADO FINAL ===")
    print(f"Score global: {result.overall_score}%")
    print(f"    - Hard skills: {result.hard_skills_score}%")
    print(f"    - Soft skills: {result.soft_skills_score}%")
    print(f"Keywords faltantes: {result.missing_keywords}")

if __name__ == "__main__":
    test_full_pipeline()