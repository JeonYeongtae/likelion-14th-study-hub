"""
Auth 스키마 — 회원가입/로그인 요청·응답 형태 정의

Phase 4: 로그인 응답에 JWT 토큰 포함, /auth/me 응답 추가
"""

from datetime import datetime
from pydantic import BaseModel, field_validator


class SignupRequest(BaseModel):
    email: str
    password: str
    nickname: str

    @field_validator("password")
    @classmethod
    def password_byte_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("비밀번호는 72바이트(영문 72자 / 한글 약 24자) 이내로 입력해주세요.")
        return v


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

    @field_validator("password")
    @classmethod
    def password_byte_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("비밀번호는 72바이트(영문 72자 / 한글 약 24자) 이내로 입력해주세요.")
        return v


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
