"""Hourly weather graph widget using textual-plotext."""

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static
from textual_plotext import PlotextPlot

from ..models.forecast import HourlyForecast
from ..utils import temp_to_rgb


class HourlyGraphWidget(Vertical):
    """Widget displaying hourly temperature and precipitation graphs using plotext."""

    DEFAULT_CSS = """
    HourlyGraphWidget {
        height: auto;
        min-height: 16;
        padding: 0;
    }

    HourlyGraphWidget PlotextPlot {
        height: 8;
    }

    HourlyGraphWidget #temp-title, HourlyGraphWidget #precip-title {
        height: 1;
        text-style: bold;
    }
    """

    def __init__(
        self,
        hourly_data: list[HourlyForecast] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._hourly_data = hourly_data or []

    def compose(self) -> ComposeResult:
        yield Static("🌡️  Temperature (°C)", id="temp-title")
        yield PlotextPlot(id="temp-plot")
        yield Static("🌧️  Precipitation (mm)", id="precip-title")
        yield PlotextPlot(id="precip-plot")

    def on_mount(self) -> None:
        """Render initial plots."""
        self._render_plots()

    def update_data(self, hourly_data: list[HourlyForecast]) -> None:
        """Update the hourly data and refresh plots."""
        self._hourly_data = hourly_data
        self._render_plots()

    def _render_plots(self) -> None:
        """Render temperature and precipitation plots."""
        if not self._hourly_data:
            return

        self._render_temp_plot()
        self._render_precip_plot()

    def _is_today(self) -> bool:
        """Check if the hourly data is for today."""
        if not self._hourly_data:
            return False
        first_hour = self._hourly_data[0].time
        today = datetime.now().date()
        return first_hour.date() == today

    def _get_current_hour_fraction(self) -> float:
        """Get current time as hour with fraction for minute."""
        now = datetime.now()
        return now.hour + now.minute / 60.0

    def _render_temp_plot(self) -> None:
        """Render temperature line plot with temperature-based colors."""
        temp_plot = self.query_one("#temp-plot", PlotextPlot)
        plt = temp_plot.plt

        plt.clear_figure()
        plt.theme("dark")

        hours = []
        temps = []
        for h in self._hourly_data[:24]:
            hours.append(h.time.hour)
            temps.append(h.temperature if h.temperature is not None else 0)

        if temps:
            # Plot each segment with color based on temperature
            for i in range(len(hours) - 1):
                avg_temp = (temps[i] + temps[i + 1]) / 2
                color = temp_to_rgb(avg_temp)
                plt.plot(
                    [hours[i], hours[i + 1]],
                    [temps[i], temps[i + 1]],
                    marker="braille",
                    color=color,
                )

            plt.xlabel("Hour")

            # Set x ticks to show every 3 hours
            xticks = list(range(0, 24, 3))
            plt.xticks(xticks)

            # Format y-axis labels with consistent width (6 chars)
            min_temp = min(temps)
            max_temp = max(temps)
            # Create ~5 tick marks based on data range
            temp_range = max_temp - min_temp
            step = max(1.0, temp_range / 4)
            y_min = min_temp - step * 0.1
            y_max = max_temp + step * 0.1
            yticks = [y_min + i * (y_max - y_min) / 4 for i in range(5)]
            ylabels = [f"{t:6.1f}" for t in yticks]
            plt.yticks(yticks, ylabels)

            # Add current time marker if showing today
            if self._is_today():
                current_hour = self._get_current_hour_fraction()
                plt.vline(current_hour, color="white")

        temp_plot.refresh()

    def _render_precip_plot(self) -> None:
        """Render precipitation bar plot."""
        precip_plot = self.query_one("#precip-plot", PlotextPlot)
        plt = precip_plot.plt

        plt.clear_figure()
        plt.theme("dark")

        hours = []
        precs = []
        for h in self._hourly_data[:24]:
            hours.append(h.time.hour)
            precs.append(h.precipitation if h.precipitation is not None else 0)

        if precs:
            plt.bar(hours, precs, color="blue", width=0.8)
            plt.xlabel("Hour")

            # Set x ticks to show every 3 hours
            xticks = list(range(0, 24, 3))
            plt.xticks(xticks)

            # Format y-axis labels with consistent width (6 chars to match temp)
            max_prec = max(precs)
            if max_prec == 0:
                # No precipitation - just show 0.0
                yticks = [0.0]
                ylabels = [f"{0.0:6.1f}"]
            else:
                y_max = max_prec * 1.1
                yticks = [i * y_max / 4 for i in range(5)]
                ylabels = [f"{p:6.1f}" for p in yticks]
            plt.yticks(yticks, ylabels)

            # Add current time marker if showing today
            if self._is_today():
                current_hour = self._get_current_hour_fraction()
                plt.vline(current_hour, color="white")

        precip_plot.refresh()
