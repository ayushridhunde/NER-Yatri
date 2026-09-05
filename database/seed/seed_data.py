import datetime
import json
from sqlalchemy.orm import Session
from backend.database.database import engine, Base, SessionLocal
from backend.models.models import (
    User, RiskZone, Road, HistoricalLandslide, CitizenReport, Alert,
    SMSLog, WeatherObservation, SatelliteObservation, AuditLog
)
from backend.authentication.security import hash_password

def seed_all_demo_data():
    """Populate database with rich, realistic demonstration data across Northeast India."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if already seeded
    if db.query(User).count() > 0:
        print("Database already contains records. Skipping initial seeding.")
        db.close()
        return

    print("Seeding NER YATRI database with Northeast Region intelligence data...")

    # ==========================================
    # 1. Users
    # ==========================================
    users = [
        User(
            name="Dr. Hemanta Barua",
            email="admin@neryatri.gov.in",
            phone="9876543200",
            password_hash=hash_password("admin123"),
            role="GOVERNMENT_ADMIN",
            department="Northeast Regional Disaster Mitigation Authority",
            latitude=26.1445,
            longitude=91.7362,
            notification_enabled=True
        ),
        User(
            name="Sunita Debbarma",
            email="operator@neryatri.gov.in",
            phone="9876543201",
            password_hash=hash_password("operator123"),
            role="GOVERNMENT_OPERATOR",
            department="Highway Emergency Traffic Command",
            latitude=26.1850,
            longitude=91.7500,
            notification_enabled=True
        ),
        User(
            name="Priya Sharma (Demo Citizen)",
            email="citizen.priya@example.com",
            phone="8308200763",  # Matches DEMO_SMS_RECIPIENT
            password_hash=hash_password("citizen123"),
            role="CITIZEN",
            latitude=25.5788,
            longitude=91.8933,  # Shillong, Meghalaya
            notification_enabled=True
        ),
        User(
            name="Tashi Norbu (Demo Driver)",
            email="driver.tashi@example.com",
            phone="9876543210",
            password_hash=hash_password("driver123"),
            role="DRIVER",
            latitude=27.3389,
            longitude=88.6065,  # Gangtok, Sikkim
            notification_enabled=True
        ),
        User(
            name="Zoramthanga Sailo",
            email="driver.zoram@example.com",
            phone="9876543211",
            password_hash=hash_password("driver123"),
            role="DRIVER",
            latitude=23.7271,
            longitude=92.7176,  # Aizawl, Mizoram
            notification_enabled=True
        ),
        User(
            name="Lobsang Dorjee",
            email="citizen.lobsang@example.com",
            phone="9876543212",
            password_hash=hash_password("citizen123"),
            role="CITIZEN",
            latitude=27.1023,
            longitude=93.6920,  # Itanagar, Arunachal Pradesh
            notification_enabled=True
        )
    ]
    db.add_all(users)
    db.commit()

    # ==========================================
    # 2. Risk Zones across 8 Northeast States
    # ==========================================
    risk_zones = [
        RiskZone(
            name="East Khasi Hills (NH-6 Meghalaya Plateau)",
            state="Meghalaya",
            district="East Khasi Hills",
            geometry={
                "type": "Polygon",
                "coordinates": [[
                    [91.82, 25.52],
                    [92.15, 25.52],
                    [92.15, 25.75],
                    [91.82, 25.75],
                    [91.82, 25.52]
                ]]
            },
            risk_probability=0.87,
            risk_level="VERY HIGH",
            prediction_window="6–24 hours",
            confidence=0.84,
            rainfall=148.0,
            slope=38.5,
            elevation=1420.0,
            soil_moisture=0.86,
            soil_type="Clayey Silt",
            geology_type="Tertiary Friable Shale & Sandstone",
            vegetation="Subtropical Pine Forest (Road Cut Exposed)",
            contributing_factors=[
                {"factor": "Torrential monsoonal rainfall (148 mm in 24h)", "impact": "+++"},
                {"factor": "Steep cut-slope along highway alignment (38.5°)", "impact": "+++"},
                {"factor": "High pore-water saturation index (86%)", "impact": "+++"},
                {"factor": "Interbedded friable shale vulnerable to toe erosion", "impact": "++"}
            ],
            source="DEMO"
        ),
        RiskZone(
            name="Teesta Basin & NH-10 Corridor",
            state="Sikkim",
            district="East Sikkim",
            geometry={
                "type": "Polygon",
                "coordinates": [[
                    [88.45, 27.15],
                    [88.75, 27.15],
                    [88.75, 27.42],
                    [88.45, 27.42],
                    [88.45, 27.15]
                ]]
            },
            risk_probability=0.74,
            risk_level="HIGH",
            prediction_window="6–24 hours",
            confidence=0.81,
            rainfall=96.0,
            slope=42.0,
            elevation=1850.0,
            soil_moisture=0.79,
            soil_type="Gravelly Colluvium",
            geology_type="Daling Group Pelitic Schist",
            vegetation="Temperate Montane Forest",
            contributing_factors=[
                {"factor": "Steep gorge slopes exceeding 40°", "impact": "+++"},
                {"factor": "Active river-bank undercut by Teesta River", "impact": "+++"},
                {"factor": "Antecedent cumulative precipitation (96 mm)", "impact": "++"}
            ],
            source="DEMO"
        ),
        RiskZone(
            name="Dima Hasao Hill Section (Jatinga Valley)",
            state="Assam",
            district="Dima Hasao",
            geometry={
                "type": "Polygon",
                "coordinates": [[
                    [92.85, 25.10],
                    [93.25, 25.10],
                    [93.25, 25.40],
                    [92.85, 25.40],
                    [92.85, 25.10]
                ]]
            },
            risk_probability=0.68,
            risk_level="HIGH",
            prediction_window="6–24 hours",
            confidence=0.79,
            rainfall=82.0,
            slope=31.0,
            elevation=750.0,
            soil_moisture=0.75,
            soil_type="Sandy Clay",
            geology_type="Disang Series Shale",
            vegetation="Dense Bamboo & Tropical Evergreen",
            contributing_factors=[
                {"factor": "Unstable mudstone and sheared shale geology", "impact": "+++"},
                {"factor": "Hill railway/highway cut destabilization", "impact": "++"},
                {"factor": "Sustained moderate rainfall (82 mm)", "impact": "++"}
            ],
            source="DEMO"
        ),
        RiskZone(
            name="Kohima Ridge & Pherima Sector (NH-29)",
            state="Nagaland",
            district="Kohima",
            geometry={
                "type": "Polygon",
                "coordinates": [[
                    [93.95, 25.55],
                    [94.25, 25.55],
                    [94.25, 25.85],
                    [93.95, 25.85],
                    [93.95, 25.55]
                ]]
            },
            risk_probability=0.62,
            risk_level="HIGH",
            prediction_window="6–24 hours",
            confidence=0.77,
            rainfall=68.0,
            slope=29.0,
            elevation=1440.0,
            soil_moisture=0.72,
            soil_type="Clay Loam",
            geology_type="Barail & Disang Flysch",
            vegetation="Subtropical Broadleaf",
            contributing_factors=[
                {"factor": "Sinking zone history along NH-29 bypass", "impact": "+++"},
                {"factor": "High soil moisture retention", "impact": "++"}
            ],
            source="DEMO"
        ),
        RiskZone(
            name="Papum Pare Foothills (NH-415)",
            state="Arunachal Pradesh",
            district="Papum Pare",
            geometry={
                "type": "Polygon",
                "coordinates": [[
                    [93.50, 27.00],
                    [93.85, 27.00],
                    [93.85, 27.25],
                    [93.50, 27.25],
                    [93.50, 27.00]
                ]]
            },
            risk_probability=0.42,
            risk_level="MEDIUM",
            prediction_window="6–24 hours",
            confidence=0.83,
            rainfall=45.0,
            slope=24.0,
            elevation=520.0,
            soil_moisture=0.64,
            soil_type="Alluvial Colluvium",
            geology_type="Siwalik Sandstone",
            vegetation="Tropical Semi-Evergreen",
            contributing_factors=[
                {"factor": "Friable Siwalik sandstone formations", "impact": "++"},
                {"factor": "Moderate continuous showers (45 mm)", "impact": "+"}
            ],
            source="DEMO"
        ),
        RiskZone(
            name="Aizawl North Hill Slopes",
            state="Mizoram",
            district="Aizawl",
            geometry={
                "type": "Polygon",
                "coordinates": [[
                    [92.65, 23.65],
                    [92.85, 23.65],
                    [92.85, 23.85],
                    [92.65, 23.85],
                    [92.65, 23.65]
                ]]
            },
            risk_probability=0.46,
            risk_level="MEDIUM",
            prediction_window="6–24 hours",
            confidence=0.80,
            rainfall=52.0,
            slope=33.0,
            elevation=1130.0,
            soil_moisture=0.67,
            soil_type="Silty Loam",
            geology_type="Surma Group Siltstone",
            vegetation="Bamboo & Secondary Regrowth",
            contributing_factors=[
                {"factor": "Steep structural dip parallel to hillside", "impact": "++"},
                {"factor": "Moderate drainage runoff saturation", "impact": "+"}
            ],
            source="DEMO"
        ),
        RiskZone(
            name="Guwahati Metro & Kamrup Valley",
            state="Assam",
            district="Kamrup Metropolitan",
            geometry={
                "type": "Polygon",
                "coordinates": [[
                    [91.60, 26.05],
                    [91.90, 26.05],
                    [91.90, 26.25],
                    [91.60, 26.25],
                    [91.60, 26.05]
                ]]
            },
            risk_probability=0.18,
            risk_level="LOW",
            prediction_window="6–24 hours",
            confidence=0.88,
            rainfall=22.0,
            slope=8.0,
            elevation=75.0,
            soil_moisture=0.48,
            soil_type="Alluvial Loam",
            geology_type="Brahmaputra Alluvium",
            vegetation="Urban & Cultivated Plains",
            contributing_factors=[
                {"factor": "Flat river plain topography (slope < 10°)", "impact": "LOW"},
                {"factor": "Engineered highway drainage system", "impact": "LOW"}
            ],
            source="DEMO"
        ),
        RiskZone(
            name="Atharamura Ridge Highway Pass",
            state="Tripura",
            district="Khowai",
            geometry={
                "type": "Polygon",
                "coordinates": [[
                    [91.65, 23.75],
                    [91.90, 23.75],
                    [91.90, 23.95],
                    [91.65, 23.95],
                    [91.65, 23.75]
                ]]
            },
            risk_probability=0.22,
            risk_level="LOW",
            prediction_window="6–24 hours",
            confidence=0.85,
            rainfall=28.0,
            slope=16.0,
            elevation=340.0,
            soil_moisture=0.52,
            soil_type="Sandy Clay",
            geology_type="Tipam Sandstone",
            vegetation="Deciduous Mixed Forest",
            contributing_factors=[
                {"factor": "Moderate gradient with stable afforestation", "impact": "LOW"}
            ],
            source="DEMO"
        )
    ]
    db.add_all(risk_zones)
    db.commit()

    # ==========================================
    # 3. Roads & Strategic Corridors
    # ==========================================
    roads = [
        Road(
            name="NH-6 (Guwahati - Shillong - Silchar Corridor)",
            road_type="National Highway",
            geometry={
                "type": "LineString",
                "coordinates": [
                    [91.7362, 26.1445],  # Guwahati
                    [91.8933, 25.5788],  # Shillong
                    [92.2045, 25.4312],  # Jowai
                    [92.8012, 24.8333]   # Silchar
                ]
            },
            status="CAUTION",
            accessibility_score=68.0,
            risk_level="HIGH",
            risk_probability=0.79,
            estimated_delay=45,
            state="Meghalaya"
        ),
        Road(
            name="NH-10 (Sevoke - Gangtok Highway)",
            road_type="National Highway",
            geometry={
                "type": "LineString",
                "coordinates": [
                    [88.4215, 26.8821],  # Sevoke
                    [88.5140, 27.0540],  # Teesta Bazar
                    [88.6065, 27.3389]   # Gangtok
                ]
            },
            status="CAUTION",
            accessibility_score=72.0,
            risk_level="HIGH",
            risk_probability=0.74,
            estimated_delay=35,
            state="Sikkim"
        ),
        Road(
            name="NH-27 (Assam East-West Highway Corridor)",
            road_type="National Highway",
            geometry={
                "type": "LineString",
                "coordinates": [
                    [89.9800, 26.4500],  # Bongaigaon
                    [91.7362, 26.1445],  # Guwahati
                    [92.8500, 26.5500],  # Nagaon
                    [94.9100, 27.4800]   # Dibrugarh
                ]
            },
            status="OPEN",
            accessibility_score=98.0,
            risk_level="LOW",
            risk_probability=0.12,
            estimated_delay=0,
            state="Assam"
        ),
        Road(
            name="NH-29 (Dimapur - Kohima Corridor)",
            road_type="National Highway",
            geometry={
                "type": "LineString",
                "coordinates": [
                    [93.7266, 25.9064],  # Dimapur
                    [93.9200, 25.7500],  # Pherima
                    [94.1086, 25.6751]   # Kohima
                ]
            },
            status="CAUTION",
            accessibility_score=74.0,
            risk_level="MEDIUM",
            risk_probability=0.58,
            estimated_delay=20,
            state="Nagaland"
        ),
        Road(
            name="NH-102 (Imphal - Moreh Border Highway)",
            road_type="National Highway",
            geometry={
                "type": "LineString",
                "coordinates": [
                    [93.9368, 24.8170],  # Imphal
                    [94.0200, 24.5000],  # Pallel
                    [94.3000, 24.2500]   # Moreh
                ]
            },
            status="OPEN",
            accessibility_score=88.0,
            risk_level="LOW",
            risk_probability=0.22,
            estimated_delay=5,
            state="Manipur"
        )
    ]
    db.add_all(roads)
    db.commit()

    # ==========================================
    # 4. Historical Landslides (GSI Records)
    # ==========================================
    history = [
        HistoricalLandslide(
            location="Sonapur Tunnel Approach, NH-6",
            state="Meghalaya",
            latitude=25.105,
            longitude=92.355,
            date="2023-06-18",
            severity="CRITICAL",
            source="Geological Survey of India (GSI) Disaster Inventory",
            description="Massive mudflow and sandstone boulder slide triggered by 220mm rainfall, completely severing Silchar connectivity for 48 hours."
        ),
        HistoricalLandslide(
            location="Birik Dara, NH-10",
            state="Sikkim",
            latitude=26.960,
            longitude=88.455,
            date="2023-10-04",
            severity="CRITICAL",
            source="GSI / Sikkim Disaster Management Authority",
            description="Catastrophic toe collapse caused by Teesta River flash flood surges; multi-segment road breach."
        ),
        HistoricalLandslide(
            location="Dima Hasao New Haflong Station Cut",
            state="Assam",
            latitude=25.160,
            longitude=93.020,
            date="2022-05-15",
            severity="HIGH",
            source="Northeast Frontier Railway (NFR) Geotechnical Division",
            description="Deep-seated translational slide across fragile shale formation engulfing 400m of permanent way."
        ),
        HistoricalLandslide(
            location="Pherima Village Bypass, NH-29",
            state="Nagaland",
            latitude=25.760,
            longitude=93.940,
            date="2024-08-30",
            severity="HIGH",
            source="Nagaland State Disaster Management Authority",
            description="Sub-surface water pore expansion causing progressive road depression and multi-vehicle trapping."
        ),
        HistoricalLandslide(
            location="Hunthar Veng Slope, Aizawl",
            state="Mizoram",
            latitude=23.750,
            longitude=92.705,
            date="2024-05-28",
            severity="HIGH",
            source="Mizoram Geology & Mineral Resources",
            description="Urban slope slumping during Cyclone Remal rainfall burst damaging outer bypass foundation."
        )
    ]
    db.add_all(history)
    db.commit()

    # ==========================================
    # 5. Citizen Reports
    # ==========================================
    reports = [
        CitizenReport(
            user_id=users[2].id,
            type="LANDSLIDE",
            description="Active mud and loose gravel rolling onto NH-6 near Mawryngkneng pass. Heavy fog and trucks backing up.",
            photo_url="https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?w=600&q=80",
            latitude=25.560,
            longitude=92.050,
            location_name="NH-6 near Mawryngkneng, Meghalaya",
            status="NEW",
            severity="HIGH"
        ),
        CitizenReport(
            user_id=users[3].id,
            type="ROAD_BLOCKAGE",
            description="Culvert overflowing with muddy debris at 29th Mile, NH-10. Only light vehicles passing intermittently.",
            photo_url="https://images.unsplash.com/photo-1517649763962-0c623266ddc0?w=600&q=80",
            latitude=27.080,
            longitude=88.520,
            location_name="29th Mile, NH-10 Sikkim Highway",
            status="VERIFIED",
            severity="MEDIUM",
            verified_by="admin@neryatri.gov.in"
        ),
        CitizenReport(
            user_id=users[4].id,
            type="FLOOD",
            description="Flash runoff across lower highway lane near Silchar bypass junction.",
            photo_url=None,
            latitude=24.840,
            longitude=92.790,
            location_name="Silchar Southern Ring Road, Assam",
            status="RESOLVED",
            severity="LOW",
            verified_by="operator@neryatri.gov.in"
        )
    ]
    db.add_all(reports)
    db.commit()

    # ==========================================
    # 6. Active Alerts
    # ==========================================
    alerts = [
        Alert(
            title="High Landslide Risk Alert — East Khasi Hills (NH-6)",
            message="NER YATRI ALERT: High landslide risk has been identified in your area for the upcoming 6–24 hour period due to heavy monsoon rainfall. Avoid non-essential travel along the NH-6 mountain pass and monitor official highway channels.",
            severity="HIGH",
            zone_id=risk_zones[0].id,
            radius_km=15.0,
            created_by="admin@neryatri.gov.in",
            status="ACTIVE",
            estimated_recipients=1240,
            sent_sms_count=1
        )
    ]
    db.add_all(alerts)
    db.commit()

    # ==========================================
    # 7. SMS Logs
    # ==========================================
    sms_logs = [
        SMSLog(
            alert_id=alerts[0].id,
            phone="8308200763",
            message=alerts[0].message,
            status="DEMO_SIMULATED",
            provider_message_id="SIM-DEMO-7721",
            sent_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
        )
    ]
    db.add_all(sms_logs)
    db.commit()

    # ==========================================
    # 8. Satellite Observations
    # ==========================================
    sat_obs = [
        SatelliteObservation(
            area="East Khasi Hills (NH-6 Slope Corridor)",
            acquisition_time="2026-09-04 06:15 UTC",
            source="Sentinel-2 MSI (10m Resolution) Demonstration",
            image_reference="S2B_MSIL2A_20260904T061519",
            before_image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80",
            after_image_url="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80",
            change_probability=0.84,
            change_type="SLOPE_DEFORMATION_SCAR",
            affected_area_sqm=14200.0,
            processing_status="ANALYSIS_COMPLETED"
        ),
        SatelliteObservation(
            area="Teesta Valley (NH-10 Sector)",
            acquisition_time="2026-09-03 12:45 UTC",
            source="Sentinel-1 SAR Coherence Demonstration",
            image_reference="S1A_IW_GRDH_1SDV_20260903",
            before_image_url="https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80",
            after_image_url="https://images.unsplash.com/photo-1434725039720-aaad6dd32dfe?w=800&q=80",
            change_probability=0.76,
            change_type="DEBRIS_APRON_DISPLACEMENT",
            affected_area_sqm=8900.0,
            processing_status="ANALYSIS_COMPLETED"
        )
    ]
    db.add_all(sat_obs)
    db.commit()

    # ==========================================
    # 9. Audit Logs
    # ==========================================
    audit = [
        AuditLog(
            user_email="admin@neryatri.gov.in",
            action="SYSTEM_INITIALIZATION",
            resource="NER_YATRI_CORE",
            details="System initialized with Northeast Regional demonstration dataset and calibrated Random Forest model.",
            ip_address="127.0.0.1"
        ),
        AuditLog(
            user_email="admin@neryatri.gov.in",
            action="ALERT_ISSUED",
            resource="Alert #1 (East Khasi Hills)",
            details="High Landslide Risk safety alert dispatched to registered recipients in 15km radius.",
            ip_address="127.0.0.1"
        )
    ]
    db.add_all(audit)
    db.commit()

    print("Initial seeding completed successfully!")
    db.close()

if __name__ == "__main__":
    seed_all_demo_data()
