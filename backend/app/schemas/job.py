import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class JobDescriptionInput(BaseModel):
    text: str = Field(min_length=1, max_length=20000)

    @field_validator("text")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Job description text cannot be blank.")
        return value


class JobCreateResponse(BaseModel):
    job_id: uuid.UUID
    job_title: str


class EvaluateCandidatesResponse(BaseModel):
    job_id: uuid.UUID
    evaluation_ids: list[uuid.UUID]


class JobSummary(BaseModel):
    job_id: uuid.UUID
    title: str
    candidate_count: int
    created_at: datetime


class JobDetail(BaseModel):
    job_id: uuid.UUID
    title: str
    raw_text: str
    structured_data: dict[str, Any]
    created_at: datetime
