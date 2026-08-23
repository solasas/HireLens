from pydantic import BaseModel


class JobExtraction(BaseModel):
    """Structured shape an LLM extracts from a job description's raw text.

    Passed directly as the provider's response_schema — same reasoning
    as ResumeExtraction: one schema definition, not a duplicate hand-
    written JSON block in the prompt.

    Note this doesn't exactly match the job_requirements table designed
    earlier (that one has a single `education_requirement` object and no
    domains/keywords columns). This schema follows the extraction spec
    as given; reconciling it with persistence is a decision for whenever
    that migration is written, not something to silently paper over here.
    """

    job_title: str | None = None
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    required_experience_years: float | None = None
    education_requirements: list[str] = []
    responsibilities: list[str] = []
    domains: list[str] = []
    keywords: list[str] = []
