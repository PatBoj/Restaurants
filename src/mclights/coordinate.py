from shapely.geometry import (
    Point,
    Polygon,
    MultiPolygon,
    LineString,
    MultiLineString,
)
from geopy.geocoders import Nominatim
from loguru import logger
from tenacity import retry, stop_after_attempt


def get_xy_coordinates(
    geometry: Point | LineString | MultiLineString | Polygon | MultiPolygon | None
) -> tuple[float, float] | None:
    """Extract x and y coordinates from a Shapely geometry.

    - Point → its coordinates
    - LineString / MultiLineString → midpoint along the line
    - Polygon / MultiPolygon → centroid
    - None → None
    """
    if geometry is None:
        return None

    if isinstance(geometry, Point):
        return geometry.x, geometry.y

    if isinstance(geometry, (LineString, MultiLineString)):
        midpoint = geometry.interpolate(0.5, normalized=True)
        return midpoint.x, midpoint.y

    if isinstance(geometry, (Polygon, MultiPolygon)):
        centroid = geometry.centroid
        return centroid.x, centroid.y

    return None


def convert_to_points(
    geometry: Point | LineString | MultiLineString | Polygon | MultiPolygon | None
) -> Point | None:
    """Convert a Shapely geometry into a Point.

    - Point → unchanged
    - LineString / MultiLineString → midpoint along the line
    - Polygon / MultiPolygon → centroid
    - None → None
    """
    if geometry is None:
        return None

    if isinstance(geometry, Point):
        return geometry

    if isinstance(geometry, (LineString, MultiLineString)):
        return geometry.interpolate(0.5, normalized=True)

    if isinstance(geometry, (Polygon, MultiPolygon)):
        return geometry.centroid

    return None


@retry(stop=stop_after_attempt(6))
def get_city(point: Point, geolocator: Nominatim):
    """Get the city name from latitude and longitude using reverse geocoding."""
    location = geolocator.reverse((point.y, point.x), exactly_one=True, language="pl")
    if location:
        address = location.raw.get("address", {})
        address = (
            address.get("city") 
            or address.get("town") 
            or address.get("village")
        )
        logger.info(f"Located city: {address}")
        return address