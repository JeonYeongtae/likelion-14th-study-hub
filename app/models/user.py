"""
User 모델 — users 테이블

Phase 2: role 컬럼 추가 (user/admin)
"""

from sqlalchemy import BigInteger, Boolean, Column, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    email = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    nickname = Column(Text, nullable=False)
    role = Column(Text, nullable=False, server_default="user")  # Phase 2: user / admin
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")

    # Relationships
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    reservation_participants = relationship("ReservationParticipant", back_populates="user")
    study_groups = relationship("StudyGroup", back_populates="leader")
    applications = relationship("Application", back_populates="applicant")
