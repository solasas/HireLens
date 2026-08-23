"""Compares a candidate's resume content against a job's requirements
using embeddings, and scores the result deterministically.

This is the orchestration layer: it does I/O (via embedding_service),
which means it can fail, and it decides what to do when it does. The
actual similarity math is delegated entirely to
app.domain.scoring.semantic.compute_semantic_score — this file never
computes a dot product itself, keeping embedding generation and scoring
logic in two separate places as required.
"""

import logging

from app.core.exceptions import EmbeddingProviderError
from app.domain.scoring.semantic import compute_semantic_score
from app.services.embedding_service import embed_documents
from app.services.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)


def _join(*groups: list[str]) -> str:
    return "\n".join(item for group in groups for item in group if item and item.strip())


async def compute_semantic_match(
    *,
    candidate_skills: list[str],
    candidate_projects: list[str],
    candidate_experience: list[str],
    job_requirements: list[str],
    job_responsibilities: list[str],
    provider: EmbeddingProvider,
) -> float:
    """Embeds the candidate's side (skills + projects + experience) and
    the job's side (requirements + responsibilities) as two documents in
    a single batched call — one API round trip, not two — then returns
    their cosine similarity as a 0-1 score.

    Degrades to 0.0 rather than raising if the embedding provider fails.
    semantic_score is one of five weighted signals in the overall match
    (see app.domain.scoring.matcher); a provider hiccup shouldn't take
    down the other four deterministic components along with it.
    """
    candidate_text = _join(candidate_skills, candidate_projects, candidate_experience)
    job_text = _join(job_requirements, job_responsibilities)

    if not candidate_text or not job_text:
        return 0.0

    try:
        candidate_vector, job_vector = await embed_documents(
            [candidate_text, job_text], provider=provider
        )
    except EmbeddingProviderError:
        logger.warning("Embedding provider failed; semantic_score defaulting to 0.0", exc_info=True)
        return 0.0

    return compute_semantic_score(candidate_vector or None, job_vector or None)
