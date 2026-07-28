"""Change-email verification codes: short-lived, single-use, in-memory.

Same storage philosophy as app/auth/signup_otp.py (a real deployment would
back this with a database/Redis for the TTL, but the security properties
that matter for the prototype hold regardless of storage). Keyed by the
account's user_id — taken from the verified JWT (CurrentTenant), never a
client-supplied identifier — rather than by email, since the whole point of
this flow is that the account performing the change (not a request-body
field) determines whose email actually gets updated. Carries the pending
new_email so verify-otp can apply it without re-collecting anything.
"""

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

_OTP_TTL_MINUTES = 10

_pending_changes: dict[str, "_PendingEmailChange"] = {}


@dataclass(frozen=True)
class _PendingEmailChange:
    new_email: str
    code: str
    expires_at: datetime


def generate_email_change_otp(user_id: str, new_email: str) -> str:
    """Creates (or replaces) the pending email change for `user_id` and
    returns the 6-digit code to send to `new_email`. Uses
    `secrets.randbelow`, not the `random` module — this code guards an
    actual account mutation, so it needs to be unguessable, not just look
    random.
    """
    code = f"{secrets.randbelow(1_000_000):06d}"
    _pending_changes[user_id] = _PendingEmailChange(
        new_email=new_email,
        code=code,
        expires_at=datetime.now(UTC) + timedelta(minutes=_OTP_TTL_MINUTES),
    )
    return code


def consume_email_change_otp(user_id: str, code: str) -> str | None:
    """Validates the code and, only on success, deletes the pending change
    (single-use). Returns the pending new_email so the caller can apply it,
    or None if there's no pending change for this user, it's expired, or
    the code doesn't match.

    A wrong code does NOT consume the pending change — otherwise a single
    mistyped digit would force the user to request an entirely new code.
    """
    entry = _pending_changes.get(user_id)
    if entry is None:
        return None
    if entry.expires_at < datetime.now(UTC):
        del _pending_changes[user_id]
        return None
    if not secrets.compare_digest(entry.code, code):
        return None
    del _pending_changes[user_id]
    return entry.new_email
