"""
FastAPI 의존성 — 인증 미들웨어

Phase 4: JWT 토큰에서 현재 유저를 추출하는 Depends() 의존성

사용법:
    from app.core.deps import get_current_user, require_admin

    @router.get("/me")
    def me(current_user = Depends(get_current_user)):
        ...

    @router.post("/rooms")
    def create_room(..., current_user = Depends(require_admin)):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token
from app.database import get_db
from app.repositories import user_repo

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Authorization: Bearer {token} 헤더에서 유저 추출

    토큰이 없거나 만료/변조된 경우 401 반환
    """
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
        )

    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
        )
    return user


def require_admin(current_user=Depends(get_current_user)):
    """admin 권한이 필요한 엔드포인트에 사용"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근할 수 있습니다",
        )
    return current_user
