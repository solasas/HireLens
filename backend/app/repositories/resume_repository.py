import hashlib
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.schemas.resume_extraction import ResumeExtraction


async def create_resume(
    session: AsyncSession,
    *,
    candidate_id: uuid.UUID,
    file_name: str,
    raw_text: str,
    extraction: ResumeExtraction,
    extraction_version: str,
    llm_model: str,
) -> Resume:
    """Re-uploading identical text for the same candidate is a no-op —
    returns the existing row instead of violating the
    (candidate_id, content_hash) uniqueness constraint."""
    content_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    existing_stmt = select(Resume).where(
        Resume.candidate_id == candidate_id, Resume.content_hash == content_hash
    )
    existing = (await session.execute(existing_stmt)).scalar_one_or_none()
    if existing is not None:
        return existing

    resume = Resume(
        candidate_id=candidate_id,
        file_name=file_name,
        raw_text=raw_text,
        structured_data=extraction.model_dump(),
        content_hash=content_hash,
        extraction_version=extraction_version,
        llm_model=llm_model,
    )
    session.add(resume)
    await session.flush()
    return resume
