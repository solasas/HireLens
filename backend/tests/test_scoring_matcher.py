import pytest

from app.domain.scoring import (
    EDUCATION_WEIGHT,
    EXPERIENCE_WEIGHT,
    PROJECT_WEIGHT,
    SEMANTIC_WEIGHT,
    SKILL_WEIGHT,
    CandidateProfile,
    JobProfile,
    score_candidate,
)


def test_weights_sum_to_one() -> None:
    total = SKILL_WEIGHT + EXPERIENCE_WEIGHT + EDUCATION_WEIGHT + SEMANTIC_WEIGHT + PROJECT_WEIGHT
    assert total == pytest.approx(1.0)


def test_perfect_candidate_scores_at_the_top() -> None:
    embedding = [1.0, 0.0, 0.0]
    candidate = CandidateProfile(
        skills=["Python", "PostgreSQL", "Docker"],
        experience_months=60,
        education=["M.S. in Computer Science"],
        project_text=["Built a payments platform in Python"],
        embedding=embedding,
    )
    job = JobProfile(
        required_skills=["Python", "PostgreSQL"],
        preferred_skills=["Docker"],
        required_experience_years=5,
        education_requirements=["Bachelor's degree required"],
        domains=["payments"],
        keywords=[],
        responsibilities=[],
        embedding=embedding,
    )

    result = score_candidate(candidate, job)

    assert result.final_score == pytest.approx(1.0, abs=0.05)


def test_final_score_is_the_documented_weighted_sum() -> None:
    candidate = CandidateProfile(
        skills=["Python"],
        experience_months=12,
        education=[],
        project_text=[],
        embedding=None,
    )
    job = JobProfile(
        required_skills=["Python", "Kubernetes"],
        preferred_skills=["Kafka"],
        required_experience_years=5,
        education_requirements=["Bachelor's degree required"],
        domains=["fintech"],
        keywords=[],
        responsibilities=[],
        embedding=None,
    )

    result = score_candidate(candidate, job)

    expected = (
        result.skill_score * SKILL_WEIGHT
        + result.experience_score * EXPERIENCE_WEIGHT
        + result.education_score * EDUCATION_WEIGHT
        + result.semantic_score * SEMANTIC_WEIGHT
        + result.project_score * PROJECT_WEIGHT
    )
    assert result.final_score == pytest.approx(expected, abs=1e-4)


def test_matcher_exposes_matched_and_missing_skill_lists() -> None:
    candidate = CandidateProfile(
        skills=["Python", "Docker"],
        experience_months=0,
        education=[],
        project_text=[],
    )
    job = JobProfile(
        required_skills=["Python", "Kubernetes"],
        preferred_skills=["Docker", "Kafka"],
        required_experience_years=None,
        education_requirements=[],
        domains=[],
        keywords=[],
        responsibilities=[],
    )

    result = score_candidate(candidate, job)

    assert result.matched_skills == ["Python"]
    assert result.missing_required_skills == ["Kubernetes"]
    assert result.matched_preferred_skills == ["Docker"]


def test_result_matches_the_required_json_shape_via_dataclass_fields() -> None:
    from dataclasses import asdict, fields

    candidate = CandidateProfile(skills=[], experience_months=0, education=[], project_text=[])
    job = JobProfile(
        required_skills=[],
        preferred_skills=[],
        required_experience_years=None,
        education_requirements=[],
        domains=[],
        keywords=[],
        responsibilities=[],
    )

    result = score_candidate(candidate, job)
    field_names = {f.name for f in fields(result)}

    assert field_names == {
        "skill_score",
        "experience_score",
        "education_score",
        "semantic_score",
        "project_score",
        "final_score",
        "matched_skills",
        "missing_required_skills",
        "matched_preferred_skills",
    }
    assert isinstance(asdict(result), dict)
