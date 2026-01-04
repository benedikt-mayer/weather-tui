"""Weather TUI main application."""

import sys
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Static

from .models.forecast import WeatherData
from .services.geocoding import GeocodingError, geocode_location
from .services.weather import WeatherError, fetch_weather
from .widgets.daily_forecast import DailyForecastWidget
from .widgets.hourly_graph import HourlyGraphWidget
from .widgets.location_input import LocationInput


class CurrentWeatherWidget(Static):
    """Widget showing current weather conditions."""

    DEFAULT_CSS = """
    CurrentWeatherWidget {
        height: auto;
        padding: 1;
        background: $surface;
        border: solid $primary;
    }
    """

    def update_weather(self, data: WeatherData) -> None:
        """Update current weather display."""
        if not data.current:
            self.update("No current weather data")
            return

        current = data.current
        today = datetime.now().strftime("%A, %B %d")
        lines = [
            f"📍 {data.location_name}" if data.location_name else "📍 Current Location",
            f"📅 {today}",
            "",
            f"{current.emoji} {current.description}",
            "",
            f"🌡️  Temperature: {current.temperature:.1f}°C"
            if current.temperature
            else "🌡️  Temperature: N/A",
        ]

        if current.wind_speed is not None:
            direction = ""
            if current.wind_direction is not None:
                direction = f" at {current.wind_direction:.0f}°"
            lines.append(f"💨 Wind: {current.wind_speed:.1f} km/h{direction}")

        self.update("\n".join(lines))

    def update_for_day(self, day, location_name: str | None = None) -> None:
        """Update display for a selected day's forecast."""
        if day is None:
            return

        day_name = day.date.strftime("%A, %B %d")
        lines = [
            f"📍 {location_name}" if location_name else "📍 Current Location",
            f"📅 {day_name}",
            "",
            f"{day.emoji} {day.description}",
            "",
        ]

        if day.temp_max is not None and day.temp_min is not None:
            lines.append(f"🌡️  High: {day.temp_max:.1f}°C / Low: {day.temp_min:.1f}°C")
        elif day.temp_max is not None:
            lines.append(f"🌡️  High: {day.temp_max:.1f}°C")
        elif day.temp_min is not None:
            lines.append(f"🌡️  Low: {day.temp_min:.1f}°C")
        else:
            lines.append("🌡️  Temperature: N/A")

        if day.precipitation_sum is not None and day.precipitation_sum > 0:
            lines.append(f"🌧️  Precipitation: {day.precipitation_sum:.1f} mm")

        self.update("\n".join(lines))


class WeatherApp(App):
    """A TUI application for displaying weather forecasts."""

    TITLE = "Weather TUI"
    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        height: 1fr;
        padding: 1;
    }

    #weather-container {
        height: 1fr;
    }

    #current-weather {
        height: auto;
        margin-bottom: 1;
    }

    #hourly-section {
        height: auto;
        margin-bottom: 1;
        border: solid $primary;
        padding: 1;
    }

    #hourly-title {
        height: 1;
        padding: 0 1;
        text-style: bold;
        margin-bottom: 1;
    }

    #daily-section {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    #status {
        height: auto;
        padding: 1;
        text-align: center;
        color: $text-muted;
    }

    .loading {
        color: $warning;
    }

    .error {
        color: $error;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("l", "focus_location", "Location"),
    ]

    def __init__(self, initial_location: str | None = None) -> None:
        super().__init__()
        self._initial_location = initial_location
        self._weather_data: WeatherData | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            LocationInput(id="location-widget"),
            Static("Enter a location to get started", id="status"),
            Vertical(
                CurrentWeatherWidget(id="current-weather"),
                Container(
                    Static("📊 Hourly Forecast - Today", id="hourly-title"),
                    HourlyGraphWidget(id="hourly-graph"),
                    id="hourly-section",
                ),
                Container(DailyForecastWidget(id="daily-forecast"), id="daily-section"),
                id="weather-container",
            ),
            id="main-container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Handle app mount - load initial location if provided."""
        # Hide weather container initially
        weather_container = self.query_one("#weather-container")
        weather_container.display = False

        if self._initial_location:
            location_widget = self.query_one("#location-widget", LocationInput)
            location_widget.set_location(self._initial_location)
            await self._load_weather(self._initial_location)

    async def on_location_input_location_submitted(
        self, event: LocationInput.LocationSubmitted
    ) -> None:
        """Handle location submission."""
        await self._load_weather(event.location)

    async def _load_weather(self, location: str) -> None:
        """Load weather for a location."""
        status = self.query_one("#status", Static)
        weather_container = self.query_one("#weather-container")

        status.update(f"🔍 Searching for {location}...")
        status.add_class("loading")
        status.remove_class("error")

        try:
            # Geocode location
            locations = await geocode_location(location)
            if not locations:
                raise GeocodingError(f"Location '{location}' not found")

            geo = locations[0]
            status.update(f"🌐 Fetching weather for {geo.display_name}...")

            # Fetch weather
            self._weather_data = await fetch_weather(
                geo.latitude, geo.longitude, geo.display_name
            )

            # Update widgets
            self._update_display()

            # Show success
            status.update(f"✅ Weather loaded for {geo.display_name}")
            status.remove_class("loading")
            weather_container.display = True

        except GeocodingError as e:
            status.update(f"❌ Geocoding error: {e}")
            status.remove_class("loading")
            status.add_class("error")
            weather_container.display = False

        except WeatherError as e:
            status.update(f"❌ Weather error: {e}")
            status.remove_class("loading")
            status.add_class("error")
            weather_container.display = False

        except Exception as e:
            status.update(f"❌ Error: {e}")
            status.remove_class("loading")
            status.add_class("error")
            weather_container.display = False

    def _update_display(self) -> None:
        """Update all weather displays."""
        if not self._weather_data:
            return

        # Update current weather
        current_widget = self.query_one("#current-weather", CurrentWeatherWidget)
        current_widget.update_weather(self._weather_data)

        # Update hourly graph with today's data
        self._update_hourly_for_today()

        # Update daily forecast
        daily_widget = self.query_one("#daily-forecast", DailyForecastWidget)
        daily_widget.update_data(self._weather_data.daily)

    def _update_hourly_for_today(self) -> None:
        """Update hourly graph with today's data."""
        if not self._weather_data:
            return

        hourly_widget = self.query_one("#hourly-graph", HourlyGraphWidget)
        hourly_title = self.query_one("#hourly-title", Static)

        today_hourly = self._weather_data.get_today_hourly()
        hourly_data = today_hourly if today_hourly else self._weather_data.hourly[:24]
        hourly_widget.update_data(hourly_data)
        hourly_title.update("📊 Hourly Forecast - Today")

    def _update_hourly_for_day(self, day_date: datetime, day_index: int) -> None:
        """Update hourly graph with a specific day's data."""
        if not self._weather_data:
            return

        hourly_widget = self.query_one("#hourly-graph", HourlyGraphWidget)
        hourly_title = self.query_one("#hourly-title", Static)

        day_hourly = self._weather_data.get_hourly_for_date(day_date)

        if day_hourly:
            hourly_widget.update_data(day_hourly)
            day_name = day_date.strftime("%A, %B %d")
            hourly_title.update(f"📊 Hourly Forecast - {day_name}")
        else:
            # If no hourly data for that day, show message
            day_name = day_date.strftime("%A")
            hourly_title.update(f"📊 Hourly Forecast - {day_name} (no data)")
            hourly_widget.update_data([])

    def on_daily_forecast_widget_day_selected(
        self, event: DailyForecastWidget.DaySelected
    ) -> None:
        """Handle day selection from the daily forecast widget."""
        self._update_hourly_for_day(event.day.date, event.index)

        # Update current weather widget with the selected day's summary
        current_widget = self.query_one("#current-weather", CurrentWeatherWidget)
        if event.index == 0 and self._weather_data and self._weather_data.current:
            # For today, show current weather
            current_widget.update_weather(self._weather_data)
        else:
            # For other days, show day summary
            location = self._weather_data.location_name if self._weather_data else None
            current_widget.update_for_day(event.day, location)

    async def action_refresh(self) -> None:
        """Refresh current weather."""
        location_widget = self.query_one("#location-widget", LocationInput)
        input_widget = location_widget.query_one("#location-input")
        location = input_widget.value.strip()
        if location:
            await self._load_weather(location)

    def action_focus_location(self) -> None:
        """Focus the location input."""
        input_widget = self.query_one("#location-input")
        input_widget.focus()


def main() -> None:
    """Main entry point."""
    initial_location = sys.argv[1] if len(sys.argv) > 1 else None
    app = WeatherApp(initial_location=initial_location)
    app.run()


if __name__ == "__main__":
    main()
