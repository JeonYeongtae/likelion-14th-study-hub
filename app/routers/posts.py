"""
Posts Router — 게시글 CRUD API

게시글 목록/상세는 누구나 가능.
작성/수정/삭제/좋아요는 user_id를 쿼리 파라미터로 받는다.

Phase 1: JWT 인증 없이 user_id를 직접 쿼리 파라미터로 전달
         (Session 2에서 JWT 토큰 기반 인증으로 변경 예정)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.services import post_service
from app.repositories import like_repo
from app.models.like import Like

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    """
    게시글 전체 목록

    GET /posts
    로그인 불필요
    """
    return post_service.get_posts(db)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    게시글 상세 조회 (조회수 +1)

    GET /posts/3
    로그인 불필요
    """
    try:
        return post_service.get_post(db, post_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=PostResponse)
def create_post(
    request: PostCreate,
    user_id: int,  # 쿼리 파라미터로 유저 id 전달 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    게시글 작성

    POST /posts?user_id=1
    요청: {"title": "...", "content": "..."}
    """
    return post_service.create_post(db, user_id, request)


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    request: PostUpdate,
    user_id: int,  # 쿼리 파라미터로 유저 id 전달 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    게시글 수정

    PATCH /posts/3?user_id=1
    요청: {"title": "새 제목"} (바꿀 필드만 보내면 된다)
    """
    try:
        return post_service.update_post(db, user_id, post_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    user_id: int,  # 쿼리 파라미터로 유저 id 전달 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    게시글 삭제

    DELETE /posts/3?user_id=1
    """
    try:
        post_service.delete_post(db, user_id, post_id)
        return {"message": "게시글이 삭제되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ── 좋아요 ──

@router.post("/{post_id}/like")
def toggle_like(
    post_id: int,
    user_id: int,  # 쿼리 파라미터로 유저 id 전달 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    좋아요 토글 (누르면 좋아요, 다시 누르면 취소)

    POST /posts/3/like?user_id=1
    이미 좋아요 했으면 -> 취소
    아직 안 했으면 -> 좋아요
    """
    existing = like_repo.get_like(db, user_id, post_id)
    if existing:
        like_repo.delete_like(db, existing)
        message = "좋아요를 취소했습니다"
    else:
        new_like = Like(user_id=user_id, post_id=post_id)
        like_repo.create_like(db, new_like)
        message = "좋아요를 눌렀습니다"

    count = like_repo.get_like_count(db, post_id)
    return {"message": message, "like_count": count}
