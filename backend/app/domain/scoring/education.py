"""Deterministic education-level scoring.

Compares the highest degree level detectable in the candidate's
education entries against the highest degree level explicitly mentioned
across the job's education requirements. A keyword-based ordinal
comparison, not free-text semantic matching — deterministic and
auditable, at the cost of missing phrasing it doesn't recognize. When it
can't detect a requirement's level at all, it defaults to full credit
rather than penalizing the candidate for a requirement it couldn't parse.
"""

_DEGREE_LEVELS: list[tuple[int, tuple[str, ...]]] = [
    (4, ("phd", "ph.d", "doctorate", "doctoral")),
    (3, ("master", "m.s.", "m.a.", "mba", "msc")),
    (2, ("bachelor", "b.s.", "b.a.", "bsc", "undergraduate")),
    (1, ("associate", "a.a.", "a.s.")),
    (0, ("high school", "secondary school")),
]

PARTIAL_CREDIT_SCORE = 0.5


def _detect_level(text: str) -> int | None:
    lowered = text.lower()
    for level, keywords in _DEGREE_LEVELS:
        if any(keyword in lowered for keyword in keywords):
            return level
    return None


def _highest_level(texts: list[str]) -> int | None:
    levels = [level for text in texts if (level := _detect_level(text)) is not None]
    return max(levels) if levels else None


def compute_education_score(
    candidate_education: list[str], education_requirements: list[str]
) -> float:
    required_level = _highest_level(education_requirements)
    if required_level is None:
        return 1.0

    candidate_level = _highest_level(candidate_education)
    if candidate_level is None:
        return 0.0

    gap = required_level - candidate_level
    if gap <= 0:
        return 1.0
    if gap == 1:
        return PARTIAL_CREDIT_SCORE
    return 0.0
