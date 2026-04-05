"""
Reservation 모델 — reservations 테이블

Phase 1: start_time + end_time (시간 겹침 방지)
Phase 6: group_id 추가 (그룹 예약)

group_id NULL → 개인 예약
group_id 존재 → 그룹 예약 (조장만 신청 가능)
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
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    group_id = Column(BigInteger, ForeignKey("study_groups.id"), nullable=True)  # Phase 6
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(Text, nullable=False, server_default="confirmed")

    # Relationships
    room = relationship("StudyRoom", back_populates="reservations")
    user = relationship("User", back_populates="reservations")
    participants = relationship("ReservationParticipant", back_populates="reservation")
    group = relationship("StudyGroup", back_populates="reservations")
