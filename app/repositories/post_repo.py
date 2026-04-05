"""
Post Repository — 게시글 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.user import User


def get_posts(db: Session, keyword: str = None, page: int = 1, size: int = 20):
    """
    게시글 목록 조회 (최신순, 검색·페이징 지원)

    keyword: 제목/내용/작성자 닉네임으로 필터링 (OR 조건)
    page: 1부터 시작
    size: 페이지당 항목 수
    """
    query = db.query(Post).join(User, Post.user_id == User.id)

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            Post.title.ilike(like) |
            Post.content.ilike(like) |
            User.nickname.ilike(like)
        )

    total = query.count()
    items = (
        query.order_by(Post.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return items, total


def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()


def get_posts_by_user(db: Session, user_id: int):
    return db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()


def create_post(db: Session, post: Post):
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post: Post):
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post):
    db.delete(post)
    db.commit()
