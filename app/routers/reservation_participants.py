"""
ReservationParticipants Router — 예약 참석자 API

Phase 4: JWT 인증으로 변경 (기존 user_id 쿼리 파라미터 방식 제거)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
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
    로그인 불필요
    """
    return reservation_participant_service.get_participants(db, reservation_id)


@router.post("/", response_model=ReservationParticipantResponse)
def add_participant(
    reservation_id: int,
    request: ReservationParticipantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    참석자 추가 (대표자만 가능)

    POST /reservations/1/participants
    Authorization: Bearer {token}
    요청: {"user_id": 2}
    """
    try:
        return reservation_participant_service.add_participant(db, current_user.id, reservation_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{target_user_id}")
def remove_participant(
    reservation_id: int,
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    참석자 삭제 (대표자만 가능)

    DELETE /reservations/1/participants/2
    Authorization: Bearer {token}
    """
    try:
        reservation_participant_service.remove_participant(db, current_user.id, reservation_id, target_user_id)
        return {"message": "참석자가 삭제되었습니다"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
