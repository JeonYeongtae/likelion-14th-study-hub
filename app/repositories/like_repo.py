"""
Like Repository — 좋아요 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.like import Like


def get_like(db: Session, user_id: int, post_id: int):
    """
    특정 유저가 특정 게시글에 좋아요 했는지 조회

    SQL: SELECT * FROM likes WHERE user_id = ? AND post_id = ? LIMIT 1;
    """
    return db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()


def get_like_count(db: Session, post_id: int):
    """
    게시글의 좋아요 수

    .count(): 행의 개수를 반환
    SQL: SELECT COUNT(*) FROM likes WHERE post_id = ?;
    """
    return db.query(Like).filter(Like.post_id == post_id).count()


def create_like(db: Session, like: Like):
    """좋아요 생성"""
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


def delete_like(db: Session, like: Like):
    """좋아요 취소"""
    db.delete(like)
    db.commit()
