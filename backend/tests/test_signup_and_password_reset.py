import re
import uuid
from typing import Any
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def _unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@example.com"


def _request_otp(
    client: TestClient, email: str, password: str, organization_name: str = "New Co"
) -> tuple[Any, MagicMock]:
    with patch("app.api.auth.send_email") as mock_send:
        response = client.post(
            "/auth/signup/request-otp",
            json={"organization_name": organization_name, "email": email, "password": password},
        )
    return response, mock_send


def _extract_code(mock_send: MagicMock) -> str:
    body = mock_send.call_args.kwargs["body"]
    match = re.search(r"\b(\d{6})\b", body)
    assert match, f"no 6-digit code found in email body: {body!r}"
    return match.group(1)


def _signup(
    client: TestClient, email: str, password: str, organization_name: str = "New Co"
) -> Any:
    """Full two-step signup, returning the verify-otp response (a
    LoginResponse on success)."""
    response, mock_send = _request_otp(client, email, password, organization_name)
    assert response.status_code == 202
    code = _extract_code(mock_send)
    return client.post("/auth/signup/verify-otp", json={"email": email, "code": code})


def test_signup_creates_a_new_isolated_tenant(client: TestClient) -> None:
    email = _unique_email()
    response = _signup(client, email, "correct-horse-battery")
    assert response.status_code == 200
    assert "token" in response.json()

    # The new account can immediately list its own (empty) documents.
    token = response.json()["token"]
    docs = client.get("/documents", headers={"Authorization": f"Bearer {token}"})
    assert docs.status_code == 200
    assert docs.json() == []


def test_request_otp_rejects_duplicate_email(client: TestClient) -> None:
    email = _unique_email()
    first = _signup(client, email, "correct-horse-battery")
    assert first.status_code == 200

    second, _ = _request_otp(client, email, "correct-horse-battery")
    assert second.status_code == 409


def test_request_otp_rejects_short_password(client: TestClient) -> None:
    response, _ = _request_otp(client, _unique_email(), "short")
    assert response.status_code == 422


def test_verify_otp_rejects_wrong_code(client: TestClient) -> None:
    email = _unique_email()
    response, mock_send = _request_otp(client, email, "correct-horse-battery")
    assert response.status_code == 202
    real_code = _extract_code(mock_send)
    wrong_code = "000000" if real_code != "000000" else "111111"

    verify = client.post("/auth/signup/verify-otp", json={"email": email, "code": wrong_code})
    assert verify.status_code == 400

    # The real code is still usable afterwards — a wrong guess must not
    # burn the legitimate code.
    retry = client.post("/auth/signup/verify-otp", json={"email": email, "code": real_code})
    assert retry.status_code == 200


def test_verify_otp_rejects_expired_code(client: TestClient) -> None:
    email = _unique_email()
    with patch("app.auth.signup_otp._OTP_TTL_MINUTES", -1):
        response, mock_send = _request_otp(client, email, "correct-horse-battery")
    assert response.status_code == 202
    code = _extract_code(mock_send)

    verify = client.post("/auth/signup/verify-otp", json={"email": email, "code": code})
    assert verify.status_code == 400


def test_verify_otp_rejects_unknown_email(client: TestClient) -> None:
    response = client.post(
        "/auth/signup/verify-otp", json={"email": _unique_email(), "code": "123456"}
    )
    assert response.status_code == 400


def test_forgot_password_gives_same_response_for_unknown_email(client: TestClient) -> None:
    response = client.post("/auth/forgot-password", json={"email": _unique_email()})
    assert response.status_code == 202
    assert "detail" in response.json()


def test_forgot_password_and_reset_flow(client: TestClient) -> None:
    email = _unique_email()
    _signup(client, email, "original-password-1")

    with patch("app.api.auth.send_email") as mock_send, patch(
        "app.api.auth.generate_reset_token", return_value="fake-token"
    ):
        response = client.post("/auth/forgot-password", json={"email": email})
        assert response.status_code == 202
        mock_send.assert_called_once()

    with patch("app.api.auth.consume_reset_token", return_value=email):
        reset = client.post(
            "/auth/reset-password", json={"token": "fake-token", "new_password": "brand-new-pass1"}
        )
        assert reset.status_code == 200

    # Old password no longer works, new one does.
    old = client.post("/auth/login", json={"email": email, "password": "original-password-1"})
    assert old.status_code == 401
    new = client.post("/auth/login", json={"email": email, "password": "brand-new-pass1"})
    assert new.status_code == 200


def test_reset_password_rejects_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/auth/reset-password", json={"token": "not-a-real-token", "new_password": "whatever12345"}
    )
    assert response.status_code == 400
