"""
StudyRoom 모델 — study_rooms 테이블
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
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_available = Column(Boolean, nullable=False, server_default="true")

    # Relationships
    reservations = relationship("Reservation", back_populates="room")
