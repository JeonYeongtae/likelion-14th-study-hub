"""
Post Repository — 게시글 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.post import Post


def get_posts(db: Session):
    """
    게시글 전체 목록 조회 (최신순)

    .order_by(Post.created_at.desc()): 최신 글이 위로
    .all(): 전부 가져오기

    SQL: SELECT * FROM posts ORDER BY created_at DESC;
    """
    return db.query(Post).order_by(Post.created_at.desc()).all()


def get_post_by_id(db: Session, post_id: int):
    """
    게시글 1개 조회

    SQL: SELECT * FROM posts WHERE id = ? LIMIT 1;
    """
    return db.query(Post).filter(Post.id == post_id).first()


def create_post(db: Session, post: Post):
    """
    게시글 생성

    SQL: INSERT INTO posts (user_id, title, content) VALUES (...);
    """
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post: Post):
    """
    게시글 수정

    이미 조회해서 수정한 post 객체를 DB에 반영한다.
    db.commit()하면 변경된 필드만 UPDATE된다.

    SQL: UPDATE posts SET title=?, content=? WHERE id=?;
    """
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post):
    """
    게시글 삭제

    SQL: DELETE FROM posts WHERE id = ?;
    """
    db.delete(post)
    db.commit()
