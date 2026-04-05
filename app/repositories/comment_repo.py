"""
Comment Repository — 댓글 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.comment import Comment


def get_comments_by_post(db: Session, post_id: int):
    return db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()


def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


def get_comments_by_user(db: Session, user_id: int):
    return db.query(Comment).filter(Comment.user_id == user_id).order_by(Comment.created_at.desc()).all()


def create_comment(db: Session, comment: Comment):
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(db: Session, comment: Comment):
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: Comment):
    db.delete(comment)
    db.commit()
