import logging

from google import genai
from google.genai import types

from app.core.exceptions import EmbeddingProviderError

logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider:
    """EmbeddingProvider implementation backed by Google's Gemini API.

    Deliberately dumb: it embeds exactly what it's given, with no
    opinion about blank inputs, deduplication, or batching policy — that
    input-hygiene logic belongs to app.services.embedding_service, one
    layer up, so it isn't duplicated per vendor when a second provider
    is added.
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def embed_text(self, text: str) -> list[float]:
        vectors = await self.embed_documents([text])
        return vectors[0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        # A plain list[str] gets treated by this API as one combined
        # input rather than N independent documents — wrapping each
        # text in its own Content is what actually produces one
        # embedding per input. Verified against the live API; a bare
        # string list silently returns a single embedding instead of
        # raising, which is exactly the kind of mismatch the length
        # check below exists to catch.
        contents = [types.Content(parts=[types.Part(text=text)]) for text in texts]

        try:
            response = await self._client.aio.models.embed_content(
                model=self.model_name,
                contents=contents,
            )
        except Exception as exc:
            logger.warning("Gemini embedding request failed: %s", exc)
            raise EmbeddingProviderError(f"Embedding request failed: {exc}") from exc

        embeddings = getattr(response, "embeddings", None)
        if not embeddings or len(embeddings) != len(texts):
            raise EmbeddingProviderError(
                "Embedding response did not match the number of inputs."
            )

        return [list(item.values) for item in embeddings]
