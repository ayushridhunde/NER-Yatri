from typing import Optional
from fastapi import APIRouter, Query
from backend.weather.weather_service import weather_service
from backend.models.schemas import WeatherResponse

router = APIRouter(prefix="/api/weather", tags=["Weather Intelligence"])


@router.get("", response_model=WeatherResponse)
def get_weather(
    lat: float = Query(25.5788, description="Latitude (default: Shillong)"),
    lon: float = Query(91.8933, description="Longitude (default: Shillong)")
):
    """Retrieve normalized meteorological observations with caching and offline fallback."""
    data = weather_service.get_weather(lat, lon)
    return data


@router.get("/regional")
def get_regional_weather_summary():
    """Retrieve weather snapshots for key transportation hubs across Northeast India."""
    hubs = [
        {"name": "Guwahati (Assam Hub)", "lat": 26.1445, "lon": 91.7362},
        {"name": "Shillong (Meghalaya Gateway)", "lat": 25.5788, "lon": 91.8933},
        {"name": "Gangtok (Sikkim Corridor)", "lat": 27.3389, "lon": 88.6065},
        {"name": "Silchar (Barak Valley Link)", "lat": 24.8333, "lon": 92.8012},
        {"name": "Itanagar (Arunachal Pass)", "lat": 27.1023, "lon": 93.6920},
        {"name": "Kohima (Nagaland Highway)", "lat": 25.6751, "lon": 94.1086}
    ]

    results = []
    for h in hubs:
        w = weather_service.get_weather(h["lat"], h["lon"])
        results.append({
            "hub": h["name"],
            "temperature_c": w["temperature_c"],
            "rainfall_24h_mm": w["rainfall_24h"],
            "soil_moisture": w["soil_moisture"],
            "status": "CAUTION (High Rain)" if w["rainfall_24h"] > 70.0 else "NORMAL",
            "last_updated": w["last_updated"]
        })

    return results
