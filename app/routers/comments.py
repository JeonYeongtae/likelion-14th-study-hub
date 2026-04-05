"""
Comments Router — 댓글 API

명세서: PATCH 댓글 수정 추가
Phase 4: JWT 인증
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services import comment_service

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["Comments"])


@router.get("/", response_model=list[CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return comment_service.get_comments(db, post_id)


@router.post("/", response_model=CommentResponse)
def create_comment(
    post_id: int,
    request: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return comment_service.create_comment(db, current_user.id, post_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment(
    post_id: int,
    comment_id: int,
    request: CommentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """댓글 수정 (본인만)"""
    try:
        return comment_service.update_comment(db, current_user.id, comment_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        comment_service.delete_comment(db, current_user.id, comment_id)
        return {"message": "댓글이 삭제되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
