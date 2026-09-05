from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.database import get_db, haversine_distance
from backend.models.models import RiskZone, Road
from backend.models.schemas import RiskZoneResponse
from ai.inference.inference import landslide_engine

router = APIRouter(prefix="/api/risk", tags=["Risk Intelligence"])


@router.get("", response_model=List[RiskZoneResponse])
def get_risk_zones(
    state: Optional[str] = Query(None, description="Filter by Northeast State"),
    risk_level: Optional[str] = Query(None, description="LOW, MEDIUM, HIGH, VERY HIGH"),
    search: Optional[str] = Query(None, description="Search zone name or district"),
    db: Session = Depends(get_db)
):
    query = db.query(RiskZone)
    if state and state != "All":
        query = query.filter(RiskZone.state == state)
    if risk_level and risk_level != "ALL":
        query = query.filter(RiskZone.risk_level == risk_level)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter((RiskZone.name.ilike(search_fmt)) | (RiskZone.district.ilike(search_fmt)))

    return query.all()


@router.get("/nearby")
def get_nearby_risk(
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude"),
    db: Session = Depends(get_db)
):
    """Find the closest risk zone and determine local hazard status."""
    zones = db.query(RiskZone).all()
    if not zones:
        return {
            "local_risk_level": "LOW",
            "risk_probability": 0.12,
            "prediction_window": "6–24 hours",
            "closest_zone": "General Northeast Plains",
            "distance_km": 0.0
        }

    closest = None
    min_dist = float("inf")

    for z in zones:
        # Approximate center from polygon coordinates
        geom = z.geometry or {}
        coords = geom.get("coordinates", [[]])[0]
        if coords:
            c_lon = sum([p[0] for p in coords]) / len(coords)
            c_lat = sum([p[1] for p in coords]) / len(coords)
            d = haversine_distance(lat, lon, c_lat, c_lon)
            if d < min_dist:
                min_dist = d
                closest = z

    if not closest:
        return {
            "local_risk_level": "LOW",
            "risk_probability": 0.15,
            "prediction_window": "6–24 hours",
            "closest_zone": "General Area",
            "distance_km": 0.0
        }

    # If within 25 km of high risk zone, report that risk; otherwise decay with distance
    decayed_prob = closest.risk_probability if min_dist <= 25.0 else max(closest.risk_probability * (25.0 / min_dist), 0.15)
    if decayed_prob >= 0.75:
        local_level = "VERY HIGH"
    elif decayed_prob >= 0.50:
        local_level = "HIGH"
    elif decayed_prob >= 0.25:
        local_level = "MEDIUM"
    else:
        local_level = "LOW"

    return {
        "local_risk_level": local_level,
        "risk_probability": round(decayed_prob, 3),
        "prediction_window": closest.prediction_window,
        "confidence": closest.confidence,
        "closest_zone": closest.name,
        "closest_zone_id": closest.id,
        "distance_km": round(min_dist, 1),
        "factors": closest.contributing_factors
    }


@router.get("/{zone_id}", response_model=RiskZoneResponse)
def get_risk_zone_details(zone_id: int, db: Session = Depends(get_db)):
    zone = db.query(RiskZone).filter(RiskZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Risk zone not found.")
    return zone


@router.post("/recalculate")
def recalculate_risk_all(db: Session = Depends(get_db)):
    """Trigger AI inference recalculation across all risk zones."""
    zones = db.query(RiskZone).all()
    updated = 0

    for z in zones:
        pred = landslide_engine.predict({
            "rainfall_24h": z.rainfall,
            "rainfall": z.rainfall,
            "slope": z.slope,
            "elevation": z.elevation,
            "soil_moisture": z.soil_moisture,
            "soil_type": 1,
            "geology": 0 if "Shale" in (z.geology_type or "") else 1,
            "historical_landslide_density": 0.5 if z.risk_level in ["HIGH", "VERY HIGH"] else 0.2
        })

        z.risk_probability = pred["risk_probability"]
        z.risk_level = pred["risk_level"]
        z.confidence = pred["confidence"]
        z.prediction_window = pred["prediction_window"]
        z.contributing_factors = pred["contributing_factors"]
        updated += 1

    db.commit()
    return {"message": f"Successfully recalculated risk predictions for {updated} zones using AI engine."}
