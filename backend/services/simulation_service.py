import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models.models import RiskZone
from ai.inference.inference import landslide_engine


class SimulationService:
    def run_simulation(
        self,
        db: Session,
        rainfall_delta_percent: float = 0.0,
        rainfall_duration_hours: int = 12,
        soil_moisture_delta: float = 0.0,
        target_zone_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Execute in-memory What-If scenario simulation across Northeast risk zones.
        Explicitly does NOT persist simulated values to the database.
        """
        query = db.query(RiskZone)
        if target_zone_ids:
            query = query.filter(RiskZone.id.in_(target_zone_ids))
        zones = query.all()

        before_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "VERY HIGH": 0}
        after_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "VERY HIGH": 0}
        affected_zones = []

        total_zones = max(len(zones), 1)

        for z in zones:
            # Record baseline
            before_level = z.risk_level or "LOW"
            before_counts[before_level] = before_counts.get(before_level, 0) + 1

            # Compute simulated parameters
            base_rain = float(z.rainfall or 45.0)
            sim_rain = max(0.0, base_rain * (1.0 + rainfall_delta_percent / 100.0))

            base_moist = float(z.soil_moisture or 0.55)
            sim_moist = min(max(0.10, base_moist + soil_moisture_delta), 0.98)

            # Re-predict using AI engine
            pred = landslide_engine.predict({
                "rainfall_24h": sim_rain,
                "rainfall": sim_rain,
                "slope": float(z.slope or 28.0),
                "elevation": float(z.elevation or 900.0),
                "soil_moisture": sim_moist,
                "soil_type": 1,
                "geology": 0,
                "historical_landslide_density": 0.4
            })

            sim_level = pred["risk_level"]
            after_counts[sim_level] = after_counts.get(sim_level, 0) + 1

            affected_zones.append({
                "id": z.id,
                "name": z.name,
                "state": z.state,
                "district": z.district,
                "before": {
                    "risk_level": before_level,
                    "probability": z.risk_probability,
                    "rainfall": base_rain,
                    "soil_moisture": base_moist
                },
                "after": {
                    "risk_level": sim_level,
                    "probability": pred["risk_probability"],
                    "rainfall": round(sim_rain, 1),
                    "soil_moisture": round(sim_moist, 2),
                    "factors": pred["contributing_factors"]
                },
                "geometry": z.geometry,
                "risk_increased": pred["risk_probability"] > z.risk_probability
            })

        scenario_title = (
            f"Scenario: Rainfall {('+' if rainfall_delta_percent >= 0 else '')}{rainfall_delta_percent:.0f}%, "
            f"Soil Moisture {('+' if soil_moisture_delta >= 0 else '')}{soil_moisture_delta:.2f} ({rainfall_duration_hours}h duration)"
        )

        return {
            "scenario_name": scenario_title,
            "is_simulation": True,
            "notice": "SIMULATION — NOT LIVE DATA (Live database unchanged)",
            "before": {
                "low_count": before_counts["LOW"],
                "low_pct": round(before_counts["LOW"] / total_zones * 100, 1),
                "medium_count": before_counts["MEDIUM"],
                "medium_pct": round(before_counts["MEDIUM"] / total_zones * 100, 1),
                "high_count": before_counts["HIGH"],
                "high_pct": round(before_counts["HIGH"] / total_zones * 100, 1),
                "very_high_count": before_counts["VERY HIGH"],
                "very_high_pct": round(before_counts["VERY HIGH"] / total_zones * 100, 1),
            },
            "after": {
                "low_count": after_counts["LOW"],
                "low_pct": round(after_counts["LOW"] / total_zones * 100, 1),
                "medium_count": after_counts["MEDIUM"],
                "medium_pct": round(after_counts["MEDIUM"] / total_zones * 100, 1),
                "high_count": after_counts["HIGH"],
                "high_pct": round(after_counts["HIGH"] / total_zones * 100, 1),
                "very_high_count": after_counts["VERY HIGH"],
                "very_high_pct": round(after_counts["VERY HIGH"] / total_zones * 100, 1),
            },
            "affected_zones": affected_zones,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        }


simulation_service = SimulationService()
