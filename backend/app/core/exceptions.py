class AppError(Exception):
    """Base class for application-specific, expected errors.

    Subclasses are caught by the handler in app.main and turned into a
    well-formed HTTP response instead of a bare 500. Anything that is
    *not* an AppError is treated as a bug and logged with a traceback.

    status_code lives on the exception itself, not in a lookup table in
    main.py — that keeps "what HTTP status does this error mean" next to
    the error's definition instead of scattered across route handlers.
    Plain ints, not fastapi.status, so this module has no web-framework
    dependency.
    """

    status_code: int = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ServiceUnavailableError(AppError):
    """A required upstream dependency (database, LLM/embedding provider) is unreachable."""

    status_code = 503


class PDFProcessingError(AppError):
    """Base class for errors raised while validating or parsing an uploaded PDF."""

    status_code = 422


class InvalidFileTypeError(PDFProcessingError):
    """The upload isn't a PDF (wrong extension or bad file signature)."""

    status_code = 400


class EmptyFileError(PDFProcessingError):
    """The upload contained zero bytes."""

    status_code = 400


class FileTooLargeError(PDFProcessingError):
    """The upload exceeds the configured size limit."""

    status_code = 413


class CorruptedPDFError(PDFProcessingError):
    """The file has a valid PDF signature but PyMuPDF could not open it."""


class NoExtractableTextError(PDFProcessingError):
    """The PDF opened fine but contains no usable text (blank or scanned)."""
