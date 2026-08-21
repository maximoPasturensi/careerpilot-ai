from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from google.genai import errors as genai_errors

def _is_retryable(exception: BaseException) -> bool:
    code = getattr(exception, "code", None) or getattr(exception, "status_code", None)
    if isinstance(exception, (genai_errors.ServerError, genai_errors.ClientError)):
        return code in (429,503)
    return False

llm_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception(_is_retryable),
    reraise=True,
)