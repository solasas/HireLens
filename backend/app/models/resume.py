import uuid
from typing import Any

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Resume(Base, TimestampMixin):
    """A candidate's uploaded resume — raw text plus the LLM's
    structured extraction, stored together rather than split into a
    separate one-to-one table. Nothing in this project ever queries
    into individual fields of the extraction (filter by a specific
    skill, etc.) — it's always read back whole — so a second table
    bought normalization with no real benefit."""

    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Nullable: no durable file-storage backend (S3/disk) exists yet in
    # this project. raw_text is retained and is what everything actually
    # operates on; storage_path stays null rather than holding a made-up
    # path until real file storage is implemented.
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    extraction_version: Mapped[str] = mapped_column(String(50), nullable=False)
    llm_model: Mapped[str] = mapped_column(String(100), nullable=False)

    candidate: Mapped["Candidate"] = relationship(back_populates="resumes")

    __table_args__ = (
        # Re-uploading the same file for the same candidate is a no-op, not a new row.
        UniqueConstraint("candidate_id", "content_hash", name="uq_resumes_candidate_content_hash"),
        Index("ix_resumes_candidate_id", "candidate_id"),
    )
