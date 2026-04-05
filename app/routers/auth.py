"""
Auth Router — 회원가입/로그인/로그아웃/탈퇴/내 정보 API

Phase 4: JWT 토큰, /auth/me
명세서: 로그아웃, 회원탈퇴(소프트 딜리트)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MeResponse,
    SignupRequest,
    SignupResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=SignupResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    회원가입

    POST /auth/signup
    - 이메일/닉네임 중복 검사
    - 비밀번호 bcrypt 해싱
    """
    try:
        return auth_service.signup(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    로그인

    POST /auth/login
    - 탈퇴 계정(is_active=False) 로그인 불가
    - 성공 시 JWT 토큰 반환
    """
    try:
        return auth_service.login(db, request)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
def logout():
    """
    로그아웃

    POST /auth/logout
    JWT는 서버 상태가 없으므로 클라이언트에서 토큰을 삭제하면 됩니다.
    서버는 성공 응답만 반환합니다.
    """
    return {"message": "로그아웃 되었습니다"}


@router.delete("/withdraw")
def withdraw(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    회원 탈퇴 (소프트 딜리트)

    DELETE /auth/withdraw
    - is_active = False, deleted_at = 현재 시각
    - 30일 후 pg_cron이 하드딜리트 처리 (migrations.sql 참고)
    """
    try:
        auth_service.withdraw(db, current_user.id)
        return {"message": "탈퇴 처리되었습니다. 30일 후 계정이 완전히 삭제됩니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/me", response_model=MeResponse)
def me(current_user=Depends(get_current_user)):
    """내 정보 조회"""
    return current_user
