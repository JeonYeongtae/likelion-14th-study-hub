"""
Like Repository — 좋아요 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.like import Like


def get_like(db: Session, user_id: int, post_id: int):
    return db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()


def get_like_count(db: Session, post_id: int):
    return db.query(Like).filter(Like.post_id == post_id).count()


def get_likes_by_user(db: Session, user_id: int):
    """내가 좋아요 누른 항목 목록 (최신순, post 관계 포함)"""
    return (
        db.query(Like)
        .filter(Like.user_id == user_id)
        .order_by(Like.created_at.desc())
        .all()
    )


def create_like(db: Session, like: Like):
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


def delete_like(db: Session, like: Like):
    db.delete(like)
    db.commit()
