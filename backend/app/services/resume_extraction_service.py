import logging

from app.core.exceptions import LLMResponseValidationError
from app.schemas.resume_extraction import ResumeExtraction
from app.services.duration import compute_duration_months
from app.services.llm.base import LLMProvider
from app.services.llm.prompts.resume_extraction import build_resume_extraction_prompt

logger = logging.getLogger(__name__)


async def extract_resume(resume_text: str, *, llm: LLMProvider) -> ResumeExtraction:
    """Run structured extraction over a resume's plain text.

    On an invalid first response, retries exactly once with the
    validation error appended to the prompt — this catches a model
    momentarily drifting from the schema without masking a genuinely
    broken provider (the second failure propagates as-is).
    """
    prompt = build_resume_extraction_prompt(resume_text)

    try:
        extraction = await llm.extract_structured(prompt=prompt, schema=ResumeExtraction)
    except LLMResponseValidationError as exc:
        logger.warning("Resume extraction failed validation, retrying once: %s", exc.message)
        retry_prompt = (
            f"{prompt}\n\nYour previous response was invalid: {exc.message}\n"
            "Return valid JSON matching the required schema exactly."
        )
        extraction = await llm.extract_structured(prompt=retry_prompt, schema=ResumeExtraction)

    return _apply_computed_durations(extraction)


def _apply_computed_durations(extraction: ResumeExtraction) -> ResumeExtraction:
    updated_experience = []
    for entry in extraction.experience:
        computed = compute_duration_months(entry.start_date, entry.end_date)
        if computed is not None:
            entry = entry.model_copy(update={"duration_months": computed})
        updated_experience.append(entry)
    return extraction.model_copy(update={"experience": updated_experience})
