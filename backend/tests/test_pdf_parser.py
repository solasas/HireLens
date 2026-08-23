import pytest

from app.core.exceptions import (
    EmptyFileError,
    ExtractedTextTooLargeError,
    FileTooLargeError,
    InvalidFileTypeError,
    NoExtractableTextError,
)
from app.services import pdf_parser
from app.services.pdf_parser import parse_resume_pdf
from tests.factories.pdf import make_blank_pdf, make_image_only_pdf, make_text_pdf


def test_valid_pdf_extracts_normalized_text() -> None:
    pdf_bytes = make_text_pdf(["Jane   Doe\nSoftware Engineer"])

    result = parse_resume_pdf(pdf_bytes, filename="resume.pdf")

    assert result.page_count == 1
    assert "Jane Doe" in result.text
    assert "Software Engineer" in result.text
    assert result.character_count == len(result.text)
    # Runs of horizontal whitespace from the source line are collapsed.
    assert "Jane   Doe" not in result.text


def test_multi_page_pdf_captures_every_page_in_order() -> None:
    pdf_bytes = make_text_pdf(["Page one content", "Page two content", "Page three content"])

    result = parse_resume_pdf(pdf_bytes, filename="resume.pdf")

    assert result.page_count == 3
    assert result.text.index("Page one") < result.text.index("Page two") < result.text.index(
        "Page three"
    )


def test_blank_pdf_raises_no_extractable_text_error() -> None:
    pdf_bytes = make_blank_pdf(page_count=2)

    with pytest.raises(NoExtractableTextError) as exc_info:
        parse_resume_pdf(pdf_bytes, filename="resume.pdf")

    assert "blank" in exc_info.value.message.lower() or "no readable text" in exc_info.value.message.lower()


def test_empty_upload_raises_empty_file_error() -> None:
    with pytest.raises(EmptyFileError):
        parse_resume_pdf(b"", filename="resume.pdf")


def test_non_pdf_bytes_raise_invalid_file_type_error() -> None:
    with pytest.raises(InvalidFileTypeError):
        parse_resume_pdf(b"this is a plain text file, not a pdf", filename="resume.pdf")


def test_wrong_extension_raises_invalid_file_type_error() -> None:
    pdf_bytes = make_text_pdf(["Some content"])

    with pytest.raises(InvalidFileTypeError):
        parse_resume_pdf(pdf_bytes, filename="resume.docx")


def test_scanned_image_only_pdf_raises_no_extractable_text_error() -> None:
    pdf_bytes = make_image_only_pdf()

    with pytest.raises(NoExtractableTextError) as exc_info:
        parse_resume_pdf(pdf_bytes, filename="scanned-resume.pdf")

    assert "scanned" in exc_info.value.message.lower()


def test_file_over_size_limit_raises_file_too_large_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Monkeypatch the threshold instead of generating a real 10 MB PDF —
    # this tests the same boundary check without a slow, heavy fixture.
    monkeypatch.setattr(pdf_parser, "MAX_FILE_SIZE_BYTES", 1024)
    oversized_bytes = b"%PDF-1.7\n" + b"0" * 2000

    with pytest.raises(FileTooLargeError):
        parse_resume_pdf(oversized_bytes, filename="resume.pdf")


def test_extracted_text_over_limit_is_rejected_not_truncated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Same boundary-check-via-monkeypatch pattern as the file-size test —
    # tests the real limit logic without needing an enormous fixture.
    monkeypatch.setattr(pdf_parser, "MAX_EXTRACTED_TEXT_CHARS", 50)
    pdf_bytes = make_text_pdf(["This line of resume text is long enough to exceed the limit."])

    with pytest.raises(ExtractedTextTooLargeError):
        parse_resume_pdf(pdf_bytes, filename="resume.pdf")


def test_control_characters_are_stripped_from_extracted_text() -> None:
    pdf_bytes = make_text_pdf(["Jane Doe\x00\x07 Software Engineer"])

    result = parse_resume_pdf(pdf_bytes, filename="resume.pdf")

    assert "\x00" not in result.text
    assert "\x07" not in result.text


def test_normalize_whitespace_collapses_runs_and_blank_lines() -> None:
    raw = "Line one   with   spaces\n\n\n\nLine two\r\n\r\nLine three   "

    result = pdf_parser._normalize_whitespace(raw)

    assert result == "Line one with spaces\n\nLine two\n\nLine three"
