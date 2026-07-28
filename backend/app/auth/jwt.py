from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.config import settings


def create_access_token(
    user_id: str,
    tenant_id: str,
    tenant_name: str,
    role: str = "admin",
    email: str = "",
    name: str = "",
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "tenant_name": tenant_name,
        "role": role,
        "email": email,
        "name": name,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expiry_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
