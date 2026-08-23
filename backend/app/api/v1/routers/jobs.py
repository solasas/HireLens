import logging

from fastapi import APIRouter, status

from app.api.deps import LLMProviderDep
from app.schemas.job import JobDescriptionInput
from app.schemas.job_extraction import JobExtraction
from app.services.job_extraction_service import extract_job_description

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/extract", response_model=JobExtraction, status_code=status.HTTP_200_OK)
async def extract_job_route(payload: JobDescriptionInput, llm: LLMProviderDep) -> JobExtraction:
    """Extract structured requirements from a job description's raw text.

    No persistence yet — same shape as /resumes/extract. Full job
    ingestion (this plus a stored job_description/job_requirements pair)
    is a later endpoint.
    """
    return await extract_job_description(payload.text, llm=llm)
