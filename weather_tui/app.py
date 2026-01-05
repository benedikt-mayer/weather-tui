"""Weather TUI main application."""

from textual.app import App

from .screens import WeatherScreen


class WeatherApp(App):
    """A TUI application for displaying weather forecasts."""

    TITLE = "Weather TUI"
    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }
    """

    def on_mount(self) -> None:
        """Push the weather screen on mount."""
        weather_screen = WeatherScreen()
        self.push_screen(weather_screen)
        weather_screen.run_worker(weather_screen.load_weather("Munich"))


def main() -> None:
    """Main entry point."""
    app = WeatherApp()
    app.run()


if __name__ == "__main__":
    main()
