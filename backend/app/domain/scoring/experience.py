"""Deterministic experience-duration scoring.

candidate_experience_months is expected to already be computed
deterministically (see app.services.duration) — this module only does
the comparison against the job's stated requirement.
"""


def compute_experience_score(
    candidate_experience_months: int, required_experience_years: float | None
) -> float:
    """A saturating ratio: meeting or exceeding the requirement is full
    credit, exceeding it further adds nothing more. A job that states no
    experience requirement can't be failed on one."""
    if required_experience_years is None or required_experience_years <= 0:
        return 1.0

    required_months = required_experience_years * 12
    ratio = candidate_experience_months / required_months
    return min(max(ratio, 0.0), 1.0)
