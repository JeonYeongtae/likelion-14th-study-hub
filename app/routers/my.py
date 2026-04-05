"""
My Router — 마이페이지 통합 활동 기록 API

GET /my/posts    내가 쓴 게시글
GET /my/comments 내가 쓴 댓글
GET /my/likes    내가 좋아요 누른 게시글
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.repositories import comment_repo, like_repo, post_repo
from app.schemas.comment import CommentResponse
from app.schemas.post import PostResponse

router = APIRouter(prefix="/my", tags=["My Page"])


@router.get("/posts", response_model=list[PostResponse])
def my_posts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 쓴 게시글 목록 (최신순)"""
    return post_repo.get_posts_by_user(db, current_user.id)


@router.get("/comments", response_model=list[CommentResponse])
def my_comments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 쓴 댓글 목록 (최신순, post_id 포함으로 상세 페이지 이동 가능)"""
    return comment_repo.get_comments_by_user(db, current_user.id)


@router.get("/likes", response_model=list[PostResponse])
def my_likes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 좋아요 누른 게시글 목록"""
    likes = like_repo.get_likes_by_user(db, current_user.id)
    return [like.post for like in likes]
