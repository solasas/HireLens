import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import Evaluation
from app.models.job_description import JobDescription
from app.schemas.job_extraction import JobExtraction


async def create_job(
    session: AsyncSession,
    *,
    raw_text: str,
    extraction: JobExtraction,
    extraction_version: str,
    llm_model: str,
) -> JobDescription:
    job = JobDescription(
        title=extraction.job_title or "Untitled role",
        raw_text=raw_text,
        structured_data=extraction.model_dump(),
        extraction_version=extraction_version,
        llm_model=llm_model,
    )
    session.add(job)
    await session.flush()
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> JobDescription | None:
    result = await session.execute(select(JobDescription).where(JobDescription.id == job_id))
    return result.scalar_one_or_none()


@dataclass(frozen=True)
class JobSummaryRow:
    job_id: uuid.UUID
    title: str
    candidate_count: int
    created_at: datetime


async def list_jobs(session: AsyncSession) -> list[JobSummaryRow]:
    stmt = (
        select(
            JobDescription.id,
            JobDescription.title,
            JobDescription.created_at,
            func.count(Evaluation.id).label("candidate_count"),
        )
        .outerjoin(Evaluation, Evaluation.job_description_id == JobDescription.id)
        .group_by(JobDescription.id)
        .order_by(JobDescription.created_at.desc())
    )
    rows = (await session.execute(stmt)).all()
    return [
        JobSummaryRow(
            job_id=row.id,
            title=row.title,
            candidate_count=row.candidate_count,
            created_at=row.created_at,
        )
        for row in rows
    ]
