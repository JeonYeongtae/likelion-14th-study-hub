"""
Room Service — 스터디룸 비즈니스 로직

Phase 1에서는 단순 조회만.
"""

from sqlalchemy.orm import Session
from app.repositories import room_repo


def get_rooms(db: Session):
    """스터디룸 전체 목록"""
    return room_repo.get_rooms(db)


def get_room(db: Session, room_id: int):
    """스터디룸 1개 조회"""
    room = room_repo.get_room_by_id(db, room_id)
    if not room:
        raise ValueError("스터디룸을 찾을 수 없습니다")
    return room
