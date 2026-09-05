import pytest
from backend.database.database import SessionLocal
from backend.services.simulation_service import simulation_service
from backend.models.models import RiskZone

def test_what_if_simulation_non_mutating():
    """Verify that What-If simulation recalculates distributions without mutating live data."""
    db = SessionLocal()
    try:
        # Get baseline
        zone = db.query(RiskZone).first()
        initial_prob = zone.risk_probability
        initial_rain = zone.rainfall

        # Run simulation with +50% rain
        res = simulation_service.run_simulation(
            db=db,
            rainfall_delta_percent=50.0,
            soil_moisture_delta=0.15
        )

        assert res["is_simulation"] is True
        assert "SIMULATION — NOT LIVE DATA" in res["notice"]
        assert "before" in res
        assert "after" in res

        # Verify live database object is completely unchanged!
        db.refresh(zone)
        assert zone.risk_probability == initial_prob
        assert zone.rainfall == initial_rain

        # Verify that all zones were processed in simulation
        assert len(res["affected_zones"]) == db.query(RiskZone).count()
        assert "low_count" in res["after"]
        assert "very_high_count" in res["after"]
    finally:
        db.close()
