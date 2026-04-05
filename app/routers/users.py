"""
Users Router — 프로필 조회/수정 API

GET  /users/me   내 프로필 조회
PATCH /users/me  닉네임 수정 (중복 검사)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.repositories import user_repo
from app.schemas.user import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ProfileResponse)
def get_profile(current_user=Depends(get_current_user)):
    """내 프로필 조회"""
    return current_user


@router.patch("/me", response_model=ProfileResponse)
def update_profile(
    request: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """닉네임 수정 (중복 검사 포함)"""
    existing = user_repo.get_user_by_nickname(db, request.nickname)
    if existing and existing.id != current_user.id:
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다")

    current_user.nickname = request.nickname
    return user_repo.update_user(db, current_user)
