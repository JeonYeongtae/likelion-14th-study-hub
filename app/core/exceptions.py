"""
커스텀 예외 — 비즈니스 로직 전용 에러 타입

라우터에서 HTTPException 상태 코드를 결정할 때 사용.
ValueError와 구분하여 세분화된 HTTP 응답을 반환하기 위함.
"""


class DeactivatedAccountError(Exception):
    """
    30일 유예 기간 내 비활성화 계정(Soft Deleted)으로 로그인 시도.

    라우터에서 HTTP 403 + ACCOUNT_DEACTIVATED 코드로 변환됨.
    """
    pass
