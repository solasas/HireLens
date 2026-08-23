import pytest

from app.schemas.job_extraction import JobExtraction
from app.services.job_extraction_service import extract_job_description
from tests.factories.llm import FakeLLMProvider


@pytest.mark.asyncio
async def test_extract_job_description_returns_result_on_success() -> None:
    extraction = JobExtraction(
        job_title="Backend Engineer",
        required_skills=["Python", "PostgreSQL"],
        preferred_skills=["Kubernetes"],
    )
    llm = FakeLLMProvider([extraction])

    result = await extract_job_description("We need a backend engineer...", llm=llm)

    assert result.job_title == "Backend Engineer"
    assert result.required_skills == ["Python", "PostgreSQL"]
    assert result.preferred_skills == ["Kubernetes"]


@pytest.mark.asyncio
async def test_extract_job_description_includes_source_text_in_prompt() -> None:
    llm = FakeLLMProvider([JobExtraction()])

    await extract_job_description("Unique marker: senior platform engineer role", llm=llm)

    assert "Unique marker: senior platform engineer role" in llm.prompts[0]
