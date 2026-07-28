import sqlite3
import uuid
from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.storage.db import get_connection

_hasher = PasswordHasher()

# Prototype-scope seed data (docs/plan/06-auth.md) — two tenants, one user
# each, so the cross-tenant isolation scenario has real accounts out of the
# box. Hashed once at import time (argon2 is deliberately slow); re-inserted
# idempotently (INSERT OR IGNORE) on every connection so seeding doesn't
# depend on when/whether this module happened to run first.
_ACME_HASH = _hasher.hash("acme-demo-pass")
_GLOBEX_HASH = _hasher.hash("globex-demo-pass")


@dataclass(frozen=True)
class User:
    email: str
    password_hash: str
    user_id: str
    tenant_id: str
    tenant_name: str
    role: str
    name: str


class EmailAlreadyRegisteredError(Exception):
    """Raised by create_user()/invite_user() when the email is already in use."""


_EMAIL_EXISTS_QUERY = "SELECT 1 FROM users WHERE email = ?"


def _local_part(email: str) -> str:
    """Best-effort display name when one hasn't been collected: the bit
    before the @. Used to backfill signups that didn't provide a "Full
    name" and for invited employees, who have no UI to set one yet."""
    return email.split("@", 1)[0]


def _connection() -> sqlite3.Connection:
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "alice@acme.example",
            _ACME_HASH,
            "user-acme-1",
            "tenant-acme",
            "Acme Corp",
            "admin",
            "Alice",
        ),
    )
    conn.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "bob@globex.example",
            _GLOBEX_HASH,
            "user-globex-1",
            "tenant-globex",
            "Globex Inc",
            "admin",
            "Bob",
        ),
    )
    conn.commit()
    return conn


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        email=row["email"],
        password_hash=row["password_hash"],
        user_id=row["user_id"],
        tenant_id=row["tenant_id"],
        tenant_name=row["tenant_name"],
        role=row["role"],
        name=row["name"],
    )


def authenticate(email: str, password: str) -> User | None:
    conn = _connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row is None:
        return None

    user = _row_to_user(row)
    try:
        _hasher.verify(user.password_hash, password)
    except VerifyMismatchError:
        return None
    return user


def hash_password(password: str) -> str:
    """Exposed so a caller that must hash a password ahead of actually
    creating the user (e.g. the signup-OTP flow in app/auth/signup_otp.py,
    which stores the hash while email verification is pending) can reuse
    this same Argon2 hasher instead of hashing twice or reaching into the
    module-private `_hasher`.
    """
    return _hasher.hash(password)


def create_user_with_hash(
    organization_name: str, email: str, password_hash: str, name: str = ""
) -> User:
    """Same as create_user() below, but takes an already-hashed password.
    Used by the signup-OTP flow to finalize an account at verify-otp time
    without re-hashing a password that was already hashed (via
    hash_password()) when the OTP was first requested.

    `name` is the "Full name" collected in the signup form; if it wasn't
    collected (empty), fall back to the email's local-part rather than
    leaving the display name blank.
    """
    conn = _connection()
    existing = conn.execute(_EMAIL_EXISTS_QUERY, (email,)).fetchone()
    if existing is not None:
        conn.close()
        raise EmailAlreadyRegisteredError(f"{email} is already registered")

    user = User(
        email=email,
        password_hash=password_hash,
        user_id=f"user-{uuid.uuid4().hex[:8]}",
        tenant_id=f"tenant-{uuid.uuid4().hex[:8]}",
        tenant_name=organization_name,
        role="admin",
        name=name.strip() or _local_part(email),
    )
    conn.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            user.email,
            user.password_hash,
            user.user_id,
            user.tenant_id,
            user.tenant_name,
            user.role,
            user.name,
        ),
    )
    conn.commit()
    conn.close()
    return user


def create_user(organization_name: str, email: str, password: str, name: str = "") -> User:
    """Signup: creates a brand-new organization (tenant), with this user as
    its admin. This is the only way a new tenant gets created — see
    invite_user() for how additional teammates join an *existing* tenant.
    """
    return create_user_with_hash(organization_name, email, hash_password(password), name)


def invite_user(tenant_id: str, tenant_name: str, email: str, password: str, name: str = "") -> User:
    """Adds an employee to an *existing* org (tenant_id/tenant_name come from
    the inviting admin's own account — the new user joins the SAME tenant,
    never a new one). The admin sets the email/name/password directly, and
    the account is active immediately — an admin vouching for a known
    teammate is treated as sufficient verification, unlike public signup
    (which requires an email-OTP round trip; see /auth/signup/*). If this
    member later changes their own email, that new address still goes
    through the OTP-verified change-email flow like anyone else's.
    """
    conn = _connection()
    existing = conn.execute(_EMAIL_EXISTS_QUERY, (email,)).fetchone()
    if existing is not None:
        conn.close()
        raise EmailAlreadyRegisteredError(f"{email} is already registered")

    user = User(
        email=email,
        password_hash=_hasher.hash(password),
        user_id=f"user-{uuid.uuid4().hex[:8]}",
        tenant_id=tenant_id,
        tenant_name=tenant_name,
        role="member",
        name=name.strip() or _local_part(email),
    )
    conn.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            user.email,
            user.password_hash,
            user.user_id,
            user.tenant_id,
            user.tenant_name,
            user.role,
            user.name,
        ),
    )
    conn.commit()
    conn.close()
    return user


def user_exists(email: str) -> bool:
    conn = _connection()
    row = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row is not None


def set_password(email: str, new_password: str) -> None:
    conn = _connection()
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE email = ?",
        (_hasher.hash(new_password), email),
    )
    conn.commit()
    conn.close()


def set_email(current_email: str, new_email: str) -> None:
    """Change-email, step 2 (after the new address has been OTP-verified —
    see app/auth/email_change_otp.py). `email` is the users table's PRIMARY
    KEY, but SQLite allows updating a primary-key column in place; every
    other table (documents, audit_log) keys off user_id/tenant_id, not
    email, so this doesn't orphan anything elsewhere.
    """
    conn = _connection()
    conn.execute(
        "UPDATE users SET email = ? WHERE email = ?",
        (new_email, current_email),
    )
    conn.commit()
    conn.close()
