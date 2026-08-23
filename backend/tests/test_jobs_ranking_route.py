import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.main import app
from tests.test_evaluation_repository_ranking import _add_evaluation, _make_job


@pytest.mark.asyncio
async def test_ranking_route_returns_ordered_candidates_with_absolute_rank(
    db_session: AsyncSession,
) -> None:
    job = await _make_job(db_session)
    await _add_evaluation(db_session, job.id, full_name="Low Scorer", overall_score=4.0)
    await _add_evaluation(db_session, job.id, full_name="High Scorer", overall_score=9.0)

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/jobs/{job.id}/candidates")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == str(job.id)
    assert body["total"] == 2
    assert [c["rank"] for c in body["candidates"]] == [1, 2]
    assert [c["name"] for c in body["candidates"]] == ["High Scorer", "Low Scorer"]
    assert body["candidates"][0]["score"] == 9.0
    assert body["candidates"][0]["fit_level"] == "Moderate Fit"


@pytest.mark.asyncio
async def test_ranking_route_second_page_continues_absolute_rank(db_session: AsyncSession) -> None:
    job = await _make_job(db_session)
    for index, score in enumerate([9.0, 8.0, 7.0]):
        await _add_evaluation(db_session, job.id, full_name=f"Candidate {index}", overall_score=score)

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/jobs/{job.id}/candidates", params={"page": 2, "page_size": 2}
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    # page_size=2, page=2 -> the 3rd-ranked candidate, rank continues from page 1.
    assert [c["rank"] for c in body["candidates"]] == [3]
    assert body["candidates"][0]["score"] == 7.0


@pytest.mark.asyncio
async def test_ranking_route_returns_404_for_unknown_job(db_session: AsyncSession) -> None:
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/jobs/{uuid.uuid4()}/candidates")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
