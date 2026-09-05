from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.models.schemas import SimulationRequest, SimulationResponse
from backend.services.simulation_service import simulation_service
from backend.authentication.security import require_roles
from backend.models.models import User
from backend.services.audit_service import log_action

router = APIRouter(prefix="/api/simulation", tags=["What-If Risk Simulation"])


@router.post("/run", response_model=SimulationResponse)
def run_what_if_simulation(
    req: SimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["GOVERNMENT_ADMIN", "GOVERNMENT_OPERATOR"]))
):
    """
    Run What-If landslide risk scenario simulation.
    Does NOT overwrite live database tables. Clearly marks output as SIMULATION.
    """
    result = simulation_service.run_simulation(
        db=db,
        rainfall_delta_percent=req.rainfall_delta_percent,
        rainfall_duration_hours=req.rainfall_duration_hours,
        soil_moisture_delta=req.soil_moisture_delta,
        target_zone_ids=req.target_zone_ids
    )

    log_action(
        db,
        current_user.email,
        "RUN_SIMULATION",
        "What-If Engine",
        f"Executed scenario: Rain {req.rainfall_delta_percent}%, Moisture {req.soil_moisture_delta}"
    )

    return result
