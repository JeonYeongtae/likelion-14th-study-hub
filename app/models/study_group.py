"""
StudyGroup 모델 — study_groups 테이블

Phase 5: 스터디 모집 시스템
- status: 모집중 / 모집완료 / 종료
- current_members는 조장 포함 (기본값 1)
"""

from sqlalchemy import BigInteger, Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class StudyGroup(Base):
    __tablename__ = "study_groups"

    id = Column(BigInteger, primary_key=True)
    leader_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    max_members = Column(Integer, nullable=False)
    current_members = Column(Integer, nullable=False, server_default="1")
    status = Column(Text, nullable=False, server_default="모집중")  # 모집중 / 모집완료 / 종료
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    leader = relationship("User", back_populates="study_groups")
    applications = relationship("Application", back_populates="group")
    reservations = relationship("Reservation", back_populates="group")
    chat_messages = relationship("ChatMessage", back_populates="group", cascade="all, delete-orphan")
