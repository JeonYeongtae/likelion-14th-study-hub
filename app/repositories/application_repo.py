"""
Application Repository — 스터디 가입 신청 DB 조작

Phase 5
"""

from sqlalchemy.orm import Session
from app.models.application import Application


def get_application_by_id(db: Session, application_id: int):
    """신청 1개 조회"""
    return db.query(Application).filter(Application.id == application_id).first()


def get_applications_by_group(db: Session, group_id: int):
    """그룹의 신청 목록"""
    return (
        db.query(Application)
        .filter(Application.group_id == group_id)
        .order_by(Application.created_at.asc())
        .all()
    )


def get_applications_by_user(db: Session, user_id: int):
    """유저가 신청한 전체 목록 (최신순)"""
    return (
        db.query(Application)
        .filter(Application.applicant_id == user_id)
        .order_by(Application.created_at.desc())
        .all()
    )


def get_application_by_group_and_user(db: Session, group_id: int, user_id: int):
    """특정 유저의 특정 그룹 신청 조회 (중복 방지)"""
    return db.query(Application).filter(
        Application.group_id == group_id,
        Application.applicant_id == user_id,
    ).first()


def create_application(db: Session, application: Application):
    """신청 생성"""
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def update_application(db: Session, application: Application):
    """신청 상태 수정"""
    db.commit()
    db.refresh(application)
    return application


def delete_application(db: Session, application: Application):
    """신청 삭제 (재신청 허용 시 기존 rejected 신청 제거용)"""
    db.delete(application)
    db.commit()
