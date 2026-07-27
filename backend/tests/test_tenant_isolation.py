"""The single most important test in this project — see docs/plan/00-overview.md
and docs/scenarios/cross-tenant-isolation.md. This is an in-memory-store version
of the same guarantee; tests/test_vector_store_isolation.py and test_query.py
prove the same thing against the real Qdrant-backed pipeline.

Assertions here check for presence/absence of this test's own unique fixture
data rather than an empty starting state — the in-memory stores are shared
module-level state across the whole test session, so other tests legitimately
populate them first depending on run order.
"""

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

ACME = {"email": "alice@acme.example", "password": "acme-demo-pass"}
GLOBEX = {"email": "bob@globex.example", "password": "globex-demo-pass"}


def _login(client: TestClient, credentials: dict[str, str]) -> str:
    response = client.post("/auth/login", json=credentials)
    token = response.json()["token"]
    assert isinstance(token, str)
    return token


def test_tenant_cannot_see_other_tenants_documents(client: TestClient) -> None:
    token_a = _login(client, ACME)
    token_b = _login(client, GLOBEX)
    filename = f"acme-confidential-{uuid.uuid4().hex[:8]}.txt"

    upload = client.post(
        "/documents",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": (filename, b"tenant-a-only-content", "text/plain")},
    )
    assert upload.status_code == 200

    docs_a = client.get("/documents", headers={"Authorization": f"Bearer {token_a}"}).json()
    docs_b = client.get("/documents", headers={"Authorization": f"Bearer {token_b}"}).json()

    assert any(d["filename"] == filename for d in docs_a)
    assert not any(d["filename"] == filename for d in docs_b), (
        "tenant B must never see tenant A's document, even by listing all"
    )


def test_audit_log_is_scoped_per_tenant(client: TestClient) -> None:
    token_a = _login(client, ACME)
    token_b = _login(client, GLOBEX)
    question = f"isolation-check-{uuid.uuid4().hex[:8]}"

    # Mocked defensively: this question isn't expected to match any indexed
    # content, but with fixture documents accumulating across the test session
    # a coincidental above-threshold match is possible — tests must never
    # depend on a real (unauthenticated, keyless) network call either way.
    with patch("app.api.query.OllamaCloudClient") as mock_llm_cls:
        mock_llm_cls.return_value.generate.return_value = "mocked answer"
        client.post(
            "/query",
            json={"question": question},
            headers={"Authorization": f"Bearer {token_a}"},
        )

    entries_a = client.get("/audit-log", headers={"Authorization": f"Bearer {token_a}"}).json()
    entries_b = client.get("/audit-log", headers={"Authorization": f"Bearer {token_b}"}).json()

    assert any(e["question"] == question for e in entries_a)
    assert not any(e["question"] == question for e in entries_b), (
        "tenant B must never see an entry from tenant A's audit log"
    )
