"""
Comment Service — 댓글 비즈니스 로직

명세서: 댓글 수정(PATCH) 추가
알림: 댓글 생성 시 게시글 작성자에게 알림
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.repositories import comment_repo, post_repo
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services import notification_service


def get_comments(db: Session, post_id: int):
    """특정 게시글의 댓글 목록"""
    return comment_repo.get_comments_by_post(db, post_id)


def create_comment(db: Session, user_id: int, post_id: int, request: CommentCreate):
    """댓글/대댓글 작성 + 작성자에게 알림"""
    post = post_repo.get_post_by_id(db, post_id)
    if not post:
        raise ValueError("게시글을 찾을 수 없습니다")

    new_comment = Comment(
        post_id=post_id,
        user_id=user_id,
        parent_comment_id=request.parent_comment_id,
        content=request.content,
    )
    comment = comment_repo.create_comment(db, new_comment)

    # 게시글 작성자에게 댓글 알림 (본인 제외)
    notification_service.create_comment_notification(
        db,
        post_author_id=post.user_id,
        commenter_id=user_id,
        post_id=post_id,
        post_title=post.title,
    )

    return comment


def update_comment(db: Session, user_id: int, comment_id: int, request: CommentUpdate):
    """댓글 수정 (작성자 본인만)"""
    comment = comment_repo.get_comment_by_id(db, comment_id)
    if not comment:
        raise ValueError("댓글을 찾을 수 없습니다")
    if comment.user_id != user_id:
        raise PermissionError("본인의 댓글만 수정할 수 있습니다")

    comment.content = request.content
    comment.updated_at = datetime.now(timezone.utc)
    return comment_repo.update_comment(db, comment)


def delete_comment(db: Session, user_id: int, comment_id: int):
    """댓글 삭제 (작성자 본인만)"""
    comment = comment_repo.get_comment_by_id(db, comment_id)
    if not comment:
        raise ValueError("댓글을 찾을 수 없습니다")
    if comment.user_id != user_id:
        raise PermissionError("본인의 댓글만 삭제할 수 있습니다")

    comment_repo.delete_comment(db, comment)
