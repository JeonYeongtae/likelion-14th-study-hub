"""
Chat 스키마 — 채팅 메시지 요청/응답 형태
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ChatMessageResponse(BaseModel):
    id: int
    group_id: int
    sender_id: int
    sender_nickname: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    """히스토리 조회 응답 — 페이지네이션 포함"""
    messages: list[ChatMessageResponse]
    has_more: bool  # 더 이전 메시지 존재 여부


class ChatMemberResponse(BaseModel):
    """채팅방 멤버 (확정 인원)"""
    user_id: int
    nickname: str
    is_leader: bool

    model_config = {"from_attributes": True}


class ChatRoomInfoResponse(BaseModel):
    """채팅방 진입 시 초기 정보"""
    group_id: int
    group_title: str
    members: list[ChatMemberResponse]
    unread_count: int


class UnreadCountResponse(BaseModel):
    group_id: int
    unread_count: int


class ChatRoomListItem(BaseModel):
    """내 채팅방 목록 항목"""
    group_id: int
    group_title: str
    member_count: int
    unread_count: int
    is_leader: bool
    last_message: Optional[str] = None
    last_message_at: Optional[str] = None


class WsMessageOut(BaseModel):
    """WebSocket 브로드캐스트 페이로드"""
    type: str  # "message" | "system"
    id: Optional[int] = None
    group_id: Optional[int] = None
    sender_id: Optional[int] = None
    sender_nickname: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[str] = None
