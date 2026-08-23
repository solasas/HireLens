from pydantic import BaseModel, Field, field_validator


class JobDescriptionInput(BaseModel):
    text: str = Field(min_length=1, max_length=20000)

    @field_validator("text")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Job description text cannot be blank.")
        return value
