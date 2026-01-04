"""Tests for geocoding service."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from weather_tui.services.geocoding import (
    GeocodingError,
    GeoLocation,
    geocode_location,
)


class TestGeoLocation:
    """Tests for GeoLocation dataclass."""

    def test_display_name_with_state(self):
        loc = GeoLocation(
            name="Munich",
            country="DE",
            state="Bavaria",
            latitude=48.137,
            longitude=11.575,
        )
        assert loc.display_name == "Munich, Bavaria, DE"

    def test_display_name_without_state(self):
        loc = GeoLocation(
            name="Paris",
            country="FR",
            state=None,
            latitude=48.856,
            longitude=2.352,
        )
        assert loc.display_name == "Paris, FR"


class TestGeocodeLocation:
    """Tests for geocode_location function."""

    @pytest.mark.asyncio
    async def test_geocode_success(self):
        mock_response = [
            {
                "name": "Munich",
                "country": "DE",
                "state": "Bavaria",
                "lat": 48.137,
                "lon": 11.575,
            }
        ]

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_instance.get.return_value = AsyncMock(
                    json=lambda: mock_response,
                    raise_for_status=lambda: None,
                )

                results = await geocode_location("Munich")

                assert len(results) == 1
                assert results[0].name == "Munich"
                assert results[0].latitude == 48.137
                assert results[0].longitude == 11.575

    @pytest.mark.asyncio
    async def test_geocode_no_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            # Remove the key if it exists
            import os

            if "OPENWEATHERMAP_API_KEY" in os.environ:
                del os.environ["OPENWEATHERMAP_API_KEY"]

            with pytest.raises(GeocodingError) as exc_info:
                await geocode_location("Munich")

            assert "OPENWEATHERMAP_API_KEY" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_geocode_no_results(self):
        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_instance.get.return_value = AsyncMock(
                    json=lambda: [],
                    raise_for_status=lambda: None,
                )

                with pytest.raises(GeocodingError) as exc_info:
                    await geocode_location("NonexistentPlace123")

                assert "No locations found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_geocode_http_error(self):
        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            with patch(
                "weather_tui.services.geocoding.httpx.AsyncClient"
            ) as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance

                mock_request = httpx.Request("GET", "http://test")
                mock_response = httpx.Response(401, request=mock_request)
                mock_instance.get.side_effect = httpx.HTTPStatusError(
                    "Unauthorized",
                    request=mock_request,
                    response=mock_response,
                )

                with pytest.raises(GeocodingError) as exc_info:
                    await geocode_location("Munich")

                assert "API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_geocode_with_country_code(self):
        mock_response = [
            {
                "name": "Paris",
                "country": "FR",
                "lat": 48.856,
                "lon": 2.352,
            }
        ]

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_instance.get.return_value = AsyncMock(
                    json=lambda: mock_response,
                    raise_for_status=lambda: None,
                )

                results = await geocode_location("Paris", country_code="FR")

                assert len(results) == 1
                assert results[0].country == "FR"

                # Verify the query was constructed with country code
                call_args = mock_instance.get.call_args
                assert "Paris,FR" in str(call_args)
