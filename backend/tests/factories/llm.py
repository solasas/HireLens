"""A test double for app.services.llm.base.LLMProvider.

Lives entirely under tests/ — the app never imports this. It exists so
app.services.resume_extraction_service can be unit tested (retry
behavior, duration post-processing) without a real provider or network
access.
"""

from app.services.llm.base import SchemaT


class FakeLLMProvider:
    """Replays a fixed sequence of responses, one per call.

    Each entry in `responses` is either an Exception instance to raise or
    an already-built schema instance to return. Every prompt and
    system_instruction the caller passed in is recorded, so tests can
    assert on retry-prompt content and on the system/user separation
    itself (e.g. that untrusted resume text never appears in
    system_instruction).
    """

    def __init__(self, responses: list) -> None:
        self._responses = list(responses)
        self.model_name = "fake-model"
        self.prompts: list[str] = []
        self.system_instructions: list[str] = []

    async def extract_structured(
        self, *, system_instruction: str, prompt: str, schema: type[SchemaT]
    ) -> SchemaT:
        self.system_instructions.append(system_instruction)
        self.prompts.append(prompt)
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response
