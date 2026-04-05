"""
Auth 스키마 — 회원가입/로그인 요청·응답 형태 정의
"""

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


class LoginResponse(BaseModel):
    user_id: int
