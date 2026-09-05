import math
from typing import List, Tuple, Dict, Any, Optional

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points
    on the Earth in kilometers.
    """
    R = 6371.0  # Earth's radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c


def point_in_polygon(lat: float, lon: float, polygon: List[List[float]]) -> bool:
    """
    Ray-casting algorithm to determine if a point (lat, lon) is inside a GeoJSON polygon ring.
    GeoJSON polygon coordinates are in [lon, lat] format.
    """
    inside = False
    n = len(polygon)
    if n < 3:
        return False

    p1x, p1y = polygon[0][0], polygon[0][1]  # lon, lat
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n][0], polygon[i % n][1]
        if lat > min(p1y, p2y):
            if lat <= max(p1y, p2y):
                if lon <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or lon <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def distance_point_to_linestring(lat: float, lon: float, linestring_coords: List[List[float]]) -> float:
    """
    Calculate minimum distance in kilometers from a point (lat, lon)
    to a GeoJSON LineString [[lon, lat], ...].
    """
    if not linestring_coords:
        return float('inf')

    min_dist = float('inf')
    for i in range(len(linestring_coords) - 1):
        lon1, lat1 = linestring_coords[i]
        lon2, lat2 = linestring_coords[i + 1]

        # Calculate distance to vertices
        d1 = haversine_distance(lat, lon, lat1, lon1)
        d2 = haversine_distance(lat, lon, lat2, lon2)
        min_dist = min(min_dist, d1, d2)

        # Midpoint check
        mid_lat = (lat1 + lat2) / 2.0
        mid_lon = (lon1 + lon2) / 2.0
        d_mid = haversine_distance(lat, lon, mid_lat, mid_lon)
        min_dist = min(min_dist, d_mid)

    return min_dist


def interpolate_points(coord1: List[float], coord2: List[float], max_step_km: float = 10.0) -> List[List[float]]:
    """
    Interpolate points between two coordinates [lon, lat] so long corridors
    can be sampled thoroughly against risk zones.
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    
    if dist <= max_step_km:
        return [coord1, coord2]

    num_steps = max(2, int(math.ceil(dist / max_step_km)))
    points = []
    for i in range(num_steps + 1):
        frac = i / float(num_steps)
        lon = lon1 + frac * (lon2 - lon1)
        lat = lat1 + frac * (lat2 - lat1)
        points.append([round(lon, 5), round(lat, 5)])
    return points
