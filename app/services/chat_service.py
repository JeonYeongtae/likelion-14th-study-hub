"""
Chat Service — 채팅 비즈니스 로직

권한 규칙:
- 채팅방 접근 가능: 그룹 조장 OR accepted 신청자
- 단, 그룹 status가 '종료' (확정 완료)인 경우에만 입장 허용
"""

from sqlalchemy.orm import Session

from app.models.study_group import StudyGroup
from app.models.application import Application
from app.models.notification import Notification
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.repositories import chat_repo
from app.schemas.chat import (
    ChatMessageResponse,
    ChatHistoryResponse,
    ChatMemberResponse,
    ChatRoomInfoResponse,
    UnreadCountResponse,
)


# ── 권한 ───────────────────────────────────────────────────────────────────────

def check_chat_access(db: Session, group_id: int, user_id: int) -> StudyGroup:
    """
    채팅방 접근 권한 검증.
    통과하면 StudyGroup 반환, 실패 시 예외 발생.

    조건:
    1. 그룹 status가 '종료' (조장이 그룹 확정하기를 누른 상태)여야 함
    2. 조장이거나 accepted 신청자여야 함
    """
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise ValueError("존재하지 않는 스터디 그룹입니다")

    # 그룹이 확정(종료) 상태인지 확인
    if group.status != "종료":
        raise PermissionError("채팅방은 조장이 그룹을 확정한 후에만 입장할 수 있습니다")

    is_leader = group.leader_id == user_id
    if is_leader:
        return group

    app = db.query(Application).filter(
        Application.group_id == group_id,
        Application.applicant_id == user_id,
        Application.status == "accepted",
    ).first()

    if not app:
        raise PermissionError("채팅방은 확정된 멤버만 입장할 수 있습니다")

    return group


def get_chat_members(db: Session, group: StudyGroup) -> list[ChatMemberResponse]:
    """
    확정 멤버 목록 반환:
    - 조장
    - accepted 신청자
    """
    members: list[ChatMemberResponse] = []

    leader = db.query(User).filter(User.id == group.leader_id).first()
    if leader:
        members.append(ChatMemberResponse(
            user_id=leader.id,
            nickname=leader.nickname,
            is_leader=True,
        ))

    accepted_apps = db.query(Application).filter(
        Application.group_id == group.id,
        Application.status == "accepted",
    ).all()

    for app in accepted_apps:
        if app.applicant_id == group.leader_id:
            continue  # 조장이 본인 그룹에 신청하는 경우 방지
        user = db.query(User).filter(User.id == app.applicant_id).first()
        if user:
            members.append(ChatMemberResponse(
                user_id=user.id,
                nickname=user.nickname,
                is_leader=False,
            ))

    return members


# ── 채팅방 진입 정보 ───────────────────────────────────────────────────────────

def get_room_info(db: Session, group_id: int, user_id: int) -> ChatRoomInfoResponse:
    group = check_chat_access(db, group_id, user_id)
    members = get_chat_members(db, group)
    unread = chat_repo.count_unread(db, group_id, user_id)
    return ChatRoomInfoResponse(
        group_id=group.id,
        group_title=group.title,
        members=members,
        unread_count=unread,
    )


# ── 히스토리 ───────────────────────────────────────────────────────────────────

def get_history(
    db: Session,
    group_id: int,
    user_id: int,
    limit: int = 50,
    before_id: int | None = None,
) -> ChatHistoryResponse:
    check_chat_access(db, group_id, user_id)

    messages = chat_repo.get_messages(db, group_id, limit=limit + 1, before_id=before_id)
    has_more = len(messages) > limit
    if has_more:
        messages = messages[1:]  # 첫 번째(가장 오래된 것) 제거해서 limit 유지

    result = []
    for msg in messages:
        result.append(ChatMessageResponse(
            id=msg.id,
            group_id=msg.group_id,
            sender_id=msg.sender_id,
            sender_nickname=msg.sender.nickname if msg.sender else f"user_{msg.sender_id}",
            content=msg.content,
            created_at=msg.created_at,
        ))

    return ChatHistoryResponse(messages=result, has_more=has_more)


# ── 메시지 저장 ────────────────────────────────────────────────────────────────

def save_message(db: Session, group_id: int, sender_id: int, content: str) -> ChatMessageResponse:
    msg = chat_repo.create_message(db, group_id, sender_id, content.strip())
    sender_nickname = msg.sender.nickname if msg.sender else f"user_{sender_id}"

    # 채팅 알림: 발신자 제외 확정 멤버 전원에게
    try:
        group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
        if group:
            preview = content.strip()[:40]
            notif_message = f"[{group.title}] {sender_nickname}: {preview}"

            recipient_ids: set[int] = set()
            recipient_ids.add(group.leader_id)
            accepted_apps = db.query(Application).filter(
                Application.group_id == group_id,
                Application.status == "accepted",
            ).all()
            for app in accepted_apps:
                recipient_ids.add(app.applicant_id)
            recipient_ids.discard(sender_id)

            for uid in recipient_ids:
                db.add(Notification(
                    user_id=uid,
                    type="chat",
                    message=notif_message,
                    related_id=group_id,
                    is_read=False,
                ))
            db.commit()
    except Exception:
        db.rollback()

    return ChatMessageResponse(
        id=msg.id,
        group_id=msg.group_id,
        sender_id=msg.sender_id,
        sender_nickname=sender_nickname,
        content=msg.content,
        created_at=msg.created_at,
    )


# ── 읽음 처리 ──────────────────────────────────────────────────────────────────

def mark_read(db: Session, group_id: int, user_id: int, last_message_id: int) -> UnreadCountResponse:
    chat_repo.upsert_read_receipt(db, group_id, user_id, last_message_id)
    return UnreadCountResponse(group_id=group_id, unread_count=0)


def get_unread_count(db: Session, group_id: int, user_id: int) -> UnreadCountResponse:
    count = chat_repo.count_unread(db, group_id, user_id)
    return UnreadCountResponse(group_id=group_id, unread_count=count)


# ── 내 채팅방 목록 ──────────────────────────────────────────────────────────────

def get_my_chat_rooms(db: Session, user_id: int) -> list[dict]:
    """
    현재 유저가 접근 가능한 모든 채팅방 목록 반환.
    - 조장인 그룹 (status='종료')
    - accepted 신청자인 그룹 (group status='종료')
    """
    result = []
    seen_group_ids: set[int] = set()

    # 1. 조장인 확정 그룹
    leader_groups = db.query(StudyGroup).filter(
        StudyGroup.leader_id == user_id,
        StudyGroup.status == "종료",
    ).order_by(StudyGroup.id.desc()).all()

    for group in leader_groups:
        members = get_chat_members(db, group)
        unread = chat_repo.count_unread(db, group.id, user_id)
        last_msg = db.query(ChatMessage).filter(
            ChatMessage.group_id == group.id,
        ).order_by(ChatMessage.id.desc()).first()
        result.append({
            "group_id": group.id,
            "group_title": group.title,
            "member_count": len(members),
            "unread_count": unread,
            "is_leader": True,
            "last_message": last_msg.content[:100] if last_msg else None,
            "last_message_at": last_msg.created_at.isoformat() if last_msg else None,
        })
        seen_group_ids.add(group.id)

    # 2. accepted 신청자인 확정 그룹
    accepted_apps = db.query(Application).filter(
        Application.applicant_id == user_id,
        Application.status == "accepted",
    ).all()

    for app in accepted_apps:
        if app.group_id in seen_group_ids:
            continue
        group = db.query(StudyGroup).filter(
            StudyGroup.id == app.group_id,
            StudyGroup.status == "종료",
        ).first()
        if not group:
            continue
        members = get_chat_members(db, group)
        unread = chat_repo.count_unread(db, group.id, user_id)
        last_msg = db.query(ChatMessage).filter(
            ChatMessage.group_id == group.id,
        ).order_by(ChatMessage.id.desc()).first()
        result.append({
            "group_id": group.id,
            "group_title": group.title,
            "member_count": len(members),
            "unread_count": unread,
            "is_leader": False,
            "last_message": last_msg.content[:100] if last_msg else None,
            "last_message_at": last_msg.created_at.isoformat() if last_msg else None,
        })
        seen_group_ids.add(group.id)

    return result
