import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.job_extraction import JobExtraction
from app.services.llm.factory import get_llm_provider
from tests.factories.llm import FakeLLMProvider


@pytest.mark.asyncio
async def test_extract_job_route_returns_structured_requirements() -> None:
    extraction = JobExtraction(job_title="Backend Engineer", required_skills=["Python"])
    app.dependency_overrides[get_llm_provider] = lambda: FakeLLMProvider([extraction])
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/jobs/extract", json={"text": "We are hiring a backend engineer."}
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["job_title"] == "Backend Engineer"
    assert body["required_skills"] == ["Python"]


@pytest.mark.asyncio
async def test_extract_job_route_rejects_blank_text() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/jobs/extract", json={"text": "   "})

    assert response.status_code == 422
