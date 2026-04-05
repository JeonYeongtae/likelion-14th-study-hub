"""
PostImage 모델 — post_images 테이블

Phase 3: 게시글 이미지 첨부
- image_url: Supabase Storage에 업로드된 파일의 공개 URL
- 파일 자체는 DB에 저장하지 않음
"""

from sqlalchemy import BigInteger, Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    post = relationship("Post", back_populates="images")
