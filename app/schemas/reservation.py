"""
Reservation 스키마 — 예약 요청/응답 형태
"""

from datetime import datetime
from pydantic import BaseModel


class ReservationCreate(BaseModel):
    room_id: int
    reservation_time: datetime


class ReservationResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    reservation_time: datetime
    created_at: datetime
    status: str

    model_config = {"from_attributes": True}
