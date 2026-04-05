"""
ReservationParticipant Repository — 예약 참석자 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.reservation_participant import ReservationParticipant


def get_participants_by_reservation(db: Session, reservation_id: int):
    """
    예약의 참석자 목록 조회

    SQL: SELECT * FROM reservation_participants WHERE reservation_id = ?;
    """
    return (
        db.query(ReservationParticipant)
        .filter(ReservationParticipant.reservation_id == reservation_id)
        .all()
    )


def get_participant(db: Session, reservation_id: int, user_id: int):
    """
    특정 예약에 특정 유저가 참석자로 등록되어 있는지 조회

    SQL: SELECT * FROM reservation_participants
         WHERE reservation_id = ? AND user_id = ? LIMIT 1;
    """
    return (
        db.query(ReservationParticipant)
        .filter(
            ReservationParticipant.reservation_id == reservation_id,
            ReservationParticipant.user_id == user_id,
        )
        .first()
    )


def create_participant(db: Session, participant: ReservationParticipant):
    """참석자 추가"""
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def delete_participant(db: Session, participant: ReservationParticipant):
    """참석자 삭제"""
    db.delete(participant)
    db.commit()
