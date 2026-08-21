import time
from app.models import PipelineResult
from app.cv_parser import parse_cv_to_profile
from app.job_extractor import parse_job_to_description
from app.match_engine import compute_match_result
from app.cv_adapter import adapt_cv
from app.cover_letter_generator import generate_cover_letter
from app.interview_kit_generator import generate_interview_kit

def run_full_pipeline(cv_raw_text: str, job_raw_text: str) -> PipelineResult:
    """Orquesta el pipeline completo: parsers -> matching -> agentes generativos."""
    start_time = time.time()

    cv_profile = parse_cv_to_profile(cv_raw_text)
    job_description = parse_job_to_description(job_raw_text)
    match_result = compute_match_result(cv_profile, job_description)
    adapted_cv = adapt_cv(cv_profile, job_description, match_result)
    cover_letter = generate_cover_letter(cv_profile, job_description, match_result)
    interview_kit = generate_interview_kit(cv_profile, job_description, match_result)

    elapsed = round(time.time() - start_time, 2)

    return PipelineResult(
        cv_profile=cv_profile,
        job_description=job_description,
        match_result=match_result,
        adapted_cv=adapted_cv,
        cover_letter=cover_letter,
        interview_kit=interview_kit,
        processing_time_seconds=elapsed,
    )