"""
공용 의존성 — app/core/deps.py의 re-export

Week 4 가이드 호환: `from app.dependencies import get_current_user, admin_required`
기존 코드: `from app.core.deps import get_current_user, require_admin` 모두 유효

- get_current_user: JWT 검증 + is_active 체크 (탈퇴 계정 자동 차단)
- get_optional_user: 비로그인 허용 (None 반환)
- admin_required / require_admin: role == "admin" 필수
"""

from app.core.deps import (  # noqa: F401
    get_current_user,
    get_optional_user,
    require_admin,
    require_admin as admin_required,
)

__all__ = [
    "get_current_user",
    "get_optional_user",
    "admin_required",
    "require_admin",
]
