"""
Reservations Router — 예약 API

Phase 1: JWT 인증 없이 user_id를 쿼리 파라미터로 전달
         (Session 2에서 JWT 토큰 기반 인증으로 변경 예정)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services import reservation_service

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/room/{room_id}", response_model=list[ReservationResponse])
def get_room_reservations(
    room_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 방의 예약 목록

    GET /reservations/room/1
    로그인 불필요
    """
    return reservation_service.get_reservations_by_room(db, room_id)


@router.get("/my", response_model=list[ReservationResponse])
def get_my_reservations(
    user_id: int,  # 쿼리 파라미터 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    내 예약 목록

    GET /reservations/my?user_id=1
    """
    return reservation_service.get_my_reservations(db, user_id)


@router.post("/", response_model=ReservationResponse)
def create_reservation(
    request: ReservationCreate,
    user_id: int,  # 쿼리 파라미터 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    예약 생성

    POST /reservations?user_id=1
    요청: {"room_id": 1, "reservation_time": "2026-04-02T10:00:00+09:00"}
    """
    try:
        return reservation_service.create_reservation(db, user_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{reservation_id}")
def cancel_reservation(
    reservation_id: int,
    user_id: int,  # 쿼리 파라미터 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    예약 취소

    DELETE /reservations/5?user_id=1
    """
    try:
        reservation_service.cancel_reservation(db, user_id, reservation_id)
        return {"message": "예약이 취소되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
