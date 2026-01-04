"""Location input widget with search functionality."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Input


class LocationInput(Horizontal):
    """Widget for entering and searching locations."""

    DEFAULT_CSS = """
    LocationInput {
        height: auto;
        padding: 1;
    }

    LocationInput Input {
        width: 1fr;
    }

    LocationInput Button {
        width: auto;
        min-width: 10;
    }
    """

    class LocationSubmitted(Message):
        """Message sent when a location is submitted."""

        def __init__(self, location: str) -> None:
            self.location = location
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter location...", id="location-input")
        yield Button("Search", id="search-button", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle search button press."""
        if event.button.id == "search-button":
            self._submit_location()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input."""
        self._submit_location()

    def _submit_location(self) -> None:
        """Submit the current location."""
        input_widget = self.query_one("#location-input", Input)
        location = input_widget.value.strip()
        if location:
            self.post_message(self.LocationSubmitted(location))

    def set_location(self, location: str) -> None:
        """Set the location input value."""
        input_widget = self.query_one("#location-input", Input)
        input_widget.value = location
