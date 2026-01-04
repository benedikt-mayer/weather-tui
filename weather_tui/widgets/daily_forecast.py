"""Daily forecast widget showing multi-day forecast cards."""

from textual.widgets import Static

from ..models.forecast import DailyForecast


class DailyForecastWidget(Static):
    """Widget displaying multi-day weather forecast."""

    DEFAULT_CSS = """
    DailyForecastWidget {
        height: auto;
        padding: 1;
    }
    """

    def __init__(
        self,
        daily_data: list[DailyForecast] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._daily_data = daily_data or []

    def update_data(self, daily_data: list[DailyForecast]) -> None:
        """Update the daily data and refresh display."""
        self._daily_data = daily_data
        self.update(self._render_forecast())

    def on_mount(self) -> None:
        """Render initial content."""
        self.update(self._render_forecast())

    def _render_forecast(self) -> str:
        """Render the daily forecast cards."""
        if not self._daily_data:
            return "No daily forecast available"

        lines = []
        lines.append("📅 Weekly Forecast")
        lines.append("")

        # Render up to 7 days
        days = self._daily_data[:7]

        # Header row with day names
        header = "│"
        for day in days:
            day_name = day.date.strftime("%a")
            header += f" {day_name:^7} │"
        lines.append("┌" + "─────────┬" * (len(days) - 1) + "─────────┐")
        lines.append(header)

        # Date row
        date_row = "│"
        for day in days:
            date_str = day.date.strftime("%d/%m")
            date_row += f" {date_str:^7} │"
        lines.append(date_row)

        # Separator
        lines.append("├" + "─────────┼" * (len(days) - 1) + "─────────┤")

        # Emoji row
        emoji_row = "│"
        for day in days:
            emoji_row += f"   {day.emoji:^3}   │"
        lines.append(emoji_row)

        # Temperature row
        temp_row = "│"
        for day in days:
            max_t = f"{day.temp_max:.0f}" if day.temp_max is not None else "?"
            min_t = f"{day.temp_min:.0f}" if day.temp_min is not None else "?"
            temp_str = f"{max_t}/{min_t}°"
            temp_row += f" {temp_str:^7} │"
        lines.append(temp_row)

        # Precipitation row
        precip_row = "│"
        for day in days:
            prec = f"{day.precipitation_sum:.0f}" if day.precipitation_sum else "0"
            prec_str = f"{prec}mm"
            precip_row += f" {prec_str:^7} │"
        lines.append(precip_row)

        # Bottom border
        lines.append("└" + "─────────┴" * (len(days) - 1) + "─────────┘")

        return "\n".join(lines)
