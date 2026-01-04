"""Data models for weather data."""

from .forecast import (
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    WeatherData,
)

__all__ = ["CurrentWeather", "DailyForecast", "HourlyForecast", "WeatherData"]
