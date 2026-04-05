"""
Reservation Service — 예약 비즈니스 로직

Phase 1: start_time + end_time, 시간 겹침 방지
Phase 2: capacity 기반 겹침 허용 (COUNT < capacity)
Phase 4: 이용 시간(open/close) 및 슬롯 단위 검증
Phase 6: 그룹 예약 (group_id, 조장만, 그룹 인원 <= capacity)
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.reservation import Reservation
from app.repositories import reservation_repo, room_repo, room_settings_repo, study_group_repo
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

    검증 순서:
    1. 스터디룸 존재 확인
    2. 시작/종료 시간 유효성 (end > start)
    3. 이용 시간 내 검증 (Phase 4: room_settings)
    4. 슬롯 단위 검증 (Phase 4)
    5. 그룹 예약 검증 (Phase 6)
    6. capacity 기반 겹침 검증 (Phase 2)
    """
    room = room_repo.get_room_by_id(db, request.room_id)
    if not room:
        raise ValueError("스터디룸을 찾을 수 없습니다")

    # 기본 시간 유효성
    if request.end_time <= request.start_time:
        raise ValueError("종료 시간은 시작 시간보다 늦어야 합니다")

    # Phase 4: 이용 시간 및 슬롯 단위 검증
    settings = room_settings_repo.get_settings_by_room(db, request.room_id)
    if settings:
        req_start = request.start_time.astimezone(timezone.utc).time()
        req_end = request.end_time.astimezone(timezone.utc).time()

        if req_start < settings.open_time:
            raise ValueError("이용 시작 시간 이전에는 예약할 수 없습니다")
        if req_end > settings.close_time:
            raise ValueError("이용 종료 시간 이후에는 예약할 수 없습니다")

        duration_minutes = int((request.end_time - request.start_time).total_seconds() // 60)
        if duration_minutes % settings.slot_duration != 0:
            raise ValueError(f"예약 시간은 슬롯 단위({settings.slot_duration}분)의 배수여야 합니다")

    # Phase 6: 그룹 예약 검증
    new_members = 1  # 개인 예약 기본 1명
    if request.group_id is not None:
        group = study_group_repo.get_group_by_id(db, request.group_id)
        if not group:
            raise ValueError("스터디 그룹을 찾을 수 없습니다")
        if group.status != "모집완료":
            raise ValueError("모집이 완료된 그룹만 예약할 수 있습니다")
        if group.leader_id != user_id:
            raise PermissionError("조장만 그룹 예약을 할 수 있습니다")
        new_members = group.current_members

    # Phase 2: capacity 기반 겹침 검증
    # 겹치는 예약들의 총 인원 계산
    overlapping = reservation_repo.count_overlapping(
        db, request.room_id, request.start_time, request.end_time
    )
    total_occupancy = sum(
        1 if r.group_id is None else (r.group.current_members if r.group else 1)
        for r in overlapping
    )
    if total_occupancy + new_members > room.capacity:
        raise ValueError("해당 시간대 수용 인원이 초과됩니다")

    new_reservation = Reservation(
        user_id=user_id,
        room_id=request.room_id,
        start_time=request.start_time,
        end_time=request.end_time,
        group_id=request.group_id,
        status="confirmed",
    )
    return reservation_repo.create_reservation(db, new_reservation)


def cancel_reservation(db: Session, user_id: int, reservation_id: int):
    """예약 취소 (본인 예약만)"""
    reservation = reservation_repo.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise ValueError("예약을 찾을 수 없습니다")
    if reservation.user_id != user_id:
        raise PermissionError("본인의 예약만 취소할 수 있습니다")

    reservation_repo.delete_reservation(db, reservation)
