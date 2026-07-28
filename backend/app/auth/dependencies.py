from dataclasses import dataclass
from typing import Annotated

import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import decode_access_token

_security = HTTPBearer()
_Credentials = Annotated[HTTPAuthorizationCredentials, Depends(_security)]


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
    role: str
    email: str
    name: str


def get_current_tenant(credentials: _Credentials) -> TenantContext:
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
        tenant_name=str(payload.get("tenant_name") or payload["tenant_id"]),
        role=str(payload.get("role") or "admin"),
        email=str(payload.get("email") or ""),
        name=str(payload.get("name") or ""),
    )


# Shared FastAPI dependency annotation — every protected endpoint takes
# `tenant: CurrentTenant` instead of repeating `Depends(get_current_tenant)`.
CurrentTenant = Annotated[TenantContext, Depends(get_current_tenant)]
