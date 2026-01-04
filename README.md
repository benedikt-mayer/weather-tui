# Weather TUI

A terminal user interface for displaying weather forecasts with hour-by-hour graphs and multi-day forecasts.

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![CI](https://github.com/benedikt-mayer/weather-tui/actions/workflows/ci.yml/badge.svg)](https://github.com/benedikt-mayer/weather-tui/actions/workflows/ci.yml)

## Features

- Current weather conditions with temperature
- Hourly temperature and precipitation graphs
- 7-day weather forecast with clickable day selection
- Location search powered by OpenWeatherMap Geocoding
- Keyboard-friendly navigation

## Installation

### From PyPI (recommended)

```bash
pip install weather-tui
```

### From source

```bash
# Clone the repository
git clone https://github.com/benedikt-mayer/weather-tui.git
cd weather-tui

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Usage

```bash
# Run the TUI (defaults to Munich)
weather-tui

# Or with a specific location
weather-tui "Berlin"

# Or run as module
python -m weather_tui "Paris"
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENWEATHERMAP_API_KEY` | Yes | API key for geocoding. Get a free key at [OpenWeatherMap](https://openweathermap.org/api) |

Create a `.env` file in your working directory:

```bash
OPENWEATHERMAP_API_KEY=your_api_key_here
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `s` | Search for a new location |
| `r` | Refresh weather data |
| `q` | Quit |
| `Escape` | Cancel search |
| Click | Select a day to view its hourly forecast |

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

## Tech Stack

- [Textual](https://github.com/Textualize/textual) - TUI framework
- [textual-plotext](https://github.com/Textualize/textual-plotext) - Terminal plotting
- [Open-Meteo](https://open-meteo.com/) - Weather data API (no key required)
- [OpenWeatherMap Geocoding](https://openweathermap.org/api/geocoding-api) - Location search

## License

MIT License - see [LICENSE](LICENSE) for details.
