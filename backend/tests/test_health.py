import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db
from app.main import app


class _FakeSession:
    """Stands in for an AsyncSession so this test needs no live database."""

    async def execute(self, *_args: object, **_kwargs: object) -> None:
        return None

    async def rollback(self) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def close(self) -> None:
        return None


async def _fake_get_db():
    yield _FakeSession()


@pytest.mark.asyncio
async def test_health_check_reports_ok_when_database_is_reachable() -> None:
    app.dependency_overrides[get_db] = _fake_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["components"] == [{"name": "database", "status": "up", "detail": None}]


@pytest.mark.asyncio
async def test_health_check_reports_degraded_when_database_is_unreachable() -> None:
    class _BrokenSession(_FakeSession):
        async def execute(self, *_args: object, **_kwargs: object) -> None:
            raise ConnectionError("could not connect to server")

    async def _broken_get_db():
        yield _BrokenSession()

    app.dependency_overrides[get_db] = _broken_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["components"][0]["status"] == "down"
