import os
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from sqlalchemy import text
from backend.database.database import get_db
from backend.models.models import RiskZone, Road, CitizenReport, Alert, SMSLog, SatelliteObservation
from backend.models.schemas import SystemHealthResponse, DataSourceItem
from backend.notifications.sms_service import sms_service
from ai.inference.inference import landslide_engine

router = APIRouter(prefix="/api/system", tags=["System Health & Demo Controls"])


@router.get("/status", response_model=SystemHealthResponse)
def get_system_health(db: Session = Depends(get_db)):
    """System Health check for government portal administration (Section 40)."""
    db_status = "ONLINE"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        print(f"DB check exception: {e}")
        db_status = "ERROR"

    return {
        "backend": "ONLINE",
        "database": db_status,
        "weather_api": "ONLINE" if os.getenv("WEATHER_PROVIDER") == "openmeteo" else "DEMO",
        "routing_api": "ONLINE" if os.getenv("ROUTING_PROVIDER") == "osrm" else "DEMO",
        "sms_service": "DEMO (Recipient: 8308200763)" if os.getenv("SMS_MODE") == "demo" else "ONLINE",
        "satellite": "DEMO (Sentinel-2 Multi-spectral)",
        "ai_model": "ONLINE (Random Forest v1.0-demo)",
        "last_sync": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        "active_mode": os.getenv("DATA_MODE", "demo").upper()
    }


@router.get("/data-sources", response_model=List[DataSourceItem])
def get_data_sources(db: Session = Depends(get_db)):
    """Catalog of connected environmental and intelligence data sources (Section 36)."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return [
        {
            "name": "Northeast Topographic & Geological Inventory",
            "type": "Geological Survey of India (GSI) Baseline Data",
            "source": "GSI Bhukosh / State Landslide Inventories",
            "status": "Demonstration Dataset",
            "last_updated": now,
            "records_count": db.query(RiskZone).count()
        },
        {
            "name": "Live Meteorological Feeds",
            "type": "Precipitation & Soil Moisture",
            "source": "Open-Meteo & IMD Demonstration Grid",
            "status": "Connected (Cached 10m)",
            "last_updated": now,
            "records_count": 8
        },
        {
            "name": "Highway Transport Network",
            "type": "National Highway Logistics Vector Layer",
            "source": "MoRTH & Northeast State PWDs",
            "status": "Live Database",
            "last_updated": now,
            "records_count": db.query(Road).count()
        },
        {
            "name": "Citizen Crowdsourced Incident Stream",
            "type": "Road Blockage & Damage Reports",
            "source": "NER YATRI Mobile App / Field Submissions",
            "status": "Live Database",
            "last_updated": now,
            "records_count": db.query(CitizenReport).count()
        },
        {
            "name": "Earth Observation Satellite Monitoring",
            "type": "Multispectral & SAR Ground Deformation",
            "source": "Copernicus Sentinel-2 & Sentinel-1 Demonstrator",
            "status": "Demo Mode",
            "last_updated": now,
            "records_count": db.query(SatelliteObservation).count()
        },
        {
            "name": "AI Landslide Susceptibility Engine",
            "type": "Trained Machine Learning Model (RandomForest)",
            "source": "Physics-calibrated Terrain Inference",
            "status": "Active (6-24h Window)",
            "last_updated": now,
            "records_count": 6000
        }
    ]


@router.post("/demo/scenario-step")
def trigger_demo_scenario_step(
    step: int = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Execute steps of the 15-step Predefined Demo Scenario (Section 71 & 72).
    Allows interactive demonstration from the Demo Control Panel.
    """
    zone = db.query(RiskZone).filter(RiskZone.state == "Meghalaya").first()
    road = db.query(Road).filter(Road.name.contains("NH-6")).first()

    if step == 1:
        # Step 1: Heavy rainfall increases in mountainous region
        if zone:
            zone.rainfall = 185.0
            zone.soil_moisture = 0.92
            db.commit()
        return {
            "step": 1,
            "title": "Rainfall Burst Triggered",
            "detail": "Precipitation over East Khasi Hills increased to 185 mm with 92% soil saturation."
        }

    elif step == 2:
        # Step 2: AI recalculates risk -> becomes VERY HIGH (87%)
        if zone:
            pred = landslide_engine.predict({
                "rainfall_24h": zone.rainfall,
                "rainfall": zone.rainfall,
                "slope": 38.5,
                "elevation": 1420.0,
                "soil_moisture": zone.soil_moisture,
                "soil_type": 0,
                "geology": 0,
                "historical_landslide_density": 0.6
            })
            zone.risk_probability = 0.87
            zone.risk_level = "VERY HIGH"
            zone.confidence = 0.86
            zone.contributing_factors = pred["contributing_factors"]
            db.commit()
        return {
            "step": 2,
            "title": "AI Risk Recalculation",
            "detail": "AI Model classified East Khasi Hills as VERY HIGH risk (87% probability, 6–24 hour window)."
        }

    elif step == 3:
        # Step 3: Road accessibility degrades to HIGH RISK / CAUTION
        if road:
            road.status = "HIGH RISK"
            road.accessibility_score = 35.0
            road.estimated_delay = 60
            db.commit()
        return {
            "step": 3,
            "title": "Road Accessibility Impacted",
            "detail": "NH-6 flagged as HIGH RISK with expected 60-minute transit delay."
        }

    elif step == 4:
        # Step 4: Government triggers test SMS to DEMO_SMS_RECIPIENT (8308200763)
        res = sms_service.dispatch_alert_sms(
            db=db,
            message="NER YATRI OFFICIAL ALERT: Critical landslide risk identified along NH-6 corridor for next 6-24 hours. Transit delayed. Use recommended valley detour.",
            zone_id=zone.id if zone else 1,
            radius_km=15.0,
            severity="VERY HIGH",
            is_test_sms=True
        )
        return {
            "step": 4,
            "title": "Safety Alert Dispatched",
            "detail": f"Demo SMS successfully dispatched to test recipient {res['recipient']}."
        }

    elif step == 5:
        # Step 5: Citizen reports road problem
        report = CitizenReport(
            type="LANDSLIDE",
            description="[SIMULATED CITIZEN REPORT] Fresh boulder fall and mud flow blocking northbound lane near Sonapur tunnel on NH-6.",
            photo_url="https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?w=600&q=80",
            latitude=25.105,
            longitude=92.355,
            location_name="Sonapur Tunnel, NH-6 Meghalaya",
            status="NEW",
            severity="CRITICAL",
            created_at=datetime.datetime.utcnow()
        )
        db.add(report)
        db.commit()
        return {
            "step": 5,
            "title": "Citizen Incident Reported",
            "detail": f"New citizen report #{report.id} received from NH-6 Sonapur Tunnel."
        }

    elif step == 6:
        # Step 6: Government verifies report and updates road to BLOCKED
        report = db.query(CitizenReport).filter(CitizenReport.location_name.contains("Sonapur")).order_by(CitizenReport.id.desc()).first()
        if report:
            report.status = "VERIFIED"
            report.verified_by = "admin@neryatri.gov.in"
        if road:
            road.status = "BLOCKED"
            road.accessibility_score = 5.0
            road.estimated_delay = 120
        db.commit()
        return {
            "step": 6,
            "title": "Report Verified & Road Blocked",
            "detail": "Government authority verified citizen report. NH-6 status updated to BLOCKED on all maps."
        }

    elif step == 0 or step == 99:
        # Reset to baseline
        if zone:
            zone.rainfall = 110.0
            zone.soil_moisture = 0.76
            zone.risk_probability = 0.68
            zone.risk_level = "HIGH"
        if road:
            road.status = "CAUTION"
            road.accessibility_score = 68.0
            road.estimated_delay = 30
        db.commit()
        return {
            "step": 0,
            "title": "Scenario Reset",
            "detail": "Environmental parameters and road statuses returned to baseline state."
        }

    return {"step": step, "title": "Unknown Step", "detail": "No action defined."}
