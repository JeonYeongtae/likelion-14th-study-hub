"""
ReservationParticipant 스키마 — 예약 참석자 요청/응답 형태
"""

from pydantic import BaseModel


class ReservationParticipantCreate(BaseModel):
    user_id: int


class ReservationParticipantResponse(BaseModel):
    id: int
    reservation_id: int
    user_id: int
    is_representative: bool

    model_config = {"from_attributes": True}
