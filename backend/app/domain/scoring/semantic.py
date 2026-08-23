"""Deterministic semantic-similarity scoring from precomputed embeddings.

This module does no embedding generation itself — it only computes
cosine similarity between two already-computed vectors, which keeps the
scoring engine independent of any LLM/embedding-provider call. Embedding
generation (an I/O concern, can fail, costs money) lives in
app.services.embedding_service; this module only ever sees the numbers
that come out of it. A caller with no vectors to pass — the embedding
provider isn't configured, or the call failed — gets 0.0 here rather
than a fabricated similarity.
"""

import math


def normalize_vector(vector: list[float]) -> list[float] | None:
    """L2-normalize a vector to unit length. Returns None for an empty
    vector or a zero vector — there's no direction to normalize."""
    if not vector:
        return None
    magnitude = math.sqrt(sum(component * component for component in vector))
    if magnitude == 0:
        return None
    return [component / magnitude for component in vector]


def compute_semantic_score(
    candidate_embedding: list[float] | None, job_embedding: list[float] | None
) -> float:
    if not candidate_embedding or not job_embedding:
        return 0.0
    if len(candidate_embedding) != len(job_embedding):
        return 0.0

    normalized_candidate = normalize_vector(candidate_embedding)
    normalized_job = normalize_vector(job_embedding)
    if normalized_candidate is None or normalized_job is None:
        return 0.0

    # Dot product of two unit vectors is exactly their cosine similarity.
    cosine_similarity = sum(a * b for a, b in zip(normalized_candidate, normalized_job))
    # Cosine similarity ranges [-1, 1]; map onto a [0, 1] score.
    return max(0.0, min(1.0, (cosine_similarity + 1) / 2))
