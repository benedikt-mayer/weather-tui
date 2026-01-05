"""Current weather summary widget."""

from datetime import datetime

from textual.widgets import Static

from ..models.forecast import DailyForecast, WeatherData
from ..utils import temp_to_color


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

        # Format current temperature with color
        if current.temperature is not None:
            temp_color = temp_to_color(current.temperature)
            temp_str = f"Temperature Now: [{temp_color}]{current.temperature:5.1f}°C[/]"
        else:
            temp_str = "Temperature: N/A"

        lines = [
            data.location_name if data.location_name else "Current Location",
            today,
            "",
            f"{current.emoji}  {current.description}",
            "",
            temp_str,
        ]

        # Add high/low from today's daily forecast
        if data.daily:
            today_daily = data.daily[0]
            if today_daily.temp_max is not None and today_daily.temp_min is not None:
                min_color = temp_to_color(today_daily.temp_min)
                max_color = temp_to_color(today_daily.temp_max)
                lines.append(
                    f"Low: [{min_color}]{today_daily.temp_min:5.1f}°C[/] / "
                    f"High: [{max_color}]{today_daily.temp_max:5.1f}°C[/]"
                )

        self.update("\n".join(lines))

    def update_for_day(
        self, day: DailyForecast, location_name: str | None = None
    ) -> None:
        """Update display for a selected day's forecast."""
        if day is None:
            return

        day_name = day.date.strftime("%A, %B %d")
        lines = [
            location_name if location_name else "Current Location",
            day_name,
            "",
            f"{day.emoji}  {day.description}",
            "",
            "",  # Empty line to match today's "Temperature:" line
        ]

        if day.temp_max is not None and day.temp_min is not None:
            min_color = temp_to_color(day.temp_min)
            max_color = temp_to_color(day.temp_max)
            lines.append(
                f"Low: [{min_color}]{day.temp_min:5.1f}°C[/] / "
                f"High: [{max_color}]{day.temp_max:5.1f}°C[/]"
            )
        elif day.temp_max is not None:
            max_color = temp_to_color(day.temp_max)
            lines.append(f"High: [{max_color}]{day.temp_max:5.1f}°C[/]")
        elif day.temp_min is not None:
            min_color = temp_to_color(day.temp_min)
            lines.append(f"Low: [{min_color}]{day.temp_min:5.1f}°C[/]")
        else:
            lines.append("Temperature: N/A")

        self.update("\n".join(lines))
