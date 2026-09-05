import datetime
from sqlalchemy.orm import Session
from backend.models.models import AuditLog


def log_action(
    db: Session,
    user_email: str,
    action: str,
    resource: str,
    details: str = "",
    ip_address: str = "127.0.0.1"
):
    """Record an audit trail event for administrative transparency."""
    try:
        log = AuditLog(
            user_email=user_email,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            timestamp=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error writing audit log: {e}")
