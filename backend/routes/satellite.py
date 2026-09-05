from typing import Optional, List
from fastapi import APIRouter, Query
from backend.satellite.satellite_service import satellite_service
from backend.models.schemas import SatelliteResponse

router = APIRouter(prefix="/api/satellite", tags=["Satellite Change Detection"])


@router.get("/observations", response_model=List[SatelliteResponse])
def get_satellite_observations(
    area: Optional[str] = Query(None, description="Filter by area name")
):
    """
    Retrieve Earth Observation change detection records.
    Prediction is BEFORE the event. Satellite detection is post-event monitoring/confirmation.
    """
    return satellite_service.get_observations(area)
