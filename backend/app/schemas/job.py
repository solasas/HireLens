import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.services.text_sanitization import strip_control_characters


class JobDescriptionInput(BaseModel):
    text: str = Field(min_length=1, max_length=20000)

    @field_validator("text", mode="before")
    @classmethod
    def _sanitize(cls, value: object) -> object:
        # Runs before the min_length/max_length checks below, so those
        # constraints apply to the sanitized text — text padded out to
        # min_length using invisible characters doesn't sneak through,
        # and stripping only ever shrinks text, so it can't cause a
        # legitimate submission to newly exceed max_length.
        if isinstance(value, str):
            return strip_control_characters(value)
        return value

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
