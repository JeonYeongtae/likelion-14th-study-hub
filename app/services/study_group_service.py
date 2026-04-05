"""
StudyGroup Service — 스터디 모집 비즈니스 로직

Phase 5
"""

from sqlalchemy.orm import Session

from app.models.study_group import StudyGroup
from app.repositories import study_group_repo
from app.schemas.study_group import StudyGroupCreate, StudyGroupUpdate


def get_groups(db: Session):
    """스터디 그룹 전체 목록"""
    return study_group_repo.get_groups(db)


def get_group(db: Session, group_id: int):
    """스터디 그룹 상세 조회"""
    group = study_group_repo.get_group_by_id(db, group_id)
    if not group:
        raise ValueError("스터디 그룹을 찾을 수 없습니다")
    return group


def create_group(db: Session, user_id: int, request: StudyGroupCreate):
    """스터디 모집 글 생성"""
    if request.max_members < 2:
        raise ValueError("최대 인원은 2명 이상이어야 합니다")

    new_group = StudyGroup(
        leader_id=user_id,
        title=request.title,
        description=request.description,
        max_members=request.max_members,
        current_members=1,
        status="모집중",
    )
    return study_group_repo.create_group(db, new_group)


def update_group(db: Session, user_id: int, group_id: int, request: StudyGroupUpdate):
    """스터디 모집 글 수정 (조장만)"""
    group = study_group_repo.get_group_by_id(db, group_id)
    if not group:
        raise ValueError("스터디 그룹을 찾을 수 없습니다")
    if group.leader_id != user_id:
        raise PermissionError("조장만 수정할 수 있습니다")

    if request.title is not None:
        group.title = request.title
    if request.description is not None:
        group.description = request.description
    if request.max_members is not None:
        if request.max_members < group.current_members:
            raise ValueError("최대 인원을 현재 인원보다 적게 설정할 수 없습니다")
        group.max_members = request.max_members
    if request.status is not None:
        group.status = request.status

    return study_group_repo.update_group(db, group)


def delete_group(db: Session, user_id: int, group_id: int):
    """스터디 모집 글 삭제 (조장만)"""
    group = study_group_repo.get_group_by_id(db, group_id)
    if not group:
        raise ValueError("스터디 그룹을 찾을 수 없습니다")
    if group.leader_id != user_id:
        raise PermissionError("조장만 삭제할 수 있습니다")

    study_group_repo.delete_group(db, group)
