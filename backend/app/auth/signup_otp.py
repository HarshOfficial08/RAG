"""Signup email-verification codes: short-lived, single-use, in-memory.

Same storage philosophy as app/auth/reset_tokens.py (a real deployment would
back this with a database/Redis for the TTL, but the security properties
that matter for the prototype hold regardless of storage) — except this
store is keyed by email rather than by the secret itself, since the "token"
here is a 6-digit code a human types in rather than an unguessable URL
fragment. It also carries the rest of the pending signup (organization name
+ an already-hashed password) so the account can be created at verify time
without re-collecting anything or hashing the password twice.
"""

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

_OTP_TTL_MINUTES = 10

_pending_signups: dict[str, "_PendingSignup"] = {}


@dataclass(frozen=True)
class _PendingSignup:
    organization_name: str
    password_hash: str
    name: str
    code: str
    expires_at: datetime


@dataclass(frozen=True)
class VerifiedSignup:
    organization_name: str
    password_hash: str
    name: str


def generate_signup_otp(
    organization_name: str, email: str, password_hash: str, name: str = ""
) -> str:
    """Creates (or replaces) the pending signup for `email` and returns the
    6-digit code to send them. Uses `secrets.randbelow`, not the `random`
    module — this code guards actual account creation, so it needs to be
    unguessable, not just look random.

    `name` (the "Full name" field on the signup form) is stashed alongside
    the rest of the pending signup so it's available at verify-otp time,
    when the account is actually created — same treatment as
    organization_name/password_hash.
    """
    code = f"{secrets.randbelow(1_000_000):06d}"
    _pending_signups[email] = _PendingSignup(
        organization_name=organization_name,
        password_hash=password_hash,
        name=name,
        code=code,
        expires_at=datetime.now(UTC) + timedelta(minutes=_OTP_TTL_MINUTES),
    )
    return code


def consume_signup_otp(email: str, code: str) -> VerifiedSignup | None:
    """Validates the code and, only on success, deletes the pending signup
    (single-use). Returns the pending organization_name/password_hash so the
    caller can finalize the account, or None if there's no pending signup
    for this email, it's expired, or the code doesn't match.

    A wrong code does NOT consume the pending signup — otherwise a single
    mistyped digit would lock a legitimate user out until they request a
    fresh code.
    """
    entry = _pending_signups.get(email)
    if entry is None:
        return None
    if entry.expires_at < datetime.now(UTC):
        del _pending_signups[email]
        return None
    if not secrets.compare_digest(entry.code, code):
        return None
    del _pending_signups[email]
    return VerifiedSignup(
        organization_name=entry.organization_name,
        password_hash=entry.password_hash,
        name=entry.name,
    )
