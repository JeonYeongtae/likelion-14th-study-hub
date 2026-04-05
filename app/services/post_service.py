"""
Post Service — 게시글 비즈니스 로직

규칙:
- 게시글 수정/삭제는 작성자 본인만 가능
- 게시글 조회 시 조회수 +1
- 수정 시 is_edited = True로 변경
"""

from sqlalchemy.orm import Session

from app.models.post import Post
from app.repositories import post_repo
from app.schemas.post import PostCreate, PostUpdate


def get_posts(db: Session):
    """게시글 전체 목록"""
    return post_repo.get_posts(db)


def get_post(db: Session, post_id: int):
    """게시글 상세 조회 + 조회수 증가"""
    post = post_repo.get_post_by_id(db, post_id)
    if not post:
        raise ValueError("게시글을 찾을 수 없습니다")

    post.view_count = (post.view_count or 0) + 1
    post_repo.update_post(db, post)
    return post


def create_post(db: Session, user_id: int, request: PostCreate):
    """게시글 작성"""
    new_post = Post(
        user_id=user_id,
        title=request.title,
        content=request.content,
    )
    return post_repo.create_post(db, new_post)


def update_post(db: Session, user_id: int, post_id: int, request: PostUpdate):
    """게시글 수정 (작성자 본인만)"""
    post = post_repo.get_post_by_id(db, post_id)
    if not post:
        raise ValueError("게시글을 찾을 수 없습니다")
    if post.user_id != user_id:
        raise PermissionError("본인의 게시글만 수정할 수 있습니다")

    if request.title is not None:
        post.title = request.title
    if request.content is not None:
        post.content = request.content
    post.is_edited = True

    return post_repo.update_post(db, post)


def delete_post(db: Session, user_id: int, post_id: int):
    """게시글 삭제 (작성자 본인만)"""
    post = post_repo.get_post_by_id(db, post_id)
    if not post:
        raise ValueError("게시글을 찾을 수 없습니다")
    if post.user_id != user_id:
        raise PermissionError("본인의 게시글만 삭제할 수 있습니다")

    post_repo.delete_post(db, post)
