import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.ingestion.pipeline import run as run_ingestion

ACME = {"email": "alice@acme.example", "password": "acme-demo-pass"}
GLOBEX = {"email": "bob@globex.example", "password": "globex-demo-pass"}


def _login(client: TestClient, credentials: dict[str, str]) -> str:
    token = client.post("/auth/login", json=credentials).json()["token"]
    assert isinstance(token, str)
    return token


def test_query_with_no_relevant_documents_returns_not_found(client: TestClient) -> None:
    token = _login(client, GLOBEX)
    response = client.post(
        "/query",
        json={"question": f"Anything about {uuid.uuid4().hex}?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "couldn't find" in body["answer"].lower()
    assert body["sources"] == []


def test_query_answers_only_from_own_tenants_documents(client: TestClient) -> None:
    token_a = _login(client, ACME)
    token_b = _login(client, GLOBEX)

    marker = uuid.uuid4().hex[:12]
    run_ingestion(
        "tenant-acme",
        f"doc-fixture-{marker}",
        "policy.txt",
        f"Refund policy {marker}: refunds are processed within 5 business days.".encode(),
    )

    with patch("app.api.query.OllamaCloudClient") as mock_llm_cls:
        mock_llm_cls.return_value.generate.return_value = "Refunds take 5 business days."

        response_a = client.post(
            "/query",
            json={"question": f"How long do refunds take under policy {marker}?"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        response_b = client.post(
            "/query",
            json={"question": f"How long do refunds take under policy {marker}?"},
            headers={"Authorization": f"Bearer {token_b}"},
        )

    body_a = response_a.json()
    assert response_a.status_code == 200
    assert len(body_a["sources"]) == 1
    assert body_a["sources"][0]["filename"] == "policy.txt"

    body_b = response_b.json()
    assert response_b.status_code == 200
    assert body_b["sources"] == [], "tenant B must never receive tenant A's document as a source"
    assert "couldn't find" in body_b["answer"].lower()


def test_query_is_logged_to_the_caller_tenants_audit_log(client: TestClient) -> None:
    token = _login(client, GLOBEX)
    question = f"Audit trail check {uuid.uuid4().hex[:8]}"

    client.post(
        "/query",
        json={"question": question},
        headers={"Authorization": f"Bearer {token}"},
    )

    entries = client.get("/audit-log", headers={"Authorization": f"Bearer {token}"}).json()
    assert any(e["question"] == question for e in entries)
