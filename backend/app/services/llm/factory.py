from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.gemini_provider import GeminiProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    """Construct the configured LLMProvider. Fails fast at startup/first
    use if the selected provider is misconfigured, rather than surfacing
    a confusing error deep inside a request."""
    if settings.llm_provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("LLM_PROVIDER is 'gemini' but GEMINI_API_KEY is not set.")
        return GeminiProvider(api_key=settings.gemini_api_key, model_name=settings.gemini_model)

    raise NotImplementedError(
        f"LLM provider '{settings.llm_provider}' is not implemented yet. "
        "Only 'gemini' is currently available."
    )


@lru_cache
def get_llm_provider() -> LLMProvider:
    """FastAPI dependency: one provider instance per process."""
    return build_llm_provider(get_settings())
