import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), default="CITIZEN")  # CITIZEN, DRIVER, GOVERNMENT_ADMIN, GOVERNMENT_OPERATOR
    department = Column(String(100), nullable=True)  # for govt users
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    notification_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    reports = relationship("CitizenReport", back_populates="user")
    routes = relationship("RouteRecord", back_populates="user")


class RiskZone(Base):
    __tablename__ = "risk_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)  # Assam, Meghalaya, etc.
    district = Column(String(100), nullable=True, index=True)
    geometry = Column(JSON, nullable=False)  # GeoJSON Polygon / MultiPolygon
    risk_probability = Column(Float, default=0.0)  # 0.0 - 1.0 (e.g. 0.87 for 87%)
    risk_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH, VERY HIGH
    prediction_window = Column(String(50), default="6–24 hours")
    confidence = Column(Float, default=0.85)
    rainfall = Column(Float, default=0.0)  # mm
    slope = Column(Float, default=0.0)  # degrees
    elevation = Column(Float, default=0.0)  # meters
    soil_moisture = Column(Float, default=0.0)  # index 0.0 - 1.0
    soil_type = Column(String(50), nullable=True)
    geology_type = Column(String(50), nullable=True)
    vegetation = Column(String(50), nullable=True)
    contributing_factors = Column(JSON, nullable=True)  # [{factor, impact}]
    source = Column(String(50), default="DEMO")  # DEMO, LIVE, SATELLITE_HYBRID
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    alerts = relationship("Alert", back_populates="zone")


class Road(Base):
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    road_type = Column(String(50), default="National Highway")  # NH, State Highway, District Road
    geometry = Column(JSON, nullable=False)  # GeoJSON LineString
    status = Column(String(30), default="OPEN")  # OPEN, CAUTION, HIGH RISK, BLOCKED, UNKNOWN
    accessibility_score = Column(Float, default=100.0)  # 0 - 100
    risk_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH, VERY HIGH
    risk_probability = Column(Float, default=0.0)
    estimated_delay = Column(Integer, default=0)  # minutes
    state = Column(String(50), nullable=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class HistoricalLandslide(Base):
    __tablename__ = "historical_landslides"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(150), nullable=False)
    state = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    date = Column(String(30), nullable=True)
    severity = Column(String(30), default="HIGH")
    source = Column(String(100), default="Geological Survey of India (GSI)")
    description = Column(Text, nullable=True)


class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    type = Column(String(40), nullable=False)  # LANDSLIDE, ROAD_BLOCKAGE, FLOOD, DAMAGED_ROAD, OTHER
    description = Column(Text, nullable=False)
    photo_url = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(150), nullable=True)
    status = Column(String(30), default="NEW")  # NEW, UNDER REVIEW, VERIFIED, REJECTED, RESOLVED
    severity = Column(String(30), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    verified_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="reports")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(30), default="HIGH")  # CAUTION, HIGH, VERY HIGH
    zone_id = Column(Integer, ForeignKey("risk_zones.id"), nullable=True)
    radius_km = Column(Float, default=10.0)
    created_by = Column(String(100), nullable=False)  # official user email
    status = Column(String(30), default="ACTIVE")  # ACTIVE, EXPIRED, CANCELLED
    estimated_recipients = Column(Integer, default=0)
    sent_sms_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    zone = relationship("RiskZone", back_populates="alerts")
    sms_logs = relationship("SMSLog", back_populates="alert")


class SMSLog(Base):
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    phone = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(30), default="DELIVERED")  # SENT, DELIVERED, FAILED, DEMO_SIMULATED
    provider_message_id = Column(String(100), nullable=True)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)

    alert = relationship("Alert", back_populates="sms_logs")


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rainfall = Column(Float, default=0.0)  # mm
    rainfall_1h = Column(Float, default=0.0)
    rainfall_6h = Column(Float, default=0.0)
    rainfall_12h = Column(Float, default=0.0)
    rainfall_24h = Column(Float, default=0.0)
    temperature = Column(Float, default=24.0)  # deg C
    humidity = Column(Float, default=80.0)  # %
    soil_moisture = Column(Float, default=0.6)  # 0 - 1
    wind_speed = Column(Float, default=10.0)  # km/h
    forecast_time = Column(String(50), nullable=True)
    source = Column(String(50), default="DEMO")  # DEMO, OPENMETEO, IMD
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class RouteRecord(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)
    distance = Column(Float, default=0.0)  # km
    duration = Column(Integer, default=0)  # minutes
    fuel_cost = Column(Float, default=0.0)  # INR
    toll_cost = Column(Float, default=0.0)  # INR
    risk_score = Column(Float, default=0.0)
    delay_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    route_name = Column(String(50), default="Route A")
    is_recommended = Column(Boolean, default=False)
    recommendation_reason = Column(Text, nullable=True)
    segments = Column(JSON, nullable=True)  # [{name, risk_level, delay, factor}]
    geometry_geojson = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="routes")


class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String(150), nullable=False)
    acquisition_time = Column(String(50), nullable=False)
    source = Column(String(100), default="Sentinel-2 Demonstration")
    image_reference = Column(String(100), nullable=True)
    before_image_url = Column(String(255), nullable=True)
    after_image_url = Column(String(255), nullable=True)
    change_probability = Column(Float, default=0.0)  # 0.0 - 1.0
    change_type = Column(String(50), default="SLOPE_DEFORMATION")
    affected_area_sqm = Column(Float, default=0.0)
    processing_status = Column(String(50), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(120), nullable=False)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
