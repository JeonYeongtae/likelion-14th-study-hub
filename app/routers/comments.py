"""
Comments Router — 댓글 API

Phase 4: JWT 인증으로 변경
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.schemas.comment import CommentCreate, CommentResponse
from app.services import comment_service

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["Comments"])


@router.get("/", response_model=list[CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    """
    댓글 목록 조회

    GET /posts/3/comments
    로그인 불필요
    """
    return comment_service.get_comments(db, post_id)


@router.post("/", response_model=CommentResponse)
def create_comment(
    post_id: int,
    request: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    댓글 작성

    POST /posts/3/comments
    Authorization: Bearer {token}
    """
    try:
        return comment_service.create_comment(db, current_user.id, post_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    댓글 삭제

    DELETE /posts/3/comments/7
    Authorization: Bearer {token}
    """
    try:
        comment_service.delete_comment(db, current_user.id, comment_id)
        return {"message": "댓글이 삭제되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
