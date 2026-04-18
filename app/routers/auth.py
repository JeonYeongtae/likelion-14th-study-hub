"""
Auth Router — 회원가입/로그인/로그아웃/탈퇴/복구/내 정보/토큰 갱신 API

Phase 4: JWT 토큰, /auth/me
고도화: 30일 유예 비활성화 + 계정 복구(Reactivate)
Week 4 업그레이드:
  - 로그인/복구 시 Access Token(Body) + Refresh Token(httpOnly Cookie) 분리 발급
  - POST /auth/refresh — Refresh Token Rotation
  - POST /auth/logout — 쿠키 삭제
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.exceptions import DeactivatedAccountError
from app.core.jwt import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.database import get_db
from app.repositories import user_repo
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MeResponse,
    ReactivateRequest,
    SignupRequest,
    SignupResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

# Refresh Token 쿠키 이름 상수
_REFRESH_COOKIE = "refresh_token"
_REFRESH_COOKIE_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # 초 단위


def _set_refresh_cookie(response: Response, token: str) -> None:
    """Refresh Token을 httpOnly 보안 쿠키에 저장"""
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_REFRESH_COOKIE_MAX_AGE,
        path="/api/v1/auth",  # /auth 경로에서만 쿠키 전송
    )


@router.post("/signup", response_model=SignupResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    회원가입

    POST /auth/signup
    - 이메일/닉네임 중복 검사
    - 비밀번호 bcrypt 해싱
    """
    try:
        logger.info("signup attempt: email=%s nickname=%s", request.email, request.nickname)
        result = auth_service.signup(db, request)
        logger.info("signup success: id=%s", result.id)
        return result
    except ValueError as e:
        logger.warning("signup ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("signup unexpected error: %s", e)
        raise


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    로그인

    POST /auth/login
    - 비활성화 계정(30일 유예 기간 내): 403 + ACCOUNT_DEACTIVATED 코드 반환
    - 탈퇴 완료/30일 초과 계정: 401 (일반 인증 실패와 동일 처리)
    - 성공 시:
        - Body: {"access_token": ..., "token_type": "bearer", "user_id": ...}
        - Cookie: refresh_token (httpOnly, Secure, SameSite=Lax, 7일)
    """
    try:
        result = auth_service.login(db, request)
    except DeactivatedAccountError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_DEACTIVATED",
                "message": "탈퇴 대기 중인 계정입니다. 복구하시겠습니까?",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    refresh_token = result.pop("refresh_token")
    _set_refresh_cookie(response, refresh_token)
    return result


@router.post("/refresh", response_model=LoginResponse)
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Access Token 갱신 (Refresh Token Rotation)

    POST /auth/refresh
    - Cookie: refresh_token 필요
    - 검증 성공 시 Access Token + Refresh Token 모두 재발급
    - 기존 Refresh Token은 새 토큰으로 덮어씀(Rotation)
    - 응답 Body: {"access_token": ..., "token_type": "bearer", "user_id": ...}
    - 응답 Cookie: 새 refresh_token (기존 쿠키 교체)
    """
    token = request.cookies.get(_REFRESH_COOKIE)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 없습니다. 다시 로그인해 주세요.",
        )

    try:
        payload = decode_refresh_token(token)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 리프레시 토큰입니다. 다시 로그인해 주세요.",
        )

    # 사용자 존재 및 활성 상태 확인 (탈퇴 계정 차단)
    user = user_repo.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
        )

    # 새 토큰 쌍 발급 (Rotation)
    new_access_token = create_access_token(user.id, user.role)
    new_refresh_token = create_refresh_token(user.id, user.role)

    _set_refresh_cookie(response, new_refresh_token)
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "user_id": user.id,
    }


@router.post("/logout")
def logout(response: Response):
    """
    로그아웃

    POST /auth/logout
    - httpOnly 쿠키(refresh_token)를 삭제
    - Access Token은 클라이언트에서 폐기 (서버 상태 없음)
    """
    response.delete_cookie(key=_REFRESH_COOKIE, path="/api/v1/auth")
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


@router.post("/reactivate", response_model=LoginResponse)
def reactivate(
    request: ReactivateRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    계정 복구 (Reactivate)

    POST /auth/reactivate
    - 탈퇴 후 30일 이내 계정을 복구하고 토큰 즉시 발급 (Auto-login)
    - 인증 헤더 불필요: 탈퇴 계정은 JWT를 발급받을 수 없으므로 credentials 직접 수신
    - 성공 시:
        - Body: {"access_token": ..., "token_type": "bearer", "user_id": ...}
        - Cookie: refresh_token (httpOnly, Secure, SameSite=Lax, 7일)
    """
    try:
        result = auth_service.reactivate(db, request.email, request.password)
    except ValueError as e:
        msg = str(e)
        if "이메일 또는 비밀번호" in msg:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    refresh_token = result.pop("refresh_token")
    _set_refresh_cookie(response, refresh_token)
    return result


@router.get("/me", response_model=MeResponse)
def me(current_user=Depends(get_current_user)):
    """내 정보 조회"""
    return current_user
