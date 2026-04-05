"""
Application Service — 스터디 가입 신청 비즈니스 로직

Phase 5: 신청 → 수락/거절 상태 머신
- pending → accepted / rejected
- 수락 시 current_members += 1
- 수락 후 current_members >= max_members → status = '모집완료'
- 거절/취소 시 수락된 신청이면 current_members -= 1, 모집완료 → 모집중 복원
"""

from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories import application_repo, study_group_repo
from app.schemas.application import ApplicationCreate, ApplicationUpdate


def apply(db: Session, user_id: int, group_id: int, request: ApplicationCreate):
    """
    스터디 신청

    1. 그룹 모집 중 확인
    2. 인원 확인
    3. 중복 신청 확인
    4. 신청 생성
    """
    group = study_group_repo.get_group_by_id(db, group_id)
    if not group:
        raise ValueError("스터디 그룹을 찾을 수 없습니다")
    if group.leader_id == user_id:
        raise ValueError("조장은 본인 그룹에 신청할 수 없습니다")
    if group.status != "모집중":
        raise ValueError("모집이 마감되었습니다")
    if group.current_members >= group.max_members:
        raise ValueError("인원이 가득 찼습니다")

    existing = application_repo.get_application_by_group_and_user(db, group_id, user_id)
    if existing:
        raise ValueError("이미 신청한 그룹입니다")

    new_app = Application(
        group_id=group_id,
        applicant_id=user_id,
        status="pending",
        message=request.message,
    )
    return application_repo.create_application(db, new_app)


def get_applications(db: Session, user_id: int, group_id: int):
    """신청 목록 조회 (조장만)"""
    group = study_group_repo.get_group_by_id(db, group_id)
    if not group:
        raise ValueError("스터디 그룹을 찾을 수 없습니다")
    if group.leader_id != user_id:
        raise PermissionError("조장만 신청 목록을 조회할 수 있습니다")

    return application_repo.get_applications_by_group(db, group_id)


def process_application(db: Session, user_id: int, application_id: int, request: ApplicationUpdate):
    """
    신청 수락/거절 (조장만)

    수락(accepted):
    - current_members += 1
    - current_members >= max_members → status = '모집완료'

    거절(rejected):
    - status만 변경
    """
    application = application_repo.get_application_by_id(db, application_id)
    if not application:
        raise ValueError("신청을 찾을 수 없습니다")

    group = study_group_repo.get_group_by_id(db, application.group_id)
    if group.leader_id != user_id:
        raise PermissionError("조장만 신청을 처리할 수 있습니다")
    if application.status != "pending":
        raise ValueError("이미 처리된 신청입니다")

    if request.status not in ("accepted", "rejected"):
        raise ValueError("status는 accepted 또는 rejected여야 합니다")

    application.status = request.status

    if request.status == "accepted":
        group.current_members += 1
        if group.current_members >= group.max_members:
            group.status = "모집완료"
        study_group_repo.update_group(db, group)

    return application_repo.update_application(db, application)
