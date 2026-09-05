import os
import time
import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_PROVIDER_TYPE = os.getenv("WEATHER_PROVIDER", "mock").lower()
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")


class WeatherProvider(ABC):
    @abstractmethod
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        pass


class MockWeatherProvider(WeatherProvider):
    """
    Simulates high-resolution weather observations for Northeast Indian topography.
    Calibrated against Cherrapunji/Mawsynram/Sub-Himalayan rainfall patterns.
    """
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        # Pseudo-deterministic based on coordinate hashes and current hour
        current_hour = datetime.datetime.now(datetime.timezone.utc).hour
        coord_seed = int((lat * 100 + lon * 100)) % 100

        # Areas in Meghalaya (lat ~25.5, lon ~91.8) and Sikkim (lat ~27.3, lon ~88.6) have higher monsoon showers
        is_high_monsoon_zone = (25.0 <= lat <= 26.2 and 91.0 <= lon <= 93.0) or (27.0 <= lat <= 28.0 and 88.0 <= lon <= 89.0)

        if is_high_monsoon_zone:
            base_rain = 85.0 + (coord_seed % 45)
            soil_moisture = 0.82
            temp = 21.5
            humidity = 92.0
            wind = 14.5
        else:
            base_rain = 25.0 + (coord_seed % 30)
            soil_moisture = 0.62
            temp = 26.0
            humidity = 78.0
            wind = 9.0

        return {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "location_name": "Shillong / Cherrapunji Station" if is_high_monsoon_zone else "Brahmaputra Valley Station",
            "rainfall_mm": round(base_rain, 1),
            "rainfall_1h": round(base_rain * 0.25, 1),
            "rainfall_6h": round(base_rain * 0.65, 1),
            "rainfall_12h": round(base_rain * 0.85, 1),
            "rainfall_24h": round(base_rain, 1),
            "temperature_c": round(temp, 1),
            "humidity": round(humidity, 1),
            "soil_moisture": round(soil_moisture, 2),
            "wind_speed_kmh": round(wind, 1),
            "forecast_hours": 12,
            "source": "MockWeatherProvider (Northeast Climatology)",
            "status": "Demo Mode",
            "last_updated": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        }


class OpenMeteoProvider(WeatherProvider):
    """
    Live real-time weather provider using Open-Meteo API.
    Zero-key public API for meteorological measurements.
    """
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "wind_speed_10m"],
            "hourly": ["precipitation", "soil_moisture_0_to_1cm"],
            "forecast_days": 1
        }
        resp = requests.get(WEATHER_API_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})

        rain_curr = float(current.get("rain", 0.0) or 0.0)
        temp_curr = float(current.get("temperature_2m", 22.0) or 22.0)
        humidity_curr = float(current.get("relative_humidity_2m", 80.0) or 80.0)
        wind_curr = float(current.get("wind_speed_10m", 10.0) or 10.0)

        # Sum past hours if available
        precip_list = hourly.get("precipitation", [rain_curr])
        moist_list = hourly.get("soil_moisture_0_to_1cm", [0.65])

        rain_24h = float(sum(precip_list[:24])) if precip_list else rain_curr * 10
        soil_moisture = float(moist_list[0]) if moist_list else 0.65

        return {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "rainfall_mm": round(rain_24h, 1),
            "rainfall_1h": round(rain_curr, 1),
            "rainfall_6h": round(rain_24h * 0.45, 1),
            "rainfall_12h": round(rain_24h * 0.75, 1),
            "rainfall_24h": round(rain_24h, 1),
            "temperature_c": round(temp_curr, 1),
            "humidity": round(humidity_curr, 1),
            "soil_moisture": round(min(max(soil_moisture, 0.1), 0.99), 2),
            "wind_speed_kmh": round(wind_curr, 1),
            "forecast_hours": 24,
            "source": "Open-Meteo Live API",
            "status": "Live Connected",
            "last_updated": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        }


class WeatherService:
    """
    Orchestrates weather retrieval with caching, fallback, and normalized schema.
    """
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_ttl_seconds = 600  # 10 minutes cache

    def __init__(self):
        if WEATHER_PROVIDER_TYPE == "openmeteo":
            self.provider = OpenMeteoProvider()
        else:
            self.provider = MockWeatherProvider()
        self.fallback_provider = MockWeatherProvider()

    def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
        now = time.time()

        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["timestamp"] < self._cache_ttl_seconds:
                cached_data = entry["data"].copy()
                cached_data["cached"] = True
                return cached_data

        try:
            data = self.provider.get_current_weather(lat, lon)
            self._cache[cache_key] = {"data": data, "timestamp": now}
            return data
        except Exception as err:
            print(f"Weather Provider failed ({err}). Utilizing cached/fallback observation.")
            if cache_key in self._cache:
                fallback_data = self._cache[cache_key]["data"].copy()
                fallback_data["status"] = "Cached (External API Unavailable)"
                return fallback_data

            fallback_data = self.fallback_provider.get_current_weather(lat, lon)
            fallback_data["status"] = "Fallback Observation (External API Unavailable)"
            return fallback_data


weather_service = WeatherService()
