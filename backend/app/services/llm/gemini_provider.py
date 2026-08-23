import json
import logging

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.core.exceptions import LLMProviderError, LLMResponseValidationError
from app.services.llm.base import SchemaT

logger = logging.getLogger(__name__)


class GeminiProvider:
    """LLMProvider implementation backed by Google's Gemini API."""

    def __init__(self, api_key: str, model_name: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def extract_structured(self, *, prompt: str, schema: type[SchemaT]) -> SchemaT:
        try:
            response = await self._client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0,
                ),
            )
        except Exception as exc:
            # Anything from the SDK itself (rate limits, quota, network,
            # server overload) — not just schema-validation failures —
            # needs to surface as a typed AppError. Left unwrapped, it
            # hits the generic 500 handler instead of the 502 this
            # actually is, and (per live testing) a response that never
            # goes through our own AppError path is exactly the case
            # that produced an opaque "Network Error" in the frontend
            # instead of the real message.
            logger.warning("Gemini generate_content request failed: %s", exc)
            raise LLMProviderError(f"LLM request failed: {exc}") from exc

        text = response.text
        if not text:
            raise LLMResponseValidationError("The model returned an empty response.")

        try:
            return schema.model_validate_json(text)
        except (ValidationError, json.JSONDecodeError) as exc:
            logger.warning("Gemini response failed schema validation: %s", exc)
            raise LLMResponseValidationError(
                f"Model response did not match the expected schema: {exc}"
            ) from exc
