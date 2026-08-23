from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate


async def get_or_create_candidate(
    session: AsyncSession, *, full_name: str, email: str | None, phone: str | None
) -> Candidate:
    """Dedupes by email (case-insensitive) when one was extracted. A
    resume with no extractable email always creates a new Candidate —
    there's nothing reliable to dedupe against, and guessing would risk
    merging two different people."""
    if email:
        stmt = select(Candidate).where(func.lower(Candidate.email) == email.lower())
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing

    candidate = Candidate(full_name=full_name, email=email, phone=phone)
    session.add(candidate)
    await session.flush()
    return candidate
