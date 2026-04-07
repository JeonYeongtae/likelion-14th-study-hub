"""
Auth 스키마 — 회원가입/로그인 요청·응답 형태 정의

Phase 4: 로그인 응답에 JWT 토큰 포함, /auth/me 응답 추가
"""

from datetime import datetime
from pydantic import BaseModel


class SignupRequest(BaseModel):
    email: str
    password: str
    nickname: str


class SignupResponse(BaseModel):
    id: int
    email: str
    nickname: str

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class ReactivateRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    """Phase 4: JWT 토큰 반환"""
    access_token: str
    token_type: str = "bearer"
    user_id: int


class MeResponse(BaseModel):
    """Phase 4: /auth/me — 현재 로그인 유저 정보"""
    id: int
    email: str
    nickname: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
