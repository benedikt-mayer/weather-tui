# Agents & Tools — weather-tui

A TUI application for displaying weather forecasts using Textual, with hour-by-hour graphs and multi-day forecasts.

## Overview ✅
- Terminal User Interface (TUI) built with [Textual](https://github.com/Textualize/textual)
- Displays current weather, hourly temperature/rain graphs for today, and rough forecasts for upcoming days
- Uses Open-Meteo for weather data (adapted from `weather-mcp-server`)
- Uses OpenWeatherMap Geocoding for location lookups (adapted from `lat-long-mcp-server`)

## Tooling 🔧
- **Always use `uv`** instead of pip for dependency management
- Use `textual` for the TUI framework
- Use `pytest` for testing all relevant functions
- Use `ruff` for linting and formatting

## Dependencies
Key dependencies (add to `pyproject.toml`):
- `textual` — TUI framework
- `httpx` — async HTTP client
- `openmeteo-requests` — Open-Meteo API client
- `python-dotenv` — environment variable loading

Dev dependencies:
- `pytest` / `pytest-asyncio` — testing
- `ruff` — linting/formatting
- `textual-dev` — Textual development tools (console, devtools)

## Running the app 🚀
```bash
# Install dependencies
uv sync

# Run the TUI
uv run python -m weather_tui
```

## Environment variables 🌐
- `OPENWEATHERMAP_API_KEY` — Required for geocoding place names to lat/lon

## Project structure 📁
```
weather-tui/
├── weather_tui/
│   ├── __init__.py
│   ├── __main__.py       # Entry point for python -m weather_tui
│   ├── app.py            # WeatherApp class and main() (~30 lines)
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── search.py     # SearchScreen for location search modal
│   │   └── weather.py    # WeatherScreen main display screen
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── current_weather.py  # Current weather conditions widget
│   │   ├── hourly_graph.py     # Hour-by-hour temperature/rain graph
│   │   └── daily_forecast.py   # Multi-day forecast widget
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather.py    # Open-Meteo weather fetching
│   │   └── geocoding.py  # OpenWeatherMap geocoding
│   ├── models/
│   │   ├── __init__.py
│   │   └── forecast.py   # Data classes for weather data
│   └── utils/
│       ├── __init__.py
│       └── colors.py     # Color utilities (temp_to_color, precip_to_color)
├── tests/
│   ├── __init__.py
│   ├── test_colors.py    # Tests for color utilities
│   ├── test_weather.py   # Tests for weather service
│   ├── test_geocoding.py # Tests for geocoding service
│   ├── test_widgets.py   # Tests for Textual widgets
│   └── test_models.py    # Tests for data models
├── pyproject.toml
├── agents.md
└── README.md
```

## Features ✅

### 1. Location Search
- Press `s` to open search modal
- Uses OpenWeatherMap Geocoding API to resolve place names to lat/lon
- Default location: Munich

### 2. Current Weather Display
- Shows location name, date, weather emoji/description
- Temperature with color coding (blue=cold, green=mild, red=hot)
- High/low temperatures for the day

### 3. Hourly Graph (Today)
- Temperature line graph using `textual-plotext`
- Precipitation bar chart with color coding
- Click on a day in daily forecast to show that day's hourly data

### 4. Daily Forecast (7 Days)
- Clickable day cards showing date, emoji, high/low temps, precipitation
- Selecting a day updates hourly graph and current weather display

### 5. Large Clock Display
- Real-time clock using Textual's Digits widget
- Updates every second

### 6. Auto-refresh
- Weather data refreshes automatically every hour
- Press `r` to manually refresh

## Testing 🧪
- **Run tests:** `uv run --extra dev pytest`
- **With coverage:** `uv run --extra dev pytest --cov=weather_tui`
- Write tests for:
  - Weather data fetching (mock HTTP responses)
  - Geocoding service (mock HTTP responses)
  - Data model parsing/validation
  - Widget rendering (use Textual's test utilities)

### Textual testing example:
```python
from textual.testing import AppTest
from weather_tui.app import WeatherApp

async def test_app_loads():
    async with WeatherApp().run_test() as pilot:
        assert pilot.app.query_one("#main-container")
```

## Linting & Formatting 🔍
- **After every code change, run:**
  ```bash
  ruff check --fix .
  ruff format .
  ```
- CI should run `ruff format --check .` and `ruff check .`

## Git workflow 📝
- **Commit and push separately:** run `git commit` first, then `git push` as separate steps
- Always ask before pushing to any remote

## Releasing 📦
- **Do NOT publish from local** — releases are handled by the GitHub Actions release pipeline
- To release: push a version tag (e.g., `git tag -a v1.3.0 -m "Release v1.3.0"` then `git push origin v1.3.0`)
- The pipeline will build and publish to PyPI automatically

## Debugging tips 🐞
- Use `textual console` to view logs and debug output
- Use `textual run --dev weather_tui.app:WeatherApp` for hot-reloading
- If weather data is incomplete, check retry logic and Open-Meteo response structure
- If geocoding fails, verify `OPENWEATHERMAP_API_KEY` is set

## Example TUI layout 📺
```
┌─────────────────────────────────────────────────────────────┐
│  🌤️ Weather TUI                          📍 Munich, Germany │
├─────────────────────────────────────────────────────────────┤
│  Location: [___________________] [Search]                   │
├─────────────────────────────────────────────────────────────┤
│  Today's Hourly Forecast (Temperature °C)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │    ·  ·                                              │   │
│  │   ·    ·  ·                                          │   │
│  │  ·        ·  ·  ·                                    │   │
│  │ ·              ·  ·  ·                               │   │
│  │·                    ·  ·  ·                          │   │
│  └──────────────────────────────────────────────────────┘   │
│   00 02 04 06 08 10 12 14 16 18 20 22                       │
├─────────────────────────────────────────────────────────────┤
│  Rain (mm)                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │      ██                                              │   │
│  │   █  ██  █                                           │   │
│  │   █  ██  █                                           │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Weekly Forecast                                            │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┐   │
│  │  Mon   │  Tue   │  Wed   │  Thu   │  Fri   │  Sat   │   │
│  │  ☀️    │  ⛅    │  🌧️   │  ☁️    │  ☀️    │  ⛅    │   │
│  │ 12/5°C │ 10/4°C │  8/3°C │  9/4°C │ 11/5°C │ 10/4°C │   │
│  │  0mm   │  2mm   │  8mm   │  1mm   │  0mm   │  3mm   │   │
│  └────────┴────────┴────────┴────────┴────────┴────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Extending the project ⚡
- Add keyboard shortcuts (Textual bindings) for navigation
- Add settings panel for units (°C/°F, mm/inches)
- Cache recent locations
- Add weather alerts/warnings display
- Support multiple locations comparison

---

Concise, practical, and targeted at contributors building the weather TUI application.
