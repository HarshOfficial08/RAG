import uuid

from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token

ACME = {"email": "alice@acme.example", "password": "acme-demo-pass"}
GLOBEX = {"email": "bob@globex.example", "password": "globex-demo-pass"}


def _login(client: TestClient, credentials: dict[str, str]) -> str:
    token = client.post("/auth/login", json=credentials).json()["token"]
    assert isinstance(token, str)
    return token


def test_admin_can_add_teammate_to_own_tenant(client: TestClient) -> None:
    token = _login(client, ACME)
    email = f"teammate-{uuid.uuid4().hex[:8]}@acme.example"

    response = client.post(
        "/auth/invite",
        json={"email": email, "password": "teammate-pass", "name": "Teammate"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    # Active immediately with the password the admin set — no email
    # verification step in this flow (unlike public signup).
    login_attempt = client.post(
        "/auth/login", json={"email": email, "password": "teammate-pass"}
    )
    assert login_attempt.status_code == 200


def test_member_cannot_invite_teammates(client: TestClient) -> None:
    member_token = create_access_token(
        "user-fake-member", "tenant-acme", "Acme Corp", role="member"
    )

    response = client.post(
        "/auth/invite",
        json={
            "email": f"blocked-{uuid.uuid4().hex[:8]}@acme.example",
            "password": "irrelevant-pass",
            "name": "Blocked",
        },
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert response.status_code == 403


def test_cannot_invite_duplicate_email(client: TestClient) -> None:
    token = _login(client, ACME)
    email = f"dup-{uuid.uuid4().hex[:8]}@acme.example"

    first = client.post(
        "/auth/invite",
        json={"email": email, "password": "teammate-pass", "name": "Dup"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first.status_code == 201

    second = client.post(
        "/auth/invite",
        json={"email": email, "password": "teammate-pass", "name": "Dup"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second.status_code == 409


def test_preview_returns_masked_document_text(client: TestClient) -> None:
    token = _login(client, ACME)
    marker = uuid.uuid4().hex[:8]
    upload = client.post(
        "/documents",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                f"preview-{marker}.txt",
                f"Contact preview-{marker}@example.com for details.".encode(),
                "text/plain",
            )
        },
    )
    document_id = upload.json()["id"]

    preview = client.get(
        f"/documents/{document_id}/preview", headers={"Authorization": f"Bearer {token}"}
    )
    assert preview.status_code == 200
    body = preview.json()
    assert body["filename"] == f"preview-{marker}.txt"
    # The email must be masked in the preview, never shown raw.
    assert f"preview-{marker}@example.com" not in body["text"]

    client.delete(f"/documents/{document_id}", headers={"Authorization": f"Bearer {token}"})


def test_preview_404_for_unknown_document(client: TestClient) -> None:
    token = _login(client, ACME)
    response = client.get(
        f"/documents/{uuid.uuid4()}/preview", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_cannot_preview_another_tenants_document(client: TestClient) -> None:
    token_a = _login(client, ACME)
    token_b = _login(client, GLOBEX)
    upload = client.post(
        "/documents",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("secret.txt", b"acme only content", "text/plain")},
    )
    document_id = upload.json()["id"]

    response = client.get(
        f"/documents/{document_id}/preview", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 404

    client.delete(f"/documents/{document_id}", headers={"Authorization": f"Bearer {token_a}"})
