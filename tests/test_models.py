"""Tests for forecast data models."""

from datetime import datetime

from weather_tui.models.forecast import (
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    WeatherData,
    get_weather_description,
    get_weather_emoji,
)


class TestWeatherCodeFunctions:
    """Tests for weather code helper functions."""

    def test_get_weather_emoji_clear(self):
        assert get_weather_emoji(0) == "☀️"

    def test_get_weather_emoji_cloudy(self):
        assert get_weather_emoji(3) == "☁️"

    def test_get_weather_emoji_rain(self):
        assert get_weather_emoji(63) == "🌧️"

    def test_get_weather_emoji_unknown(self):
        assert get_weather_emoji(None) == "❓"
        assert get_weather_emoji(999) == "❓"

    def test_get_weather_description_clear(self):
        assert get_weather_description(0) == "Clear sky"

    def test_get_weather_description_rain(self):
        assert get_weather_description(63) == "Moderate rain"

    def test_get_weather_description_unknown(self):
        assert get_weather_description(None) == "Unknown"
        assert get_weather_description(999) == "Code 999"


class TestCurrentWeather:
    """Tests for CurrentWeather dataclass."""

    def test_create_with_all_fields(self):
        weather = CurrentWeather(
            temperature=20.5,
            wind_speed=10.0,
            wind_direction=180.0,
            weather_code=0,
        )
        assert weather.temperature == 20.5
        assert weather.wind_speed == 10.0
        assert weather.wind_direction == 180.0
        assert weather.weather_code == 0

    def test_create_with_defaults(self):
        weather = CurrentWeather()
        assert weather.temperature is None
        assert weather.wind_speed is None
        assert weather.wind_direction is None
        assert weather.weather_code is None

    def test_emoji_property(self):
        weather = CurrentWeather(weather_code=0)
        assert weather.emoji == "☀️"

    def test_description_property(self):
        weather = CurrentWeather(weather_code=63)
        assert weather.description == "Moderate rain"


class TestHourlyForecast:
    """Tests for HourlyForecast dataclass."""

    def test_create_hourly(self):
        dt = datetime(2026, 1, 4, 12, 0)
        hourly = HourlyForecast(
            time=dt,
            temperature=15.0,
            precipitation=0.5,
            wind_speed=5.0,
        )
        assert hourly.time == dt
        assert hourly.temperature == 15.0
        assert hourly.precipitation == 0.5
        assert hourly.wind_speed == 5.0


class TestDailyForecast:
    """Tests for DailyForecast dataclass."""

    def test_create_daily(self):
        dt = datetime(2026, 1, 4)
        daily = DailyForecast(
            date=dt,
            temp_max=20.0,
            temp_min=10.0,
            precipitation_sum=5.0,
            weather_code=3,
        )
        assert daily.date == dt
        assert daily.temp_max == 20.0
        assert daily.temp_min == 10.0
        assert daily.precipitation_sum == 5.0
        assert daily.weather_code == 3

    def test_emoji_property(self):
        daily = DailyForecast(date=datetime.now(), weather_code=61)
        assert daily.emoji == "🌧️"

    def test_description_property(self):
        daily = DailyForecast(date=datetime.now(), weather_code=3)
        assert daily.description == "Overcast"


class TestWeatherData:
    """Tests for WeatherData dataclass."""

    def test_create_empty(self):
        data = WeatherData()
        assert data.location_name == ""
        assert data.latitude == 0.0
        assert data.longitude == 0.0
        assert data.timezone == "UTC"
        assert data.current is None
        assert data.hourly == []
        assert data.daily == []

    def test_create_with_data(self):
        data = WeatherData(
            location_name="Munich",
            latitude=48.137,
            longitude=11.575,
            timezone="Europe/Berlin",
            current=CurrentWeather(temperature=15.0),
            hourly=[HourlyForecast(time=datetime.now(), temperature=15.0)],
            daily=[DailyForecast(date=datetime.now(), temp_max=20.0)],
        )
        assert data.location_name == "Munich"
        assert data.latitude == 48.137
        assert len(data.hourly) == 1
        assert len(data.daily) == 1

    def test_get_today_hourly(self):
        today = datetime.now()
        tomorrow = datetime(today.year, today.month, today.day + 1, 12, 0)

        data = WeatherData(
            hourly=[
                HourlyForecast(
                    time=datetime(today.year, today.month, today.day, 10, 0),
                    temperature=10.0,
                ),
                HourlyForecast(
                    time=datetime(today.year, today.month, today.day, 11, 0),
                    temperature=12.0,
                ),
                HourlyForecast(time=tomorrow, temperature=15.0),
            ]
        )

        today_hourly = data.get_today_hourly()
        assert len(today_hourly) == 2
        assert all(h.time.date() == today.date() for h in today_hourly)

    def test_get_today_hourly_empty(self):
        data = WeatherData()
        assert data.get_today_hourly() == []
