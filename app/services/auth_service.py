"""
Auth Service — 회원가입/로그인/탈퇴 비즈니스 로직

Phase 2: bcrypt 비밀번호 해싱
Phase 4: JWT 토큰 발급
명세서: 닉네임 중복 체크, is_active 검사, 소프트 딜리트
"""

from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.jwt import create_access_token
from app.models.user import User
from app.repositories import user_repo
from app.schemas.auth import LoginRequest, SignupRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def signup(db: Session, request: SignupRequest):
    """
    회원가입

    1. 이메일 중복 체크
    2. 닉네임 중복 체크
    3. bcrypt 해싱
    4. DB 저장
    """
    if user_repo.get_user_by_email(db, request.email):
        raise ValueError("이미 존재하는 이메일입니다")
    if user_repo.get_user_by_nickname(db, request.nickname):
        raise ValueError("이미 사용 중인 닉네임입니다")

    new_user = User(
        email=request.email,
        password=pwd_context.hash(request.password),
        nickname=request.nickname,
    )
    return user_repo.create_user(db, new_user)


def login(db: Session, request: LoginRequest):
    """
    로그인

    1. email로 유저 조회
    2. is_active 검사 (탈퇴 계정 차단)
    3. bcrypt verify
    4. JWT 토큰 발급
    """
    user = user_repo.get_user_by_email(db, request.email)

    if not user or not pwd_context.verify(request.password, user.password):
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다")

    if not user.is_active:
        raise ValueError("탈퇴 처리된 계정입니다")

    token = create_access_token(user.id, user.role)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}


def withdraw(db: Session, user_id: int):
    """
    회원 탈퇴 (소프트 딜리트)

    - is_active = False
    - deleted_at = 현재 시각 (30일 후 하드딜리트 기준)
    - 실제 삭제는 pg_cron 스케줄러가 처리 (migrations.sql 참고)
    """
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("사용자를 찾을 수 없습니다")

    user.is_active = False
    user.deleted_at = datetime.now(timezone.utc)
    user_repo.update_user(db, user)
