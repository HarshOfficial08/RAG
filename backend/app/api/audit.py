import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app.auth.dependencies import TenantContext, get_current_tenant
from app.models.schemas import AuditLogEntry

router = APIRouter(tags=["audit"])

_audit_log: dict[str, list[AuditLogEntry]] = {}


def log_query(tenant_id: str, user_id: str, question: str, masking_triggered: bool) -> None:
    # Deliberately logs only the question and a boolean flag — never the raw
    # retrieved chunk text or full answer, per docs/plan/07-rag-generation.md.
    entry = AuditLogEntry(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(UTC).isoformat(),
        user_id=user_id,
        question=question,
        masking_triggered=masking_triggered,
    )
    _audit_log.setdefault(tenant_id, []).append(entry)


@router.get("/audit-log", response_model=list[AuditLogEntry])
async def list_audit_log(
    tenant: TenantContext = Depends(get_current_tenant),
) -> list[AuditLogEntry]:
    return _audit_log.get(tenant.tenant_id, [])
