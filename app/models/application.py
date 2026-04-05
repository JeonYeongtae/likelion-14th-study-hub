"""
Application 모델 — applications 테이블

Phase 5: 스터디 그룹 가입 신청
- status: pending / accepted / rejected
- UNIQUE(group_id, applicant_id) → 중복 신청 방지
"""

from sqlalchemy import BigInteger, Column, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("group_id", "applicant_id", name="uq_application"),)

    id = Column(BigInteger, primary_key=True)
    group_id = Column(BigInteger, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False)
    applicant_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Text, nullable=False, server_default="pending")  # pending / accepted / rejected
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    group = relationship("StudyGroup", back_populates="applications")
    applicant = relationship("User", back_populates="applications")
