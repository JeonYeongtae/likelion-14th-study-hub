"""
Room Repository — 스터디룸 DB 조작

Phase 2: 관리자 CRUD 추가
"""

from sqlalchemy.orm import Session
from app.models.study_room import StudyRoom


def get_rooms(db: Session):
    """스터디룸 전체 목록 조회"""
    return db.query(StudyRoom).all()


def get_room_by_id(db: Session, room_id: int):
    """스터디룸 1개 조회"""
    return db.query(StudyRoom).filter(StudyRoom.id == room_id).first()


def create_room(db: Session, room: StudyRoom):
    """스터디룸 생성"""
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def update_room(db: Session, room: StudyRoom):
    """스터디룸 수정 (변경된 객체를 그대로 저장)"""
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room: StudyRoom):
    """스터디룸 삭제"""
    db.delete(room)
    db.commit()
