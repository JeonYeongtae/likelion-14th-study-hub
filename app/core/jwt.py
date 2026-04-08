"""
JWT 유틸리티 — 토큰 생성/검증

Phase 4: JWT 기반 인증 (단일 토큰)
Week 4 업그레이드: Access Token(15분) + Refresh Token(7일) 분리
- Access Token: Authorization 헤더로 전달 (15분 수명)
- Refresh Token: httpOnly 쿠키로 전달 (7일 수명, Rotation 방식)
"""

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(user_id: int, role: str) -> str:
    """
    JWT 액세스 토큰 생성 (수명: 15분)

    payload: {"sub": user_id, "role": role, "type": "access", "exp": expiry}
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int, role: str) -> str:
    """
    JWT 리프레시 토큰 생성 (수명: 7일)

    httpOnly 쿠키에 저장. Rotation 방식으로 재발급 시 기존 토큰을 덮어씀.
    payload: {"sub": user_id, "role": role, "type": "refresh", "exp": expiry}
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    액세스 토큰 디코딩

    Returns: {"sub": "user_id", "role": "user/admin", "type": "access"}
    Raises: JWTError (만료, 변조 등)
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def decode_refresh_token(token: str) -> dict:
    """
    리프레시 토큰 디코딩 + 타입 검증

    Returns: {"sub": "user_id", "role": "user/admin", "type": "refresh"}
    Raises: JWTError (만료, 변조, 타입 불일치)
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != "refresh":
        raise JWTError("액세스 토큰은 리프레시에 사용할 수 없습니다")
    return payload
