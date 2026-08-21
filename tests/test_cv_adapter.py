from app.cv_parser import parse_cv_to_profile
from app.job_extractor import parse_job_to_description
from app.match_engine import compute_match_result
from app.cv_adapter import adapt_cv

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

def test_cv_adapter():
    print("1/4 - Parseando CV...")
    cv = parse_cv_to_profile(DUMMY_CV_TEXT)

    print("2/4 - Parseando oferta laboral...")
    job = parse_job_to_description(DUMMY_JOB_TEXT)

    print("3/4 - Calculando match...")
    match = compute_match_result(cv, job)
    print(f"    Score: {match.overall_score}% | Gaps: {match.missing_keywords}\n")

    print("4/4 - Adaptando CV...\n")
    adapted = adapt_cv(cv, job, match)

    print("=== HEADLINE ===")
    print(f"Antes:  {cv.headline}")
    print(f"Despues:{adapted.headline}\n")

    print("=== SUMMARY ===")
    print(f"Antes:  {cv.summary}")
    print(f"Despues:{adapted.summary}\n")

    print("=== BULLETS (Antes / Despues) ===")
    for exp in adapted.experience:
        print(f"\n{exp.role} @ {exp.company}")
        for bullet in exp.bullets:
            print(f"    Antes:  {bullet.original}")
            print(f"    Despues:{bullet.adapted}\n")

    print("=== SKILLS DESTACADOS (reordenados) ===")
    print(adapted.highlighted_skills)

if __name__ == "__main__":
    test_cv_adapter()