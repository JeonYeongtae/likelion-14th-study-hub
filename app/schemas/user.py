"""
User 스키마 — 프로필 요청/응답 형태
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: int
    email: str
    nickname: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    nickname: str
