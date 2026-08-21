from app.match_engine import compare_skill_lists

def test_gap_analysis_hybrid():
    job_skills = ["Python", "SQL", "Airflow", "dbt", "AWS"]

    cv_skills = [
        "Python",
        "PostgreSQL",
        "Google Cloud Platform",
        "Excel",
    ]

    results = compare_skill_lists(job_skills, cv_skills)

    print("=== GAP ANALYSIS (Fuzzy + LLM-Judge) ===\n")
    for r in results:
        status = "❌ GAP" if r["is_gap"] else "✅ MATCH"
        print(f"{status} | Requerido: {r['required_skill']:10} | "
              f"Match CV: {str(r['best_match_in_cv']):25} | "
              f"Razon: {r['reasoning']}")

if __name__ == "__main__":
    test_gap_analysis_hybrid()

