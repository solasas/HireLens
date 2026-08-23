"""Text-to-vector embedding generation.

Wraps an EmbeddingProvider with the input-hygiene rules every caller
needs: never call the provider for blank text, never call it twice for
the same text within one batch, and always return a result aligned with
the input — including a placeholder for text that never reached the API.

Keeps embedding *generation* (this file — does I/O, can fail, costs
money) separate from similarity *scoring* (app.domain.scoring.semantic —
pure math on already-computed vectors, cannot fail, free to call as
often as needed). See app/services/semantic_matching_service.py for
where the two get combined.
"""

from app.services.embeddings.base import EmbeddingProvider


async def embed_text(text: str, *, provider: EmbeddingProvider) -> list[float]:
    """Empty or whitespace-only text returns [] without calling the provider."""
    if not text or not text.strip():
        return []
    vectors = await embed_documents([text], provider=provider)
    return vectors[0]


async def embed_documents(texts: list[str], *, provider: EmbeddingProvider) -> list[list[float]]:
    """One vector per input text, in the same order.

    Blank entries become [] without ever reaching the provider. Repeated
    non-blank text is sent to the provider once and the same vector is
    reused for every occurrence — a batch listing the same skill twice
    costs one embedding call for that text, not two.
    """
    if not texts:
        return []

    unique_non_blank = list(dict.fromkeys(text for text in texts if text and text.strip()))
    if not unique_non_blank:
        return [[] for _ in texts]

    embeddings = await provider.embed_documents(unique_non_blank)
    vector_by_text = dict(zip(unique_non_blank, embeddings))

    return [vector_by_text.get(text, []) for text in texts]
