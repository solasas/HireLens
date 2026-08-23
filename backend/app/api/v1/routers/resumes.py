import logging

from fastapi import APIRouter, File, UploadFile, status

from app.api.deps import LLMProviderDep
from app.api.upload import read_bounded
from app.schemas.resume import ParsedResumePreview
from app.schemas.resume_extraction import ResumeExtraction
from app.services.pdf_parser import MAX_FILE_SIZE_BYTES, parse_resume_pdf
from app.services.resume_extraction_service import extract_resume

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/parse", response_model=ParsedResumePreview, status_code=status.HTTP_200_OK)
async def parse_resume(file: UploadFile = File(...)) -> ParsedResumePreview:
    """Parse an uploaded resume PDF and return its extracted text.

    This is the parsing pipeline in isolation — it does not create a
    candidate or persist anything. Full resume ingestion (parse + LLM
    extraction + persistence) is a later endpoint that calls the same
    pdf_parser service internally, plus a repository and an LLM provider.
    """
    file_bytes = await read_bounded(file, MAX_FILE_SIZE_BYTES)
    filename = file.filename or "upload.pdf"
    parsed = parse_resume_pdf(file_bytes, filename=filename)
    return ParsedResumePreview(
        file_name=filename,
        page_count=parsed.page_count,
        character_count=parsed.character_count,
        text=parsed.text,
    )


@router.post("/extract", response_model=ResumeExtraction, status_code=status.HTTP_200_OK)
async def extract_resume_route(llm: LLMProviderDep, file: UploadFile = File(...)) -> ResumeExtraction:
    """Parse an uploaded resume PDF and run structured LLM extraction over it.

    Still no persistence — this proves the parse-then-extract pipeline
    end to end. Full ingestion (this plus a candidate/resume record and
    a stored resume_profile) happens as part of POST /jobs/{job_id}/candidates.
    """
    file_bytes = await read_bounded(file, MAX_FILE_SIZE_BYTES)
    filename = file.filename or "upload.pdf"
    parsed = parse_resume_pdf(file_bytes, filename=filename)
    return await extract_resume(parsed.text, llm=llm)
