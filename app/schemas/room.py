"""
Room 스키마 — 스터디룸 요청/응답 형태

Phase 2: description 추가, 관리자 CRUD 스키마
Phase 4: RoomSettings 스키마 추가
"""

from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel


class RoomCreate(BaseModel):
    """Phase 2: 관리자 룸 생성"""
    name: str
    capacity: int
    description: Optional[str] = None


class RoomUpdate(BaseModel):
    """Phase 2: 관리자 룸 수정"""
    name: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    is_available: Optional[bool] = None


class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    description: Optional[str] = None
    created_at: datetime
    is_available: bool

    model_config = {"from_attributes": True}


class RoomSettingsUpdate(BaseModel):
    """Phase 4: 룸 설정 수정"""
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    slot_duration: Optional[int] = None  # 분 단위


class RoomSettingsResponse(BaseModel):
    """Phase 4: 룸 설정 응답"""
    id: int
    room_id: int
    open_time: time
    close_time: time
    slot_duration: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
