from dataclasses import dataclass

import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import decode_access_token

_security = HTTPBearer()


@dataclass(frozen=True)
class TenantContext:
    """Identity derived from a verified JWT.

    This is the ONLY object other modules should use to know which tenant a
    request belongs to — nothing downstream re-reads the token or accepts a
    client-supplied tenant identifier. See docs/plan/00-overview.md, "the one
    rule that overrides all others".
    """

    user_id: str
    tenant_id: str
    tenant_name: str


def get_current_tenant(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> TenantContext:
    try:
        payload = decode_access_token(credentials.credentials)
    except pyjwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        ) from exc
    except pyjwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc

    return TenantContext(
        user_id=payload["sub"],
        tenant_id=payload["tenant_id"],
        tenant_name=payload.get("tenant_name", payload["tenant_id"]),
    )
