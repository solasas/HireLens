from app.schemas.resume_extraction import ResumeExtraction
from app.services.duration import compute_duration_months
from app.services.llm.base import LLMProvider
from app.services.llm.extraction import extract_with_retry
from app.services.llm.prompts.resume_extraction import (
    SYSTEM_INSTRUCTIONS,
    build_resume_extraction_prompt,
)


async def extract_resume(resume_text: str, *, llm: LLMProvider) -> ResumeExtraction:
    """Run structured extraction over a resume's plain text, then
    override duration_months deterministically (see app.services.duration)."""
    prompt = build_resume_extraction_prompt(resume_text)
    extraction = await extract_with_retry(
        llm, system_instruction=SYSTEM_INSTRUCTIONS, prompt=prompt, schema=ResumeExtraction
    )
    return _apply_computed_durations(extraction)


def _apply_computed_durations(extraction: ResumeExtraction) -> ResumeExtraction:
    updated_experience = []
    for entry in extraction.experience:
        computed = compute_duration_months(entry.start_date, entry.end_date)
        if computed is not None:
            entry = entry.model_copy(update={"duration_months": computed})
        updated_experience.append(entry)
    return extraction.model_copy(update={"experience": updated_experience})
