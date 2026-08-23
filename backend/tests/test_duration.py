from app.services.duration import compute_duration_months, parse_flexible_date


def test_parse_flexible_date_handles_common_resume_formats() -> None:
    assert parse_flexible_date("2020-03-15").isoformat() == "2020-03-01"
    assert parse_flexible_date("2020-03").isoformat() == "2020-03-01"
    assert parse_flexible_date("March 2020").isoformat() == "2020-03-01"
    assert parse_flexible_date("Mar 2020").isoformat() == "2020-03-01"
    assert parse_flexible_date("03/2020").isoformat() == "2020-03-01"
    assert parse_flexible_date("2020").isoformat() == "2020-01-01"


def test_parse_flexible_date_returns_none_for_unrecognized_or_missing_input() -> None:
    assert parse_flexible_date(None) is None
    assert parse_flexible_date("") is None
    assert parse_flexible_date("sometime last year") is None


def test_compute_duration_months_between_two_dates() -> None:
    assert compute_duration_months("Jan 2020", "Jul 2020") == 6


def test_compute_duration_months_treats_present_as_ongoing() -> None:
    # Just asserts it resolves to *something* non-negative rather than
    # pinning "today" — pinning the clock would make this test flaky.
    result = compute_duration_months("Jan 2020", "Present")
    assert result is not None
    assert result >= 0


def test_compute_duration_months_returns_none_when_start_is_unparseable() -> None:
    assert compute_duration_months("a while back", "2020") is None


def test_compute_duration_months_returns_none_when_end_is_unparseable() -> None:
    assert compute_duration_months("2020", "whenever it ended") is None
