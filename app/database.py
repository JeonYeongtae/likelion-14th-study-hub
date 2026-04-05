"""
database.py — Supabase(PostgreSQL) 연결 설정

이 파일이 하는 일:
1. .env 파일에서 DB 주소(DATABASE_URL)를 읽어온다
2. SQLAlchemy가 DB에 연결할 수 있도록 설정한다
3. API 요청마다 DB 세션을 열고 닫는 함수를 제공한다

Supabase는 내부적으로 PostgreSQL이다.
SQLAlchemy는 PostgreSQL에 직접 연결할 수 있다.
그래서 Supabase를 "그냥 PostgreSQL DB"로 쓰는 것.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ──────────────────────────────────────────────
# 1단계: .env 파일에서 환경변수를 읽어온다
#
# load_dotenv() = 프로젝트 루트의 .env 파일을 찾아서 그 안의 변수들을 메모리에 올린다
# os.getenv("DATABASE_URL") = 메모리에 올라간 변수 중 DATABASE_URL을 꺼낸다
#
# .env 파일은 이렇게 생겼다:
# DATABASE_URL=postgresql://postgres.abcdefg:내비밀번호@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
#
# 왜 .env에 넣나?
# - DB 비밀번호가 포함되어 있어서 코드에 직접 쓰면 GitHub에 올라갈 수 있다
# - .gitignore에 .env를 넣어서 깃에 안 올라가게 한다
# - 배포 환경마다 DB 주소가 다를 수 있어서 환경변수로 분리하는 게 좋다
# ──────────────────────────────────────────────
load_dotenv(override=True)
DATABASE_URL = os.getenv("DATABASE_URL")

# ──────────────────────────────────────────────
# 2단계: SQLAlchemy 설정 (3개의 핵심 객체)
#
# engine (엔진)
# - "어떤 DB에 어떻게 연결할지" 설정을 담고 있는 객체
# - 아직 실제로 연결한 건 아니다. 설정만 해둔 것.
# - 비유: 네비게이션에 목적지를 입력한 것 (아직 출발은 안 함)
#
# SessionLocal (세션 공장)
# - SessionLocal()을 호출하면 "DB와 대화하는 통로" 하나가 만들어진다
# - 이 통로를 통해 SELECT, INSERT, DELETE 등을 실행한다
# - autocommit=False: 명시적으로 commit()을 해야 DB에 반영된다
# - autoflush=False: commit() 전에 자동으로 DB에 보내지 않는다
# - 비유: 전화기 공장. 전화기를 만들면 그걸로 DB한테 전화할 수 있다.
#
# Base (베이스 클래스)
# - 모든 Model(테이블 정의 클래스)이 상속받는 부모 클래스
# - class User(Base): 이렇게 쓰면 SQLAlchemy가
#   "아, 이 클래스는 DB 테이블이구나"를 인식한다
# ──────────────────────────────────────────────
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    DB 세션(통로)을 열고 닫는 함수.
    FastAPI의 Depends()와 함께 사용한다.

    사용법 (Router에서):
        @router.get("/posts")
        def get_posts(db: Session = Depends(get_db)):
            ...

    위처럼 쓰면 FastAPI가 자동으로:
    1. get_db() 함수를 실행한다
    2. SessionLocal()로 DB 세션을 하나 만든다
    3. yield db → 이 세션을 Router 함수의 db 파라미터로 넘겨준다
    4. Router 함수가 끝나면 (응답 완료)
    5. finally: db.close() → 세션을 닫는다

    왜 이렇게 하나?
    - DB 세션은 쓰고 나면 반드시 닫아야 한다 (안 닫으면 연결이 쌓여서 DB가 터짐)
    - 매 API 함수마다 열고 닫는 코드를 반복하면 실수할 수 있다
    - get_db()에 한 번만 정의해두면 Depends()가 자동으로 처리해준다
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
