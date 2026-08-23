from app.domain.scoring.project import compute_project_score


def test_overlapping_keywords_increase_score() -> None:
    score = compute_project_score(
        candidate_project_text=["Built a payments reconciliation pipeline in Python"],
        job_domains=["fintech"],
        job_keywords=["payments"],
        job_responsibilities=["Build backend services for our payments platform"],
    )
    assert score > 0.0


def test_no_overlap_returns_zero() -> None:
    score = compute_project_score(
        candidate_project_text=["Built a mobile game in Unity"],
        job_domains=["fintech"],
        job_keywords=["payments"],
        job_responsibilities=["Build backend services for our payments platform"],
    )
    assert score == 0.0


def test_no_job_signal_returns_full_credit() -> None:
    score = compute_project_score(
        candidate_project_text=["Anything at all"],
        job_domains=[],
        job_keywords=[],
        job_responsibilities=[],
    )
    assert score == 1.0


def test_no_candidate_projects_returns_zero_when_job_has_signal() -> None:
    score = compute_project_score(
        candidate_project_text=[],
        job_domains=["fintech"],
        job_keywords=[],
        job_responsibilities=[],
    )
    assert score == 0.0


def test_full_keyword_overlap_scores_one() -> None:
    score = compute_project_score(
        candidate_project_text=["payments platform"],
        job_domains=["payments"],
        job_keywords=[],
        job_responsibilities=[],
    )
    assert score == 1.0
