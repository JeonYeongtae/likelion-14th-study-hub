"""
Notifications Router — 알림 API

GET   /notifications         내 알림 목록
PATCH /notifications/{id}/read  읽음 처리
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
