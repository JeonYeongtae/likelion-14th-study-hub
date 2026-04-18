"""
Chat Repository — 채팅 메시지 & 읽음 처리 DB 조작
"""

from sqlalchemy.orm import Session
from app.models.chat_message import ChatMessage
from app.models.chat_read_receipt import ChatReadReceipt


# ── 메시지 ────────────────────────────────────────────────────────────────────

def create_message(db: Session, group_id: int, sender_id: int, content: str) -> ChatMessage:
    """메시지 저장"""
    msg = ChatMessage(group_id=group_id, sender_id=sender_id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(db: Session, group_id: int, limit: int = 50, before_id: int | None = None) -> list[ChatMessage]:
    """
    채팅 히스토리 조회 (최신순으로 limit개 → 반환 시 오름차순 정렬)
    before_id: 페이지네이션 — 해당 id보다 이전 메시지만 조회
    """
    q = db.query(ChatMessage).filter(ChatMessage.group_id == group_id)
    if before_id is not None:
        q = q.filter(ChatMessage.id < before_id)
    messages = q.order_by(ChatMessage.id.desc()).limit(limit).all()
    return list(reversed(messages))  # 오래된 것이 위에 오도록 뒤집기


def get_message_by_id(db: Session, message_id: int) -> ChatMessage | None:
    return db.query(ChatMessage).filter(ChatMessage.id == message_id).first()


# ── 읽음 처리 ──────────────────────────────────────────────────────────────────

def get_read_receipt(db: Session, group_id: int, user_id: int) -> ChatReadReceipt | None:
    return db.query(ChatReadReceipt).filter(
        ChatReadReceipt.group_id == group_id,
        ChatReadReceipt.user_id == user_id,
    ).first()


def upsert_read_receipt(db: Session, group_id: int, user_id: int, last_message_id: int) -> ChatReadReceipt:
    """읽음 위치 UPSERT — 더 최신 메시지일 때만 업데이트"""
    receipt = get_read_receipt(db, group_id, user_id)
    if receipt is None:
        receipt = ChatReadReceipt(
            group_id=group_id,
            user_id=user_id,
            last_read_message_id=last_message_id,
        )
        db.add(receipt)
    else:
        # 이미 읽은 위치보다 최신일 때만 업데이트
        if receipt.last_read_message_id is None or last_message_id > receipt.last_read_message_id:
            receipt.last_read_message_id = last_message_id
    db.commit()
    db.refresh(receipt)
    return receipt


def count_unread(db: Session, group_id: int, user_id: int) -> int:
    """미읽은 메시지 수"""
    receipt = get_read_receipt(db, group_id, user_id)
    last_id = receipt.last_read_message_id if receipt else 0

    q = db.query(ChatMessage).filter(ChatMessage.group_id == group_id)
    if last_id:
        q = q.filter(ChatMessage.id > last_id)
    return q.count()
