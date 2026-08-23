"""Validates and extracts text from an uploaded resume PDF.

Pure and stateless — no database, no HTTP, no LLM. Given the raw bytes of
an upload, it returns extracted text or raises one of the typed errors in
app.core.exceptions. That makes it trivially unit-testable and reusable
from anywhere (an API route today, a batch import job later) without
dragging FastAPI along.
"""

import logging
import re
from dataclasses import dataclass

import pymupdf

from app.core.exceptions import (
    CorruptedPDFError,
    EmptyFileError,
    ExtractedTextTooLargeError,
    FileTooLargeError,
    InvalidFileTypeError,
    NoExtractableTextError,
)
from app.services.text_sanitization import strip_control_characters

logger = logging.getLogger(__name__)

PDF_MAGIC_BYTES = b"%PDF-"
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Below this many alphanumeric characters, we treat the PDF as having no
# usable content (blank page, watermark-only, or scanned image) rather
# than trust a stray page number or header as "extracted text".
MIN_EXTRACTABLE_CHARACTERS = 20

# Above this many characters, reject outright rather than silently
# truncate — bounds LLM token cost per resume and limits how much
# untrusted content a single upload can carry into a prompt. A generous
# multiple of what a real multi-page resume produces; a PDF that exceeds
# it is either not a resume or is deliberately padded.
MAX_EXTRACTED_TEXT_CHARS = 15_000

_WHITESPACE_RUN = re.compile(r"[ \t]+")
_SPACE_AROUND_NEWLINE = re.compile(r" *\n *")
_EXCESS_BLANK_LINES = re.compile(r"\n{3,}")
_NON_ALNUM = re.compile(r"[^0-9A-Za-z]+")


@dataclass(frozen=True)
class ParsedResume:
    text: str
    page_count: int
    character_count: int


def parse_resume_pdf(file_bytes: bytes, filename: str) -> ParsedResume:
    """Validate an upload and extract its text.

    Raises a subclass of app.core.exceptions.PDFProcessingError for every
    failure mode (empty file, wrong type, too large, corrupted, no
    extractable text) — each with a message that is safe to return to
    the user as-is.
    """
    _validate_not_empty(file_bytes)
    _validate_file_size(file_bytes)
    _validate_pdf_signature(file_bytes, filename)

    document = _open_document(file_bytes, filename)
    try:
        page_texts: list[str] = []
        has_images = False
        for page in document:
            page_texts.append(_extract_page_text(page))
            if not has_images and page.get_images(full=True):
                has_images = True
    finally:
        document.close()

    normalized_text = _normalize_whitespace("\n\n".join(page_texts))

    if len(_NON_ALNUM.sub("", normalized_text)) < MIN_EXTRACTABLE_CHARACTERS:
        raise _no_extractable_text_error(filename, len(page_texts), has_images)

    if len(normalized_text) > MAX_EXTRACTED_TEXT_CHARS:
        raise ExtractedTextTooLargeError(
            f"Extracted resume text exceeds the {MAX_EXTRACTED_TEXT_CHARS:,} "
            "character limit supported for a single resume."
        )

    return ParsedResume(
        text=normalized_text,
        page_count=len(page_texts),
        character_count=len(normalized_text),
    )


def _validate_not_empty(file_bytes: bytes) -> None:
    if not file_bytes:
        raise EmptyFileError("The uploaded file is empty.")


def _validate_file_size(file_bytes: bytes) -> None:
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(
            f"File exceeds the {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB upload limit."
        )


def _validate_pdf_signature(file_bytes: bytes, filename: str) -> None:
    if not filename.lower().endswith(".pdf"):
        raise InvalidFileTypeError("Only .pdf files are accepted.")
    if not file_bytes.startswith(PDF_MAGIC_BYTES):
        raise InvalidFileTypeError("The uploaded file is not a valid PDF.")


def _open_document(file_bytes: bytes, filename: str) -> pymupdf.Document:
    try:
        return pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        logger.warning("Failed to open %s as a PDF: %s", filename, exc)
        raise CorruptedPDFError(
            "The uploaded PDF could not be opened; it may be corrupted or password-protected."
        ) from exc


def _extract_page_text(page: pymupdf.Page) -> str:
    """Extract one page's text in approximate reading order.

    get_text("blocks") returns each text block as a top-left-anchored
    rectangle rather than one raw content stream, so sorting blocks by
    (top, left) survives multi-column layouts far better than trusting
    the PDF's internal stream order does. It is a heuristic, not a full
    column-aware layout reconstruction: two columns that share a row of
    y-coordinates can still interleave. Good enough for resumes, which
    are mostly single-column with the occasional sidebar.
    """
    blocks = page.get_text("blocks")
    text_blocks = [block for block in blocks if block[6] == 0 and block[4].strip()]
    text_blocks.sort(key=lambda block: (round(block[1]), block[0]))
    return "\n".join(block[4].strip() for block in text_blocks)


def _normalize_whitespace(text: str) -> str:
    """Tidy up PDF extraction artifacts without collapsing real structure.

    Collapses runs of spaces/tabs and caps blank-line runs at one blank
    line, but deliberately keeps single line breaks — resumes are full of
    meaningful short lines (skills, bullet points, dates) that a naive
    "join everything into one paragraph" normalization would destroy.

    Also strips control/format characters (see text_sanitization) here,
    at the point of ingestion — not just later, right before an LLM call.
    A PDF's embedded text can legally contain arbitrary Unicode, and
    resume text ends up stored as raw_text and eventually in prompts;
    cleaning it once at the source means every downstream consumer gets
    already-sanitized text instead of each one needing to remember to.
    """
    text = strip_control_characters(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WHITESPACE_RUN.sub(" ", text)
    text = _SPACE_AROUND_NEWLINE.sub("\n", text)
    text = _EXCESS_BLANK_LINES.sub("\n\n", text)
    return text.strip()


def _no_extractable_text_error(
    filename: str, page_count: int, has_images: bool
) -> NoExtractableTextError:
    logger.warning(
        "No extractable text in %s (%d pages, has_images=%s)", filename, page_count, has_images
    )
    if has_images:
        return NoExtractableTextError(
            "No selectable text was found, but the PDF contains images — this looks "
            "like a scanned resume. Scanned/image-only PDFs aren't supported yet; "
            "please upload a text-based PDF export instead."
        )
    return NoExtractableTextError(
        "No readable text was found in this PDF. It may be blank or empty."
    )
