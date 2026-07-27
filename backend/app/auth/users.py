from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


@dataclass(frozen=True)
class SeedUser:
    email: str
    password_hash: str
    user_id: str
    tenant_id: str
    tenant_name: str


# Prototype-scope seed data (docs/plan/06-auth.md). Two tenants, one user each,
# so the cross-tenant isolation scenario (docs/scenarios/cross-tenant-isolation.md)
# has real accounts to log in as and prove data never crosses between them.
_USERS: dict[str, SeedUser] = {
    "alice@acme.example": SeedUser(
        email="alice@acme.example",
        password_hash=_hasher.hash("acme-demo-pass"),
        user_id="user-acme-1",
        tenant_id="tenant-acme",
        tenant_name="Acme Corp",
    ),
    "bob@globex.example": SeedUser(
        email="bob@globex.example",
        password_hash=_hasher.hash("globex-demo-pass"),
        user_id="user-globex-1",
        tenant_id="tenant-globex",
        tenant_name="Globex Inc",
    ),
}


def authenticate(email: str, password: str) -> SeedUser | None:
    user = _USERS.get(email)
    if user is None:
        return None
    try:
        _hasher.verify(user.password_hash, password)
    except VerifyMismatchError:
        return None
    return user
