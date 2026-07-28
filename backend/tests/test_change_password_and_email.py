import re
import uuid
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

ACME = {"email": "alice@acme.example", "password": "acme-demo-pass"}


def _unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@example.com"


def _extract_code(mock_send: MagicMock) -> str:
    body = mock_send.call_args.kwargs["body"]
    match = re.search(r"\b(\d{6})\b", body)
    assert match, f"no 6-digit code found in email body: {body!r}"
    return match.group(1)


def _signup(client: TestClient, email: str, password: str) -> str:
    """Full two-step signup, returning the access token."""
    with patch("app.api.auth.send_email") as mock_send:
        request_otp = client.post(
            "/auth/signup/request-otp",
            json={"organization_name": "New Co", "email": email, "password": password},
        )
        assert request_otp.status_code == 202
        code = _extract_code(mock_send)

    verify = client.post("/auth/signup/verify-otp", json={"email": email, "code": code})
    assert verify.status_code == 200
    token: str = verify.json()["token"]
    return token


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_change_password_rejects_wrong_current_password(client: TestClient) -> None:
    email = _unique_email()
    token = _signup(client, email, "original-password-1")

    response = client.post(
        "/auth/change-password",
        json={"current_password": "totally-wrong", "new_password": "new-password-1"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 400

    # Old password still works — the rejected attempt must not have changed anything.
    login = client.post("/auth/login", json={"email": email, "password": "original-password-1"})
    assert login.status_code == 200


def test_change_password_correct_flow_updates_password(client: TestClient) -> None:
    email = _unique_email()
    token = _signup(client, email, "original-password-1")

    response = client.post(
        "/auth/change-password",
        json={"current_password": "original-password-1", "new_password": "brand-new-pass1"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 200

    old_login = client.post(
        "/auth/login", json={"email": email, "password": "original-password-1"}
    )
    assert old_login.status_code == 401

    new_login = client.post("/auth/login", json={"email": email, "password": "brand-new-pass1"})
    assert new_login.status_code == 200


def test_change_password_rejects_short_new_password(client: TestClient) -> None:
    email = _unique_email()
    token = _signup(client, email, "original-password-1")

    response = client.post(
        "/auth/change-password",
        json={"current_password": "original-password-1", "new_password": "short"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 422


def test_change_email_request_otp_rejects_wrong_password(client: TestClient) -> None:
    email = _unique_email()
    token = _signup(client, email, "original-password-1")

    with patch("app.api.auth.send_email") as mock_send:
        response = client.post(
            "/auth/change-email/request-otp",
            json={"new_email": _unique_email(), "current_password": "totally-wrong"},
            headers=_auth_headers(token),
        )
    assert response.status_code == 400
    mock_send.assert_not_called()


def test_change_email_request_otp_rejects_duplicate_new_email(client: TestClient) -> None:
    email = _unique_email()
    token = _signup(client, email, "original-password-1")

    other_email = _unique_email()
    _signup(client, other_email, "some-other-pass1")

    with patch("app.api.auth.send_email") as mock_send:
        response = client.post(
            "/auth/change-email/request-otp",
            json={"new_email": other_email, "current_password": "original-password-1"},
            headers=_auth_headers(token),
        )
    assert response.status_code == 409
    mock_send.assert_not_called()


def test_change_email_full_flow_updates_login_capability(client: TestClient) -> None:
    old_email = _unique_email()
    token = _signup(client, old_email, "original-password-1")
    new_email = _unique_email()

    with patch("app.api.auth.send_email") as mock_send:
        request_otp = client.post(
            "/auth/change-email/request-otp",
            json={"new_email": new_email, "current_password": "original-password-1"},
            headers=_auth_headers(token),
        )
        assert request_otp.status_code == 202
        code = _extract_code(mock_send)

    verify = client.post(
        "/auth/change-email/verify-otp",
        json={"code": code},
        headers=_auth_headers(token),
    )
    assert verify.status_code == 200
    new_token = verify.json()["token"]
    assert isinstance(new_token, str)

    # Old email no longer works, new one does.
    old_login = client.post(
        "/auth/login", json={"email": old_email, "password": "original-password-1"}
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login", json={"email": new_email, "password": "original-password-1"}
    )
    assert new_login.status_code == 200

    # The freshly issued token also still works for authenticated requests.
    docs = client.get("/documents", headers=_auth_headers(new_token))
    assert docs.status_code == 200


def test_change_email_verify_rejects_wrong_code(client: TestClient) -> None:
    email = _unique_email()
    token = _signup(client, email, "original-password-1")
    new_email = _unique_email()

    with patch("app.api.auth.send_email") as mock_send:
        request_otp = client.post(
            "/auth/change-email/request-otp",
            json={"new_email": new_email, "current_password": "original-password-1"},
            headers=_auth_headers(token),
        )
        assert request_otp.status_code == 202
        real_code = _extract_code(mock_send)
    wrong_code = "000000" if real_code != "000000" else "111111"

    verify = client.post(
        "/auth/change-email/verify-otp",
        json={"code": wrong_code},
        headers=_auth_headers(token),
    )
    assert verify.status_code == 400

    # The real code is still usable afterwards — a wrong guess must not
    # burn the legitimate code.
    retry = client.post(
        "/auth/change-email/verify-otp",
        json={"code": real_code},
        headers=_auth_headers(token),
    )
    assert retry.status_code == 200


def test_change_email_verify_rejects_expired_code(client: TestClient) -> None:
    email = _unique_email()
    token = _signup(client, email, "original-password-1")
    new_email = _unique_email()

    with patch("app.auth.email_change_otp._OTP_TTL_MINUTES", -1), patch(
        "app.api.auth.send_email"
    ) as mock_send:
        request_otp = client.post(
            "/auth/change-email/request-otp",
            json={"new_email": new_email, "current_password": "original-password-1"},
            headers=_auth_headers(token),
        )
        assert request_otp.status_code == 202
        code = _extract_code(mock_send)

    verify = client.post(
        "/auth/change-email/verify-otp",
        json={"code": code},
        headers=_auth_headers(token),
    )
    assert verify.status_code == 400


def test_change_email_verify_uses_caller_identity_not_body(client: TestClient) -> None:
    # There is no client-supplied email/user identifier in the verify-otp
    # request body at all — only `code`. This test exists to document (and
    # pin down) that the endpoint can only ever act on the caller's own
    # pending change, derived from the bearer token.
    email = _unique_email()
    token_a = _signup(client, email, "original-password-1")
    email_b = _unique_email()
    token_b = _signup(client, email_b, "another-password-1")

    new_email = _unique_email()
    with patch("app.api.auth.send_email") as mock_send:
        request_otp = client.post(
            "/auth/change-email/request-otp",
            json={"new_email": new_email, "current_password": "original-password-1"},
            headers=_auth_headers(token_a),
        )
        assert request_otp.status_code == 202
        code = _extract_code(mock_send)

    # token_b has no pending change of its own, so the same code doesn't verify for it.
    verify_wrong_caller = client.post(
        "/auth/change-email/verify-otp",
        json={"code": code},
        headers=_auth_headers(token_b),
    )
    assert verify_wrong_caller.status_code == 400

    verify_right_caller = client.post(
        "/auth/change-email/verify-otp",
        json={"code": code},
        headers=_auth_headers(token_a),
    )
    assert verify_right_caller.status_code == 200


def test_admin_seed_account_can_change_password(client: TestClient) -> None:
    # Sanity check against the pre-seeded fixture account, restored at the
    # end so other tests relying on ACME's known password keep working.
    login = client.post("/auth/login", json=ACME)
    assert login.status_code == 200
    token = login.json()["token"]

    change = client.post(
        "/auth/change-password",
        json={"current_password": ACME["password"], "new_password": "temporary-pass1"},
        headers=_auth_headers(token),
    )
    assert change.status_code == 200

    relogin = client.post(
        "/auth/login", json={"email": ACME["email"], "password": "temporary-pass1"}
    )
    assert relogin.status_code == 200

    # Restore the original password so other tests (and re-runs) that log
    # in as ACME with its documented demo password keep working.
    restore = client.post(
        "/auth/change-password",
        json={"current_password": "temporary-pass1", "new_password": ACME["password"]},
        headers=_auth_headers(relogin.json()["token"]),
    )
    assert restore.status_code == 200
