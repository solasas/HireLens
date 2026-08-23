"""A test double for app.services.embeddings.base.EmbeddingProvider.

Lives entirely under tests/ — the app never imports this.
"""


class FakeEmbeddingProvider:
    """Returns a configured vector per text, or raises a configured
    error. Records every batch it was called with, so tests can assert
    on call count and deduplication behavior."""

    def __init__(
        self,
        vectors_by_text: dict[str, list[float]] | None = None,
        error: Exception | None = None,
    ) -> None:
        self._vectors_by_text = vectors_by_text or {}
        self._error = error
        self.model_name = "fake-embedding-model"
        self.calls: list[list[str]] = []

    async def embed_text(self, text: str) -> list[float]:
        vectors = await self.embed_documents([text])
        return vectors[0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        if self._error is not None:
            raise self._error
        return [self._vectors_by_text[text] for text in texts]
