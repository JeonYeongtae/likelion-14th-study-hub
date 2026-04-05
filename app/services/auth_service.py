"""
Auth Service — 회원가입/로그인 비즈니스 로직

Phase 2: bcrypt 비밀번호 해싱
Phase 4: JWT 토큰 발급
"""

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
    2. bcrypt 해싱
    3. DB에 저장
    """
    existing = user_repo.get_user_by_email(db, request.email)
    if existing:
        raise ValueError("이미 존재하는 이메일입니다")

    new_user = User(
        email=request.email,
        password=pwd_context.hash(request.password),  # Phase 2: bcrypt 해싱
        nickname=request.nickname,
    )
    return user_repo.create_user(db, new_user)


def login(db: Session, request: LoginRequest):
    """
    로그인

    1. email로 유저 조회
    2. bcrypt verify
    3. JWT 토큰 발급 (Phase 4)
    """
    user = user_repo.get_user_by_email(db, request.email)

    if not user or not pwd_context.verify(request.password, user.password):
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다")

    token = create_access_token(user.id, user.role)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}
