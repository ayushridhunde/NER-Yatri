from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.models.models import Alert, SMSLog, User
from backend.models.schemas import SMSPreviewRequest, SMSPreviewResponse, SMSSendRequest, SMSSendResponse
from backend.notifications.sms_service import sms_service
from backend.authentication.security import require_roles
from backend.services.audit_service import log_action

router = APIRouter(prefix="/api/alerts", tags=["Government Alerts & SMS"])


@router.get("")
def list_active_alerts(db: Session = Depends(get_db)):
    """Retrieve all active official safety alerts."""
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    results = []
    for a in alerts:
        results.append({
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "severity": a.severity,
            "zone_id": a.zone_id,
            "radius_km": a.radius_km,
            "created_by": a.created_by,
            "status": a.status,
            "estimated_recipients": a.estimated_recipients,
            "sent_sms_count": a.sent_sms_count,
            "created_at": a.created_at
        })
    return results


@router.post("/preview", response_model=SMSPreviewResponse)
def preview_alert_targeting(
    req: SMSPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["GOVERNMENT_ADMIN", "GOVERNMENT_OPERATOR"]))
):
    """
    Calculate recipient counts and demographic breakdown within risk zone / radius.
    """
    preview = sms_service.preview_recipients(
        db=db,
        zone_id=req.zone_id,
        radius_km=req.radius_km,
        target_role=req.target_role
    )
    return preview


@router.post("/send", response_model=SMSSendResponse)
def dispatch_alert(
    req: SMSSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["GOVERNMENT_ADMIN", "GOVERNMENT_OPERATOR"]))
):
    """
    Official safety bulletin SMS dispatch.
    Requires Government Authority authorization.
    In DEMO mode, securely simulates and directs test SMS to DEMO_SMS_RECIPIENT (8308200763).
    """
    result = sms_service.dispatch_alert_sms(
        db=db,
        message=req.message,
        zone_id=req.zone_id,
        radius_km=req.radius_km,
        severity=req.severity,
        created_by=current_user.email,
        is_test_sms=req.is_test_sms,
        test_recipient=req.test_recipient
    )

    log_action(
        db,
        current_user.email,
        "DISPATCH_SMS_ALERT",
        f"Zone #{req.zone_id or 'General'}",
        f"Dispatched alert (Severity: {req.severity}, Sent: {result['sent_count']}) to {result['recipient']}"
    )

    return result


@router.get("/logs")
def get_sms_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["GOVERNMENT_ADMIN", "GOVERNMENT_OPERATOR"]))
):
    """Retrieve SMS delivery audit logs with masked recipient numbers."""
    logs = db.query(SMSLog).order_by(SMSLog.sent_at.desc()).limit(limit).all()
    results = []
    for l in logs:
        # Mask phone number for citizen privacy protection (Section 31 & 80)
        phone = l.phone
        masked_phone = f"+91 {phone[:3]}XXXX{phone[-2:]}" if len(phone) >= 10 else phone

        results.append({
            "id": l.id,
            "alert_id": l.alert_id,
            "phone_masked": masked_phone,
            "message": l.message,
            "status": l.status,
            "provider_message_id": l.provider_message_id,
            "sent_at": l.sent_at
        })
    return results
