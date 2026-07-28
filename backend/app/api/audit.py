import sqlite3
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter

from app.auth.dependencies import CurrentTenant
from app.models.schemas import AuditLogEntry
from app.storage.db import get_connection

router = APIRouter(tags=["audit"])


def _row_to_entry(row: sqlite3.Row) -> AuditLogEntry:
    return AuditLogEntry(
        id=row["id"],
        timestamp=row["timestamp"],
        user_id=row["user_id"],
        question=row["question"],
        masking_triggered=bool(row["masking_triggered"]),
    )


def log_query(tenant_id: str, user_id: str, question: str, masking_triggered: bool) -> None:
    # Deliberately logs only the question and a boolean flag — never the raw
    # retrieved chunk text or full answer, per docs/plan/07-rag-generation.md.
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_log (id, tenant_id, user_id, question, masking_triggered, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            str(uuid.uuid4()),
            tenant_id,
            user_id,
            question,
            int(masking_triggered),
            datetime.now(UTC).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


@router.get("/audit-log")
async def list_audit_log(tenant: CurrentTenant) -> list[AuditLogEntry]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM audit_log WHERE tenant_id = ? ORDER BY timestamp DESC", (tenant.tenant_id,)
    ).fetchall()
    conn.close()
    return [_row_to_entry(row) for row in rows]
