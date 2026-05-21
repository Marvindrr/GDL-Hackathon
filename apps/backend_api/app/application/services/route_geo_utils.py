import math
from geoalchemy2 import WKTElement

# aqui van utilidades para calcular distancias, offsets, etc entre puntos geograficos y rutas
EARTH_RADIUS_M = 6371000


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_M * c


def point_wkt(lon: float, lat: float):
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def linestring_wkt(points: list[dict]):
    coords = ", ".join(f"{p['lon']} {p['lat']}" for p in points)
    return WKTElement(f"LINESTRING({coords})", srid=4326)


def route_distance_m(points: list[dict]) -> float:
    total = 0.0

    for i in range(len(points) - 1):
        a = points[i]
        b = points[i + 1]
        total += haversine_m(a["lat"], a["lon"], b["lat"], b["lon"])

    return total


def offset_point_m(lat: float, lon: float, north_m: float = 0, east_m: float = 0) -> dict:
    dlat = north_m / 111_320
    dlon = east_m / (111_320 * math.cos(math.radians(lat)))

    return {
        "lat": lat + dlat,
        "lon": lon + dlon,
    }


def midpoint(a: dict, b: dict) -> dict:
    return {
        "lat": (a["lat"] + b["lat"]) / 2,
        "lon": (a["lon"] + b["lon"]) / 2,
    }


def latlon_to_xy_m(lat: float, lon: float, ref_lat: float) -> tuple[float, float]:
    x = math.radians(lon) * EARTH_RADIUS_M * math.cos(math.radians(ref_lat))
    y = math.radians(lat) * EARTH_RADIUS_M
    return x, y


def distance_point_to_segment_m(point: dict, a: dict, b: dict) -> float:
    ref_lat = point["lat"]

    px, py = latlon_to_xy_m(point["lat"], point["lon"], ref_lat)
    ax, ay = latlon_to_xy_m(a["lat"], a["lon"], ref_lat)
    bx, by = latlon_to_xy_m(b["lat"], b["lon"], ref_lat)

    dx = bx - ax
    dy = by - ay

    if dx == 0 and dy == 0:
        return math.sqrt((px - ax) ** 2 + (py - ay) ** 2)

    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))

    closest_x = ax + t * dx
    closest_y = ay + t * dy

    return math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)


def distance_point_to_route_m(point: dict, route_points: list[dict]) -> float:
    if len(route_points) == 1:
        return haversine_m(
            point["lat"],
            point["lon"],
            route_points[0]["lat"],
            route_points[0]["lon"],
        )

    distances = []

    for i in range(len(route_points) - 1):
        distances.append(
            distance_point_to_segment_m(point, route_points[i], route_points[i + 1])
        )

    return min(distances)


def route_to_geojson_feature(points: list[dict], properties: dict | None = None) -> dict:
    return {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[p["lon"], p["lat"]] for p in points],
        },
        "properties": properties or {},
    }


def point_to_geojson_feature(point: dict, properties: dict | None = None) -> dict:
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [point["lon"], point["lat"]],
        },
        "properties": properties or {},
    }