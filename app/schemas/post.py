"""
Post 스키마 — 게시글 요청/응답 형태
"""

from datetime import datetime
from pydantic import BaseModel


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

    model_config = {"from_attributes": True}
