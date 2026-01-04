"""Hourly weather graph widget using textual-plotext."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static
from textual_plotext import PlotextPlot

from ..models.forecast import HourlyForecast


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

    def _render_temp_plot(self) -> None:
        """Render temperature line plot."""
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
            plt.plot(hours, temps, marker="braille", color="red")
            plt.xlabel("Hour")
            plt.ylabel("°C")

            # Set x ticks to show every 3 hours
            xticks = list(range(0, 24, 3))
            plt.xticks(xticks)

            # Fixed Y-axis scale for temperature: -20°C to 40°C
            plt.ylim(-20, 40)

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
            plt.ylabel("mm")

            # Set x ticks to show every 3 hours
            xticks = list(range(0, 24, 3))
            plt.xticks(xticks)

            # Fixed Y-axis scale for precipitation: 0 to 20mm
            plt.ylim(0, 20)

        precip_plot.refresh()
