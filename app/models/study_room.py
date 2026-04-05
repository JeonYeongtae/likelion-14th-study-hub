"""
StudyRoom 모델 — study_rooms 테이블

Phase 2: description 컬럼 추가
Phase 4: room_settings 관계 추가
"""

from sqlalchemy import BigInteger, Boolean, Column, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class StudyRoom(Base):
    __tablename__ = "study_rooms"

    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    capacity = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)  # Phase 2
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_available = Column(Boolean, nullable=False, server_default="true")

    # Relationships
    reservations = relationship("Reservation", back_populates="room")
    settings = relationship("RoomSettings", back_populates="room", uselist=False)
