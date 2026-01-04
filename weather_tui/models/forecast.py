"""Data classes for weather forecast data."""

from dataclasses import dataclass, field
from datetime import datetime

# Mapping of Open-Meteo weather codes to emoji icons
WEATHER_CODE_EMOJI = {
    0: "☀️",  # Clear sky
    1: "🌤️",  # Mainly clear
    2: "⛅",  # Partly cloudy
    3: "☁️",  # Overcast
    45: "🌫️",  # Fog
    48: "🌫️",  # Depositing rime fog
    51: "🌧️",  # Drizzle: Light
    53: "🌧️",  # Drizzle: Moderate
    55: "🌧️",  # Drizzle: Dense
    61: "🌧️",  # Rain: Slight
    63: "🌧️",  # Rain: Moderate
    65: "🌧️",  # Rain: Heavy
    71: "🌨️",  # Snow: Slight
    73: "🌨️",  # Snow: Moderate
    75: "🌨️",  # Snow: Heavy
    77: "🌨️",  # Snow grains
    80: "🌦️",  # Rain showers: Slight
    81: "🌦️",  # Rain showers: Moderate
    82: "⛈️",  # Rain showers: Violent
    95: "⛈️",  # Thunderstorm
    96: "⛈️",  # Thunderstorm with slight hail
    99: "⛈️",  # Thunderstorm with heavy hail
}

WEATHER_CODE_DESCRIPTION = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Moderate showers",
    82: "Violent showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm",
}


def get_weather_emoji(code: int | None) -> str:
    """Get emoji for weather code."""
    if code is None:
        return "❓"
    return WEATHER_CODE_EMOJI.get(code, "❓")


def get_weather_description(code: int | None) -> str:
    """Get description for weather code."""
    if code is None:
        return "Unknown"
    return WEATHER_CODE_DESCRIPTION.get(code, f"Code {code}")


@dataclass
class CurrentWeather:
    """Current weather conditions."""

    temperature: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    weather_code: int | None = None

    @property
    def emoji(self) -> str:
        return get_weather_emoji(self.weather_code)

    @property
    def description(self) -> str:
        return get_weather_description(self.weather_code)


@dataclass
class HourlyForecast:
    """Single hour forecast data."""

    time: datetime
    temperature: float | None = None
    precipitation: float | None = None
    wind_speed: float | None = None


@dataclass
class DailyForecast:
    """Single day forecast data."""

    date: datetime
    temp_max: float | None = None
    temp_min: float | None = None
    precipitation_sum: float | None = None
    weather_code: int | None = None

    @property
    def emoji(self) -> str:
        return get_weather_emoji(self.weather_code)

    @property
    def description(self) -> str:
        return get_weather_description(self.weather_code)


@dataclass
class WeatherData:
    """Complete weather data for a location."""

    location_name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = "UTC"
    current: CurrentWeather | None = None
    hourly: list[HourlyForecast] = field(default_factory=list)
    daily: list[DailyForecast] = field(default_factory=list)

    def get_today_hourly(self) -> list[HourlyForecast]:
        """Get hourly forecasts for today only."""
        if not self.hourly:
            return []
        today = datetime.now().date()
        return [h for h in self.hourly if h.time.date() == today]
