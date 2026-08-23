import uuid

from pydantic import BaseModel


class RankedCandidate(BaseModel):
    rank: int
    candidate_id: uuid.UUID
    evaluation_id: uuid.UUID
    name: str
    score: float
    fit_level: str


class JobCandidateRanking(BaseModel):
    job_id: uuid.UUID
    page: int
    page_size: int
    total: int
    candidates: list[RankedCandidate]
