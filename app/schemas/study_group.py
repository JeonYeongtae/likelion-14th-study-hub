"""
StudyGroup 스키마 — 스터디 모집 요청/응답 형태

Phase 5
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class StudyGroupCreate(BaseModel):
    title: str
    description: Optional[str] = None
    max_members: int


class StudyGroupUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    max_members: Optional[int] = None
    status: Optional[str] = None  # 모집중 / 모집완료 / 종료


class ApplicationSummary(BaseModel):
    id: int
    applicant_id: int
    status: str
    message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class StudyGroupResponse(BaseModel):
    id: int
    leader_id: int
    title: str
    description: Optional[str] = None
    max_members: int
    current_members: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StudyGroupDetailResponse(StudyGroupResponse):
    """GET /groups/{id} — 신청 목록 포함 (조장에게만 노출)"""
    applications: Optional[List[ApplicationSummary]] = []
