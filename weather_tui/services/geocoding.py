"""OpenWeatherMap Geocoding service.

Adapted from lat-long-mcp-server.
"""

import os
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.openweathermap.org/geo/1.0"


class GeocodingError(Exception):
    """Error during geocoding."""

    pass


@dataclass
class GeoLocation:
    """Geocoded location result."""

    name: str
    country: str
    state: str | None
    latitude: float
    longitude: float

    @property
    def display_name(self) -> str:
        """Get display name with country/state."""
        parts = [self.name]
        if self.state:
            parts.append(self.state)
        parts.append(self.country)
        return ", ".join(parts)


def _get_api_key() -> str:
    """Get OpenWeatherMap API key from environment."""
    key = os.environ.get("OPENWEATHERMAP_API_KEY")
    if not key:
        raise GeocodingError(
            "OPENWEATHERMAP_API_KEY environment variable is required for geocoding."
        )
    return key


async def geocode_location(
    query: str, limit: int = 1, country_code: str | None = None
) -> list[GeoLocation]:
    """Resolve a place name to latitude/longitude.

    Args:
        query: Place name to search for
        limit: Maximum number of results (1-5)
        country_code: Optional ISO 3166-1 alpha-2 country code

    Returns:
        List of GeoLocation results

    Raises:
        GeocodingError: If geocoding fails
    """
    key = _get_api_key()
    limit = max(1, min(limit, 5))

    q = query.strip()
    if country_code:
        q = f"{q},{country_code.strip()}"

    url = f"{API_BASE}/direct"
    params = {"q": q, "limit": limit, "appid": key}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise GeocodingError(f"Geocoding API error: {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise GeocodingError(f"Geocoding request failed: {e}") from e

    if not data:
        raise GeocodingError(f"No locations found for '{query}'")

    results = []
    for item in data:
        results.append(
            GeoLocation(
                name=item.get("name", "Unknown"),
                country=item.get("country", ""),
                state=item.get("state"),
                latitude=item.get("lat", 0.0),
                longitude=item.get("lon", 0.0),
            )
        )

    return results
