from app.domain.scoring.skills import canonical_skill, match_skills, skills_match


def test_canonical_skill_applies_known_aliases() -> None:
    assert canonical_skill("JS") == "javascript"
    assert canonical_skill("TS") == "typescript"
    assert canonical_skill("Postgres") == "postgresql"
    assert canonical_skill("React.js") == "react"
    assert canonical_skill("Node") == "node.js"


def test_canonical_skill_is_case_and_whitespace_insensitive() -> None:
    assert canonical_skill("  PostgreSQL  ") == canonical_skill("postgresql")
    assert canonical_skill("Node   JS") == canonical_skill("node js")


def test_skills_match_recognizes_aliases() -> None:
    assert skills_match("JS", "JavaScript") is True
    assert skills_match("Postgres", "PostgreSQL") is True
    assert skills_match("Node", "Node.js") is True


def test_skills_match_rejects_unrelated_technologies() -> None:
    assert skills_match("Java", "JavaScript") is False
    assert skills_match("React", "React Native") is False
    assert skills_match("C", "C++") is False
    assert skills_match("Postgres", "MySQL") is False


def test_skills_match_catches_minor_typos() -> None:
    assert skills_match("Kubernetes", "Kubernets") is True
    assert skills_match("PostgreSQL", "PostgeSQL") is True


def test_match_skills_weighs_required_above_preferred() -> None:
    required_only = match_skills(
        candidate_skills=["Python"],
        required_skills=["Python"],
        preferred_skills=["Kubernetes"],
    )
    preferred_only = match_skills(
        candidate_skills=["Kubernetes"],
        required_skills=["Python"],
        preferred_skills=["Kubernetes"],
    )

    assert required_only.score > preferred_only.score


def test_match_skills_reports_matched_and_missing_correctly() -> None:
    result = match_skills(
        candidate_skills=["Python", "PostgreSQL", "Docker"],
        required_skills=["Python", "PostgreSQL", "Kubernetes"],
        preferred_skills=["Kafka", "Docker"],
    )

    assert result.matched_required == ["Python", "PostgreSQL"]
    assert result.missing_required == ["Kubernetes"]
    assert result.matched_preferred == ["Docker"]


def test_match_skills_treats_empty_requirement_lists_as_full_credit() -> None:
    result = match_skills(candidate_skills=[], required_skills=[], preferred_skills=[])

    assert result.score == 1.0
    assert result.matched_required == []
    assert result.missing_required == []
    assert result.matched_preferred == []


def test_match_skills_with_nothing_matched_scores_zero() -> None:
    result = match_skills(
        candidate_skills=["Ruby"],
        required_skills=["Python"],
        preferred_skills=["Go"],
    )

    assert result.score == 0.0
    assert result.missing_required == ["Python"]
