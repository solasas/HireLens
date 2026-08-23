from typing import Protocol, TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LLMProvider(Protocol):
    """A provider that can turn a prompt into a schema-validated object.

    Concrete implementations (GeminiProvider, and later OpenAIProvider)
    are the only code that knows which vendor SDK is in use. Everything
    above this line — the extraction service, the API route — depends
    only on this interface, so switching providers is a config change,
    not a rewrite.

    system_instruction and prompt are deliberately separate parameters,
    not one concatenated string. system_instruction carries the fixed
    extraction/evaluation rules and is never derived from user input;
    prompt carries the untrusted resume/job-description content (see
    app.services.llm.prompt_safety). Concrete providers must pass these
    to the vendor SDK's actual system/user channel separation — Gemini's
    GenerateContentConfig.system_instruction, for instance — not
    re-concatenate them into a single blob, which would throw away the
    one structural guarantee that untrusted content can't rewrite the
    rules it's being evaluated under.
    """

    model_name: str

    async def extract_structured(
        self, *, system_instruction: str, prompt: str, schema: type[SchemaT]
    ) -> SchemaT: ...
