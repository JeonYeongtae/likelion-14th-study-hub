"""
Comment Service — 댓글 비즈니스 로직

규칙:
- 댓글 삭제는 작성자 본인만 가능
- parent_comment_id가 있으면 대댓글
"""

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.repositories import comment_repo, post_repo
from app.schemas.comment import CommentCreate


def get_comments(db: Session, post_id: int):
    """특정 게시글의 댓글 목록"""
    return comment_repo.get_comments_by_post(db, post_id)


def create_comment(db: Session, user_id: int, post_id: int, request: CommentCreate):
    """댓글/대댓글 작성"""
    post = post_repo.get_post_by_id(db, post_id)
    if not post:
        raise ValueError("게시글을 찾을 수 없습니다")

    new_comment = Comment(
        post_id=post_id,
        user_id=user_id,
        parent_comment_id=request.parent_comment_id,
        content=request.content,
    )
    return comment_repo.create_comment(db, new_comment)


def delete_comment(db: Session, user_id: int, comment_id: int):
    """댓글 삭제 (작성자 본인만)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise ValueError("댓글을 찾을 수 없습니다")
    if comment.user_id != user_id:
        raise PermissionError("본인의 댓글만 삭제할 수 있습니다")

    comment_repo.delete_comment(db, comment)
