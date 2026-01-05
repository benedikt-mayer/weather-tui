"""Search screen for location input."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static


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
