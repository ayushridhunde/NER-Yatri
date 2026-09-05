import pytest
from backend.routing.routing_service import routing_service, KNOWN_LOCATIONS, resolve_coordinates

def test_multi_criteria_routing_prefers_safety():
    """Verify that Route B (safer bypass) is prioritized over hazardous Route A."""
    res = routing_service.calculate_routes(
        source="Guwahati",
        destination="Silchar",
        source_coords=[26.1445, 91.7362],
        dest_coords=[24.8333, 92.8012]
    )

    assert "routes" in res
    routes = res["routes"]
    assert len(routes) == 3

    recommended = [r for r in routes if r["is_recommended"]]
    assert len(recommended) == 1
    best_route = recommended[0]

    # Best route must have acceptable risk and high accessibility
    assert best_route["risk_level"] in ["LOW", "MEDIUM"]
    assert best_route["accessibility_score"] > 70.0
    assert best_route["recommendation_reason"] is not None
    assert len(best_route["segments"]) > 0


def test_route_segment_inspection():
    """Verify that each route exposes segment risk factors and expected delay."""
    res = routing_service.calculate_routes("Shillong", "Silchar")
    routes = res["routes"]

    for r in routes:
        assert len(r["segments"]) > 0
        for seg in r["segments"]:
            assert "name" in seg
            assert "risk_level" in seg
            assert "expected_delay" in seg
            assert "main_factor" in seg


def test_known_locations_resolution():
    """Verify Northeast hubs resolve without requiring explicit coordinates."""
    coords_guwahati = resolve_coordinates("Guwahati, Assam")
    assert abs(coords_guwahati[0] - 26.1445) < 0.01
    assert abs(coords_guwahati[1] - 91.7362) < 0.01

    coords_gangtok = resolve_coordinates("Gangtok")
    assert abs(coords_gangtok[0] - 27.3389) < 0.01

    res = routing_service.calculate_routes("Gangtok", "Sevoke")
    assert len(res["routes"]) == 3
    assert res["routes"][0]["distance"] > 0


def test_driver_turn_by_turn_alerts():
    """Verify hazardous routes generate upcoming driver alerts for driver mode."""
    res = routing_service.calculate_routes("Guwahati", "Silchar")
    routes = res["routes"]

    # At least one hazardous route (Route A) must contain driver alerts
    high_risk_routes = [r for r in routes if r["risk_level"] == "HIGH"]
    assert len(high_risk_routes) > 0
    for hr in high_risk_routes:
        assert "turn_by_turn_alerts" in hr
        assert len(hr["turn_by_turn_alerts"]) > 0
        alert = hr["turn_by_turn_alerts"][0]
        assert "distance_ahead_km" in alert
        assert "hazard_type" in alert
        assert "advice" in alert


def test_geometry_geojson_structure():
    """Verify route geometry adheres to valid GeoJSON LineString formatting."""
    res = routing_service.calculate_routes("Guwahati", "Shillong")
    routes = res["routes"]

    for r in routes:
        geo = r["geometry"]
        assert geo["type"] == "LineString"
        assert len(geo["coordinates"]) >= 2
        for pt in geo["coordinates"]:
            assert len(pt) == 2
            # GeoJSON coordinates format: [longitude, latitude]
            lon, lat = pt
            assert 80.0 <= lon <= 100.0  # Northeast India longitude range
            assert 20.0 <= lat <= 30.0   # Northeast India latitude range