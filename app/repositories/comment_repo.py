"""
Comment Repository — 댓글 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.comment import Comment


def get_comments_by_post(db: Session, post_id: int):
    """
    특정 게시글의 댓글 목록 조회 (오래된 순)

    SQL: SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC;
    """
    return db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()


def create_comment(db: Session, comment: Comment):
    """댓글 생성"""
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: Comment):
    """댓글 삭제"""
    db.delete(comment)
    db.commit()
