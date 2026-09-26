"""احراز هویت با کوکی برای پنل مدیریت شیشه‌ای."""
import secrets
from fastapi import Request, HTTPException, status
from config import ADMIN_PANEL_USERNAME, ADMIN_PANEL_PASSWORD

_ACTIVE_SESSION = None

def create_session():
    global _ACTIVE_SESSION
    _ACTIVE_SESSION = secrets.token_hex(16)
    return _ACTIVE_SESSION

def require_admin(request: Request):
    if not ADMIN_PANEL_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="پنل مدیریت غیرفعاله چون ADMIN_PANEL_PASSWORD ست نشده.",
        )
    
    session_cookie = request.cookies.get("teletube_session")
    if not session_cookie or session_cookie != _ACTIVE_SESSION:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return ADMIN_PANEL_USERNAME
