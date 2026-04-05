"""
Reservation Repository — 예약 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.reservation import Reservation


def get_reservations_by_room(db: Session, room_id: int):
    """
    특정 스터디룸의 예약 목록 (예약 시간 오름차순)

    SQL: SELECT * FROM reservations WHERE room_id = ? ORDER BY reservation_time;
    """
    return (
        db.query(Reservation)
        .filter(Reservation.room_id == room_id)
        .order_by(Reservation.reservation_time.asc())
        .all()
    )


def get_reservations_by_user(db: Session, user_id: int):
    """
    특정 유저의 예약 목록 (예약 시간 오름차순)

    SQL: SELECT * FROM reservations WHERE user_id = ? ORDER BY reservation_time;
    """
    return (
        db.query(Reservation)
        .filter(Reservation.user_id == user_id)
        .order_by(Reservation.reservation_time.asc())
        .all()
    )


def get_reservation_by_id(db: Session, reservation_id: int):
    """
    예약 1개 조회

    SQL: SELECT * FROM reservations WHERE id = ? LIMIT 1;
    """
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


def create_reservation(db: Session, reservation: Reservation):
    """예약 생성"""
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def delete_reservation(db: Session, reservation: Reservation):
    """예약 취소"""
    db.delete(reservation)
    db.commit()
