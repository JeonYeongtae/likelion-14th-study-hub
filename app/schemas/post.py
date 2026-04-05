"""
Post 스키마 — 게시글 요청/응답 형태

Phase 3: images 포함
명세서: 검색·페이징 응답 (total 포함)
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class PostImageResponse(BaseModel):
    id: int
    image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    view_count: int | None
    created_at: datetime
    updated_at: datetime | None
    is_edited: bool | None
    images: Optional[List[PostImageResponse]] = []

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    """검색·페이징 목록 응답"""
    items: List[PostResponse]
    total: int
    page: int
    size: int
