"""
RoomSettings 모델 — room_settings 테이블

Phase 4: 룸별 이용 시간 설정
- open_time / close_time: 이용 가능 시간대
- slot_duration: 예약 단위 (분, 기본 60분)
"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RoomSettings(Base):
    __tablename__ = "room_settings"

    id = Column(BigInteger, primary_key=True)
    room_id = Column(BigInteger, ForeignKey("study_rooms.id", ondelete="CASCADE"), nullable=False, unique=True)
    open_time = Column(Time, nullable=False, server_default="09:00")
    close_time = Column(Time, nullable=False, server_default="22:00")
    slot_duration = Column(Integer, nullable=False, server_default="60")  # 분 단위
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    room = relationship("StudyRoom", back_populates="settings")
