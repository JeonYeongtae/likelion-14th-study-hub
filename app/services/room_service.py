"""
Room Service — 스터디룸 비즈니스 로직

Phase 2: 관리자 CRUD (생성/수정/삭제)
"""

from sqlalchemy.orm import Session

from app.models.study_room import StudyRoom
from app.repositories import room_repo
from app.schemas.room import RoomCreate, RoomUpdate


def get_rooms(db: Session):
    """스터디룸 전체 목록"""
    return room_repo.get_rooms(db)


def get_room(db: Session, room_id: int):
    """스터디룸 1개 조회"""
    room = room_repo.get_room_by_id(db, room_id)
    if not room:
        raise ValueError("스터디룸을 찾을 수 없습니다")
    return room


def create_room(db: Session, request: RoomCreate):
    """스터디룸 생성 (admin 전용)"""
    new_room = StudyRoom(
        name=request.name,
        capacity=request.capacity,
        description=request.description,
    )
    return room_repo.create_room(db, new_room)


def update_room(db: Session, room_id: int, request: RoomUpdate):
    """스터디룸 수정 (admin 전용)"""
    room = room_repo.get_room_by_id(db, room_id)
    if not room:
        raise ValueError("스터디룸을 찾을 수 없습니다")

    if request.name is not None:
        room.name = request.name
    if request.capacity is not None:
        room.capacity = request.capacity
    if request.description is not None:
        room.description = request.description
    if request.is_available is not None:
        room.is_available = request.is_available

    return room_repo.update_room(db, room)


def delete_room(db: Session, room_id: int):
    """스터디룸 삭제 (admin 전용)"""
    room = room_repo.get_room_by_id(db, room_id)
    if not room:
        raise ValueError("스터디룸을 찾을 수 없습니다")
    room_repo.delete_room(db, room)
