"""Integration tests for the ranking query against a real Postgres
database — ordering, tie-breaking, and pagination all depend on genuine
SQL behavior that a mock can't stand in for."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.evaluation import Evaluation
from app.models.job_description import JobDescription
from app.repositories.evaluation_repository import list_ranked_evaluations


async def _make_job(session: AsyncSession) -> JobDescription:
    job = JobDescription(
        title="Test Job",
        raw_text="job description text",
        structured_data={"required_skills": ["Python"]},
        extraction_version="test",
        llm_model="test",
    )
    session.add(job)
    await session.flush()
    return job


async def _add_evaluation(
    session: AsyncSession,
    job_id,
    *,
    full_name: str,
    overall_score: float,
    skill_score: float = 0.5,
) -> Evaluation:
    candidate = Candidate(full_name=full_name, email=None)
    session.add(candidate)
    await session.flush()

    evaluation = Evaluation(
        candidate_id=candidate.id,
        job_description_id=job_id,
        overall_score=overall_score,
        skill_score=skill_score,
        experience_score=0.5,
        education_score=0.5,
        semantic_score=0.5,
        project_score=0.5,
        llm_explanation={
            "fit_level": "Moderate Fit",
            "matched_skills": [],
            "missing_required_skills": [],
            "matched_preferred_skills": [],
            "strengths": [],
            "relevant_experience": [],
            "concerns": [],
            "recommendation": "",
        },
        scoring_version="test",
    )
    session.add(evaluation)
    await session.flush()
    return evaluation


@pytest.mark.asyncio
async def test_candidates_are_ranked_by_score_descending(db_session: AsyncSession) -> None:
    job = await _make_job(db_session)
    await _add_evaluation(db_session, job.id, full_name="Low Scorer", overall_score=4.0)
    await _add_evaluation(db_session, job.id, full_name="High Scorer", overall_score=9.0)
    await _add_evaluation(db_session, job.id, full_name="Mid Scorer", overall_score=6.5)

    rows, total = await list_ranked_evaluations(
        db_session, job_description_id=job.id, limit=10, offset=0
    )

    assert total == 3
    assert [row.candidate_name for row in rows] == ["High Scorer", "Mid Scorer", "Low Scorer"]
    assert [row.score for row in rows] == [9.0, 6.5, 4.0]
    assert rows[0].fit_level == "Moderate Fit"


@pytest.mark.asyncio
async def test_tied_final_score_is_broken_by_skill_score(db_session: AsyncSession) -> None:
    job = await _make_job(db_session)
    await _add_evaluation(
        db_session, job.id, full_name="Tied Lower Skill", overall_score=7.0, skill_score=0.4
    )
    await _add_evaluation(
        db_session, job.id, full_name="Tied Higher Skill", overall_score=7.0, skill_score=0.8
    )

    rows, _ = await list_ranked_evaluations(db_session, job_description_id=job.id, limit=10, offset=0)

    assert [row.candidate_name for row in rows] == ["Tied Higher Skill", "Tied Lower Skill"]


@pytest.mark.asyncio
async def test_full_tie_is_stable_and_identical_across_repeated_calls(
    db_session: AsyncSession,
) -> None:
    job = await _make_job(db_session)
    await _add_evaluation(
        db_session, job.id, full_name="First Inserted", overall_score=5.0, skill_score=0.5
    )
    await _add_evaluation(
        db_session, job.id, full_name="Second Inserted", overall_score=5.0, skill_score=0.5
    )

    first_call, _ = await list_ranked_evaluations(
        db_session, job_description_id=job.id, limit=10, offset=0
    )
    second_call, _ = await list_ranked_evaluations(
        db_session, job_description_id=job.id, limit=10, offset=0
    )

    assert [row.candidate_name for row in first_call] == ["First Inserted", "Second Inserted"]
    assert [row.candidate_name for row in first_call] == [row.candidate_name for row in second_call]


@pytest.mark.asyncio
async def test_pagination_slices_the_ranked_list_without_gaps_or_overlap(
    db_session: AsyncSession,
) -> None:
    job = await _make_job(db_session)
    for index, score in enumerate([9.0, 8.0, 7.0, 6.0, 5.0]):
        await _add_evaluation(db_session, job.id, full_name=f"Candidate {index}", overall_score=score)

    page_one, total = await list_ranked_evaluations(
        db_session, job_description_id=job.id, limit=2, offset=0
    )
    page_two, _ = await list_ranked_evaluations(db_session, job_description_id=job.id, limit=2, offset=2)
    page_three, _ = await list_ranked_evaluations(
        db_session, job_description_id=job.id, limit=2, offset=4
    )

    assert total == 5
    assert [row.score for row in page_one] == [9.0, 8.0]
    assert [row.score for row in page_two] == [7.0, 6.0]
    assert [row.score for row in page_three] == [5.0]


@pytest.mark.asyncio
async def test_candidate_with_no_matched_preferred_skills_is_still_ranked(
    db_session: AsyncSession,
) -> None:
    """Requirement: don't discard a candidate just for missing preferred
    skills. The ranking query has no filter on llm_explanation at all —
    this proves a candidate with none still appears."""
    job = await _make_job(db_session)
    await _add_evaluation(db_session, job.id, full_name="No Preferred Match", overall_score=6.0)

    rows, total = await list_ranked_evaluations(
        db_session, job_description_id=job.id, limit=10, offset=0
    )

    assert total == 1
    assert rows[0].candidate_name == "No Preferred Match"


@pytest.mark.asyncio
async def test_ranking_is_scoped_to_the_given_job(db_session: AsyncSession) -> None:
    job_one = await _make_job(db_session)
    job_two = await _make_job(db_session)
    await _add_evaluation(db_session, job_one.id, full_name="Job One Candidate", overall_score=8.0)
    await _add_evaluation(db_session, job_two.id, full_name="Job Two Candidate", overall_score=8.0)

    rows, total = await list_ranked_evaluations(
        db_session, job_description_id=job_one.id, limit=10, offset=0
    )

    assert total == 1
    assert rows[0].candidate_name == "Job One Candidate"
