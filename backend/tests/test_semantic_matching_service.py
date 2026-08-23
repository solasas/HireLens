import pytest

from app.core.exceptions import EmbeddingProviderError
from app.services.semantic_matching_service import compute_semantic_match
from tests.factories.embeddings import FakeEmbeddingProvider


@pytest.mark.asyncio
async def test_identical_vectors_score_near_one() -> None:
    vector = [1.0, 0.0, 0.0]
    provider = FakeEmbeddingProvider(
        {
            "Python\nPostgreSQL\nBuilt a payments service": vector,
            "Python\nPostgreSQL\nBuild backend services": vector,
        }
    )

    score = await compute_semantic_match(
        candidate_skills=["Python", "PostgreSQL"],
        candidate_projects=[],
        candidate_experience=["Built a payments service"],
        job_requirements=["Python", "PostgreSQL"],
        job_responsibilities=["Build backend services"],
        provider=provider,
    )

    assert score == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_similar_vectors_score_highly_but_not_perfectly() -> None:
    provider = FakeEmbeddingProvider(
        {
            "candidate text": [1.0, 1.0, 0.0],
            "job text": [1.0, 0.9, 0.1],
        }
    )

    score = await compute_semantic_match(
        candidate_skills=["candidate text"],
        candidate_projects=[],
        candidate_experience=[],
        job_requirements=["job text"],
        job_responsibilities=[],
        provider=provider,
    )

    assert 0.9 < score < 1.0


@pytest.mark.asyncio
async def test_orthogonal_vectors_score_around_half() -> None:
    provider = FakeEmbeddingProvider(
        {
            "candidate text": [1.0, 0.0],
            "job text": [0.0, 1.0],
        }
    )

    score = await compute_semantic_match(
        candidate_skills=["candidate text"],
        candidate_projects=[],
        candidate_experience=[],
        job_requirements=["job text"],
        job_responsibilities=[],
        provider=provider,
    )

    assert score == pytest.approx(0.5)


@pytest.mark.asyncio
async def test_empty_candidate_input_returns_zero_without_calling_provider() -> None:
    provider = FakeEmbeddingProvider()

    score = await compute_semantic_match(
        candidate_skills=[],
        candidate_projects=[],
        candidate_experience=[],
        job_requirements=["Python"],
        job_responsibilities=[],
        provider=provider,
    )

    assert score == 0.0
    assert provider.calls == []


@pytest.mark.asyncio
async def test_empty_job_input_returns_zero_without_calling_provider() -> None:
    provider = FakeEmbeddingProvider()

    score = await compute_semantic_match(
        candidate_skills=["Python"],
        candidate_projects=[],
        candidate_experience=[],
        job_requirements=[],
        job_responsibilities=[],
        provider=provider,
    )

    assert score == 0.0
    assert provider.calls == []


@pytest.mark.asyncio
async def test_embedding_api_failure_degrades_to_zero_instead_of_raising() -> None:
    provider = FakeEmbeddingProvider(error=EmbeddingProviderError("provider unavailable"))

    score = await compute_semantic_match(
        candidate_skills=["Python"],
        candidate_projects=[],
        candidate_experience=[],
        job_requirements=["Python"],
        job_responsibilities=[],
        provider=provider,
    )

    assert score == 0.0
