"""
Comment 모델 — comments 테이블

parent_comment_id: 대댓글을 위한 자기 참조 FK (NULL이면 최상위 댓글)
"""

from sqlalchemy import BigInteger, Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey("posts.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    parent_comment_id = Column(BigInteger, ForeignKey("comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", back_populates="parent", foreign_keys=[parent_comment_id])
    parent = relationship("Comment", back_populates="replies", remote_side="Comment.id")

    # ─── 스키마 직렬화용 computed 속성 ──────────────────────────────────────────
    @property
    def nickname(self) -> str:
        return self.user.nickname if self.user else ""
