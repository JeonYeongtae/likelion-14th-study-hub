"""
JWT 유틸리티 — 토큰 생성/검증

Phase 4: JWT 기반 인증
- 토큰 구조: {"sub": user_id, "role": role, "exp": expiry}
- Authorization: Bearer {token} 헤더 방식
"""

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


def create_access_token(user_id: int, role: str) -> str:
    """JWT 액세스 토큰 생성"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    JWT 토큰 디코딩

    Returns: {"sub": "user_id", "role": "user/admin"}
    Raises: JWTError (만료, 변조 등)
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
