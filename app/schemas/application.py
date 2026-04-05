"""
Application 스키마 — 스터디 가입 신청 요청/응답 형태

Phase 5
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    message: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """조장이 수락/거절 처리"""
    status: str  # accepted / rejected


class ApplicationResponse(BaseModel):
    id: int
    group_id: int
    applicant_id: int
    status: str
    message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
