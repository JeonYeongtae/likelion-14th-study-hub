"""
StudyGroups Router — 스터디 모집 API

Phase 5
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.schemas.study_group import StudyGroupCreate, StudyGroupDetailResponse, StudyGroupResponse, StudyGroupUpdate
from app.services import application_service, study_group_service

router = APIRouter(prefix="/groups", tags=["Study Groups"])


@router.get("/", response_model=list[StudyGroupResponse])
def get_groups(db: Session = Depends(get_db)):
    """
    스터디 모집 글 목록

    GET /groups
    로그인 불필요
    """
    return study_group_service.get_groups(db)


@router.post("/", response_model=StudyGroupResponse)
def create_group(
    request: StudyGroupCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    스터디 모집 글 생성

    POST /groups
    Authorization: Bearer {token}
    """
    try:
        return study_group_service.create_group(db, current_user.id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{group_id}", response_model=StudyGroupDetailResponse)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    스터디 모집 글 상세 조회 (신청 목록 포함)

    GET /groups/1
    Authorization: Bearer {token}
    - 조장: 신청 목록 포함
    - 일반: 신청 목록 빈 배열
    """
    try:
        group = study_group_service.get_group(db, group_id)
        # 조장이면 신청 목록 포함, 아니면 빈 배열
        if group.leader_id == current_user.id:
            return group
        # 일반 유저: applications 숨김
        result = StudyGroupDetailResponse.model_validate(group)
        result.applications = []
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{group_id}", response_model=StudyGroupResponse)
def update_group(
    group_id: int,
    request: StudyGroupUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    스터디 모집 글 수정 (조장만)

    PATCH /groups/1
    Authorization: Bearer {token}
    """
    try:
        return study_group_service.update_group(db, current_user.id, group_id, request)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{group_id}")
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    스터디 모집 글 삭제 (조장만)

    DELETE /groups/1
    Authorization: Bearer {token}
    """
    try:
        study_group_service.delete_group(db, current_user.id, group_id)
        return {"message": "스터디 그룹이 삭제되었습니다"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── 신청 관련 ──

@router.post("/{group_id}/apply", response_model=ApplicationResponse)
def apply(
    group_id: int,
    request: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    스터디 신청

    POST /groups/1/apply
    Authorization: Bearer {token}
    요청: {"message": "열심히 하겠습니다"} (선택)
    """
    try:
        return application_service.apply(db, current_user.id, group_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{group_id}/applications", response_model=list[ApplicationResponse])
def get_applications(
    group_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    신청 목록 조회 (조장만)

    GET /groups/1/applications
    Authorization: Bearer {token}
    """
    try:
        return application_service.get_applications(db, current_user.id, group_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/applications/{application_id}", response_model=ApplicationResponse)
def process_application(
    application_id: int,
    request: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    신청 수락/거절 (조장만)

    PATCH /groups/applications/1
    Authorization: Bearer {token}
    요청: {"status": "accepted"} 또는 {"status": "rejected"}
    """
    try:
        return application_service.process_application(db, current_user.id, application_id, request)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
