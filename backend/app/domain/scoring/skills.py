"""Deterministic skill matching between a candidate and a job.

Not exact-string-only: skills are canonicalized (case, whitespace, and a
small set of known aliases) before comparison, then a conservative
fuzzy-match pass catches near-identical spellings — typos, stray
formatting — without conflating genuinely different technologies. See
FUZZY_MATCH_THRESHOLD for why that bar is set where it is.
"""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

# Required skills matter more than preferred ones for the overall
# skill_score. Named, tunable constants rather than a magic split buried
# in the formula.
REQUIRED_SKILL_WEIGHT = 0.75
PREFERRED_SKILL_WEIGHT = 0.25

# SequenceMatcher.ratio() for genuinely different technologies sits well
# below this bar (e.g. "java" vs "javascript" ~0.57, "react" vs
# "react native" ~0.59, "c" vs "c++" ~0.5), so 0.92 only catches
# near-identical spellings — typos, stray whitespace — not semantically
# different skills.
FUZZY_MATCH_THRESHOLD = 0.92

_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "postgres": "postgresql",
    "react.js": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
}

_WHITESPACE_RUN = re.compile(r"\s+")


def canonical_skill(name: str) -> str:
    """Lowercase, collapse whitespace, and resolve known aliases."""
    normalized = _WHITESPACE_RUN.sub(" ", name.strip().lower())
    return _ALIASES.get(normalized, normalized)


def skills_match(a: str, b: str) -> bool:
    canon_a, canon_b = canonical_skill(a), canonical_skill(b)
    if not canon_a or not canon_b:
        return False
    if canon_a == canon_b:
        return True
    return SequenceMatcher(None, canon_a, canon_b).ratio() >= FUZZY_MATCH_THRESHOLD


def _find_match(target: str, pool: list[str]) -> str | None:
    for candidate_skill in pool:
        if skills_match(target, candidate_skill):
            return candidate_skill
    return None


@dataclass(frozen=True)
class SkillMatchResult:
    score: float
    matched_required: list[str]
    missing_required: list[str]
    matched_preferred: list[str]


def match_skills(
    candidate_skills: list[str], required_skills: list[str], preferred_skills: list[str]
) -> SkillMatchResult:
    """Score is required_ratio * 0.75 + preferred_ratio * 0.25.

    A job that lists no skills in a category can't be failed on that
    category — an empty required_skills or preferred_skills list scores
    that category as fully satisfied rather than penalizing or silently
    dropping it from the weighted formula.
    """
    matched_required: list[str] = []
    missing_required: list[str] = []
    for skill in required_skills:
        if _find_match(skill, candidate_skills) is not None:
            matched_required.append(skill)
        else:
            missing_required.append(skill)

    matched_preferred = [
        skill for skill in preferred_skills if _find_match(skill, candidate_skills) is not None
    ]

    required_ratio = len(matched_required) / len(required_skills) if required_skills else 1.0
    preferred_ratio = (
        len(matched_preferred) / len(preferred_skills) if preferred_skills else 1.0
    )
    score = required_ratio * REQUIRED_SKILL_WEIGHT + preferred_ratio * PREFERRED_SKILL_WEIGHT

    return SkillMatchResult(
        score=score,
        matched_required=matched_required,
        missing_required=missing_required,
        matched_preferred=matched_preferred,
    )
