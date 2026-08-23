import logging
import sys


def configure_logging(log_level: str) -> None:
    """Configure stdlib logging once, at process startup."""
    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
    # Uvicorn's access log is noisy at INFO for a service with a polled health check.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
