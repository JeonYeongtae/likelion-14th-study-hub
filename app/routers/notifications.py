"""
Notifications Router — 알림 API

GET    /notifications/               내 알림 목록
GET    /notifications/unread-count   읽지 않은 알림 수
PATCH  /notifications/{id}/read      읽음 처리
DELETE /notifications/all            전체 알림 삭제
DELETE /notifications/read-only      읽음 알림만 삭제
DELETE /notifications/{id}           단건 알림 삭제
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.schemas.notification import NotificationResponse
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=list[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내 알림 목록 (최신순)"""
    return notification_service.get_my_notifications(db, current_user.id)


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """읽지 않은 알림 수 (헤더 뱃지용)"""
    notis = notification_service.get_my_notifications(db, current_user.id)
    count = sum(1 for n in notis if not n.is_read)
    return {"count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """알림 읽음 처리"""
    try:
        return notification_service.mark_read(db, current_user.id, notification_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ── 삭제 엔드포인트 (정적 경로를 파라미터 경로보다 먼저 선언) ──────────────────

@router.delete("/all", status_code=204)
def delete_all(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """전체 알림 삭제"""
    notification_service.delete_all_notifications(db, current_user.id)


@router.delete("/read-only", status_code=204)
def delete_read_only(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """읽음 알림만 삭제"""
    notification_service.delete_read_notifications(db, current_user.id)


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """알림 단건 삭제"""
    try:
        notification_service.delete_notification(db, current_user.id, notification_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
