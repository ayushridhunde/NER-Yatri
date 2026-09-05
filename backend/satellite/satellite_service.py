import os
import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

SATELLITE_CAVEAT = (
    "Notice: Earth observation change detection represents spectral reflectance alterations "
    "between orbital passes. Absence of detected satellite change does NOT confirm absence of "
    "a landslide or road obstruction."
)


class SatelliteProvider(ABC):
    @abstractmethod
    def get_latest_observations(self, area: Optional[str] = None) -> List[Dict[str, Any]]:
        pass


class MockSatelliteProvider(SatelliteProvider):
    """
    Demonstration Earth Observation provider modeling Sentinel-2 Multispectral Instrument (MSI)
    and Sentinel-1 Synthetic Aperture Radar (SAR) ground deformation passes over the Northeast Region.
    """
    def get_latest_observations(self, area: Optional[str] = None) -> List[Dict[str, Any]]:
        now = datetime.datetime.utcnow()
        t_minus_1 = (now - datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M UTC")
        t_minus_2 = (now - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M UTC")

        observations = [
            {
                "id": 1,
                "area": "East Khasi Hills (NH-6 Slope Corridor)",
                "acquisition_time": t_minus_1,
                "source": "Sentinel-2 MSI (10m Resolution) Demonstration",
                "before_image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80",
                "after_image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80",
                "change_probability": 0.84,
                "change_type": "SLOPE_DEFORMATION_SCAR",
                "affected_area_sqm": 14200.0,
                "processing_status": "ANALYSIS_COMPLETED",
                "confidence_score": 0.86,
                "notes": "Significant optical NDVI loss and bare soil reflectance surge identified across road-cut toe.",
                "last_updated": now
            },
            {
                "id": 2,
                "area": "Sikkim Teesta Valley (NH-10 Sector)",
                "acquisition_time": t_minus_1,
                "source": "Sentinel-1 SAR Coherence Demonstration",
                "before_image_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80",
                "after_image_url": "https://images.unsplash.com/photo-1434725039720-aaad6dd32dfe?w=800&q=80",
                "change_probability": 0.76,
                "change_type": "DEBRIS_APRON_DISPLACEMENT",
                "affected_area_sqm": 8900.0,
                "processing_status": "ANALYSIS_COMPLETED",
                "confidence_score": 0.79,
                "notes": "Interferometric decorrelation indicative of active surface downslope movement.",
                "last_updated": now
            },
            {
                "id": 3,
                "area": "Dima Hasao Hill Section (Lumding-Badarpur)",
                "acquisition_time": t_minus_2,
                "source": "Sentinel-2 MSI (10m Resolution) Demonstration",
                "before_image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80",
                "after_image_url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&q=80",
                "change_probability": 0.38,
                "change_type": "SURFACE_RUNOFF_SATURATION",
                "affected_area_sqm": 3500.0,
                "processing_status": "ANALYSIS_COMPLETED",
                "confidence_score": 0.72,
                "notes": "Moderate moisture saturation index change without macroscopic debris displacement.",
                "last_updated": now
            }
        ]

        if area:
            return [o for o in observations if area.lower() in o["area"].lower()]
        return observations


class SatelliteService:
    def __init__(self):
        self.provider = MockSatelliteProvider()

    def get_observations(self, area: Optional[str] = None) -> List[Dict[str, Any]]:
        obs = self.provider.get_latest_observations(area)
        for item in obs:
            item["caveat"] = SATELLITE_CAVEAT
        return obs


satellite_service = SatelliteService()
