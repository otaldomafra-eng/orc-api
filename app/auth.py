import hashlib
import hmac
import secrets
from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import ApiKey

bearer_scheme = HTTPBearer(auto_error=False)


def hash_api_key(api_key: str) -> str:
    pepper = get_settings().api_key_pepper.encode("utf-8")
    return hmac.new(pepper, api_key.encode("utf-8"), hashlib.sha256).hexdigest()


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)


def _require_key(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
    *,
    admin_required: bool,
) -> ApiKey:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    key_hash = hash_api_key(credentials.credentials)
    api_key = db.scalar(select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.ativa.is_(True)))
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")

    if admin_required and api_key.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin token required")

    api_key.last_used_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    return api_key


def require_read_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> ApiKey:
    return _require_key(credentials, db, admin_required=False)


def require_admin_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> ApiKey:
    return _require_key(credentials, db, admin_required=True)
