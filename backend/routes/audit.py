from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.models.models import AuditLog, User
from backend.authentication.security import require_roles

router = APIRouter(prefix="/api/audit", tags=["Audit Logs"])


@router.get("/logs")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["GOVERNMENT_ADMIN"]))
):
    """Retrieve official government actions audit trail."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    results = []
    for l in logs:
        results.append({
            "id": l.id,
            "user_email": l.user_email,
            "action": l.action,
            "resource": l.resource,
            "details": l.details,
            "ip_address": l.ip_address,
            "timestamp": l.timestamp
        })
    return results
