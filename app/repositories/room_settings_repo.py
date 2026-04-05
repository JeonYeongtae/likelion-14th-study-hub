"""
RoomSettings Repository — 룸 설정 DB 조작

Phase 4
"""

from sqlalchemy.orm import Session
from app.models.room_settings import RoomSettings


def get_settings_by_room(db: Session, room_id: int):
    """룸 설정 조회"""
    return db.query(RoomSettings).filter(RoomSettings.room_id == room_id).first()


def create_settings(db: Session, settings: RoomSettings):
    """룸 설정 생성"""
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_settings(db: Session, settings: RoomSettings):
    """룸 설정 수정"""
    db.commit()
    db.refresh(settings)
    return settings
