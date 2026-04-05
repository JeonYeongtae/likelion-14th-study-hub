"""
Rooms Router — 스터디룸 API

Phase 2: 관리자 CRUD (생성/수정/삭제)
Phase 4: 룸 설정 조회/수정
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.database import get_db
from app.schemas.room import RoomCreate, RoomResponse, RoomSettingsResponse, RoomSettingsUpdate, RoomUpdate
from app.services import room_service, room_settings_service

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=list[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):
    """
    스터디룸 전체 목록

    GET /rooms
    로그인 불필요
    """
    return room_service.get_rooms(db)


@router.post("/", response_model=RoomResponse)
def create_room(
    request: RoomCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    스터디룸 생성 (admin 전용, Phase 2)

    POST /rooms
    Authorization: Bearer {admin_token}
    """
    try:
        return room_service.create_room(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    request: RoomUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    스터디룸 수정 (admin 전용, Phase 2)

    PATCH /rooms/1
    Authorization: Bearer {admin_token}
    """
    try:
        return room_service.update_room(db, room_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    스터디룸 삭제 (admin 전용, Phase 2)

    DELETE /rooms/1
    Authorization: Bearer {admin_token}
    """
    try:
        room_service.delete_room(db, room_id)
        return {"message": "스터디룸이 삭제되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── 룸 설정 (Phase 4) ──

@router.get("/{room_id}/settings", response_model=RoomSettingsResponse)
def get_room_settings(
    room_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    룸 설정 조회 (admin 전용, Phase 4)

    GET /rooms/1/settings
    Authorization: Bearer {admin_token}
    """
    try:
        return room_settings_service.get_settings(db, room_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{room_id}/settings", response_model=RoomSettingsResponse)
def update_room_settings(
    room_id: int,
    request: RoomSettingsUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    룸 설정 수정 (admin 전용, Phase 4)

    PATCH /rooms/1/settings
    Authorization: Bearer {admin_token}
    요청: {"open_time": "09:00", "close_time": "22:00", "slot_duration": 60}
    """
    try:
        return room_settings_service.update_settings(db, room_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
