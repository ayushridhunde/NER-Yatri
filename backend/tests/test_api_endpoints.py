import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ONLINE"
    assert "NER YATRI" in data["system"]

def test_get_risk_zones():
    resp = client.get("/api/risk")
    assert resp.status_code == 200
    zones = resp.json()
    assert len(zones) >= 5
    assert any("East Khasi Hills" in z["name"] for z in zones)

def test_nearby_risk_query():
    resp = client.get("/api/risk/nearby?lat=25.5788&lon=91.8933")
    assert resp.status_code == 200
    data = resp.json()
    assert "local_risk_level" in data
    assert "prediction_window" in data

def test_weather_endpoint():
    resp = client.get("/api/weather?lat=25.5788&lon=91.8933")
    assert resp.status_code == 200
    data = resp.json()
    assert "rainfall_mm" in data
    assert "temperature_c" in data

def test_roads_endpoint():
    resp = client.get("/api/roads")
    assert resp.status_code == 200
    roads = resp.json()
    assert len(roads) >= 3

def test_calculate_routes():
    payload = {
        "source": "Guwahati",
        "destination": "Shillong",
        "source_coords": [26.1445, 91.7362],
        "dest_coords": [25.5788, 91.8933]
    }
    resp = client.post("/api/routes/calculate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["routes"]) == 3
    assert data["routes"][0]["is_recommended"] is True
    assert data["routes"][0]["risk_level"] in ["LOW", "MEDIUM"]
    assert "segments" in data["routes"][0]

def test_dashboard_summary():
    resp = client.get("/api/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["very_high_risk"] >= 1
    assert data["affected_roads"] >= 1

def test_system_status():
    resp = client.get("/api/system/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["backend"] == "ONLINE"
    assert data["database"] == "ONLINE"
