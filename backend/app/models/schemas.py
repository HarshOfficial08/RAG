from typing import Literal

from pydantic import BaseModel

DocumentStatus = Literal["processing", "indexed", "failed"]


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str


class DocumentRecord(BaseModel):
    id: str
    filename: str
    status: DocumentStatus
    uploaded_at: str
    pii_masked: bool
    failure_reason: str | None = None


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
