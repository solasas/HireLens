import uuid

from sqlalchemy import Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Nullable: extraction can't always find an email on a resume, and
    # fabricating a placeholder to satisfy NOT NULL would be worse than
    # just not deduping that candidate. Postgres treats NULL as distinct
    # from every other NULL in a unique index, so this doesn't weaken
    # the case-insensitive uniqueness guarantee below for candidates
    # that *do* have an email.
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Case-insensitive uniqueness without depending on the citext extension.
        Index("uq_candidates_email_lower", func.lower(email), unique=True),
    )

    def __repr__(self) -> str:
        return f"Candidate(id={self.id!r}, email={self.email!r})"
