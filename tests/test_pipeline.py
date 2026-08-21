from app.pipeline import run_full_pipeline

DUMMY_CV_TEXT = """
Juan Pérez
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

def test_full_pipeline_orchestrator():
    print("Corriendo pipeline completo...\n")
    result = run_full_pipeline(DUMMY_CV_TEXT, DUMMY_JOB_TEXT)

    print("=" * 50)
    print(f"⏱️  TIEMPO DE PROCESAMIENTO: {result.processing_time_seconds}s")
    print(f"    (vs. ~45 min = 2700s del proceso manual)")
    print(f"    Reduccion: {round((1- result.processing_time_seconds / 2700) * 100, 1)}%")
    print("=" * 50)

    print(f"\n📊 Score de compatibilidad: {result.match_result.overall_score}%")
    print(f"👤 Candidato: {result.cv_profile.full_name}")
    print(f"💼 Puesto: {result.job_description.job_title}")
    print(f"📝 CV adaptado: {len(result.adapted_cv.experience)} experiencias reescritas")
    print(f"✉️  Cover letter: tono '{result.cover_letter.tone_used}'")
    print(f"🎤 Kit de entrevista: {len(result.interview_kit.questions)} preguntas")

if __name__ == "__main__":
    test_full_pipeline_orchestrator()