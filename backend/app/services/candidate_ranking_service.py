"""Evaluates a batch of resumes against one job and persists each result.

Orchestrates everything already built — PDF parsing, resume extraction,
the deterministic matching engine, semantic similarity, and LLM
evaluation reasoning — then writes one Evaluation row per candidate.
Embeds the job text exactly once and batches every candidate's
embedding into a single call, rather than re-embedding the job text
once per candidate (see _embed_job_and_candidates below).
"""

import logging
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.scoring import CandidateProfile, JobProfile, score_candidate
from app.models.job_description import JobDescription
from app.repositories.candidate_repository import get_or_create_candidate
from app.repositories.evaluation_repository import create_evaluation
from app.repositories.resume_repository import create_resume
from app.schemas.job_extraction import JobExtraction
from app.schemas.resume_extraction import ResumeExtraction
from app.services.embedding_service import embed_documents, embed_text
from app.services.embeddings.base import EmbeddingProvider
from app.services.evaluation_service import evaluate_candidate
from app.services.llm.base import LLMProvider
from app.services.llm.prompts.resume_extraction import RESUME_EXTRACTION_PROMPT_VERSION
from app.services.pdf_parser import parse_resume_pdf
from app.services.resume_extraction_service import extract_resume

logger = logging.getLogger(__name__)

SCORING_VERSION = "match-v1"


@dataclass
class _ParsedCandidate:
    filename: str
    raw_text: str
    extraction: ResumeExtraction


def _job_extraction_view(job: JobDescription) -> JobExtraction:
    """job.structured_data is exactly extraction.model_dump() from when
    the job was created, so this is just re-hydrating it — no field
    mapping to keep in sync."""
    return JobExtraction.model_validate(job.structured_data)


def _job_semantic_text(job_extraction: JobExtraction) -> str:
    return "\n".join(
        [
            *job_extraction.required_skills,
            *job_extraction.preferred_skills,
            *job_extraction.responsibilities,
        ]
    )


def _candidate_semantic_text(extraction: ResumeExtraction) -> str:
    experience_text = [
        responsibility for entry in extraction.experience for responsibility in entry.responsibilities
    ]
    project_text = [
        f"{project.name or ''}: {project.description or ''}".strip() for project in extraction.projects
    ]
    return "\n".join([*extraction.skills, *project_text, *experience_text])


async def _embed_job_and_candidates(
    job_extraction: JobExtraction,
    candidates: list[_ParsedCandidate],
    *,
    embedding_provider: EmbeddingProvider,
) -> tuple[list[float], list[list[float]]]:
    """One call for the job's embedding, one batched call for every
    candidate's embedding — never one call per candidate."""
    job_vector = await embed_text(_job_semantic_text(job_extraction), provider=embedding_provider)
    candidate_texts = [_candidate_semantic_text(c.extraction) for c in candidates]
    candidate_vectors = await embed_documents(candidate_texts, provider=embedding_provider)
    return job_vector, candidate_vectors


async def evaluate_resumes_for_job(
    session: AsyncSession,
    job: JobDescription,
    resumes: list[tuple[str, bytes]],
    *,
    llm: LLMProvider,
    embedding_provider: EmbeddingProvider,
) -> list[uuid.UUID]:
    """resumes is a list of (filename, pdf_bytes). Returns the created
    evaluation ids, in the same order as the input. A single failed
    resume (bad PDF, LLM error) fails the whole batch rather than
    silently skipping a candidate — a partially-evaluated job would be
    misleading to rank against."""
    if not resumes:
        return []

    parsed_candidates: list[_ParsedCandidate] = []
    for filename, pdf_bytes in resumes:
        parsed = parse_resume_pdf(pdf_bytes, filename=filename)
        extraction = await extract_resume(parsed.text, llm=llm)
        parsed_candidates.append(
            _ParsedCandidate(filename=filename, raw_text=parsed.text, extraction=extraction)
        )

    job_extraction = _job_extraction_view(job)
    job_vector, candidate_vectors = await _embed_job_and_candidates(
        job_extraction, parsed_candidates, embedding_provider=embedding_provider
    )
    job_profile = JobProfile(
        required_skills=job_extraction.required_skills,
        preferred_skills=job_extraction.preferred_skills,
        required_experience_years=job_extraction.required_experience_years,
        education_requirements=job_extraction.education_requirements,
        domains=job_extraction.domains,
        keywords=job_extraction.keywords,
        responsibilities=job_extraction.responsibilities,
        embedding=job_vector or None,
    )

    evaluation_ids: list[uuid.UUID] = []
    for parsed, candidate_vector in zip(parsed_candidates, candidate_vectors):
        extraction = parsed.extraction
        candidate_months = sum(entry.duration_months or 0 for entry in extraction.experience)
        candidate_education_text = [
            f"{entry.degree or ''} {entry.field or ''}".strip() for entry in extraction.education
        ]
        candidate_project_text = [
            f"{project.name or ''}: {project.description or ''}".strip()
            for project in extraction.projects
        ]

        candidate_profile = CandidateProfile(
            skills=extraction.skills,
            experience_months=candidate_months,
            education=candidate_education_text,
            project_text=candidate_project_text,
            embedding=candidate_vector or None,
        )
        match = score_candidate(candidate_profile, job_profile)
        evaluation = await evaluate_candidate(extraction, job_extraction, match, llm=llm)

        candidate_row = await get_or_create_candidate(
            session,
            full_name=extraction.name or "Unknown Candidate",
            email=extraction.email,
            phone=extraction.phone,
        )
        await create_resume(
            session,
            candidate_id=candidate_row.id,
            file_name=parsed.filename,
            raw_text=parsed.raw_text,
            extraction=extraction,
            extraction_version=RESUME_EXTRACTION_PROMPT_VERSION,
            llm_model=llm.model_name,
        )
        evaluation_row = await create_evaluation(
            session,
            candidate_id=candidate_row.id,
            job_description_id=job.id,
            match=match,
            evaluation=evaluation,
            scoring_version=SCORING_VERSION,
        )
        evaluation_ids.append(evaluation_row.id)

    await session.commit()
    return evaluation_ids
