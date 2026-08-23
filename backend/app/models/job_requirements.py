import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JobRequirements(Base):
    """The structured data an LLM extracts from a job description's raw text."""

    __tablename__ = "job_requirements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_description_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    required_skills: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    preferred_skills: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    required_experience_years: Mapped[float | None] = mapped_column(Numeric(4, 1), nullable=True)
    education_requirement: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    responsibilities: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)

    extraction_version: Mapped[str] = mapped_column(String(50), nullable=False)
    llm_model: Mapped[str] = mapped_column(String(100), nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_description: Mapped["JobDescription"] = relationship(back_populates="requirements")
