import logging

from fastapi import APIRouter, status

from app.api.deps import DbSession
from app.repositories.dashboard_repository import get_dashboard_stats
from app.schemas.dashboard import DashboardStats, RecentEvaluation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats, status_code=status.HTTP_200_OK)
async def get_dashboard_route(db: DbSession) -> DashboardStats:
    stats = await get_dashboard_stats(db)
    return DashboardStats(
        candidate_count=stats.candidate_count,
        average_score=stats.average_score,
        strong_match_count=stats.strong_match_count,
        recent_evaluations=[
            RecentEvaluation(
                evaluation_id=row.evaluation_id,
                job_id=row.job_id,
                candidate_name=row.candidate_name,
                job_title=row.job_title,
                score=row.score,
                fit_level=row.fit_level,
                created_at=row.created_at,
            )
            for row in stats.recent_evaluations
        ],
    )
