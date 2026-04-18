"""
ChatMessage 모델 — chat_messages 테이블

채팅 기능:
- group_id로 어느 스터디 그룹의 채팅인지 연결
- sender_id로 발신자 식별
- WebSocket을 통해 실시간 전송, REST API로 히스토리 조회
"""

from sqlalchemy import BigInteger, Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True)
    group_id = Column(BigInteger, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    sender = relationship("User", back_populates="chat_messages")
    group = relationship("StudyGroup", back_populates="chat_messages")
    read_receipts = relationship("ChatReadReceipt", back_populates="message", cascade="all, delete-orphan")
