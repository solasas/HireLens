"""Deterministic semantic-similarity scoring from precomputed embeddings.

This module does no embedding generation itself — it only computes
cosine similarity between two already-computed vectors, which keeps the
scoring engine independent of any LLM/embedding-provider call. An
embedding provider hasn't been wired up yet in this project; until it
is, callers simply have no vectors to pass, and this returns 0.0 rather
than fabricating a similarity from something else.
"""

import math


def compute_semantic_score(
    candidate_embedding: list[float] | None, job_embedding: list[float] | None
) -> float:
    if not candidate_embedding or not job_embedding:
        return 0.0
    if len(candidate_embedding) != len(job_embedding):
        return 0.0

    dot = sum(a * b for a, b in zip(candidate_embedding, job_embedding))
    magnitude_a = math.sqrt(sum(a * a for a in candidate_embedding))
    magnitude_b = math.sqrt(sum(b * b for b in job_embedding))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    cosine_similarity = dot / (magnitude_a * magnitude_b)
    # Cosine similarity ranges [-1, 1]; map onto a [0, 1] score.
    return max(0.0, min(1.0, (cosine_similarity + 1) / 2))
