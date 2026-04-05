"""
Notification Service — 알림 비즈니스 로직

알림 생성 규칙:
- 내 게시글에 댓글이 달릴 때 (comment_service에서 호출)
- 예약 시간 임박 (reservation_service 또는 스케줄러에서 호출)

읽음 처리: 본인 알림만 가능
"""

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories import notification_repo


def get_my_notifications(db: Session, user_id: int):
    """내 알림 목록"""
    return notification_repo.get_notifications_by_user(db, user_id)


def mark_read(db: Session, user_id: int, notification_id: int):
    """알림 읽음 처리 (본인 알림만)"""
    noti = notification_repo.get_notification_by_id(db, notification_id)
    if not noti:
        raise ValueError("알림을 찾을 수 없습니다")
    if noti.user_id != user_id:
        raise PermissionError("본인의 알림만 처리할 수 있습니다")
    return notification_repo.mark_as_read(db, noti)


def create_comment_notification(db: Session, post_author_id: int, commenter_id: int, post_id: int, post_title: str):
    """
    댓글 알림 생성

    게시글 작성자 != 댓글 작성자일 때만 알림 발송
    """
    if post_author_id == commenter_id:
        return  # 본인 글에 본인 댓글 → 알림 없음

    noti = Notification(
        user_id=post_author_id,
        type="comment",
        message=f"'{post_title[:30]}' 게시글에 새 댓글이 달렸습니다.",
        related_id=post_id,
    )
    notification_repo.create_notification(db, noti)


def create_reservation_notification(db: Session, user_id: int, reservation_id: int, message: str):
    """예약 관련 알림 생성 (스케줄러에서 호출 가능)"""
    noti = Notification(
        user_id=user_id,
        type="reservation",
        message=message,
        related_id=reservation_id,
    )
    notification_repo.create_notification(db, noti)
