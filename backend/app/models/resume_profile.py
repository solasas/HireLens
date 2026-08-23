import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ResumeProfile(Base):
    """The structured data an LLM extracts from a resume's raw text."""

    __tablename__ = "resume_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    skills: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    education: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    experience: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    projects: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    certifications: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)

    extraction_version: Mapped[str] = mapped_column(String(50), nullable=False)
    llm_model: Mapped[str] = mapped_column(String(100), nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    resume: Mapped["Resume"] = relationship(back_populates="profile")
