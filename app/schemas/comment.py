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
    post_title: str = ""        # 댓글이 달린 게시글 제목
    user_id: int
    nickname: str = ""          # 작성자 닉네임
    parent_comment_id: int | None
    content: str
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
