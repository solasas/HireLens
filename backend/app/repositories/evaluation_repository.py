import uuid
from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.scoring import MatchResult
from app.models.candidate import Candidate
from app.models.evaluation import Evaluation
from app.models.job_description import JobDescription
from app.schemas.evaluation import CandidateEvaluation


async def create_evaluation(
    session: AsyncSession,
    *,
    candidate_id: uuid.UUID,
    job_description_id: uuid.UUID,
    match: MatchResult,
    evaluation: CandidateEvaluation,
    scoring_version: str,
) -> Evaluation:
    row = Evaluation(
        candidate_id=candidate_id,
        job_description_id=job_description_id,
        overall_score=evaluation.score,
        skill_score=match.skill_score,
        experience_score=match.experience_score,
        education_score=match.education_score,
        semantic_score=match.semantic_score,
        project_score=match.project_score,
        llm_explanation={
            "fit_level": evaluation.fit_level.value,
            "matched_skills": match.matched_skills,
            "missing_required_skills": match.missing_required_skills,
            "matched_preferred_skills": match.matched_preferred_skills,
            "strengths": evaluation.strengths,
            "relevant_experience": evaluation.relevant_experience,
            "concerns": evaluation.concerns,
            "recommendation": evaluation.recommendation,
        },
        scoring_version=scoring_version,
    )
    session.add(row)
    await session.flush()
    return row


async def delete_evaluation(session: AsyncSession, evaluation_id: uuid.UUID) -> bool:
    """Returns True if a row was deleted, False if no evaluation had that id."""
    result = await session.execute(delete(Evaluation).where(Evaluation.id == evaluation_id))
    return result.rowcount > 0


@dataclass(frozen=True)
class RankedEvaluationRow:
    """One row of a ranking query result — just what the ranking
    endpoint needs, not the full ORM entity graph."""

    evaluation_id: uuid.UUID
    candidate_id: uuid.UUID
    candidate_name: str
    score: float
    fit_level: str


async def list_ranked_evaluations(
    session: AsyncSession, *, job_description_id: uuid.UUID, limit: int, offset: int
) -> tuple[list[RankedEvaluationRow], int]:
    """Ranked by overall_score descending. Ties are broken
    deterministically — skill_score descending (the highest-weighted
    component), then created_at ascending (earliest-evaluated wins,
    using clock_timestamp() so rows inserted in the same transaction
    still get distinct values), then id ascending as an absolute final
    tiebreak — so the order is identical across repeated calls no
    matter how many fields tie. Matches ix_evaluations_ranking exactly.
    """
    base_stmt = (
        select(
            Evaluation.id,
            Evaluation.overall_score,
            Evaluation.llm_explanation["fit_level"].astext.label("fit_level"),
            Evaluation.skill_score,
            Evaluation.created_at,
            Candidate.id.label("candidate_id"),
            Candidate.full_name,
        )
        .join(Candidate, Candidate.id == Evaluation.candidate_id)
        .where(Evaluation.job_description_id == job_description_id)
    )

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    ranked_stmt = (
        base_stmt.order_by(
            Evaluation.overall_score.desc(),
            Evaluation.skill_score.desc(),
            Evaluation.created_at.asc(),
            Evaluation.id.asc(),
        )
        .limit(limit)
        .offset(offset)
    )
    rows = (await session.execute(ranked_stmt)).all()

    ranked = [
        RankedEvaluationRow(
            evaluation_id=row.id,
            candidate_id=row.candidate_id,
            candidate_name=row.full_name,
            score=float(row.overall_score),
            fit_level=row.fit_level,
        )
        for row in rows
    ]
    return ranked, total


@dataclass(frozen=True)
class EvaluationDetailRow:
    """Everything needed to render a full evaluation — one query,
    joined against both Candidate and JobDescription for their names."""

    evaluation_id: uuid.UUID
    candidate_id: uuid.UUID
    candidate_name: str
    job_id: uuid.UUID
    job_title: str
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    semantic_score: float
    project_score: float
    llm_explanation: dict
    created_at: object


async def get_evaluation_detail(
    session: AsyncSession, evaluation_id: uuid.UUID
) -> EvaluationDetailRow | None:
    stmt = (
        select(
            Evaluation.id,
            Evaluation.overall_score,
            Evaluation.skill_score,
            Evaluation.experience_score,
            Evaluation.education_score,
            Evaluation.semantic_score,
            Evaluation.project_score,
            Evaluation.llm_explanation,
            Evaluation.created_at,
            Candidate.id.label("candidate_id"),
            Candidate.full_name,
            JobDescription.id.label("job_id"),
            JobDescription.title.label("job_title"),
        )
        .join(Candidate, Candidate.id == Evaluation.candidate_id)
        .join(JobDescription, JobDescription.id == Evaluation.job_description_id)
        .where(Evaluation.id == evaluation_id)
    )
    row = (await session.execute(stmt)).first()
    if row is None:
        return None

    return EvaluationDetailRow(
        evaluation_id=row.id,
        candidate_id=row.candidate_id,
        candidate_name=row.full_name,
        job_id=row.job_id,
        job_title=row.job_title,
        overall_score=float(row.overall_score),
        skill_score=float(row.skill_score),
        experience_score=float(row.experience_score),
        education_score=float(row.education_score),
        semantic_score=float(row.semantic_score),
        project_score=float(row.project_score),
        llm_explanation=row.llm_explanation,
        created_at=row.created_at,
    )
