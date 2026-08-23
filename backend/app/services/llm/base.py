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
    """

    model_name: str

    async def extract_structured(self, *, prompt: str, schema: type[SchemaT]) -> SchemaT: ...
