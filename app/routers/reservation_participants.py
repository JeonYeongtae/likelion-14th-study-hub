"""
ReservationParticipants Router — 예약 참석자 API

Phase 1: JWT 인증 없이 user_id를 쿼리 파라미터로 전달
         (Session 2에서 JWT 토큰 기반 인증으로 변경 예정)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.reservation_participant import (
    ReservationParticipantCreate,
    ReservationParticipantResponse,
)
from app.services import reservation_participant_service

router = APIRouter(prefix="/reservations/{reservation_id}/participants", tags=["ReservationParticipants"])


@router.get("/", response_model=list[ReservationParticipantResponse])
def get_participants(reservation_id: int, db: Session = Depends(get_db)):
    """
    예약 참석자 목록 조회

    GET /reservations/1/participants
    """
    return reservation_participant_service.get_participants(db, reservation_id)


@router.post("/", response_model=ReservationParticipantResponse)
def add_participant(
    reservation_id: int,
    request: ReservationParticipantCreate,
    user_id: int,  # 쿼리 파라미터 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    참석자 추가 (대표자만 가능)

    POST /reservations/1/participants?user_id=1
    요청: {"user_id": 2}
    """
    try:
        return reservation_participant_service.add_participant(db, user_id, reservation_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{target_user_id}")
def remove_participant(
    reservation_id: int,
    target_user_id: int,
    user_id: int,  # 쿼리 파라미터 (Session 2에서 JWT 인증으로 변경 예정)
    db: Session = Depends(get_db),
):
    """
    참석자 삭제 (대표자만 가능)

    DELETE /reservations/1/participants/2?user_id=1
    """
    try:
        reservation_participant_service.remove_participant(db, user_id, reservation_id, target_user_id)
        return {"message": "참석자가 삭제되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
