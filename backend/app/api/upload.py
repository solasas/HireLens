from fastapi import UploadFile

from app.core.exceptions import FileTooLargeError

_READ_CHUNK_SIZE = 1024 * 1024  # 1 MB


async def read_bounded(file: UploadFile, max_bytes: int) -> bytes:
    """Read an upload in chunks, failing as soon as it exceeds the limit
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
