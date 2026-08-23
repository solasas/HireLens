import pytest

from app.core.exceptions import EmbeddingProviderError
from app.services.embedding_service import embed_documents, embed_text
from tests.factories.embeddings import FakeEmbeddingProvider


@pytest.mark.asyncio
async def test_embed_text_returns_empty_vector_for_blank_text_without_calling_provider() -> None:
    provider = FakeEmbeddingProvider()

    result = await embed_text("   ", provider=provider)

    assert result == []
    assert provider.calls == []


@pytest.mark.asyncio
async def test_embed_text_calls_provider_for_non_blank_text() -> None:
    provider = FakeEmbeddingProvider({"hello": [1.0, 0.0]})

    result = await embed_text("hello", provider=provider)

    assert result == [1.0, 0.0]
    assert provider.calls == [["hello"]]


@pytest.mark.asyncio
async def test_embed_documents_returns_empty_list_for_empty_input() -> None:
    provider = FakeEmbeddingProvider()

    result = await embed_documents([], provider=provider)

    assert result == []
    assert provider.calls == []


@pytest.mark.asyncio
async def test_embed_documents_skips_blank_entries_but_embeds_others() -> None:
    provider = FakeEmbeddingProvider({"python": [1.0, 0.0]})

    result = await embed_documents(["python", "", "   "], provider=provider)

    assert result == [[1.0, 0.0], [], []]
    assert provider.calls == [["python"]]


@pytest.mark.asyncio
async def test_embed_documents_deduplicates_repeated_text() -> None:
    provider = FakeEmbeddingProvider({"python": [1.0, 0.0]})

    result = await embed_documents(["python", "python"], provider=provider)

    assert result == [[1.0, 0.0], [1.0, 0.0]]
    # Sent to the provider once, not twice.
    assert provider.calls == [["python"]]


@pytest.mark.asyncio
async def test_embed_documents_all_blank_returns_placeholders_without_calling_provider() -> None:
    provider = FakeEmbeddingProvider()

    result = await embed_documents(["", "  "], provider=provider)

    assert result == [[], []]
    assert provider.calls == []


@pytest.mark.asyncio
async def test_embed_documents_propagates_provider_failure() -> None:
    provider = FakeEmbeddingProvider(error=EmbeddingProviderError("boom"))

    with pytest.raises(EmbeddingProviderError):
        await embed_documents(["python"], provider=provider)
