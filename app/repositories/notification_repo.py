"""
Notification Repository — 알림 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.notification import Notification


def get_notifications_by_user(db: Session, user_id: int):
    """내 알림 목록 (최신순)"""
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_notification_by_id(db: Session, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()


def create_notification(db: Session, notification: Notification):
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def mark_as_read(db: Session, notification: Notification):
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
