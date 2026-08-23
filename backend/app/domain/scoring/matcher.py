"""Combines the five scoring components into a final weighted match score.

CandidateProfile and JobProfile are this module's own input types —
deliberately not app.schemas.resume_extraction.ResumeExtraction or
app.schemas.job_extraction.JobExtraction. That keeps the scoring engine
independent of the LLM extraction schema shape (which can evolve on its
own); an orchestration service is responsible for building these from an
extraction result, but that adapter doesn't exist yet and isn't part of
this change.
"""

from dataclasses import dataclass

from app.domain.scoring.education import compute_education_score
from app.domain.scoring.experience import compute_experience_score
from app.domain.scoring.project import compute_project_score
from app.domain.scoring.semantic import compute_semantic_score
from app.domain.scoring.skills import match_skills

SKILL_WEIGHT = 0.40
EXPERIENCE_WEIGHT = 0.20
EDUCATION_WEIGHT = 0.15
SEMANTIC_WEIGHT = 0.15
PROJECT_WEIGHT = 0.10

_ROUND_DIGITS = 4


@dataclass(frozen=True)
class CandidateProfile:
    skills: list[str]
    experience_months: int
    education: list[str]
    project_text: list[str]
    embedding: list[float] | None = None


@dataclass(frozen=True)
class JobProfile:
    required_skills: list[str]
    preferred_skills: list[str]
    required_experience_years: float | None
    education_requirements: list[str]
    domains: list[str]
    keywords: list[str]
    responsibilities: list[str]
    embedding: list[float] | None = None


@dataclass(frozen=True)
class MatchResult:
    skill_score: float
    experience_score: float
    education_score: float
    semantic_score: float
    project_score: float
    final_score: float
    matched_skills: list[str]
    missing_required_skills: list[str]
    matched_preferred_skills: list[str]


def score_candidate(candidate: CandidateProfile, job: JobProfile) -> MatchResult:
    skill_result = match_skills(candidate.skills, job.required_skills, job.preferred_skills)
    experience_score = compute_experience_score(
        candidate.experience_months, job.required_experience_years
    )
    education_score = compute_education_score(candidate.education, job.education_requirements)
    semantic_score = compute_semantic_score(candidate.embedding, job.embedding)
    project_score = compute_project_score(
        candidate.project_text, job.domains, job.keywords, job.responsibilities
    )

    final_score = (
        skill_result.score * SKILL_WEIGHT
        + experience_score * EXPERIENCE_WEIGHT
        + education_score * EDUCATION_WEIGHT
        + semantic_score * SEMANTIC_WEIGHT
        + project_score * PROJECT_WEIGHT
    )

    return MatchResult(
        skill_score=round(skill_result.score, _ROUND_DIGITS),
        experience_score=round(experience_score, _ROUND_DIGITS),
        education_score=round(education_score, _ROUND_DIGITS),
        semantic_score=round(semantic_score, _ROUND_DIGITS),
        project_score=round(project_score, _ROUND_DIGITS),
        final_score=round(final_score, _ROUND_DIGITS),
        matched_skills=skill_result.matched_required,
        missing_required_skills=skill_result.missing_required,
        matched_preferred_skills=skill_result.matched_preferred,
    )
