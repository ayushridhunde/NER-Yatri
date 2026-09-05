from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# Auth Schemas
# ==========================================

class UserRegister(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    role: str = "CITIZEN"  # CITIZEN, DRIVER, GOVERNMENT_ADMIN, GOVERNMENT_OPERATOR
    department: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# ==========================================
# Risk Zone Schemas
# ==========================================

class RiskFactor(BaseModel):
    factor: str
    impact: str  # e.g. "+++" or "++" or "+"


class RiskZoneResponse(BaseModel):
    id: int
    name: str
    state: str
    district: Optional[str]
    geometry: Dict[str, Any]
    risk_probability: float
    risk_level: str
    prediction_window: str
    confidence: float
    rainfall: float
    slope: float
    elevation: float
    soil_moisture: float
    soil_type: Optional[str]
    geology_type: Optional[str]
    vegetation: Optional[str]
    contributing_factors: Optional[List[Dict[str, str]]]
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Road Schemas
# ==========================================

class RoadResponse(BaseModel):
    id: int
    name: str
    road_type: str
    geometry: Dict[str, Any]
    status: str
    accessibility_score: float
    risk_level: str
    risk_probability: float
    estimated_delay: int
    state: Optional[str]
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Historical Landslide Schemas
# ==========================================

class HistoricalLandslideResponse(BaseModel):
    id: int
    location: str
    state: str
    latitude: float
    longitude: float
    date: Optional[str]
    severity: str
    source: str
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Citizen Report Schemas
# ==========================================

class CitizenReportCreate(BaseModel):
    type: str  # LANDSLIDE, ROAD_BLOCKAGE, FLOOD, DAMAGED_ROAD, OTHER
    description: str
    photo_url: Optional[str] = None
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    severity: str = "MEDIUM"


class CitizenReportVerify(BaseModel):
    status: str  # VERIFIED, REJECTED, RESOLVED
    verified_by: Optional[str] = None
    road_status_impact: Optional[str] = None  # If verified, optionally update road to CAUTION or BLOCKED


class CitizenReportResponse(BaseModel):
    id: int
    user_id: Optional[int]
    type: str
    description: str
    photo_url: Optional[str]
    latitude: float
    longitude: float
    location_name: Optional[str]
    status: str
    severity: str
    verified_by: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Routing Schemas
# ==========================================

class RouteSegment(BaseModel):
    name: str
    risk_level: str
    risk_probability: float
    main_factor: str
    expected_delay: int


class RouteCalculateRequest(BaseModel):
    source: str
    destination: str
    source_coords: Optional[List[float]] = None  # [lat, lon]
    dest_coords: Optional[List[float]] = None    # [lat, lon]
    weights: Optional[Dict[str, float]] = None  # custom weights


class RouteOption(BaseModel):
    id: Optional[int] = None
    route_name: str
    is_recommended: bool
    recommendation_reason: str
    distance: float
    duration: int
    fuel_cost: float
    toll_cost: float
    risk_level: str
    risk_score: float
    accessibility_score: float
    expected_delay: int
    overall_score: float
    segments: List[Dict[str, Any]]
    geometry: Dict[str, Any]


class RouteCalculateResponse(BaseModel):
    source: str
    destination: str
    routes: List[RouteOption]


# ==========================================
# Alert & SMS Schemas
# ==========================================

class AlertCreate(BaseModel):
    title: str
    message: str
    severity: str = "HIGH"
    zone_id: Optional[int] = None
    radius_km: float = 10.0


class SMSPreviewRequest(BaseModel):
    zone_id: Optional[int] = None
    radius_km: float = 10.0
    target_role: Optional[str] = "ALL"  # ALL, CITIZEN, DRIVER


class SMSPreviewResponse(BaseModel):
    estimated_recipients: int
    recipient_breakdown: Dict[str, int]
    target_zone: Optional[str]
    radius_km: float
    sample_phone: str


class SMSSendRequest(BaseModel):
    alert_id: Optional[int] = None
    zone_id: Optional[int] = None
    radius_km: float = 10.0
    message: str
    severity: str = "HIGH"
    target_role: Optional[str] = "ALL"
    is_test_sms: bool = False
    test_recipient: Optional[str] = None


class SMSSendResponse(BaseModel):
    success: bool
    message: str
    sent_count: int
    status: str
    recipient: Optional[str]
    demo_mode: bool


# ==========================================
# What-If Simulation Schemas
# ==========================================

class SimulationRequest(BaseModel):
    rainfall_delta_percent: float = 0.0      # e.g. +30% or -20%
    rainfall_duration_hours: int = 12       # 6, 12, 24
    soil_moisture_delta: float = 0.0        # e.g. +0.15
    target_zone_ids: Optional[List[int]] = None


class SimulationDistribution(BaseModel):
    low_count: int
    low_pct: float
    medium_count: int
    medium_pct: float
    high_count: int
    high_pct: float
    very_high_count: int
    very_high_pct: float


class SimulationResponse(BaseModel):
    scenario_name: str
    is_simulation: bool = True
    notice: str = "SIMULATION — NOT LIVE DATA"
    before: SimulationDistribution
    after: SimulationDistribution
    affected_zones: List[Dict[str, Any]]
    timestamp: datetime


# ==========================================
# Weather Schemas
# ==========================================

class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str]
    rainfall_mm: float
    rainfall_1h: float
    rainfall_6h: float
    rainfall_12h: float
    rainfall_24h: float
    temperature_c: float
    humidity: float
    soil_moisture: float
    wind_speed_kmh: float
    forecast_hours: int = 12
    source: str
    status: str = "Connected"
    last_updated: datetime


# ==========================================
# Satellite Schemas
# ==========================================

class SatelliteResponse(BaseModel):
    id: int
    area: str
    acquisition_time: str
    source: str
    before_image_url: Optional[str]
    after_image_url: Optional[str]
    change_probability: float
    change_type: str
    affected_area_sqm: float
    processing_status: str
    caveat: str = "Absence of detected satellite change does not confirm absence of landslide occurrence."
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Dashboard & System Health Schemas
# ==========================================

class RegionalSummaryResponse(BaseModel):
    very_high_risk: int
    high_risk: int
    medium_risk: int
    low_risk: int
    affected_roads: int
    active_alerts: int
    citizen_reports: int
    last_sync: datetime


class DataSourceItem(BaseModel):
    name: str
    type: str
    source: str
    status: str  # Connected, Demo, Live Database
    last_updated: str
    records_count: int


class SystemHealthResponse(BaseModel):
    backend: str
    database: str
    weather_api: str
    routing_api: str
    sms_service: str
    satellite: str
    ai_model: str
    last_sync: datetime
    active_mode: str
