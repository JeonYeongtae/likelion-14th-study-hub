"""
PostImage Repository — 게시글 이미지 DB 조작

Phase 3
"""

from sqlalchemy.orm import Session
from app.models.post_image import PostImage


def get_images_by_post(db: Session, post_id: int):
    """게시글의 이미지 목록"""
    return db.query(PostImage).filter(PostImage.post_id == post_id).all()


def get_image_by_id(db: Session, image_id: int):
    """이미지 1개 조회"""
    return db.query(PostImage).filter(PostImage.id == image_id).first()


def create_image(db: Session, image: PostImage):
    """이미지 레코드 생성"""
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def delete_image(db: Session, image: PostImage):
    """이미지 레코드 삭제"""
    db.delete(image)
    db.commit()
