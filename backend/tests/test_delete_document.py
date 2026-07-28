import uuid

from fastapi.testclient import TestClient

ACME = {"email": "alice@acme.example", "password": "acme-demo-pass"}
GLOBEX = {"email": "bob@globex.example", "password": "globex-demo-pass"}


def _login(client: TestClient, credentials: dict[str, str]) -> str:
    token = client.post("/auth/login", json=credentials).json()["token"]
    assert isinstance(token, str)
    return token


def test_delete_removes_the_document(client: TestClient) -> None:
    token = _login(client, ACME)
    filename = f"to-delete-{uuid.uuid4().hex[:8]}.txt"
    upload = client.post(
        "/documents",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (filename, b"some content", "text/plain")},
    )
    document_id = upload.json()["id"]

    delete = client.delete(
        f"/documents/{document_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert delete.status_code == 204

    docs = client.get("/documents", headers={"Authorization": f"Bearer {token}"}).json()
    assert all(d["id"] != document_id for d in docs)


def test_delete_returns_404_for_unknown_document(client: TestClient) -> None:
    token = _login(client, ACME)
    response = client.delete(
        f"/documents/{uuid.uuid4()}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_cannot_delete_another_tenants_document(client: TestClient) -> None:
    token_a = _login(client, ACME)
    token_b = _login(client, GLOBEX)
    filename = f"acme-only-{uuid.uuid4().hex[:8]}.txt"

    upload = client.post(
        "/documents",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": (filename, b"tenant a content", "text/plain")},
    )
    document_id = upload.json()["id"]

    # Tenant B attempting to delete tenant A's document must not succeed.
    delete = client.delete(
        f"/documents/{document_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert delete.status_code == 404

    # It must still exist for tenant A.
    docs_a = client.get("/documents", headers={"Authorization": f"Bearer {token_a}"}).json()
    assert any(d["id"] == document_id for d in docs_a)

    # Clean up as tenant A (who can) — otherwise this chunk lingers in the
    # shared Qdrant test collection and can pad out unrelated tests' top-k
    # search results (this exact class of bug has bitten this suite before).
    client.delete(f"/documents/{document_id}", headers={"Authorization": f"Bearer {token_a}"})
