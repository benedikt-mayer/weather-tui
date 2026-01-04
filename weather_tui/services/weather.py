"""Open-Meteo weather service.

Adapted from weather-mcp-server.
"""

from datetime import datetime, timezone

from openmeteo_sdk.Variable import Variable

from ..models.forecast import (
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    WeatherData,
)

try:
    import openmeteo_requests
except ImportError:
    openmeteo_requests = None  # type: ignore

OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"


class WeatherError(Exception):
    """Error fetching weather data."""

    pass


async def _make_request(latitude: float, longitude: float):
    """Make request to Open-Meteo API."""
    if openmeteo_requests is None:
        raise WeatherError("openmeteo-requests package not installed")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "weather_code",
        ],
        "hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
        "timezone": "auto",
        "forecast_days": 7,
    }

    client = openmeteo_requests.AsyncClient()
    try:
        responses = await client.weather_api(OPEN_METEO_BASE, params=params)
        if responses and len(responses) > 0:
            return responses[0]
        return None
    except Exception as e:
        raise WeatherError(f"Failed to fetch weather: {e}") from e


def _parse_current(response) -> CurrentWeather | None:
    """Parse current weather from response."""
    try:
        current = response.Current()
        if not current or current.VariablesLength() == 0:
            return None

        result = CurrentWeather()
        for i in range(current.VariablesLength()):
            var = current.Variables(i)
            v = var.Variable()
            if v == Variable.temperature:
                result.temperature = var.Value()
            elif v == Variable.wind_speed:
                result.wind_speed = var.Value()
            elif v == Variable.wind_direction:
                result.wind_direction = var.Value()
            elif v == Variable.weather_code:
                result.weather_code = int(var.Value())

        return result
    except Exception:
        return None


def _parse_hourly(response) -> list[HourlyForecast]:
    """Parse hourly forecast from response."""
    try:
        hourly = response.Hourly()
        if not hourly or hourly.VariablesLength() == 0:
            return []

        temps: list[float] = []
        precs: list[float] = []
        winds: list[float] = []

        for vi in range(hourly.VariablesLength()):
            var = hourly.Variables(vi)
            v = var.Variable()
            try:
                values = var.ValuesAsNumpy().tolist()
            except Exception:
                try:
                    values = [var.Values(i) for i in range(var.ValuesLength())]
                except Exception:
                    values = []

            if v == Variable.temperature:
                temps = values
            elif v == Variable.precipitation:
                precs = values
            elif v == Variable.wind_speed:
                winds = values

        start = hourly.Time()
        interval = hourly.Interval()
        utc_offset = getattr(response, "UtcOffsetSeconds", lambda: 0)()

        results = []
        length = max(len(temps), len(precs), len(winds))
        for i in range(length):
            ts = start + i * interval + utc_offset
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)

            results.append(
                HourlyForecast(
                    time=dt,
                    temperature=temps[i] if i < len(temps) else None,
                    precipitation=precs[i] if i < len(precs) else None,
                    wind_speed=winds[i] if i < len(winds) else None,
                )
            )

        return results
    except Exception:
        return []


def _parse_daily(response) -> list[DailyForecast]:
    """Parse daily forecast from response."""
    try:
        daily = response.Daily()
        if not daily or daily.VariablesLength() == 0:
            return []

        tmax: list[float] = []
        tmin: list[float] = []
        precip: list[float] = []
        codes: list[int] = []

        for vi in range(daily.VariablesLength()):
            var = daily.Variables(vi)
            v = var.Variable()
            agg = getattr(var, "Aggregation", lambda: None)()

            try:
                values = var.ValuesAsNumpy().tolist()
            except Exception:
                try:
                    values = [var.Values(i) for i in range(var.ValuesLength())]
                except Exception:
                    values = []

            if v == Variable.temperature:
                if agg == 2:  # max
                    tmax = values
                elif agg == 1:  # min
                    tmin = values
            elif v == Variable.precipitation:
                precip = values
            elif v == Variable.weather_code:
                codes = [int(x) for x in values]

        start = daily.Time()
        interval = daily.Interval()
        utc_offset = getattr(response, "UtcOffsetSeconds", lambda: 0)()

        results = []
        length = max(len(tmax), len(tmin), len(precip), len(codes))
        for i in range(length):
            ts = start + i * interval + utc_offset
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)

            results.append(
                DailyForecast(
                    date=dt,
                    temp_max=tmax[i] if i < len(tmax) else None,
                    temp_min=tmin[i] if i < len(tmin) else None,
                    precipitation_sum=precip[i] if i < len(precip) else None,
                    weather_code=codes[i] if i < len(codes) else None,
                )
            )

        return results
    except Exception:
        return []


async def fetch_weather(
    latitude: float, longitude: float, location_name: str = ""
) -> WeatherData:
    """Fetch weather data for a location.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        location_name: Optional display name for the location

    Returns:
        WeatherData with current, hourly, and daily forecasts

    Raises:
        WeatherError: If fetching fails
    """
    response = await _make_request(latitude, longitude)
    if response is None:
        raise WeatherError("No weather data received")

    tz = "UTC"
    try:
        tz = response.Timezone().decode() if response.Timezone() else "UTC"
    except Exception:
        pass

    return WeatherData(
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        timezone=tz,
        current=_parse_current(response),
        hourly=_parse_hourly(response),
        daily=_parse_daily(response),
    )
