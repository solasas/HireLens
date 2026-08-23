import logging

from fastapi import APIRouter, File, UploadFile, status

from app.api.deps import LLMProviderDep
from app.core.exceptions import FileTooLargeError
from app.schemas.resume import ParsedResumePreview
from app.schemas.resume_extraction import ResumeExtraction
from app.services.pdf_parser import MAX_FILE_SIZE_BYTES, parse_resume_pdf
from app.services.resume_extraction_service import extract_resume

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resumes", tags=["resumes"])

_READ_CHUNK_SIZE = 1024 * 1024  # 1 MB


@router.post("/parse", response_model=ParsedResumePreview, status_code=status.HTTP_200_OK)
async def parse_resume(file: UploadFile = File(...)) -> ParsedResumePreview:
    """Parse an uploaded resume PDF and return its extracted text.

    This is the parsing pipeline in isolation — it does not create a
    candidate or persist anything. Full resume ingestion (parse + LLM
    extraction + persistence) is a later endpoint that calls the same
    pdf_parser service internally, plus a repository and an LLM provider.
    """
    file_bytes = await _read_bounded(file, MAX_FILE_SIZE_BYTES)
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
    a stored resume_profile) is a later endpoint.
    """
    file_bytes = await _read_bounded(file, MAX_FILE_SIZE_BYTES)
    filename = file.filename or "upload.pdf"
    parsed = parse_resume_pdf(file_bytes, filename=filename)
    return await extract_resume(parsed.text, llm=llm)


async def _read_bounded(file: UploadFile, max_bytes: int) -> bytes:
    """Read the upload in chunks, failing as soon as it exceeds the limit
    instead of buffering an arbitrarily large body in memory first."""
    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(_READ_CHUNK_SIZE):
        total += len(chunk)
        if total > max_bytes:
            raise FileTooLargeError(
                f"File exceeds the {max_bytes // (1024 * 1024)} MB upload limit."
            )
        chunks.append(chunk)
    return b"".join(chunks)
