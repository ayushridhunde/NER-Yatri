from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.models.models import RouteRecord, User
from backend.models.schemas import RouteCalculateRequest, RouteCalculateResponse
from backend.routing.routing_service import routing_service
from backend.authentication.security import get_current_user

router = APIRouter(prefix="/api/routes", tags=["Smart Logistics & Routing"])


@router.post("/calculate", response_model=RouteCalculateResponse)
def calculate_routes(
    req: RouteCalculateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Multi-criteria risk-aware routing engine.
    Compares routes by Safety, Accessibility, Time, Cost, and Distance.
    Recommends lower-risk alternatives over hazardous shortest corridors.
    """
    result = routing_service.calculate_routes(
        source=req.source,
        destination=req.destination,
        source_coords=req.source_coords,
        dest_coords=req.dest_coords,
        weights=req.weights
    )

    # Persist recommended route option for driver analytics
    if result["routes"]:
        rec = result["routes"][0]
        record = RouteRecord(
            user_id=current_user.id if current_user else None,
            source=req.source,
            destination=req.destination,
            distance=rec["distance"],
            duration=rec["duration"],
            fuel_cost=rec["fuel_cost"],
            toll_cost=rec["toll_cost"],
            risk_score=rec["risk_score"],
            delay_score=rec["expected_delay"],
            overall_score=rec["overall_score"],
            route_name=rec["route_name"],
            is_recommended=rec["is_recommended"],
            recommendation_reason=rec["recommendation_reason"],
            segments=rec["segments"],
            geometry_geojson=rec["geometry"]
        )
        db.add(record)
        db.commit()

    return result
