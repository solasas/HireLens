import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.main import app
from tests.test_evaluation_repository_ranking import _add_evaluation, _make_job


async def _get(db_session: AsyncSession, url: str, **params):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(url, params=params or None)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_jobs_returns_candidate_counts(db_session: AsyncSession) -> None:
    job_with_candidates = await _make_job(db_session)
    await _add_evaluation(db_session, job_with_candidates.id, full_name="A", overall_score=8.0)
    await _add_evaluation(db_session, job_with_candidates.id, full_name="B", overall_score=6.0)
    empty_job = await _make_job(db_session)

    response = await _get(db_session, "/api/v1/jobs")

    assert response.status_code == 200
    by_id = {row["job_id"]: row for row in response.json()}
    assert by_id[str(job_with_candidates.id)]["candidate_count"] == 2
    assert by_id[str(empty_job.id)]["candidate_count"] == 0


@pytest.mark.asyncio
async def test_get_job_detail_returns_structured_data(db_session: AsyncSession) -> None:
    job = await _make_job(db_session)

    response = await _get(db_session, f"/api/v1/jobs/{job.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == str(job.id)
    assert body["structured_data"]["required_skills"] == ["Python"]


@pytest.mark.asyncio
async def test_get_job_detail_404_for_unknown_job(db_session: AsyncSession) -> None:
    response = await _get(db_session, f"/api/v1/jobs/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_evaluation_detail_returns_full_breakdown(db_session: AsyncSession) -> None:
    job = await _make_job(db_session)
    evaluation = await _add_evaluation(
        db_session, job.id, full_name="Jordan Rivera", overall_score=7.5, skill_score=0.6
    )

    response = await _get(db_session, f"/api/v1/evaluations/{evaluation.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["candidate_name"] == "Jordan Rivera"
    assert body["job_title"] == "Test Job"
    assert body["score"] == 7.5
    assert body["fit_level"] == "Moderate Fit"
    assert body["score_breakdown"]["skill_score"] == 0.6
    assert "recommendation" in body
    assert "concerns" in body


@pytest.mark.asyncio
async def test_get_evaluation_detail_404_for_unknown_evaluation(db_session: AsyncSession) -> None:
    response = await _get(db_session, f"/api/v1/evaluations/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dashboard_reports_counts_and_average(db_session: AsyncSession) -> None:
    """Asserts deltas and the top of recent_evaluations, not absolute
    counts — the dashboard is a genuinely global, unscoped aggregate
    (that's its job), so this test can't assume it's the only data in
    the database. A shared dev DB with prior rows is normal, not a bug."""
    baseline = (await _get(db_session, "/api/v1/dashboard")).json()

    job = await _make_job(db_session)
    await _add_evaluation(db_session, job.id, full_name="Strong Candidate", overall_score=9.0)
    await _add_evaluation(db_session, job.id, full_name="Weak Candidate", overall_score=3.0)

    response = await _get(db_session, "/api/v1/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["candidate_count"] == baseline["candidate_count"] + 2
    assert body["average_score"] is not None
    assert len(body["recent_evaluations"]) >= 2
    newest_two_names = {row["candidate_name"] for row in body["recent_evaluations"][:2]}
    assert newest_two_names == {"Strong Candidate", "Weak Candidate"}


@pytest.mark.asyncio
async def test_dashboard_handles_no_evaluations_yet(db_session: AsyncSession) -> None:
    """Clears every row within this test's own (later rolled-back)
    transaction to get a genuinely empty state to assert against,
    rather than requiring the shared dev database to already be empty."""
    await db_session.execute(text("DELETE FROM evaluations"))
    await db_session.execute(text("DELETE FROM resumes"))
    await db_session.execute(text("DELETE FROM job_descriptions"))
    await db_session.execute(text("DELETE FROM candidates"))

    response = await _get(db_session, "/api/v1/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["candidate_count"] == 0
    assert body["average_score"] is None
    assert body["strong_match_count"] == 0
    assert body["recent_evaluations"] == []
