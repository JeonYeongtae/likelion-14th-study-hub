"""
Reservation 스키마 — 예약 요청/응답 형태

Phase 1: start_time + end_time (시간 범위 예약)
Phase 6: group_id 추가 (그룹 예약)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReservationCreate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    group_id: Optional[int] = None  # Phase 6: 그룹 예약 시 포함


class ReservationResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    group_id: Optional[int] = None
    created_at: datetime
    status: str

    model_config = {"from_attributes": True}
