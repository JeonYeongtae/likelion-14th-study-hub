"""
PostImages Router — 게시글 이미지 API

Phase 3: Supabase Storage 연동
"""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.schemas.post import PostImageResponse
from app.services import post_image_service

router = APIRouter(prefix="/posts/{post_id}/images", tags=["Post Images"])


@router.post("/", response_model=PostImageResponse)
def upload_image(
    post_id: int,
    file: UploadFile = File(...),
    is_representative: bool = Query(False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    이미지 업로드

    POST /posts/3/images/?is_representative=true
    Authorization: Bearer {token}
    Content-Type: multipart/form-data
    """
    try:
        return post_image_service.upload_image(db, current_user.id, post_id, file, is_representative)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{image_id}/set-representative", response_model=PostImageResponse)
def set_representative(
    post_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    대표 이미지 변경

    PATCH /posts/3/images/5/set-representative
    Authorization: Bearer {token}
    """
    try:
        return post_image_service.set_representative(db, current_user.id, post_id, image_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{image_id}")
def delete_image(
    post_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    이미지 삭제

    DELETE /posts/3/images/1
    Authorization: Bearer {token}
    """
    try:
        post_image_service.delete_image(db, current_user.id, post_id, image_id)
        return {"message": "이미지가 삭제되었습니다"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
