import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession, SettingsDep
from app.schemas.health import ComponentStatus, HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: DbSession, settings: SettingsDep) -> HealthResponse:
    components: list[ComponentStatus] = []

    try:
        await db.execute(text("SELECT 1"))
        components.append(ComponentStatus(name="database", status="up"))
    except Exception as exc:
        logger.exception("Database health check failed")
        # Leave the session in a clean state so the get_db dependency's
        # own commit-on-exit doesn't raise a second time on our way out.
        await db.rollback()
        components.append(ComponentStatus(name="database", status="down", detail=str(exc)))

    overall = "ok" if all(c.status == "up" for c in components) else "degraded"
    return HealthResponse(status=overall, version=settings.app_version, components=components)
