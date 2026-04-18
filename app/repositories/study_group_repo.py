"""
StudyGroup Repository — 스터디 그룹 DB 조작

Phase 5
"""

from sqlalchemy.orm import Session
from app.models.study_group import StudyGroup


def get_groups(db: Session):
    """스터디 그룹 전체 목록"""
    return db.query(StudyGroup).order_by(StudyGroup.created_at.desc()).all()


def get_group_by_id(db: Session, group_id: int):
    """스터디 그룹 1개 조회"""
    return db.query(StudyGroup).filter(StudyGroup.id == group_id).first()


def get_groups_by_leader(db: Session, leader_id: int):
    """조장이 만든 그룹 목록 (최신순)"""
    return (
        db.query(StudyGroup)
        .filter(StudyGroup.leader_id == leader_id)
        .order_by(StudyGroup.created_at.desc())
        .all()
    )


def create_group(db: Session, group: StudyGroup):
    """스터디 그룹 생성"""
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def update_group(db: Session, group: StudyGroup):
    """스터디 그룹 수정"""
    db.commit()
    db.refresh(group)
    return group


def delete_group(db: Session, group: StudyGroup):
    """스터디 그룹 삭제"""
    db.delete(group)
    db.commit()
