"""
ChatReadReceipt 모델 — chat_read_receipts 테이블

읽음 처리 전략:
- group_id + user_id 쌍으로 UPSERT
- last_read_message_id: 해당 유저가 마지막으로 읽은 메시지 ID
- updated_at: 마지막 읽음 시각
- 미읽음 수 = chat_messages.id > last_read_message_id 인 행 수
"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ChatReadReceipt(Base):
    __tablename__ = "chat_read_receipts"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_chat_read_receipt"),)

    id = Column(BigInteger, primary_key=True)
    group_id = Column(BigInteger, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_read_message_id = Column(BigInteger, ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_read_receipts")
    message = relationship("ChatMessage", back_populates="read_receipts")
