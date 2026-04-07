"""
FastAPI 의존성 — 인증 미들웨어

Phase 4: JWT 토큰에서 현재 유저를 추출하는 Depends() 의존성

사용법:
    from app.core.deps import get_current_user, require_admin, get_optional_user

    @router.get("/me")                         # 인증 필수
    def me(current_user = Depends(get_current_user)):
        ...

    @router.get("/groups/{id}")                # 인증 선택 (비로그인 허용)
    def detail(current_user = Depends(get_optional_user)):
        # current_user가 None이면 비로그인 상태
        ...

    @router.post("/rooms")                     # 관리자 전용
    def create_room(..., current_user = Depends(require_admin)):
        ...
"""

from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token
from app.database import get_db
from app.repositories import user_repo

# auto_error=True  → 토큰 없으면 즉시 401
# auto_error=False → 토큰 없어도 None 반환 (선택적 인증용)
_security_required = HTTPBearer(auto_error=True)
_security_optional = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security_required),
    db: Session = Depends(get_db),
):
    """인증 필수 — 토큰 없거나 만료 시 401"""
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
        )

    user = user_repo.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
        )
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_security_optional),
    db: Session = Depends(get_db),
):
    """인증 선택 — 토큰 없으면 None, 있으면 유저 반환"""
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
        return user_repo.get_user_by_id(db, user_id)
    except (JWTError, KeyError, ValueError):
        return None


def require_admin(current_user=Depends(get_current_user)):
    """admin 권한 필수"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근할 수 있습니다",
        )
    return current_user
