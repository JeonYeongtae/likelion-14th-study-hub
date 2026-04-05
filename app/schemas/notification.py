"""
Notification 스키마
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    message: str
    related_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
