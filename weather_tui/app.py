"""Weather TUI main application."""

import sys
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static

from .models.forecast import WeatherData
from .services.geocoding import GeocodingError, geocode_location
from .services.weather import WeatherError, fetch_weather
from .widgets.daily_forecast import DailyForecastWidget
from .widgets.hourly_graph import HourlyGraphWidget


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
            data.location_name if data.location_name else "Current Location",
            today,
            "",
            current.description,
            "",
            f"Temperature: {current.temperature:5.1f}°C"
            if current.temperature is not None
            else "Temperature: N/A",
        ]

        # Add high/low from today's daily forecast
        if data.daily:
            today_daily = data.daily[0]
            if today_daily.temp_max is not None and today_daily.temp_min is not None:
                lines.append(
                    f"Low: {today_daily.temp_min:5.1f}°C / "
                    f"High: {today_daily.temp_max:5.1f}°C"
                )

        self.update("\n".join(lines))

    def update_for_day(self, day, location_name: str | None = None) -> None:
        """Update display for a selected day's forecast."""
        if day is None:
            return

        day_name = day.date.strftime("%A, %B %d")
        lines = [
            location_name if location_name else "Current Location",
            day_name,
            "",
            day.description,
            "",
            "",  # Empty line to match today's "Temperature:" line
        ]

        if day.temp_max is not None and day.temp_min is not None:
            lines.append(f"Low: {day.temp_min:5.1f}°C / High: {day.temp_max:5.1f}°C")
        elif day.temp_max is not None:
            lines.append(f"High: {day.temp_max:5.1f}°C")
        elif day.temp_min is not None:
            lines.append(f"Low: {day.temp_min:5.1f}°C")
        else:
            lines.append("Temperature: N/A")

        self.update("\n".join(lines))


class SearchScreen(Screen):
    """Screen for searching locations."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    CSS = """
    SearchScreen {
        align: center middle;
    }

    #search-container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 1 2;
        background: $surface;
    }

    #search-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #search-input {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="search-container"):
            yield Static("Enter location to search", id="search-title")
            yield Input(placeholder="City name...", id="search-input")
        yield Footer()

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#search-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search submission."""
        location = event.value.strip()
        if location:
            self.dismiss(location)

    def action_cancel(self) -> None:
        """Cancel search and return to weather screen."""
        self.dismiss(None)


class WeatherScreen(Screen):
    """Main weather display screen."""

    BINDINGS = [
        ("s", "search", "Search"),
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    #main-container {
        height: 1fr;
        padding: 0 1;
    }

    #weather-container {
        height: 1fr;
    }

    #top-row {
        height: auto;
    }

    #current-weather {
        height: auto;
        width: auto;
        min-width: 25;
        margin-right: 1;
        border: solid $primary;
        padding: 0 1;
    }

    #daily-forecast {
        height: auto;
        width: 1fr;
    }

    #hourly-section {
        height: auto;
        border: solid $primary;
        padding: 0 1;
    }

    #hourly-title {
        height: 1;
        padding: 0 1;
        text-style: bold;
    }

    #status {
        height: auto;
        padding: 0 1;
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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._weather_data: WeatherData | None = None
        self._current_location: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Press 's' to search for a location", id="status"),
            Vertical(
                Horizontal(
                    CurrentWeatherWidget(id="current-weather"),
                    DailyForecastWidget(id="daily-forecast"),
                    id="top-row",
                ),
                Container(
                    Static("Hourly Forecast - Today", id="hourly-title"),
                    HourlyGraphWidget(id="hourly-graph"),
                    id="hourly-section",
                ),
                id="weather-container",
            ),
            id="main-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Hide weather container initially."""
        weather_container = self.query_one("#weather-container")
        weather_container.display = False

    async def load_weather(self, location: str) -> None:
        """Load weather for a location."""
        self._current_location = location
        status = self.query_one("#status", Static)
        weather_container = self.query_one("#weather-container")

        status.display = True
        status.update(f"Searching for {location}...")
        status.add_class("loading")
        status.remove_class("error")

        try:
            # Geocode location
            locations = await geocode_location(location)
            if not locations:
                raise GeocodingError(f"Location '{location}' not found")

            geo = locations[0]
            status.update(f"Fetching weather for {geo.display_name}...")

            # Fetch weather
            self._weather_data = await fetch_weather(
                geo.latitude, geo.longitude, geo.display_name
            )

            # Update widgets
            self._update_display()

            # Hide status, show weather
            status.display = False
            status.remove_class("loading")
            weather_container.display = True

        except GeocodingError as e:
            status.update(f"Geocoding error: {e}")
            status.remove_class("loading")
            status.add_class("error")
            weather_container.display = False

        except WeatherError as e:
            status.update(f"Weather error: {e}")
            status.remove_class("loading")
            status.add_class("error")
            weather_container.display = False

        except Exception as e:
            status.update(f"Error: {e}")
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
        hourly_title.update("Hourly Forecast - Today")

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
            hourly_title.update(f"Hourly Forecast - {day_name}")
        else:
            day_name = day_date.strftime("%A")
            hourly_title.update(f"Hourly Forecast - {day_name} (no data)")
            hourly_widget.update_data([])

    def on_daily_forecast_widget_day_selected(
        self, event: DailyForecastWidget.DaySelected
    ) -> None:
        """Handle day selection from the daily forecast widget."""
        self._update_hourly_for_day(event.day.date, event.index)

        # Update current weather widget with the selected day's summary
        current_widget = self.query_one("#current-weather", CurrentWeatherWidget)
        if event.index == 0 and self._weather_data and self._weather_data.current:
            current_widget.update_weather(self._weather_data)
        else:
            location = self._weather_data.location_name if self._weather_data else None
            current_widget.update_for_day(event.day, location)

    def action_search(self) -> None:
        """Open search screen."""
        self.app.push_screen(SearchScreen(), self._handle_search_result)

    def _handle_search_result(self, location: str | None) -> None:
        """Handle result from search screen."""
        if location:
            self.run_worker(self.load_weather(location))

    async def action_refresh(self) -> None:
        """Refresh current weather."""
        if self._current_location:
            await self.load_weather(self._current_location)

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class WeatherApp(App):
    """A TUI application for displaying weather forecasts."""

    TITLE = "Weather TUI"
    CSS = """
    Screen {
        layout: vertical;
    }
    """

    def __init__(self, initial_location: str | None = None) -> None:
        super().__init__()
        self._initial_location = initial_location

    def on_mount(self) -> None:
        """Push the weather screen on mount."""
        weather_screen = WeatherScreen()
        self.push_screen(weather_screen)

        if self._initial_location:
            weather_screen.run_worker(
                weather_screen.load_weather(self._initial_location)
            )


def main() -> None:
    """Main entry point."""
    initial_location = sys.argv[1] if len(sys.argv) > 1 else "Munich"
    app = WeatherApp(initial_location=initial_location)
    app.run()


if __name__ == "__main__":
    main()
