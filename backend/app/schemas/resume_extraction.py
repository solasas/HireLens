from pydantic import BaseModel


class ExperienceEntry(BaseModel):
    job_title: str | None = None
    company: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    duration_months: int | None = None
    responsibilities: list[str] = []
    technologies: list[str] = []


class EducationEntry(BaseModel):
    degree: str | None = None
    field: str | None = None
    institution: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ProjectEntry(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = []
    responsibilities: list[str] = []


class ResumeExtraction(BaseModel):
    """The structured shape an LLM extracts from a resume's raw text.

    This is also passed directly as the provider's response_schema, so it
    is the single source of truth for extraction shape — the prompt only
    carries the extraction *rules*, never a hand-written copy of this
    schema that could drift out of sync with it.
    """

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    skills: list[str] = []
    education: list[EducationEntry] = []
    experience: list[ExperienceEntry] = []
    projects: list[ProjectEntry] = []
    certifications: list[str] = []
