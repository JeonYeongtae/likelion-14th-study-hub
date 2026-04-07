"""
Auth Service — 회원가입/로그인/탈퇴/복구 비즈니스 로직

Phase 2: bcrypt 비밀번호 해싱
Phase 4: JWT 토큰 발급
명세서: 닉네임 중복 체크, is_active 검사, 소프트 딜리트
고도화: 30일 유예 비활성화(Soft Delete) + 계정 복구(Reactivate)
"""

from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.exceptions import DeactivatedAccountError
from app.core.jwt import create_access_token
from app.models.user import User
from app.repositories import user_repo
from app.schemas.auth import LoginRequest, SignupRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEACTIVATION_GRACE_DAYS = 30


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
    2. bcrypt 비밀번호 검증 (존재 여부와 묶어서 처리 — 계정 존재 탐지 방지)
    3. 비활성화 계정 판별:
       - 30일 유예 기간 이내 → DeactivatedAccountError (복구 안내용 403)
       - 30일 초과 (스케줄러 미처리 케이스) → ValueError (401, 일반 오류)
    4. JWT 토큰 발급
    """
    user = user_repo.get_user_by_email(db, request.email)

    if not user or not pwd_context.verify(request.password, user.password):
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다")

    if not user.is_active:
        if user.deleted_at and _is_within_grace_period(user.deleted_at):
            raise DeactivatedAccountError()
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다")

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


def reactivate(db: Session, email: str, password: str):
    """
    계정 복구 (Reactivate)

    - 인증 없이 호출되는 엔드포인트 (탈퇴 후 JWT 발급 불가이므로 credentials 직접 수신)
    1. email로 유저 조회
    2. 비밀번호 검증
    3. 비활성화 계정이고 30일 유예 기간 이내인지 확인
    4. is_active = True, deleted_at = None 으로 복구
    5. JWT 즉시 발급 (Auto-login)
    """
    user = user_repo.get_user_by_email(db, email)

    if not user or not pwd_context.verify(password, user.password):
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다")

    if user.is_active:
        raise ValueError("이미 활성화된 계정입니다")

    if not user.deleted_at or not _is_within_grace_period(user.deleted_at):
        raise ValueError("복구 가능한 기간(30일)이 지난 계정입니다")

    user.is_active = True
    user.deleted_at = None
    user_repo.update_user(db, user)

    token = create_access_token(user.id, user.role)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}


def _is_within_grace_period(deleted_at: datetime) -> bool:
    """deleted_at 기준으로 30일 유예 기간이 아직 남아있는지 확인"""
    now = datetime.now(timezone.utc)
    # deleted_at이 timezone-naive인 경우 대응
    if deleted_at.tzinfo is None:
        deleted_at = deleted_at.replace(tzinfo=timezone.utc)
    return now < deleted_at + timedelta(days=DEACTIVATION_GRACE_DAYS)
