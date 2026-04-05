"""
Room 스키마 — 스터디룸 응답 형태
"""

from datetime import datetime
from pydantic import BaseModel


class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    created_at: datetime
    is_available: bool

    model_config = {"from_attributes": True}
