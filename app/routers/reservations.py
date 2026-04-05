"""
Reservations Router — 예약 API

Phase 4: JWT 인증으로 변경
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
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


@router.get("/me", response_model=list[ReservationResponse])
def get_my_reservations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    내 예약 목록

    GET /reservations/me
    Authorization: Bearer {token}
    """
    return reservation_service.get_my_reservations(db, current_user.id)


@router.post("/", response_model=ReservationResponse)
def create_reservation(
    request: ReservationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    예약 생성

    POST /reservations
    Authorization: Bearer {token}
    요청: {"room_id": 1, "start_time": "2026-04-02T14:00:00+09:00", "end_time": "2026-04-02T16:00:00+09:00"}
    그룹 예약: group_id 추가
    """
    try:
        return reservation_service.create_reservation(db, current_user.id, request)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{reservation_id}")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    예약 취소

    DELETE /reservations/5
    Authorization: Bearer {token}
    """
    try:
        reservation_service.cancel_reservation(db, current_user.id, reservation_id)
        return {"message": "예약이 취소되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
