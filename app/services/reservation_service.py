"""
Reservation Service — 예약 비즈니스 로직

규칙:
- 예약 취소는 본인만 가능
- 예약 생성 시 신청자가 대표 참석자로 자동 등록
"""

from sqlalchemy.orm import Session

from app.models.reservation import Reservation
from app.models.reservation_participant import ReservationParticipant
from app.repositories import reservation_repo, room_repo, reservation_participant_repo
from app.schemas.reservation import ReservationCreate


def get_reservations_by_room(db: Session, room_id: int):
    """특정 방의 예약 목록"""
    return reservation_repo.get_reservations_by_room(db, room_id)


def get_my_reservations(db: Session, user_id: int):
    """내 예약 목록"""
    return reservation_repo.get_reservations_by_user(db, user_id)


def create_reservation(db: Session, user_id: int, request: ReservationCreate):
    """
    예약 생성

    1. 스터디룸 존재 확인
    2. 예약 생성 (status = 'confirmed')
    3. 신청자를 대표 참석자로 자동 등록
    """
    room = room_repo.get_room_by_id(db, request.room_id)
    if not room:
        raise ValueError("스터디룸을 찾을 수 없습니다")

    new_reservation = Reservation(
        user_id=user_id,
        room_id=request.room_id,
        reservation_time=request.reservation_time,
        status="confirmed",
    )
    reservation = reservation_repo.create_reservation(db, new_reservation)

    representative = ReservationParticipant(
        reservation_id=reservation.id,
        user_id=user_id,
        is_representative=True,
    )
    reservation_participant_repo.create_participant(db, representative)

    return reservation


def cancel_reservation(db: Session, user_id: int, reservation_id: int):
    """예약 취소 (본인 예약만)"""
    reservation = reservation_repo.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise ValueError("예약을 찾을 수 없습니다")
    if reservation.user_id != user_id:
        raise PermissionError("본인의 예약만 취소할 수 있습니다")

    reservation_repo.delete_reservation(db, reservation)
