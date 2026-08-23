"""Deterministic project/domain relevance scoring.

A keyword-overlap heuristic between the candidate's project text
(descriptions plus technologies) and the job's domains, keywords, and
responsibilities. Deliberately not embedding-based — unlike
semantic_score — and named accordingly so it's never mistaken for true
semantic similarity.
"""

import re

_WORD = re.compile(r"[a-z0-9][a-z0-9+.#-]*")
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "is", "are", "our", "we", "you", "your", "will", "be", "as", "that",
    "this", "at", "by", "from", "using",
}


def _tokenize(text: str) -> set[str]:
    return {
        word for word in _WORD.findall(text.lower()) if word not in _STOPWORDS and len(word) > 1
    }


def compute_project_score(
    candidate_project_text: list[str],
    job_domains: list[str],
    job_keywords: list[str],
    job_responsibilities: list[str],
) -> float:
    """Overlap coefficient: the fraction of the job's vocabulary that the
    candidate's project text actually covers. A job with no domain/
    keyword/responsibility signal at all can't be failed on this."""
    job_tokens: set[str] = set()
    for text in (*job_domains, *job_keywords, *job_responsibilities):
        job_tokens |= _tokenize(text)
    if not job_tokens:
        return 1.0

    candidate_tokens: set[str] = set()
    for text in candidate_project_text:
        candidate_tokens |= _tokenize(text)
    if not candidate_tokens:
        return 0.0

    overlap = job_tokens & candidate_tokens
    return len(overlap) / len(job_tokens)
