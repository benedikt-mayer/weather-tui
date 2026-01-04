"""Hourly weather graph widget."""

from textual.widgets import Static

from ..models.forecast import HourlyForecast


class HourlyGraphWidget(Static):
    """Widget displaying hourly temperature and precipitation graphs."""

    DEFAULT_CSS = """
    HourlyGraphWidget {
        height: auto;
        padding: 1;
    }
    """

    def __init__(
        self,
        hourly_data: list[HourlyForecast] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._hourly_data = hourly_data or []

    def update_data(self, hourly_data: list[HourlyForecast]) -> None:
        """Update the hourly data and refresh display."""
        self._hourly_data = hourly_data
        self.update(self._render_graphs())

    def on_mount(self) -> None:
        """Render initial content."""
        self.update(self._render_graphs())

    def _render_graphs(self) -> str:
        """Render temperature and precipitation graphs."""
        if not self._hourly_data:
            return "No hourly data available"

        lines = []

        # Temperature graph
        lines.append("🌡️  Temperature (°C)")
        lines.append(self._render_temp_graph())
        lines.append("")

        # Precipitation graph
        lines.append("🌧️  Precipitation (mm)")
        lines.append(self._render_precip_graph())
        lines.append("")

        # Time axis
        lines.append(self._render_time_axis())

        return "\n".join(lines)

    def _render_temp_graph(self) -> str:
        """Render ASCII temperature line graph."""
        temps = [h.temperature for h in self._hourly_data if h.temperature is not None]
        if not temps:
            return "  No temperature data"

        min_temp = min(temps)
        max_temp = max(temps)
        temp_range = max_temp - min_temp if max_temp != min_temp else 1

        # Graph height in rows
        height = 5
        width = min(len(temps), 24)

        # Characters for line drawing
        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        # Build graph
        graph_lines = []
        for row in range(height - 1, -1, -1):
            line = "  │"
            for i in range(width):
                if i < len(temps) and temps[i] is not None:
                    # Normalize to 0-1
                    normalized = (temps[i] - min_temp) / temp_range
                    # Map to row
                    row_value = normalized * (height - 1)
                    if abs(row_value - row) < 0.5:
                        line += "●"
                    elif row_value > row:
                        char_idx = min(
                            int((row_value - row) * len(chars)), len(chars) - 1
                        )
                        line += chars[char_idx] if row < row_value else " "
                    else:
                        line += " "
                else:
                    line += " "
            graph_lines.append(line)

        # Add scale
        graph_lines[0] = f"{max_temp:4.0f}" + graph_lines[0][4:]
        graph_lines[-1] = f"{min_temp:4.0f}" + graph_lines[-1][4:]

        return "\n".join(graph_lines)

    def _render_precip_graph(self) -> str:
        """Render ASCII precipitation bar graph."""
        precs = [
            h.precipitation if h.precipitation is not None else 0
            for h in self._hourly_data
        ]
        if not precs or max(precs) == 0:
            return "  │" + "▁" * min(len(precs), 24) + "  (no precipitation)"

        max_prec = max(precs) if max(precs) > 0 else 1

        # Bar characters
        bars = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        height = 3
        width = min(len(precs), 24)

        graph_lines = []
        for row in range(height - 1, -1, -1):
            line = "  │"
            for i in range(width):
                if i < len(precs):
                    normalized = precs[i] / max_prec
                    bar_height = normalized * height
                    if bar_height > row + 0.1:
                        line += "█"
                    elif bar_height > row:
                        char_idx = int((bar_height - row) * (len(bars) - 1))
                        line += bars[char_idx]
                    else:
                        line += " "
                else:
                    line += " "
            graph_lines.append(line)

        # Add scale
        graph_lines[0] = f"{max_prec:4.1f}" + graph_lines[0][4:]

        return "\n".join(graph_lines)

    def _render_time_axis(self) -> str:
        """Render time axis labels."""
        width = min(len(self._hourly_data), 24)
        axis = "  └" + "─" * width

        # Hour labels (every 3 hours)
        labels = "   "
        for i in range(0, width, 3):
            if i < len(self._hourly_data):
                hour = self._hourly_data[i].time.hour
                labels += f"{hour:02d}" + " "
            else:
                labels += "   "

        return axis + "\n" + labels
