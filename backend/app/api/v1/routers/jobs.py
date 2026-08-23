import logging
import uuid

from fastapi import APIRouter, File, Query, UploadFile, status

from app.api.deps import DbSession, EmbeddingProviderDep, LLMProviderDep
from app.api.upload import read_bounded
from app.core.exceptions import NotFoundError
from app.repositories.evaluation_repository import list_ranked_evaluations
from app.repositories.job_repository import create_job, get_job, list_jobs
from app.schemas.job import (
    EvaluateCandidatesResponse,
    JobCreateResponse,
    JobDescriptionInput,
    JobDetail,
    JobSummary,
)
from app.schemas.job_extraction import JobExtraction
from app.schemas.ranking import JobCandidateRanking, RankedCandidate
from app.services.candidate_ranking_service import evaluate_resumes_for_job
from app.services.job_extraction_service import extract_job_description
from app.services.llm.prompts.job_extraction import JOB_EXTRACTION_PROMPT_VERSION
from app.services.pdf_parser import MAX_FILE_SIZE_BYTES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/extract", response_model=JobExtraction, status_code=status.HTTP_200_OK)
async def extract_job_route(payload: JobDescriptionInput, llm: LLMProviderDep) -> JobExtraction:
    """Extract structured requirements from a job description's raw text
    without persisting anything — a preview, distinct from POST /jobs."""
    return await extract_job_description(payload.text, llm=llm)


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_job_route(
    payload: JobDescriptionInput, llm: LLMProviderDep, db: DbSession
) -> JobCreateResponse:
    """Extract and persist a job description. Returns the job_id needed
    to evaluate candidates against it."""
    extraction = await extract_job_description(payload.text, llm=llm)
    job = await create_job(
        db,
        raw_text=payload.text,
        extraction=extraction,
        extraction_version=JOB_EXTRACTION_PROMPT_VERSION,
        llm_model=llm.model_name,
    )
    await db.commit()
    return JobCreateResponse(job_id=job.id, job_title=job.title)


@router.get("", response_model=list[JobSummary], status_code=status.HTTP_200_OK)
async def list_jobs_route(db: DbSession) -> list[JobSummary]:
    """Every persisted job, most recent first, with how many candidates
    have been evaluated against each."""
    jobs = await list_jobs(db)
    return [
        JobSummary(
            job_id=row.job_id,
            title=row.title,
            candidate_count=row.candidate_count,
            created_at=row.created_at,
        )
        for row in jobs
    ]


@router.get("/{job_id}", response_model=JobDetail, status_code=status.HTTP_200_OK)
async def get_job_route(job_id: uuid.UUID, db: DbSession) -> JobDetail:
    job = await get_job(db, job_id)
    if job is None:
        raise NotFoundError(f"Job {job_id} was not found.")
    return JobDetail(
        job_id=job.id,
        title=job.title,
        raw_text=job.raw_text,
        structured_data=job.structured_data,
        created_at=job.created_at,
    )


@router.post(
    "/{job_id}/candidates",
    response_model=EvaluateCandidatesResponse,
    status_code=status.HTTP_201_CREATED,
)
async def evaluate_candidates_route(
    job_id: uuid.UUID,
    llm: LLMProviderDep,
    embedding_provider: EmbeddingProviderDep,
    db: DbSession,
    files: list[UploadFile] = File(...),
) -> EvaluateCandidatesResponse:
    """Evaluates every uploaded resume against the given job and
    persists one Evaluation row per candidate."""
    job = await get_job(db, job_id)
    if job is None:
        raise NotFoundError(f"Job {job_id} was not found.")

    resumes: list[tuple[str, bytes]] = []
    for file in files:
        file_bytes = await read_bounded(file, MAX_FILE_SIZE_BYTES)
        resumes.append((file.filename or "upload.pdf", file_bytes))

    evaluation_ids = await evaluate_resumes_for_job(
        db, job, resumes, llm=llm, embedding_provider=embedding_provider
    )
    return EvaluateCandidatesResponse(job_id=job.id, evaluation_ids=evaluation_ids)


@router.get("/{job_id}/candidates", response_model=JobCandidateRanking, status_code=status.HTTP_200_OK)
async def rank_candidates_route(
    job_id: uuid.UUID,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> JobCandidateRanking:
    """Candidates for a job, ranked by final score descending. Ties are
    broken deterministically (see evaluation_repository) so rank order
    never varies between requests. Rank numbers reflect absolute
    position across the full result set, not just within the page."""
    job = await get_job(db, job_id)
    if job is None:
        raise NotFoundError(f"Job {job_id} was not found.")

    offset = (page - 1) * page_size
    rows, total = await list_ranked_evaluations(
        db, job_description_id=job_id, limit=page_size, offset=offset
    )

    candidates = [
        RankedCandidate(
            rank=offset + index + 1,
            candidate_id=row.candidate_id,
            evaluation_id=row.evaluation_id,
            name=row.candidate_name,
            score=row.score,
            fit_level=row.fit_level,
        )
        for index, row in enumerate(rows)
    ]

    return JobCandidateRanking(
        job_id=job_id, page=page, page_size=page_size, total=total, candidates=candidates
    )
