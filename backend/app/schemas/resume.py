from pydantic import BaseModel, Field


class ParsedResumePreview(BaseModel):
    """API-facing shape of a parsed resume. Deliberately not the same
    object as app.services.pdf_parser.ParsedResume — internal service
    return types and public response contracts are allowed to diverge."""

    file_name: str
    page_count: int = Field(ge=0)
    character_count: int = Field(ge=0)
    text: str
