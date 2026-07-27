from fastapi.testclient import TestClient

ACME = {"email": "alice@acme.example", "password": "acme-demo-pass"}
GLOBEX = {"email": "bob@globex.example", "password": "globex-demo-pass"}


def test_login_success(client: TestClient) -> None:
    response = client.post("/auth/login", json=ACME)
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_wrong_password(client: TestClient) -> None:
    response = client.post("/auth/login", json={"email": ACME["email"], "password": "wrong"})
    assert response.status_code == 401


def test_login_unknown_email(client: TestClient) -> None:
    response = client.post(
        "/auth/login", json={"email": "nobody@nowhere.example", "password": "x"}
    )
    assert response.status_code == 401


def test_protected_endpoint_requires_token(client: TestClient) -> None:
    response = client.get("/documents")
    assert response.status_code == 401


def test_protected_endpoint_rejects_garbage_token(client: TestClient) -> None:
    response = client.get("/documents", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
