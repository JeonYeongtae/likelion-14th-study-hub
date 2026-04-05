"""
PostImage Service — 게시글 이미지 업로드/삭제 비즈니스 로직

Phase 3: Supabase Storage 연동
- 파일을 Storage에 업로드 후 URL만 DB에 저장
- 삭제 시 Storage 파일도 함께 제거
"""

import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.post_image import PostImage
from app.repositories import post_image_repo, post_repo


def _get_supabase_client():
    """Supabase 클라이언트 초기화"""
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL, SUPABASE_SERVICE_KEY 환경변수를 설정하세요")
    return create_client(url, key)


BUCKET = "post-images"


def upload_image(db: Session, user_id: int, post_id: int, file: UploadFile):
    """
    이미지 업로드

    1. 게시글 존재 및 권한 확인
    2. Supabase Storage에 파일 업로드
    3. URL을 post_images 테이블에 저장
    """
    post = post_repo.get_post_by_id(db, post_id)
    if not post:
        raise ValueError("게시글을 찾을 수 없습니다")
    if post.user_id != user_id:
        raise PermissionError("본인의 게시글에만 이미지를 첨부할 수 있습니다")

    # 고유 파일명 생성
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    file_path = f"{post_id}/{uuid.uuid4().hex}{ext}"

    supabase = _get_supabase_client()
    file_bytes = file.file.read()
    supabase.storage.from_(BUCKET).upload(file_path, file_bytes, {"content-type": file.content_type})

    public_url = supabase.storage.from_(BUCKET).get_public_url(file_path)

    image = PostImage(post_id=post_id, image_url=public_url)
    return post_image_repo.create_image(db, image)


def delete_image(db: Session, user_id: int, post_id: int, image_id: int):
    """
    이미지 삭제

    1. 이미지 및 게시글 권한 확인
    2. Storage 파일 삭제
    3. DB 레코드 삭제
    """
    image = post_image_repo.get_image_by_id(db, image_id)
    if not image:
        raise ValueError("이미지를 찾을 수 없습니다")
    if image.post_id != post_id:
        raise ValueError("해당 게시글의 이미지가 아닙니다")

    post = post_repo.get_post_by_id(db, post_id)
    if post.user_id != user_id:
        raise PermissionError("본인의 게시글 이미지만 삭제할 수 있습니다")

    # Storage에서 파일 경로 추출 후 삭제
    try:
        supabase = _get_supabase_client()
        # URL에서 버킷 이후 경로 추출
        marker = f"/object/public/{BUCKET}/"
        idx = image.image_url.find(marker)
        if idx != -1:
            file_path = image.image_url[idx + len(marker):]
            supabase.storage.from_(BUCKET).remove([file_path])
    except Exception:
        pass  # Storage 삭제 실패해도 DB 레코드는 삭제

    post_image_repo.delete_image(db, image)
