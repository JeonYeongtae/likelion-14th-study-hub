"""
RoomSettings Service — 룸 이용 시간 설정 비즈니스 로직

Phase 4: admin 전용
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.room_settings import RoomSettings
from app.repositories import room_repo, room_settings_repo
from app.schemas.room import RoomSettingsUpdate


def get_settings(db: Session, room_id: int):
    """룸 설정 조회 (없으면 기본값으로 자동 생성)"""
    room = room_repo.get_room_by_id(db, room_id)
    if not room:
        raise ValueError("스터디룸을 찾을 수 없습니다")

    settings = room_settings_repo.get_settings_by_room(db, room_id)
    if not settings:
        # 기본 설정 생성
        settings = RoomSettings(room_id=room_id)
        settings = room_settings_repo.create_settings(db, settings)
    return settings


def update_settings(db: Session, room_id: int, request: RoomSettingsUpdate):
    """룸 설정 수정 (admin 전용)"""
    room = room_repo.get_room_by_id(db, room_id)
    if not room:
        raise ValueError("스터디룸을 찾을 수 없습니다")

    settings = room_settings_repo.get_settings_by_room(db, room_id)
    if not settings:
        settings = RoomSettings(room_id=room_id)
        room_settings_repo.create_settings(db, settings)

    if request.open_time is not None:
        settings.open_time = request.open_time
    if request.close_time is not None:
        settings.close_time = request.close_time
    if request.slot_duration is not None:
        if request.slot_duration <= 0:
            raise ValueError("슬롯 단위는 양수여야 합니다")
        settings.slot_duration = request.slot_duration

    settings.updated_at = datetime.now(timezone.utc)
    return room_settings_repo.update_settings(db, settings)
