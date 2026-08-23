from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.gemini_provider import GeminiEmbeddingProvider


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    """Construct the configured EmbeddingProvider. Fails fast if the
    selected provider is misconfigured, rather than surfacing a
    confusing error deep inside a request."""
    if settings.embedding_provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("EMBEDDING_PROVIDER is 'gemini' but GEMINI_API_KEY is not set.")
        return GeminiEmbeddingProvider(
            api_key=settings.gemini_api_key, model_name=settings.gemini_embedding_model
        )

    raise NotImplementedError(
        f"Embedding provider '{settings.embedding_provider}' is not implemented yet. "
        "Only 'gemini' is currently available."
    )


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """FastAPI dependency: one provider instance per process."""
    return build_embedding_provider(get_settings())
