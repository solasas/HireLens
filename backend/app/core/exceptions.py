class AppError(Exception):
    """Base class for application-specific, expected errors.

    Subclasses are caught by the handler in app.main and turned into a
    well-formed HTTP response instead of a bare 500. Anything that is
    *not* an AppError is treated as a bug and logged with a traceback.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ServiceUnavailableError(AppError):
    """A required upstream dependency (database, LLM/embedding provider) is unreachable."""
