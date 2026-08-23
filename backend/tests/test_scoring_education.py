from app.domain.scoring.education import compute_education_score


def test_no_detectable_requirement_returns_full_credit() -> None:
    assert compute_education_score(candidate_education=[], education_requirements=[]) == 1.0
    assert (
        compute_education_score(
            candidate_education=[], education_requirements=["Strong communication skills"]
        )
        == 1.0
    )


def test_candidate_meets_required_degree_level() -> None:
    score = compute_education_score(
        candidate_education=["B.S. in Computer Science"],
        education_requirements=["Bachelor's degree in Computer Science or related field"],
    )
    assert score == 1.0


def test_candidate_exceeds_required_degree_level() -> None:
    score = compute_education_score(
        candidate_education=["M.S. in Computer Science"],
        education_requirements=["Bachelor's degree required"],
    )
    assert score == 1.0


def test_candidate_one_level_below_requirement_gets_partial_credit() -> None:
    score = compute_education_score(
        candidate_education=["Associate degree"],
        education_requirements=["Bachelor's degree required"],
    )
    assert score == 0.5


def test_candidate_more_than_one_level_below_requirement_gets_zero() -> None:
    score = compute_education_score(
        candidate_education=["High school diploma"],
        education_requirements=["Master's degree required"],
    )
    assert score == 0.0


def test_no_candidate_education_against_stated_requirement_returns_zero() -> None:
    score = compute_education_score(
        candidate_education=[], education_requirements=["Bachelor's degree required"]
    )
    assert score == 0.0
