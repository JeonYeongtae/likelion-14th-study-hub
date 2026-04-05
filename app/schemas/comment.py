"""
Comment 스키마 — 댓글 요청/응답 형태
"""

from datetime import datetime
from pydantic import BaseModel


class CommentCreate(BaseModel):
    content: str
    parent_comment_id: int | None = None


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    parent_comment_id: int | None
    content: str
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
