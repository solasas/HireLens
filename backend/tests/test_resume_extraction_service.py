import pytest

from app.schemas.resume_extraction import ExperienceEntry, ResumeExtraction
from app.services.resume_extraction_service import extract_resume
from tests.factories.llm import FakeLLMProvider


@pytest.mark.asyncio
async def test_extract_resume_returns_result_on_first_success() -> None:
    extraction = ResumeExtraction(name="Jane Doe", email="jane@example.com")
    llm = FakeLLMProvider([extraction])

    result = await extract_resume("resume text", llm=llm)

    assert result.name == "Jane Doe"
    assert len(llm.prompts) == 1


@pytest.mark.asyncio
async def test_extract_resume_overrides_duration_months_when_dates_are_parseable() -> None:
    extraction = ResumeExtraction(
        experience=[
            ExperienceEntry(
                job_title="Engineer",
                start_date="Jan 2020",
                end_date="Jul 2020",
                duration_months=999,  # deliberately wrong; should be overridden
            )
        ]
    )
    llm = FakeLLMProvider([extraction])

    result = await extract_resume("resume text", llm=llm)

    assert result.experience[0].duration_months == 6


@pytest.mark.asyncio
async def test_extract_resume_leaves_duration_months_when_dates_are_unparseable() -> None:
    extraction = ResumeExtraction(
        experience=[
            ExperienceEntry(
                job_title="Engineer",
                start_date="a while back",
                end_date=None,
                duration_months=12,
            )
        ]
    )
    llm = FakeLLMProvider([extraction])

    result = await extract_resume("resume text", llm=llm)

    assert result.experience[0].duration_months == 12
