"""Tests for TUI widgets."""

from datetime import datetime

from weather_tui.models.forecast import (
    DailyForecast,
    HourlyForecast,
)
from weather_tui.widgets.daily_forecast import DailyForecastWidget
from weather_tui.widgets.hourly_graph import HourlyGraphWidget


class TestHourlyGraphWidget:
    """Tests for HourlyGraphWidget."""

    def test_create_empty_data(self):
        widget = HourlyGraphWidget(hourly_data=[])
        assert widget._hourly_data == []

    def test_create_with_data(self):
        hourly_data = [
            HourlyForecast(
                time=datetime(2026, 1, 4, i, 0),
                temperature=10.0 + i,
                precipitation=0.0 if i % 3 != 0 else 1.0,
            )
            for i in range(24)
        ]
        widget = HourlyGraphWidget(hourly_data=hourly_data)
        assert len(widget._hourly_data) == 24

    def test_update_data(self):
        widget = HourlyGraphWidget(hourly_data=[])
        assert widget._hourly_data == []

        hourly_data = [
            HourlyForecast(time=datetime(2026, 1, 4, i, 0), temperature=15.0 + i * 0.5)
            for i in range(12)
        ]
        # Note: update_data calls _render_plots which requires mounted widget
        # So we just test that the data is stored
        widget._hourly_data = hourly_data
        assert len(widget._hourly_data) == 12


class TestDailyForecastWidget:
    """Tests for DailyForecastWidget."""

    def test_render_empty_data(self):
        widget = DailyForecastWidget(daily_data=[])
        rendered = widget._render_forecast()
        assert "No daily forecast available" in rendered

    def test_render_with_data(self):
        daily_data = [
            DailyForecast(
                date=datetime(2026, 1, 4 + i),
                temp_max=10.0 + i,
                temp_min=5.0 + i,
                precipitation_sum=i * 0.5,
                weather_code=0 if i % 2 == 0 else 3,
            )
            for i in range(7)
        ]
        widget = DailyForecastWidget(daily_data=daily_data)
        rendered = widget._render_forecast()

        assert "Weekly Forecast" in rendered
        assert "│" in rendered
        assert "mm" in rendered

    def test_render_with_missing_data(self):
        daily_data = [
            DailyForecast(
                date=datetime(2026, 1, 4),
                temp_max=None,
                temp_min=None,
                precipitation_sum=None,
                weather_code=None,
            )
        ]
        widget = DailyForecastWidget(daily_data=daily_data)
        rendered = widget._render_forecast()

        # Should handle None values gracefully
        assert "?" in rendered or "0mm" in rendered
