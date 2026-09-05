from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.models.models import Road, User
from backend.models.schemas import RoadResponse
from backend.authentication.security import require_roles

router = APIRouter(prefix="/api/roads", tags=["Roads & Logistics"])


@router.get("", response_model=List[RoadResponse])
def get_roads(
    status: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Road)
    if status and status != "ALL":
        query = query.filter(Road.status == status)
    if state and state != "ALL":
        query = query.filter(Road.state == state)
    return query.all()


@router.get("/{road_id}", response_model=RoadResponse)
def get_road_by_id(road_id: int, db: Session = Depends(get_db)):
    road = db.query(Road).filter(Road.id == road_id).first()
    if not road:
        raise HTTPException(status_code=404, detail="Road segment not found.")
    return road


@router.patch("/{road_id}", response_model=RoadResponse)
def update_road_status(
    road_id: int,
    status: str = Body(..., embed=True),
    accessibility_score: Optional[float] = Body(None, embed=True),
    estimated_delay: Optional[int] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["GOVERNMENT_ADMIN", "GOVERNMENT_OPERATOR"]))
):
    """Authority endpoint to update road accessibility status (OPEN, CAUTION, HIGH RISK, BLOCKED)."""
    road = db.query(Road).filter(Road.id == road_id).first()
    if not road:
        raise HTTPException(status_code=404, detail="Road segment not found.")

    road.status = status.upper()
    if accessibility_score is not None:
        road.accessibility_score = accessibility_score
    else:
        # Default auto-adjust score based on status
        if road.status == "OPEN":
            road.accessibility_score = 95.0
        elif road.status == "CAUTION":
            road.accessibility_score = 65.0
        elif road.status == "HIGH RISK":
            road.accessibility_score = 35.0
        elif road.status == "BLOCKED":
            road.accessibility_score = 5.0

    if estimated_delay is not None:
        road.estimated_delay = estimated_delay

    db.commit()
    db.refresh(road)
    return road
