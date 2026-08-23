"""Prompt for structured resume extraction.

Versioned so a stored extraction (resume_profiles.extraction_version, once
persistence is wired up) can always be traced back to the exact prompt
that produced it. The shape of the output is *not* repeated here as a
JSON block — it's enforced at the API level via the provider's
response_schema, using app.schemas.resume_extraction.ResumeExtraction
directly. Keeping one schema definition (the Pydantic model) instead of
two (model + hand-written JSON block in the prompt) means they can't
drift out of sync with each other.
"""

RESUME_EXTRACTION_PROMPT_VERSION = "resume-extraction-v1"

_INSTRUCTIONS = """You are a resume information extraction engine.

Your task is to extract structured information from a resume.

Rules:
1. Extract only information explicitly present in the resume.
2. Never invent skills, experience, education, companies, dates, or certifications.
3. Normalize obvious variations:
   - "JS" -> "JavaScript"
   - "Postgres" -> "PostgreSQL"
   - "Spring" -> do not automatically convert to "Spring Boot" unless explicitly stated.
4. Preserve original meaning.
5. Separate work experience from projects.
6. Calculate experience duration only when dates are available.
7. If information is missing, return null or an empty array.
8. Return valid JSON only.
9. Do not include explanations outside the JSON."""


def build_resume_extraction_prompt(resume_text: str) -> str:
    return f"{_INSTRUCTIONS}\n\nResume text:\n{resume_text}"
