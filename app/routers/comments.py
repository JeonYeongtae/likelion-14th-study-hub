"""
Comments Router — 댓글 API

댓글은 게시글에 종속되므로 URL이 /posts/{post_id}/comments 형태.

Phase 1: JWT 인증 없이 user_id를 쿼리 파라미터로 전달
         (Session 2에서 JWT 토큰 기반 인증으로 변경 예정)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
    user_id: int,  # 쿼리 파라미터로 유저 id 전달 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    댓글 작성

    POST /posts/3/comments?user_id=1
    요청: {"content": "댓글 내용"}
    """
    try:
        return comment_service.create_comment(db, user_id, post_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    user_id: int,  # 쿼리 파라미터로 유저 id 전달 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    댓글 삭제

    DELETE /posts/3/comments/7?user_id=1
    """
    try:
        comment_service.delete_comment(db, user_id, comment_id)
        return {"message": "댓글이 삭제되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
