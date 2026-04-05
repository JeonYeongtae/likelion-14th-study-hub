"""
Auth Service — 회원가입/로그인 비즈니스 로직

Phase 1:
- 비밀번호는 평문으로 저장/비교한다
- JWT 토큰 발급/검증은 Session 2에서 추가
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import user_repo
from app.schemas.auth import LoginRequest, SignupRequest


def signup(db: Session, request: SignupRequest):
    """
    회원가입

    1. 이메일 중복 체크
    2. DB에 저장
    """
    existing = user_repo.get_user_by_email(db, request.email)
    if existing:
        raise ValueError("이미 존재하는 이메일입니다")

    new_user = User(
        email=request.email,
        password=request.password,
        nickname=request.nickname,
    )
    return user_repo.create_user(db, new_user)


def login(db: Session, request: LoginRequest):
    """
    로그인

    1. email로 유저 조회
    2. password 평문 비교
    3. 맞으면 user_id 반환
    """
    user = user_repo.get_user_by_email(db, request.email)

    if not user or user.password != request.password:
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다")

    return {"user_id": user.id}
