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


def set_representative(db: Session, post_id: int, image_id: int):
    """해당 게시글의 대표 이미지를 변경 (기존 대표 해제 → 신규 지정)"""
    db.query(PostImage).filter(PostImage.post_id == post_id).update({"is_representative": False})
    db.query(PostImage).filter(PostImage.id == image_id).update({"is_representative": True})
    db.commit()


def delete_image(db: Session, image: PostImage):
    """이미지 레코드 삭제"""
    db.delete(image)
    db.commit()
