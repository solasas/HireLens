"""Prompt for structured job-description extraction.

See resume_extraction.py for why the schema shape isn't repeated here as
JSON text — it's enforced via response_schema using
app.schemas.job_extraction.JobExtraction directly.
"""

JOB_EXTRACTION_PROMPT_VERSION = "job-extraction-v2"

_INSTRUCTIONS = """You are a job description analysis engine.

Analyze the following job description and convert it into structured JSON.

Do not invent requirements.

Separate:
- mandatory requirements
- preferred requirements

Rules:
1. Skills explicitly marked as required must go into required_skills.
2. Skills described as "nice to have", "preferred", or "bonus" must go into preferred_skills.
3. Do not treat every word in the JD as a skill.
4. Preserve technical terminology.
5. Do not infer experience requirements that are not stated.
6. Return JSON only.
7. When one requirement names a specific technology alongside a general
   description of the same capability (e.g. "PostgreSQL and relational
   database design", "Docker and containerized deployments"), extract
   only the specific technology name as a single skill entry. Do not
   also add the general descriptive phrase as a second, separate skill —
   that produces a duplicate of the same requirement."""


def build_job_extraction_prompt(job_description_text: str) -> str:
    return f"{_INSTRUCTIONS}\n\nJob description:\n{job_description_text}"
