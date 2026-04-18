"""
Chat Router — 스터디 그룹 전용 채팅방 API

REST:
  GET  /groups/{group_id}/chat/info          채팅방 진입 정보 (멤버 목록, 미읽음 수)
  GET  /groups/{group_id}/chat/messages      메시지 히스토리 (페이지네이션)
  POST /groups/{group_id}/chat/read          읽음 처리
  GET  /groups/{group_id}/chat/unread        미읽음 수 조회

WebSocket:
  WS   /groups/{group_id}/chat/ws?token=...  실시간 채팅
      - 클라이언트 → 서버: {"content": "메시지 내용"}
      - 서버 → 클라이언트: WsMessageOut JSON
"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token
from app.core.deps import get_current_user
from app.database import get_db, SessionLocal
from app.repositories import user_repo
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatRoomInfoResponse,
    UnreadCountResponse,
)
from app.services import chat_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket 커넥션 매니저
# 그룹별로 연결된 WebSocket 목록을 관리
# ─────────────────────────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        # group_id → list[(websocket, user_id, nickname)]
        self._rooms: dict[int, list[tuple[WebSocket, int, str]]] = {}

    async def connect(self, ws: WebSocket, group_id: int, user_id: int, nickname: str):
        await ws.accept()
        if group_id not in self._rooms:
            self._rooms[group_id] = []
        self._rooms[group_id].append((ws, user_id, nickname))

    def disconnect(self, ws: WebSocket, group_id: int):
        if group_id in self._rooms:
            self._rooms[group_id] = [
                (w, uid, nick) for w, uid, nick in self._rooms[group_id] if w is not ws
            ]

    async def broadcast(self, group_id: int, payload: dict):
        """그룹 전원에게 메시지 전송. 끊긴 소켓은 조용히 제거."""
        if group_id not in self._rooms:
            return
        dead: list[WebSocket] = []
        for ws, _, _ in self._rooms[group_id]:
            try:
                await ws.send_text(json.dumps(payload, ensure_ascii=False, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, group_id)

    async def send_personal(self, ws: WebSocket, payload: dict):
        await ws.send_text(json.dumps(payload, ensure_ascii=False, default=str))


manager = ConnectionManager()


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket 엔드포인트
# ─────────────────────────────────────────────────────────────────────────────

@router.websocket("/groups/{group_id}/chat/ws")
async def chat_ws(
    websocket: WebSocket,
    group_id: int,
    token: str = Query(..., description="JWT access token"),
):
    """
    실시간 채팅 WebSocket

    연결: ws://host/api/v1/groups/{group_id}/chat/ws?token={access_token}
    수신: {"content": "보낼 내용"}
    발신: WsMessageOut 형태 JSON
    """
    # ── 1. 토큰 인증 ──────────────────────────────────────────────────────────
    db: Session = SessionLocal()
    try:
        try:
            payload = decode_access_token(token)
            user_id = int(payload["sub"])
        except (JWTError, KeyError, ValueError):
            await websocket.close(code=4001)
            return

        user = user_repo.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            await websocket.close(code=4001)
            return

        # ── 2. 권한 체크 ──────────────────────────────────────────────────────
        try:
            chat_service.check_chat_access(db, group_id, user_id)
        except (ValueError, PermissionError):
            await websocket.close(code=4003)
            return

        # ── 3. 연결 수락 & 입장 알림 ──────────────────────────────────────────
        await manager.connect(websocket, group_id, user_id, user.nickname)
        await manager.broadcast(group_id, {
            "type": "system",
            "content": f"{user.nickname}님이 입장했습니다.",
        })

        # ── 4. 메시지 루프 ────────────────────────────────────────────────────
        try:
            while True:
                raw = await websocket.receive_text()
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    await manager.send_personal(websocket, {"type": "error", "content": "잘못된 JSON 형식입니다."})
                    continue

                content: str = (data.get("content") or "").strip()
                if not content:
                    continue
                if len(content) > 2000:
                    await manager.send_personal(websocket, {"type": "error", "content": "메시지는 2000자 이내여야 합니다."})
                    continue

                # DB 저장 (새 세션 사용 — 장기 루프에서 세션 상태 리셋)
                msg_db: Session = SessionLocal()
                try:
                    msg_resp = chat_service.save_message(msg_db, group_id, user_id, content)
                finally:
                    msg_db.close()

                await manager.broadcast(group_id, {
                    "type": "message",
                    "id": msg_resp.id,
                    "group_id": msg_resp.group_id,
                    "sender_id": msg_resp.sender_id,
                    "sender_nickname": msg_resp.sender_nickname,
                    "content": msg_resp.content,
                    "created_at": msg_resp.created_at.isoformat(),
                })

        except WebSocketDisconnect:
            manager.disconnect(websocket, group_id)
            await manager.broadcast(group_id, {
                "type": "system",
                "content": f"{user.nickname}님이 퇴장했습니다.",
            })
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# REST 엔드포인트
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/groups/{group_id}/chat/info", response_model=ChatRoomInfoResponse)
def get_room_info(
    group_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    채팅방 진입 전 초기 정보 조회
    - 그룹 제목, 확정 멤버 목록, 미읽음 수
    """
    try:
        return chat_service.get_room_info(db, group_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/groups/{group_id}/chat/messages", response_model=ChatHistoryResponse)
def get_messages(
    group_id: int,
    limit: int = Query(50, ge=1, le=100),
    before_id: Optional[int] = Query(None, description="이 ID보다 이전 메시지 조회 (페이지네이션)"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    메시지 히스토리 조회 (오래된 순)

    GET /groups/1/chat/messages?limit=50
    GET /groups/1/chat/messages?limit=50&before_id=100   (100번 이전 메시지)
    """
    try:
        return chat_service.get_history(db, group_id, current_user.id, limit, before_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/groups/{group_id}/chat/read", response_model=UnreadCountResponse)
def mark_read(
    group_id: int,
    last_message_id: int = Query(..., description="마지막으로 읽은 메시지 ID"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """읽음 처리 — 열람한 마지막 메시지 ID 기록"""
    try:
        chat_service.check_chat_access(db, group_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return chat_service.mark_read(db, group_id, current_user.id, last_message_id)


@router.get("/groups/{group_id}/chat/unread", response_model=UnreadCountResponse)
def get_unread(
    group_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """미읽은 메시지 수 조회"""
    try:
        chat_service.check_chat_access(db, group_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return chat_service.get_unread_count(db, group_id, current_user.id)
