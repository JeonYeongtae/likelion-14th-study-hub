"""
User Repository — DB에서 유저를 조회하고 생성/수정하는 계층
"""

from sqlalchemy.orm import Session
from app.models.user import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_nickname(db: Session, nickname: str):
    return db.query(User).filter(User.nickname == nickname).first()


def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User):
    db.commit()
    db.refresh(user)
    return user
