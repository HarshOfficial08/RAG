from typing import Literal

from pydantic import BaseModel, Field

DocumentStatus = Literal["processing", "indexed", "failed"]


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str


class SignupRequest(BaseModel):
    organization_name: str
    email: str
    password: str = Field(min_length=8)
    # Optional "Full name" collected on the signup form; if omitted, the
    # account falls back to the email's local-part (see users.py).
    name: str = ""


class VerifyOtpRequest(BaseModel):
    email: str
    code: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class InviteEmployeeRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    # Admin is adding a known teammate directly (not a public self-signup),
    # so there's no signup form to collect this separately.
    name: str = ""


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class ChangeEmailRequestOtpRequest(BaseModel):
    new_email: str
    current_password: str


class ChangeEmailVerifyOtpRequest(BaseModel):
    code: str


class DocumentRecord(BaseModel):
    id: str
    filename: str
    status: DocumentStatus
    uploaded_at: str
    pii_masked: bool
    failure_reason: str | None = None


class DocumentPreview(BaseModel):
    filename: str
    # The masked text as actually indexed — never the original unmasked
    # content, consistent with the rest of the masking guarantee.
    text: str


class QueryRequest(BaseModel):
    question: str


class QuerySource(BaseModel):
    document_id: str
    filename: str
    chunk_index: int


class QueryResponse(BaseModel):
    answer: str
    sources: list[QuerySource]


class AuditLogEntry(BaseModel):
    id: str
    timestamp: str
    user_id: str
    question: str
    masking_triggered: bool


class MemberRecord(BaseModel):
    user_id: str
    name: str
    email: str
    role: str


class UpdateMemberRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = Field(default=None, min_length=8)

