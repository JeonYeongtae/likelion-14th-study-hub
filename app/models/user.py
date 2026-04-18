"""
User 모델 — users 테이블

Phase 2: role 컬럼 추가 (user/admin)
명세서: deleted_at 추가 (소프트 딜리트용)
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
    role = Column(Text, nullable=False, server_default="user")
    is_active = Column(Boolean, nullable=False, server_default="true")
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # 탈퇴 시각 (30일 후 하드딜리트 기준)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    reservation_participants = relationship("ReservationParticipant", back_populates="user")
    study_groups = relationship("StudyGroup", back_populates="leader")
    applications = relationship("Application", back_populates="applicant")
    notifications = relationship("Notification", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="sender")
    chat_read_receipts = relationship("ChatReadReceipt", back_populates="user")
