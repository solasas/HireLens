from typing import Literal

from pydantic import BaseModel


class ComponentStatus(BaseModel):
    name: str
    status: Literal["up", "down"]
    detail: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    components: list[ComponentStatus]
