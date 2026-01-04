"""Tests for weather service."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from weather_tui.services.weather import (
    WeatherError,
    _parse_current,
    _parse_daily,
    _parse_hourly,
    fetch_weather,
)


class FakeVariable:
    """Fake variable for testing."""

    def __init__(self, variable_type, value, aggregation=None):
        self._variable = variable_type
        self._value = value
        self._aggregation = aggregation

    def Variable(self):
        return self._variable

    def Value(self):
        return self._value

    def Aggregation(self):
        return self._aggregation

    def ValuesAsNumpy(self):
        import numpy as np

        if isinstance(self._value, list):
            return np.array(self._value)
        return np.array([self._value])


class FakeCurrent:
    """Fake current weather response."""

    def __init__(self, variables):
        self._variables = variables

    def VariablesLength(self):
        return len(self._variables)

    def Variables(self, i):
        return self._variables[i]


class FakeHourly:
    """Fake hourly response."""

    def __init__(self, variables, time=0, interval=3600):
        self._variables = variables
        self._time = time
        self._interval = interval

    def VariablesLength(self):
        return len(self._variables)

    def Variables(self, i):
        return self._variables[i]

    def Time(self):
        return self._time

    def Interval(self):
        return self._interval


class FakeDaily:
    """Fake daily response."""

    def __init__(self, variables, time=0, interval=86400):
        self._variables = variables
        self._time = time
        self._interval = interval

    def VariablesLength(self):
        return len(self._variables)

    def Variables(self, i):
        return self._variables[i]

    def Time(self):
        return self._time

    def Interval(self):
        return self._interval


class FakeResponse:
    """Fake API response."""

    def __init__(self, current=None, hourly=None, daily=None, timezone=b"UTC"):
        self._current = current
        self._hourly = hourly
        self._daily = daily
        self._timezone = timezone

    def Current(self):
        return self._current

    def Hourly(self):
        return self._hourly

    def Daily(self):
        return self._daily

    def Timezone(self):
        return self._timezone

    def UtcOffsetSeconds(self):
        return 0


class TestParseCurrent:
    """Tests for _parse_current function."""

    def test_parse_current_with_data(self):
        # Variable type constants from openmeteo_sdk
        TEMP = 47  # temperature
        WIND_SPEED = 59  # wind_speed
        WEATHER_CODE = 56  # weather_code

        current = FakeCurrent(
            [
                FakeVariable(TEMP, 20.5),
                FakeVariable(WIND_SPEED, 10.0),
                FakeVariable(WEATHER_CODE, 3),
            ]
        )
        response = FakeResponse(current=current)

        result = _parse_current(response)

        assert result is not None
        assert result.temperature == 20.5
        assert result.wind_speed == 10.0
        assert result.weather_code == 3

    def test_parse_current_empty(self):
        response = FakeResponse(current=None)
        result = _parse_current(response)
        assert result is None

    def test_parse_current_no_variables(self):
        current = FakeCurrent([])
        response = FakeResponse(current=current)
        result = _parse_current(response)
        assert result is None


class TestParseHourly:
    """Tests for _parse_hourly function."""

    def test_parse_hourly_with_data(self):
        TEMP = 47  # temperature
        PRECIP = 24  # precipitation

        hourly = FakeHourly(
            [
                FakeVariable(TEMP, [15.0, 16.0, 17.0]),
                FakeVariable(PRECIP, [0.0, 0.5, 1.0]),
            ],
            time=int(datetime(2026, 1, 4, 0, 0).timestamp()),
            interval=3600,
        )
        response = FakeResponse(hourly=hourly)

        result = _parse_hourly(response)

        assert len(result) == 3
        assert result[0].temperature == 15.0
        assert result[1].precipitation == 0.5

    def test_parse_hourly_empty(self):
        response = FakeResponse(hourly=None)
        result = _parse_hourly(response)
        assert result == []


class TestParseDaily:
    """Tests for _parse_daily function."""

    def test_parse_daily_with_data(self):
        TEMP = 47  # temperature
        PRECIP = 24  # precipitation
        WEATHER_CODE = 56  # weather_code

        daily = FakeDaily(
            [
                FakeVariable(TEMP, [20.0, 22.0], aggregation=2),  # max
                FakeVariable(TEMP, [10.0, 12.0], aggregation=1),  # min
                FakeVariable(PRECIP, [0.0, 5.0]),
                FakeVariable(WEATHER_CODE, [0, 63]),
            ],
            time=int(datetime(2026, 1, 4, 0, 0).timestamp()),
            interval=86400,
        )
        response = FakeResponse(daily=daily)

        result = _parse_daily(response)

        assert len(result) == 2
        assert result[0].temp_max == 20.0
        assert result[0].temp_min == 10.0
        assert result[1].weather_code == 63

    def test_parse_daily_empty(self):
        response = FakeResponse(daily=None)
        result = _parse_daily(response)
        assert result == []


class TestFetchWeather:
    """Tests for fetch_weather function."""

    @pytest.mark.asyncio
    async def test_fetch_weather_success(self):
        mock_response = FakeResponse(
            current=FakeCurrent([FakeVariable(0, 20.0)]),
            hourly=FakeHourly(
                [FakeVariable(0, [15.0, 16.0])],
                time=int(datetime(2026, 1, 4, 0, 0).timestamp()),
            ),
            daily=FakeDaily(
                [FakeVariable(0, [20.0], aggregation=2)],
                time=int(datetime(2026, 1, 4, 0, 0).timestamp()),
            ),
            timezone=b"Europe/Berlin",
        )

        with patch("weather_tui.services.weather.openmeteo_requests") as mock_om:
            mock_client = AsyncMock()
            mock_client.weather_api.return_value = [mock_response]
            mock_om.AsyncClient.return_value = mock_client

            result = await fetch_weather(48.137, 11.575, "Munich")

            assert result.location_name == "Munich"
            assert result.latitude == 48.137
            assert result.timezone == "Europe/Berlin"
            assert result.current is not None

    @pytest.mark.asyncio
    async def test_fetch_weather_no_response(self):
        with patch("weather_tui.services.weather.openmeteo_requests") as mock_om:
            mock_client = AsyncMock()
            mock_client.weather_api.return_value = None
            mock_om.AsyncClient.return_value = mock_client

            with pytest.raises(WeatherError) as exc_info:
                await fetch_weather(48.137, 11.575)

            assert "No weather data" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_weather_api_error(self):
        with patch("weather_tui.services.weather.openmeteo_requests") as mock_om:
            mock_client = AsyncMock()
            mock_client.weather_api.side_effect = Exception("API Error")
            mock_om.AsyncClient.return_value = mock_client

            with pytest.raises(WeatherError) as exc_info:
                await fetch_weather(48.137, 11.575)

            assert "Failed to fetch" in str(exc_info.value)
