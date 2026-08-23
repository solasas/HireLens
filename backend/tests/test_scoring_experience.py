from app.domain.scoring.experience import compute_experience_score


def test_no_stated_requirement_returns_full_credit() -> None:
    assert compute_experience_score(candidate_experience_months=0, required_experience_years=None) == 1.0
    assert compute_experience_score(candidate_experience_months=0, required_experience_years=0) == 1.0


def test_meeting_requirement_exactly_returns_full_credit() -> None:
    assert compute_experience_score(candidate_experience_months=60, required_experience_years=5) == 1.0


def test_partial_experience_returns_proportional_score() -> None:
    # 24 of 60 required months = 0.4
    assert compute_experience_score(candidate_experience_months=24, required_experience_years=5) == 0.4


def test_exceeding_requirement_does_not_exceed_full_credit() -> None:
    assert compute_experience_score(candidate_experience_months=240, required_experience_years=5) == 1.0


def test_zero_experience_against_stated_requirement_returns_zero() -> None:
    assert compute_experience_score(candidate_experience_months=0, required_experience_years=3) == 0.0
