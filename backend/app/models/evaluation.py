import uuid
from typing import Any

from sqlalchemy import ForeignKey, Index, Numeric, String, UniqueConstraint, desc
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Evaluation(Base, TimestampMixin):
    """One row per (candidate, job) pair, for one scoring run.

    Links to Candidate directly, not through Resume — matches the given
    relationship diagram (Candidate 1-N Evaluation). The trade-off: if a
    candidate has multiple resumes on file, an evaluation doesn't record
    which one produced it. Acceptable for a candidate normally having one
    current resume; worth revisiting if multi-resume tracking matters.

    The five sub-scores and the final overall_score stay individual,
    typed Numeric columns — the candidate-ranking endpoint sorts on them
    directly (ORDER BY), which a JSONB blob would make slower and
    clumsier. Everything else the LLM produces (fit_level, matched/
    missing skills, strengths, concerns, the narrative recommendation)
    is never filtered or sorted on, only ever read back whole, so it's
    one JSONB column — llm_explanation — instead of seven.
    """

    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False
    )
    job_description_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False
    )

    skill_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    experience_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    education_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    semantic_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    project_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    overall_score: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)

    llm_explanation: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    scoring_version: Mapped[str] = mapped_column(String(50), nullable=False)

    candidate: Mapped["Candidate"] = relationship()
    job_description: Mapped["JobDescription"] = relationship()

    __table_args__ = (
        # Re-evaluating creates a new row under a new scoring_version rather
        # than overwriting history.
        UniqueConstraint(
            "candidate_id",
            "job_description_id",
            "scoring_version",
            name="uq_evaluations_candidate_job_scoring_version",
        ),
        Index("ix_evaluations_job_description_id", "job_description_id"),
        Index("ix_evaluations_candidate_id", "candidate_id"),
        # Matches the ranking query's ORDER BY exactly (see
        # evaluation_repository.list_ranked_evaluations) — the whole
        # point of this index is to make GET /jobs/{id}/candidates a
        # sorted index scan instead of a full sort on every request.
        Index(
            "ix_evaluations_ranking",
            "job_description_id",
            desc("overall_score"),
            desc("skill_score"),
            "created_at",
        ),
    )
