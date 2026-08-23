import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.factories.pdf import make_text_pdf


@pytest.mark.asyncio
async def test_parse_resume_route_returns_extracted_text() -> None:
    pdf_bytes = make_text_pdf(["Alex Rivera\nBackend Engineer"])

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/resumes/parse",
            files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["file_name"] == "resume.pdf"
    assert body["page_count"] == 1
    assert "Alex Rivera" in body["text"]


@pytest.mark.asyncio
async def test_parse_resume_route_maps_invalid_file_to_400() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/resumes/parse",
            files={"file": ("resume.pdf", b"not a real pdf", "application/pdf")},
        )

    assert response.status_code == 400
    assert "detail" in response.json()
