from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import uuid
import datetime

from backend.database.database import get_db, haversine_distance
from backend.models.models import CitizenReport, Road, User
from backend.models.schemas import CitizenReportCreate, CitizenReportResponse, CitizenReportVerify
from backend.authentication.security import get_current_user, require_auth, require_roles
from backend.services.audit_service import log_action

router = APIRouter(prefix="/api/reports", tags=["Incident Reporting"])


@router.post("", response_model=CitizenReportResponse)
def submit_citizen_report(
    type: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    severity: str = Form("MEDIUM"),
    location_name: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Citizen endpoint: Report landslide, road blockage, flood, or road damage with GPS and photo.
    """
    photo_url = None
    if photo:
        os.makedirs("backend/uploads", exist_ok=True)
        file_ext = os.path.splitext(photo.filename)[1] or ".jpg"
        file_name = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join("backend", "uploads", file_name)

        contents = photo.file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        photo_url = f"/uploads/{file_name}"

    report = CitizenReport(
        user_id=current_user.id if current_user else None,
        type=type.upper(),
        description=description,
        photo_url=photo_url,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name or f"Coordinates {latitude:.3f}°N, {longitude:.3f}°E",
        status="NEW",
        severity=severity.upper(),
        created_at=datetime.datetime.utcnow()
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Log action
    user_email = current_user.email if current_user else "anonymous_citizen"
    log_action(db, user_email, "SUBMIT_REPORT", f"Report #{report.id} ({report.type})", f"Incident reported at {report.location_name}")

    return report


@router.get("", response_model=List[CitizenReportResponse])
def get_reports(
    status: Optional[str] = Query(None, description="NEW, UNDER REVIEW, VERIFIED, REJECTED, RESOLVED"),
    type: Optional[str] = Query(None, description="LANDSLIDE, ROAD_BLOCKAGE, etc."),
    verified_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(CitizenReport)
    if verified_only:
        query = query.filter(CitizenReport.status.in_(["VERIFIED", "RESOLVED"]))
    elif status and status != "ALL":
        query = query.filter(CitizenReport.status == status)

    if type and type != "ALL":
        query = query.filter(CitizenReport.type == type)

    return query.order_by(CitizenReport.created_at.desc()).all()


@router.get("/{report_id}", response_model=CitizenReportResponse)
def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    report = db.query(CitizenReport).filter(CitizenReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Incident report not found.")
    return report


@router.patch("/{report_id}/verify", response_model=CitizenReportResponse)
def verify_report(
    report_id: int,
    req: CitizenReportVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["GOVERNMENT_ADMIN", "GOVERNMENT_OPERATOR"]))
):
    """
    Government Authority endpoint: Review, verify, reject, or mark incident resolved.
    If verified with road status impact, automatically flags nearby roads to CAUTION or BLOCKED.
    """
    report = db.query(CitizenReport).filter(CitizenReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Incident report not found.")

    report.status = req.status.upper()
    report.verified_by = current_user.email

    # Optionally impact road accessibility if confirmed blockage
    if req.status.upper() == "VERIFIED" and req.road_status_impact:
        roads = db.query(Road).all()
        for road in roads:
            # Check proximity to road linestring
            geom = road.geometry or {}
            coords = geom.get("coordinates", [])
            for pt in coords:
                d = haversine_distance(report.latitude, report.longitude, pt[1], pt[0])
                if d <= 30.0:  # Within 30 km of highway segment
                    road.status = req.road_status_impact.upper()
                    if req.road_status_impact.upper() == "BLOCKED":
                        road.accessibility_score = 10.0
                        road.estimated_delay = 90
                    elif req.road_status_impact.upper() == "CAUTION":
                        road.accessibility_score = 55.0
                        road.estimated_delay = 45
                    break

    db.commit()
    db.refresh(report)

    log_action(
        db,
        current_user.email,
        "VERIFY_REPORT",
        f"Report #{report.id}",
        f"Updated status to {report.status}. Impact: {req.road_status_impact or 'None'}"
    )

    return report
