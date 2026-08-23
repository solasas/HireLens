import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class FitLevel(str, Enum):
    STRONG_FIT = "Strong Fit"
    MODERATE_FIT = "Moderate Fit"
    WEAK_FIT = "Weak Fit"


class CandidateEvaluationNarrative(BaseModel):
    """What the LLM actually generates — the qualitative reasoning only.

    Deliberately excludes score, fit_level, and missing_required_skills:
    those are already known exactly from the deterministic matching
    engine (app.domain.scoring) and are attached by the service after
    generation. Asking the model to reproduce numbers it doesn't need to
    compute risks it silently disagreeing with the real matcher output.
    """

    strengths: list[str] = []
    relevant_experience: list[str] = []
    concerns: list[str] = []
    recommendation: str = ""


class CandidateEvaluation(BaseModel):
    """The full evaluation returned to callers — matches the requested
    schema exactly. score/fit_level/missing_required_skills are
    deterministic; everything else is the LLM's narrative."""

    score: float
    fit_level: FitLevel
    strengths: list[str] = []
    missing_required_skills: list[str] = []
    relevant_experience: list[str] = []
    concerns: list[str] = []
    recommendation: str = ""


class ScoreBreakdown(BaseModel):
    skill_score: float
    experience_score: float
    education_score: float
    semantic_score: float
    project_score: float


class EvaluationDetail(BaseModel):
    """Everything the "evaluation page" requirement asks for, in one
    response: candidate identity, overall score/fit, the five-component
    breakdown, and the full LLM narrative — persisted, never
    reconstructed on the fly."""

    evaluation_id: uuid.UUID
    candidate_id: uuid.UUID
    candidate_name: str
    job_id: uuid.UUID
    job_title: str
    score: float
    fit_level: str
    score_breakdown: ScoreBreakdown
    matched_skills: list[str] = []
    missing_required_skills: list[str] = []
    matched_preferred_skills: list[str] = []
    strengths: list[str] = []
    relevant_experience: list[str] = []
    concerns: list[str] = []
    recommendation: str = ""
    created_at: datetime
