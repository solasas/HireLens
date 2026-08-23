"""Shared retry policy for structured-extraction LLM calls.

Every extraction service (resume, job description, and whatever follows)
needs the same behavior: call the provider, and if the response fails
schema validation, retry exactly once with the validation error appended
to the prompt before giving up. Defined once here so it can't drift
between services.
"""

import logging

from app.core.exceptions import LLMResponseValidationError
from app.services.llm.base import LLMProvider, SchemaT

logger = logging.getLogger(__name__)


async def extract_with_retry(
    llm: LLMProvider, *, system_instruction: str, prompt: str, schema: type[SchemaT]
) -> SchemaT:
    try:
        return await llm.extract_structured(
            system_instruction=system_instruction, prompt=prompt, schema=schema
        )
    except LLMResponseValidationError as exc:
        logger.warning(
            "%s extraction failed validation, retrying once: %s", schema.__name__, exc.message
        )
        retry_prompt = (
            f"{prompt}\n\nYour previous response was invalid: {exc.message}\n"
            "Return valid JSON matching the required schema exactly."
        )
        return await llm.extract_structured(
            system_instruction=system_instruction, prompt=retry_prompt, schema=schema
        )
