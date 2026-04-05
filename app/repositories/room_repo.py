"""
Room Repository — 스터디룸 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.study_room import StudyRoom


def get_rooms(db: Session):
    """
    스터디룸 전체 목록 조회

    SQL: SELECT * FROM study_rooms;
    """
    return db.query(StudyRoom).all()


def get_room_by_id(db: Session, room_id: int):
    """
    스터디룸 1개 조회

    SQL: SELECT * FROM study_rooms WHERE id = ? LIMIT 1;
    """
    return db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
