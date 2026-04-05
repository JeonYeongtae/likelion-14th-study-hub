"""
Posts Router — 게시글 CRUD API

Phase 4: JWT 인증으로 변경
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.like import Like
from app.repositories import like_repo
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.services import post_service

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
    게시글 상세 조회 (조회수 +1, 이미지 포함)

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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    게시글 작성

    POST /posts
    Authorization: Bearer {token}
    """
    return post_service.create_post(db, current_user.id, request)


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    request: PostUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    게시글 수정

    PATCH /posts/3
    Authorization: Bearer {token}
    """
    try:
        return post_service.update_post(db, current_user.id, post_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    게시글 삭제

    DELETE /posts/3
    Authorization: Bearer {token}
    """
    try:
        post_service.delete_post(db, current_user.id, post_id)
        return {"message": "게시글이 삭제되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ── 좋아요 ──

@router.post("/{post_id}/like")
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    좋아요 토글

    POST /posts/3/like
    Authorization: Bearer {token}
    """
    existing = like_repo.get_like(db, current_user.id, post_id)
    if existing:
        like_repo.delete_like(db, existing)
        message = "좋아요를 취소했습니다"
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        like_repo.create_like(db, new_like)
        message = "좋아요를 눌렀습니다"

    count = like_repo.get_like_count(db, post_id)
    return {"message": message, "like_count": count}
