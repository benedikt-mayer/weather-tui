# Weather TUI

A terminal user interface for displaying weather forecasts with hour-by-hour graphs and multi-day forecasts.

## Features

- 🌡️ Current weather conditions with temperature and wind
- 📊 Hourly temperature and precipitation graphs for today
- 📅 7-day weather forecast
- 🔍 Location search powered by OpenWeatherMap Geocoding
- ⌨️ Keyboard-friendly navigation

## Installation

```bash
# Clone the repository
git clone https://github.com/benedikt-mayer/weather-tui.git
cd weather-tui

# Install dependencies with uv
uv sync
```

## Usage

```bash
# Run the TUI
uv run python -m weather_tui

# Or with a specific location
uv run python -m weather_tui "Munich"
```

## Environment Variables

- `OPENWEATHERMAP_API_KEY` - Required for geocoding place names to lat/lon. Get a free API key at [OpenWeatherMap](https://openweathermap.org/api).

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Refresh weather data |
| `l` | Focus location input |

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format --check .

# Fix linting issues
uv run ruff check --fix .
uv run ruff format .
```

## License

MIT
