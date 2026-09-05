import pytest
from backend.database.database import SessionLocal, haversine_distance, point_in_polygon
from backend.notifications.sms_service import sms_service

def test_haversine_formula():
    """Check distance calculation between Guwahati and Shillong (~68 km direct)."""
    dist = haversine_distance(26.1445, 91.7362, 25.5788, 91.8933)
    assert 60.0 <= dist <= 75.0

def test_point_in_polygon_ray_casting():
    """Check ray casting polygon intersection."""
    square_polygon = [
        [91.0, 25.0],
        [92.0, 25.0],
        [92.0, 26.0],
        [91.0, 26.0],
        [91.0, 25.0]
    ]
    # Point inside (lat 25.5, lon 91.5)
    assert point_in_polygon(25.5, 91.5, square_polygon) is True
    # Point outside (lat 26.5, lon 91.5)
    assert point_in_polygon(26.5, 91.5, square_polygon) is False

def test_sms_targeting_preview():
    """Verify SMS targeting preview returns estimated recipients and masked demo recipient."""
    db = SessionLocal()
    try:
        preview = sms_service.preview_recipients(db, zone_id=1, radius_km=15.0)
        assert preview["estimated_recipients"] >= 1
        assert "citizens" in preview["recipient_breakdown"]
        assert "drivers" in preview["recipient_breakdown"]
        assert preview["sample_phone"].startswith("+91")
    finally:
        db.close()
