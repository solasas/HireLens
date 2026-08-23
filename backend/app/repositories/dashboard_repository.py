from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.evaluation import Evaluation
from app.models.job_description import JobDescription

RECENT_EVALUATIONS_LIMIT = 10
STRONG_FIT_LABEL = "Strong Fit"


@dataclass(frozen=True)
class RecentEvaluationRow:
    evaluation_id: UUID
    job_id: UUID
    candidate_name: str
    job_title: str
    score: float
    fit_level: str
    created_at: datetime


@dataclass(frozen=True)
class DashboardStatsRow:
    candidate_count: int
    average_score: float | None
    strong_match_count: int
    recent_evaluations: list[RecentEvaluationRow]


async def get_dashboard_stats(session: AsyncSession) -> DashboardStatsRow:
    candidate_count = (await session.execute(select(func.count(Candidate.id)))).scalar_one()

    average_score = (await session.execute(select(func.avg(Evaluation.overall_score)))).scalar_one()

    strong_match_count = (
        await session.execute(
            select(func.count(Evaluation.id)).where(
                Evaluation.llm_explanation["fit_level"].astext == STRONG_FIT_LABEL
            )
        )
    ).scalar_one()

    recent_stmt = (
        select(
            Evaluation.id,
            Evaluation.overall_score,
            Evaluation.llm_explanation["fit_level"].astext.label("fit_level"),
            Evaluation.created_at,
            Candidate.full_name,
            JobDescription.id.label("job_id"),
            JobDescription.title.label("job_title"),
        )
        .join(Candidate, Candidate.id == Evaluation.candidate_id)
        .join(JobDescription, JobDescription.id == Evaluation.job_description_id)
        .order_by(Evaluation.created_at.desc())
        .limit(RECENT_EVALUATIONS_LIMIT)
    )
    recent_rows = (await session.execute(recent_stmt)).all()

    return DashboardStatsRow(
        candidate_count=candidate_count,
        average_score=float(average_score) if average_score is not None else None,
        strong_match_count=strong_match_count,
        recent_evaluations=[
            RecentEvaluationRow(
                evaluation_id=row.id,
                job_id=row.job_id,
                candidate_name=row.full_name,
                job_title=row.job_title,
                score=float(row.overall_score),
                fit_level=row.fit_level,
                created_at=row.created_at,
            )
            for row in recent_rows
        ],
    )
