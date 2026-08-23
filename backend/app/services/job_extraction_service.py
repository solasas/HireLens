from app.schemas.job_extraction import JobExtraction
from app.services.llm.base import LLMProvider
from app.services.llm.extraction import extract_with_retry
from app.services.llm.prompts.job_extraction import build_job_extraction_prompt


async def extract_job_description(job_description_text: str, *, llm: LLMProvider) -> JobExtraction:
    """Run structured extraction over a job description's plain text."""
    prompt = build_job_extraction_prompt(job_description_text)
    return await extract_with_retry(llm, prompt, JobExtraction)
