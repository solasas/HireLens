import uuid
from datetime import datetime

from pydantic import BaseModel


class RecentEvaluation(BaseModel):
    evaluation_id: uuid.UUID
    job_id: uuid.UUID
    candidate_name: str
    job_title: str
    score: float
    fit_level: str
    created_at: datetime


class DashboardStats(BaseModel):
    candidate_count: int
    average_score: float | None
    strong_match_count: int
    recent_evaluations: list[RecentEvaluation]
