"""
Auth Router — 회원가입/로그인 API 엔드포인트

Router는 "요청 받고 응답 보내기"만 한다.
비즈니스 로직은 Service에, DB 작업은 Repository에 있다.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    SignupResponse,
)
from app.services import auth_service

# ── 라우터 생성 ──
# prefix="/auth": 이 파일의 모든 API URL 앞에 /auth가 붙는다
# tags=["Auth"]: Swagger UI(localhost:8000/docs)에서 그룹명으로 표시된다
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=SignupResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    회원가입 API

    POST /auth/signup
    요청: {"email": "...", "username": "...", "password": "...", "nickname": "..."}
    응답: {"id": 1, "email": "...", "username": "...", "nickname": "..."}

    흐름:
    1. FastAPI가 요청 body를 SignupRequest로 자동 검증
       -> 이메일 형식이 틀리면 여기서 바로 에러 (Schema가 막음)
    2. Depends(get_db)로 DB 세션을 자동으로 받음
    3. auth_service.signup() 호출 -> 비즈니스 로직 처리
    4. response_model=SignupResponse -> 응답에서 password 자동 제외
    """
    try:
        user = auth_service.signup(db, request)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    로그인 API

    POST /auth/login
    요청: {"email": "...", "password": "..."}
    응답: {"user_id": 1}

    Phase 1에서는 JWT 대신 user_id만 반환한다.
    """
    try:
        return auth_service.login(db, request)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
