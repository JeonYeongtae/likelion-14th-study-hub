"""
Posts Router — 게시글 CRUD API

명세서: keyword 검색 + page/size 페이징
Phase 4: JWT 인증
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.like import Like
from app.repositories import like_repo
from app.schemas.post import PostCreate, PostListResponse, PostResponse, PostUpdate
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=PostListResponse)
def get_posts(
    keyword: Optional[str] = Query(None, description="제목/내용/닉네임 검색어"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    게시글 목록 (검색·페이징)

    GET /posts?keyword=알고리즘&page=1&size=10
    """
    return post_service.get_posts(db, keyword=keyword, page=page, size=size)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """게시글 상세 조회 (조회수 +1, 이미지 포함)"""
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
    """게시글 작성 (Authorization: Bearer {token})"""
    return post_service.create_post(db, current_user.id, request)


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    request: PostUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """게시글 수정"""
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
    """게시글 삭제"""
    try:
        post_service.delete_post(db, current_user.id, post_id)
        return {"message": "게시글이 삭제되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{post_id}/like")
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """좋아요 토글"""
    existing = like_repo.get_like(db, current_user.id, post_id)
    if existing:
        like_repo.delete_like(db, existing)
        message = "좋아요를 취소했습니다"
    else:
        like_repo.create_like(db, Like(user_id=current_user.id, post_id=post_id))
        message = "좋아요를 눌렀습니다"
    return {"message": message, "like_count": like_repo.get_like_count(db, post_id)}
