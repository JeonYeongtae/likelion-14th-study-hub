"""
Post 스키마 — 게시글 요청/응답 형태

Phase 3: 상세 조회 응답에 images 포함
"""

from datetime import datetime
from typing import Optional, List
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
    images: Optional[List[PostImageResponse]] = []  # Phase 3

    model_config = {"from_attributes": True}
