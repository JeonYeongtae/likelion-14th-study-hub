"""
StudyGroups Router — 스터디 모집 API

Phase 5
- GET /groups, GET /groups/{id}: 비로그인도 조회 가능 (전체 공개)
- POST/PATCH/DELETE: 로그인 필수
- PATCH /groups/applications/{id}: /{group_id} 보다 먼저 선언해야 라우팅 충돌 방지
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_optional_user
from app.database import get_db
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.schemas.study_group import (
    StudyGroupCreate,
    StudyGroupDetailResponse,
    StudyGroupResponse,
    StudyGroupUpdate,
)
from app.services import application_service, study_group_service

router = APIRouter(prefix="/groups", tags=["Study Groups"])


# ────────────────────────────────────────────────────────
# 주의: /applications/{id} 라우트를 /{group_id} 보다 먼저 선언
#       그렇지 않으면 "applications"가 group_id로 오해될 수 있음
# ────────────────────────────────────────────────────────

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


# ── 그룹 CRUD ──

@router.get("/", response_model=list[StudyGroupResponse])
def get_groups(db: Session = Depends(get_db)):
    """모집 글 전체 목록 — 비로그인 허용"""
    return study_group_service.get_groups(db)


@router.post("/", response_model=StudyGroupResponse)
def create_group(
    request: StudyGroupCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """모집 글 생성 (로그인 필수)"""
    try:
        return study_group_service.create_group(db, current_user.id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{group_id}", response_model=StudyGroupDetailResponse)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),  # Phase 5: 전체 공개
):
    """
    모집 글 상세 조회

    GET /groups/1
    - 비로그인 / 일반 유저: 그룹 기본 정보만 (applications=[])
    - 조장: applications 목록 포함
    """
    try:
        group = study_group_service.get_group(db, group_id)
        is_leader = current_user is not None and group.leader_id == current_user.id
        if is_leader:
            return group
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
    """모집 글 수정 (조장만)"""
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
    """모집 글 삭제 (조장만)"""
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
    """스터디 신청 (로그인 필수)"""
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
    """신청 목록 조회 (조장만)"""
    try:
        return application_service.get_applications(db, current_user.id, group_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{group_id}/my-application", response_model=ApplicationResponse)
def get_my_application(
    group_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    내 신청 현황 조회

    GET /groups/{group_id}/my-application
    - 신청 내역 없음 → 404
    - 있음 → ApplicationResponse (status: pending / accepted / rejected)
    """
    from app.repositories import application_repo as _app_repo
    app = _app_repo.get_application_by_group_and_user(db, group_id, current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="신청 내역이 없습니다")
    return app
