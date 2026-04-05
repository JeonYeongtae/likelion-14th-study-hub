"""
ReservationParticipant Service — 예약 참석자 비즈니스 로직

규칙:
- 대표자(is_representative=True)는 삭제 불가
- 참석자 추가/삭제는 대표자만 가능
"""

from sqlalchemy.orm import Session

from app.models.reservation_participant import ReservationParticipant
from app.repositories import reservation_participant_repo, reservation_repo
from app.schemas.reservation_participant import ReservationParticipantCreate


def get_participants(db: Session, reservation_id: int):
    """예약 참석자 목록 조회"""
    return reservation_participant_repo.get_participants_by_reservation(db, reservation_id)


def add_participant(db: Session, requester_id: int, reservation_id: int, request: ReservationParticipantCreate):
    """
    참석자 추가 (대표자만 가능)

    1. 예약 존재 확인
    2. 요청자가 대표자인지 확인
    3. 이미 등록된 참석자인지 확인
    4. 참석자 추가
    """
    reservation = reservation_repo.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise ValueError("예약을 찾을 수 없습니다")

    requester = reservation_participant_repo.get_participant(db, reservation_id, requester_id)
    if not requester or not requester.is_representative:
        raise PermissionError("대표자만 참석자를 추가할 수 있습니다")

    existing = reservation_participant_repo.get_participant(db, reservation_id, request.user_id)
    if existing:
        raise ValueError("이미 등록된 참석자입니다")

    new_participant = ReservationParticipant(
        reservation_id=reservation_id,
        user_id=request.user_id,
        is_representative=False,
    )
    return reservation_participant_repo.create_participant(db, new_participant)


def remove_participant(db: Session, requester_id: int, reservation_id: int, user_id: int):
    """
    참석자 삭제 (대표자만 가능, 대표자 본인은 삭제 불가)

    1. 요청자가 대표자인지 확인
    2. 대상이 대표자인지 확인 (대표자는 삭제 불가)
    3. 삭제
    """
    requester = reservation_participant_repo.get_participant(db, reservation_id, requester_id)
    if not requester or not requester.is_representative:
        raise PermissionError("대표자만 참석자를 삭제할 수 있습니다")

    target = reservation_participant_repo.get_participant(db, reservation_id, user_id)
    if not target:
        raise ValueError("참석자를 찾을 수 없습니다")
    if target.is_representative:
        raise ValueError("대표자는 참석자 목록에서 삭제할 수 없습니다")

    reservation_participant_repo.delete_participant(db, target)
