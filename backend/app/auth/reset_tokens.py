"""Password-reset tokens: short-lived, single-use, in-memory.

A real deployment would back this with a database (and probably Redis for
the TTL), but the security properties that matter for the prototype —
single-use, time-limited, unguessable — hold regardless of storage.
"""

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

_TOKEN_TTL_MINUTES = 30

_tokens: dict[str, "_ResetToken"] = {}


@dataclass(frozen=True)
class _ResetToken:
    email: str
    expires_at: datetime


def generate_reset_token(email: str) -> str:
    token = secrets.token_urlsafe(32)
    _tokens[token] = _ResetToken(
        email=email, expires_at=datetime.now(UTC) + timedelta(minutes=_TOKEN_TTL_MINUTES)
    )
    return token


def consume_reset_token(token: str) -> str | None:
    """Validates and deletes the token in one step (single-use). Returns the
    associated email, or None if the token is missing/expired.
    """
    entry = _tokens.pop(token, None)
    if entry is None:
        return None
    if entry.expires_at < datetime.now(UTC):
        return None
    return entry.email
