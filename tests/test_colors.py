"""Tests for color utility functions."""

from weather_tui.utils.colors import (
    precip_to_color,
    precip_to_rgb,
    temp_to_color,
    temp_to_rgb,
)


class TestTempToRgb:
    """Tests for temp_to_rgb function."""

    def test_cold_temperature(self):
        """Cold temperature (-20°C) should be blue."""
        r, g, b = temp_to_rgb(-20.0)
        assert r == 0
        assert g == 0
        assert b == 255

    def test_mild_temperature(self):
        """Mild temperature (~10°C) should be green."""
        # 10°C is at normalized = (10 - (-20)) / (35 - (-20)) = 30/55 ≈ 0.545
        # slightly above 0.5, so mostly green
        r, g, b = temp_to_rgb(10.0)
        assert g > 200  # Should be mostly green
        assert b == 0  # No blue in green-to-red range

    def test_hot_temperature(self):
        """Hot temperature (35°C) should be red."""
        r, g, b = temp_to_rgb(35.0)
        assert r == 255
        assert g == 0
        assert b == 0

    def test_clamps_below_min(self):
        """Temperature below -20°C should clamp to blue."""
        r, g, b = temp_to_rgb(-50.0)
        assert r == 0
        assert g == 0
        assert b == 255

    def test_clamps_above_max(self):
        """Temperature above 35°C should clamp to red."""
        r, g, b = temp_to_rgb(50.0)
        assert r == 255
        assert g == 0
        assert b == 0


class TestTempToColor:
    """Tests for temp_to_color function."""

    def test_returns_hex_string(self):
        color = temp_to_color(15.0)
        assert color.startswith("#")
        assert len(color) == 7

    def test_cold_is_blue(self):
        color = temp_to_color(-20.0)
        assert color == "#0000ff"

    def test_hot_is_red(self):
        color = temp_to_color(35.0)
        assert color == "#ff0000"


class TestPrecipToRgb:
    """Tests for precip_to_rgb function."""

    def test_no_precipitation(self):
        """No precipitation should be gray."""
        r, g, b = precip_to_rgb(0.0)
        assert r == 136
        assert g == 136
        assert b == 136

    def test_heavy_precipitation(self):
        """Heavy precipitation (20mm+) should be purple/blue."""
        r, g, b = precip_to_rgb(20.0)
        assert r == 0
        assert g == 0
        assert b == 255

    def test_moderate_precipitation(self):
        """Moderate precipitation should be between gray and purple."""
        r, g, b = precip_to_rgb(10.0)
        # Halfway between gray and purple
        assert 0 < r < 136
        assert 0 < g < 136
        assert 136 < b < 255

    def test_clamps_above_max(self):
        """Precipitation above 20mm should clamp to max purple."""
        r, g, b = precip_to_rgb(50.0)
        assert r == 0
        assert g == 0
        assert b == 255


class TestPrecipToColor:
    """Tests for precip_to_color function."""

    def test_returns_hex_string(self):
        color = precip_to_color(5.0)
        assert color.startswith("#")
        assert len(color) == 7

    def test_no_precip_is_gray(self):
        color = precip_to_color(0.0)
        assert color == "#888888"

    def test_heavy_precip_is_blue(self):
        color = precip_to_color(20.0)
        assert color == "#0000ff"
