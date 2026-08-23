import pytest
from pydantic import BaseModel

from app.core.exceptions import LLMResponseValidationError
from app.services.llm.extraction import extract_with_retry
from tests.factories.llm import FakeLLMProvider


class _DummySchema(BaseModel):
    value: str


@pytest.mark.asyncio
async def test_extract_with_retry_returns_result_on_first_success() -> None:
    llm = FakeLLMProvider([_DummySchema(value="ok")])

    result = await extract_with_retry(llm, "prompt", _DummySchema)

    assert result.value == "ok"
    assert len(llm.prompts) == 1


@pytest.mark.asyncio
async def test_extract_with_retry_retries_once_with_error_appended_to_prompt() -> None:
    llm = FakeLLMProvider(
        [LLMResponseValidationError("missing field 'value'"), _DummySchema(value="ok")]
    )

    result = await extract_with_retry(llm, "original prompt", _DummySchema)

    assert result.value == "ok"
    assert len(llm.prompts) == 2
    assert llm.prompts[0] == "original prompt"
    assert "original prompt" in llm.prompts[1]
    assert "missing field 'value'" in llm.prompts[1]


@pytest.mark.asyncio
async def test_extract_with_retry_propagates_error_after_second_failure() -> None:
    llm = FakeLLMProvider(
        [
            LLMResponseValidationError("first failure"),
            LLMResponseValidationError("second failure"),
        ]
    )

    with pytest.raises(LLMResponseValidationError) as exc_info:
        await extract_with_retry(llm, "prompt", _DummySchema)

    assert exc_info.value.message == "second failure"
    assert len(llm.prompts) == 2
