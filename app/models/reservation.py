"""
Reservation 모델 — reservations 테이블

reservation_time: 예약 신청 대상 시간 (단일 시각)
status: 예약 상태 (예: 'confirmed', 'cancelled' 등)
"""

from sqlalchemy import BigInteger, Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(BigInteger, primary_key=True)
    room_id = Column(BigInteger, ForeignKey("study_rooms.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    reservation_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(Text, nullable=False)

    # Relationships
    room = relationship("StudyRoom", back_populates="reservations")
    user = relationship("User", back_populates="reservations")
    participants = relationship("ReservationParticipant", back_populates="reservation")
