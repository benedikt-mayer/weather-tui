"""Daily forecast widget showing multi-day forecast cards."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Static

from ..models.forecast import DailyForecast
from ..utils import precip_to_color, temp_to_color


class DayCard(Static):
    """A clickable card representing a single day in the forecast."""

    DEFAULT_CSS = """
    DayCard {
        width: 10;
        height: 6;
        min-width: 10;
        border: solid $primary;
        background: $surface;
        margin: 0;
        padding: 0;
        text-align: center;
        content-align: center middle;
    }

    DayCard:hover {
        background: $primary-darken-1;
    }

    DayCard.-selected {
        border: solid $success;
    }
    """

    class Clicked(Message):
        """Message sent when the card is clicked."""

        def __init__(self, card: "DayCard") -> None:
            self.card = card
            super().__init__()

    def __init__(self, day: DailyForecast, index: int, **kwargs) -> None:
        self.day = day
        self.day_index = index

        # Format the card label
        day_name = day.date.strftime("%a")
        date_str = day.date.strftime("%d.%m")

        # Format precipitation with color
        prec_val = day.precipitation_sum if day.precipitation_sum else 0
        prec_color = precip_to_color(prec_val)
        prec_str = f"[{prec_color}]{prec_val:.0f}mm[/]"

        # Format temps with colors
        if day.temp_min is not None:
            min_color = temp_to_color(day.temp_min)
            min_t = f"[{min_color}]{day.temp_min:.0f}[/]"
        else:
            min_t = "?"
        if day.temp_max is not None:
            max_color = temp_to_color(day.temp_max)
            max_t = f"[{max_color}]{day.temp_max:.0f}[/]"
        else:
            max_t = "?"
        temp_str = f"{min_t}/{max_t}"

        # Build label with centered text lines
        width = 8
        lines = [
            day_name.center(width),
            date_str.center(width),
            temp_str,
            prec_str,
        ]
        label = "\n".join(lines)

        super().__init__(label, **kwargs)

    def on_click(self) -> None:
        """Handle click events."""
        self.post_message(self.Clicked(self))


class DailyForecastWidget(Static):
    """Widget displaying multi-day weather forecast with clickable days."""

    DEFAULT_CSS = """
    DailyForecastWidget {
        height: auto;
        padding: 1;
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
            card = DayCard(day, i)
            if i == self._selected_index:
                card.add_class("-selected")
            container.mount(card)

    def on_day_card_clicked(self, event: DayCard.Clicked) -> None:
        """Handle day card click."""
        card = event.card
        # Update selection
        self._selected_index = card.day_index

        # Update card styles
        for c in self.query(DayCard):
            c.remove_class("-selected")
        card.add_class("-selected")

        # Post message
        self.post_message(self.DaySelected(card.day, card.day_index))

    def select_day(self, index: int) -> None:
        """Programmatically select a day."""
        if 0 <= index < len(self._daily_data):
            self._selected_index = index
            for card in self.query(DayCard):
                if card.day_index == index:
                    card.add_class("-selected")
                else:
                    card.remove_class("-selected")
