"""
Rooms Router — 스터디룸 API

Phase 1에서는 목록 조회만.
상세 조회는 Phase 2에서 description, capacity 추가 후 만든다.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.room import RoomResponse
from app.services import room_service

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=list[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):
    """
    스터디룸 전체 목록

    GET /rooms
    로그인 불필요
    """
    return room_service.get_rooms(db)
