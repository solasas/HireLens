from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.services.llm.base import LLMProvider
from app.services.llm.factory import get_llm_provider

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
LLMProviderDep = Annotated[LLMProvider, Depends(get_llm_provider)]
