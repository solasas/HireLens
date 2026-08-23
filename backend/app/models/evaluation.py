import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Recommendation(str, enum.Enum):
    STRONG_FIT = "strong_fit"
    POSSIBLE_FIT = "possible_fit"
    NOT_A_FIT = "not_a_fit"


class Evaluation(Base):
    """One row per (resume, job) pair, for one scoring run."""

    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    job_description_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False
    )

    overall_score: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    skill_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    experience_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    education_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    semantic_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    project_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)

    matching_skills: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    missing_skills: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    relevant_experience: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    concerns: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    recommendation: Mapped[Recommendation] = mapped_column(
        Enum(Recommendation, native_enum=False, length=20, validate_strings=True), nullable=False
    )

    scoring_version: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    resume: Mapped["Resume"] = relationship()
    job_description: Mapped["JobDescription"] = relationship()

    __table_args__ = (
        # Re-evaluating creates a new row under a new scoring_version rather
        # than overwriting history.
        UniqueConstraint(
            "resume_id",
            "job_description_id",
            "scoring_version",
            name="uq_evaluations_resume_job_scoring_version",
        ),
    )
