"""
Notification 모델 — notifications 테이블

알림 종류 (type):
- comment: 내 게시글에 댓글이 달렸을 때
- reservation: 예약 시간 임박 알림 (스케줄러에서 생성)
"""

from sqlalchemy import BigInteger, Boolean, Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Text, nullable=False)          # comment / reservation
    message = Column(Text, nullable=False)
    related_id = Column(BigInteger, nullable=True)   # 관련 리소스 ID (post_id, reservation_id 등)
    is_read = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")
