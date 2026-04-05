"""
Post 모델 — posts 테이블
"""

from sqlalchemy import BigInteger, Boolean, Column, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    view_count = Column(Integer, server_default="0")
    updated_at = Column(DateTime(timezone=True), nullable=True)
    is_edited = Column(Boolean, server_default="false")

    # Relationships
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")  # Phase 3
