"""Daily forecast widget showing multi-day forecast cards."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Static

from ..models.forecast import DailyForecast


class DayButton(Button):
    """A button representing a single day in the forecast."""

    DEFAULT_CSS = """
    DayButton {
        width: 12;
        height: 7;
        min-width: 12;
        border: solid $primary;
        background: $surface;
        margin: 0 1;
    }

    DayButton:hover {
        background: $primary-darken-1;
    }

    DayButton.-selected {
        border: solid $success;
        background: $success-darken-3;
    }
    """

    def __init__(self, day: DailyForecast, index: int, **kwargs) -> None:
        self.day = day
        self.day_index = index

        # Format the button label
        day_name = day.date.strftime("%a")
        date_str = day.date.strftime("%d/%m")
        max_t = f"{day.temp_max:.0f}" if day.temp_max is not None else "?"
        min_t = f"{day.temp_min:.0f}" if day.temp_min is not None else "?"
        prec = f"{day.precipitation_sum:.0f}" if day.precipitation_sum else "0"

        label = f"{day_name}\n{date_str}\n{day.emoji}\n{max_t}/{min_t}°\n{prec}mm"

        super().__init__(label, **kwargs)


class DailyForecastWidget(Static):
    """Widget displaying multi-day weather forecast with clickable days."""

    DEFAULT_CSS = """
    DailyForecastWidget {
        height: auto;
        padding: 1;
    }

    DailyForecastWidget #daily-title {
        height: 1;
        padding: 0 1;
        margin-bottom: 1;
        text-style: bold;
    }

    DailyForecastWidget #days-container {
        height: auto;
        align: center middle;
    }
    """

    class DaySelected(Message):
        """Message sent when a day is selected."""

        def __init__(self, day: DailyForecast, index: int) -> None:
            self.day = day
            self.index = index
            super().__init__()

    def __init__(
        self,
        daily_data: list[DailyForecast] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._daily_data = daily_data or []
        self._selected_index = 0

    def compose(self) -> ComposeResult:
        yield Static(
            "📅 Weekly Forecast (click a day to view details)", id="daily-title"
        )
        yield Horizontal(id="days-container")

    def on_mount(self) -> None:
        """Render initial content."""
        self._render_days()

    def update_data(self, daily_data: list[DailyForecast]) -> None:
        """Update the daily data and refresh display."""
        self._daily_data = daily_data
        self._selected_index = 0
        self._render_days()

    def _render_days(self) -> None:
        """Render day buttons."""
        container = self.query_one("#days-container", Horizontal)

        # Remove existing children first
        for child in list(container.children):
            child.remove()

        if not self._daily_data:
            container.mount(Static("No daily forecast available"))
            return

        # Render up to 7 days
        for i, day in enumerate(self._daily_data[:7]):
            btn = DayButton(day, i)
            if i == self._selected_index:
                btn.add_class("-selected")
            container.mount(btn)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle day button press."""
        if isinstance(event.button, DayButton):
            # Update selection
            self._selected_index = event.button.day_index

            # Update button styles
            for btn in self.query(DayButton):
                btn.remove_class("-selected")
            event.button.add_class("-selected")

            # Post message
            self.post_message(
                self.DaySelected(event.button.day, event.button.day_index)
            )

    def select_day(self, index: int) -> None:
        """Programmatically select a day."""
        if 0 <= index < len(self._daily_data):
            self._selected_index = index
            for btn in self.query(DayButton):
                if btn.day_index == index:
                    btn.add_class("-selected")
                else:
                    btn.remove_class("-selected")
