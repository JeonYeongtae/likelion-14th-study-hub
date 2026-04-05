"""
Reservation Repository — 예약 DB 조작

Phase 1: start_time + end_time 기반 겹침 쿼리
Phase 6: group_id 포함
"""

from sqlalchemy.orm import Session
from app.models.reservation import Reservation


def get_reservations_by_room(db: Session, room_id: int):
    """
    특정 스터디룸의 예약 목록 (시작 시간 오름차순)

    SQL: SELECT * FROM reservations WHERE room_id = ? ORDER BY start_time;
    """
    return (
        db.query(Reservation)
        .filter(Reservation.room_id == room_id)
        .order_by(Reservation.start_time.asc())
        .all()
    )


def get_reservations_by_user(db: Session, user_id: int):
    """
    특정 유저의 예약 목록 (시작 시간 오름차순)

    SQL: SELECT * FROM reservations WHERE user_id = ? ORDER BY start_time;
    """
    return (
        db.query(Reservation)
        .filter(Reservation.user_id == user_id)
        .order_by(Reservation.start_time.asc())
        .all()
    )


def get_reservation_by_id(db: Session, reservation_id: int):
    """예약 1개 조회"""
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


def count_overlapping(db: Session, room_id: int, start_time, end_time, exclude_id: int = None):
    """
    겹치는 예약 수 조회 (capacity 비교용)

    겹침 조건: start_time < end AND end_time > start
    SQL: SELECT COUNT(*) FROM reservations
         WHERE room_id = ? AND start_time < ? AND end_time > ? AND status != 'cancelled'
    """
    query = db.query(Reservation).filter(
        Reservation.room_id == room_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
        Reservation.status != "cancelled",
    )
    if exclude_id:
        query = query.filter(Reservation.id != exclude_id)
    return query.all()


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
