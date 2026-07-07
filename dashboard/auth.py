"""
Autenticação por cookie de sessão assinado — compartilhada entre o dashboard
principal (feed/stats/control) e o Hunter Scout (/scout/*). Extraído para cá
para os dois routers poderem usá-la sem import circular.
"""
from typing import Optional

from fastapi import HTTPException, Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config.settings import settings

_signer = URLSafeTimedSerializer(settings.dashboard_secret_key)


def make_session_token(username: str) -> str:
    return _signer.dumps(username, salt="session")


def verify_session_token(token: str) -> Optional[str]:
    try:
        return _signer.loads(token, salt="session", max_age=86400 * 7)
    except (BadSignature, SignatureExpired):
        return None


def get_user(request: Request) -> Optional[str]:
    token = request.cookies.get("session")
    if not token:
        return None
    return verify_session_token(token)


def require_user(request: Request) -> str:
    user = get_user(request)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user
