import logging
import uuid

from fastapi import APIRouter, status

from app.api.deps import DbSession
from app.core.exceptions import NotFoundError
from app.repositories.evaluation_repository import get_evaluation_detail
from app.schemas.evaluation import EvaluationDetail, ScoreBreakdown

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("/{evaluation_id}", response_model=EvaluationDetail, status_code=status.HTTP_200_OK)
async def get_evaluation_route(evaluation_id: uuid.UUID, db: DbSession) -> EvaluationDetail:
    row = await get_evaluation_detail(db, evaluation_id)
    if row is None:
        raise NotFoundError(f"Evaluation {evaluation_id} was not found.")

    explanation = row.llm_explanation
    return EvaluationDetail(
        evaluation_id=row.evaluation_id,
        candidate_id=row.candidate_id,
        candidate_name=row.candidate_name,
        job_id=row.job_id,
        job_title=row.job_title,
        score=row.overall_score,
        fit_level=explanation.get("fit_level", ""),
        score_breakdown=ScoreBreakdown(
            skill_score=row.skill_score,
            experience_score=row.experience_score,
            education_score=row.education_score,
            semantic_score=row.semantic_score,
            project_score=row.project_score,
        ),
        matched_skills=explanation.get("matched_skills", []),
        missing_required_skills=explanation.get("missing_required_skills", []),
        matched_preferred_skills=explanation.get("matched_preferred_skills", []),
        strengths=explanation.get("strengths", []),
        relevant_experience=explanation.get("relevant_experience", []),
        concerns=explanation.get("concerns", []),
        recommendation=explanation.get("recommendation", ""),
        created_at=row.created_at,
    )
