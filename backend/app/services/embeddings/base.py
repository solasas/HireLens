from typing import Protocol


class EmbeddingProvider(Protocol):
    """A provider that turns text into embedding vectors.

    Concrete implementations (GeminiEmbeddingProvider, and later an
    OpenAI one) are the only code that knows which vendor SDK is in use.
    Mirrors the role app.services.llm.base.LLMProvider plays for text
    generation — nothing above this line should import a concrete
    provider directly.
    """

    model_name: str

    async def embed_text(self, text: str) -> list[float]: ...

    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
