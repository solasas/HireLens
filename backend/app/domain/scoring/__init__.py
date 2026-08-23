from app.domain.scoring.matcher import (
    EDUCATION_WEIGHT,
    EXPERIENCE_WEIGHT,
    PROJECT_WEIGHT,
    SEMANTIC_WEIGHT,
    SKILL_WEIGHT,
    CandidateProfile,
    JobProfile,
    MatchResult,
    score_candidate,
)

__all__ = [
    "CandidateProfile",
    "JobProfile",
    "MatchResult",
    "score_candidate",
    "SKILL_WEIGHT",
    "EXPERIENCE_WEIGHT",
    "EDUCATION_WEIGHT",
    "SEMANTIC_WEIGHT",
    "PROJECT_WEIGHT",
]
