"""
ReservationParticipant 모델 — reservation_participants 테이블

is_representative: 대표자(예약 신청자) 여부
"""

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ReservationParticipant(Base):
    __tablename__ = "reservation_participants"

    id = Column(BigInteger, primary_key=True)
    reservation_id = Column(BigInteger, ForeignKey("reservations.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    is_representative = Column(Boolean, nullable=False, server_default="false")

    # Relationships
    reservation = relationship("Reservation", back_populates="participants")
    user = relationship("User", back_populates="reservation_participants")
