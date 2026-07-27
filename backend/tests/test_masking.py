from app.masking.presidio_service import mask


def test_masks_email_and_phone() -> None:
    result = mask("Contact Jane Doe at jane.doe@example.com or 415-555-0199.")
    assert result.triggered
    assert "jane.doe@example.com" not in result.masked_text


def test_masks_custom_client_id_pattern() -> None:
    result = mask("Client ID: CID-48213 is on file.")
    assert result.triggered
    assert "CID-48213" not in result.masked_text


def test_masks_password_like_string() -> None:
    result = mask("Internal note: password: hunter2please-rotate")
    assert result.triggered
    assert "hunter2please-rotate" not in result.masked_text


def test_plain_text_with_no_pii_is_unchanged() -> None:
    text = "The process completes successfully after validation."
    result = mask(text)
    assert result.masked_text == text
    assert result.triggered is False


def test_empty_text_is_not_triggered() -> None:
    result = mask("")
    assert result.triggered is False
    assert result.masked_text == ""
