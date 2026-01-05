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
│   ├── app.py           # Main Textual App class
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── hourly_graph.py   # Hour-by-hour temperature/rain graph
│   │   ├── daily_forecast.py # Multi-day forecast widget
│   │   └── location_input.py # Location search input
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather.py    # Open-Meteo weather fetching (from weather-mcp-server)
│   │   └── geocoding.py  # OpenWeatherMap geocoding (from lat-long-mcp-server)
│   └── models/
│       ├── __init__.py
│       └── forecast.py   # Data classes for weather data
├── tests/
│   ├── __init__.py
│   ├── test_weather.py   # Tests for weather service
│   ├── test_geocoding.py # Tests for geocoding service
│   ├── test_widgets.py   # Tests for Textual widgets
│   └── test_models.py    # Tests for data models
├── pyproject.toml
├── agents.md
└── README.md
```

## Features to implement 🎯

### 1. Location Input
- Text input for entering city/place name
- Uses OpenWeatherMap Geocoding API to resolve to lat/lon
- Adapt `forward_geocode()` from `lat-long-mcp-server/lat_long_mcp_server/server.py`

### 2. Hourly Graph (Today)
- ASCII/Unicode bar graph showing hour-by-hour data
- Temperature curve (°C)
- Rain/precipitation bars (mm)
- Use Textual's `Static` or custom `Widget` with Rich renderables

### 3. Daily Forecast (Next Days)
- Summary cards for upcoming days (e.g., 5-7 days)
- Show: date, high/low temp, weather condition icon (emoji), precipitation chance

### 4. Weather Data Fetching
- Adapt from `weather-mcp-server/weather_mcp_server/`:
  - `client.py` — `make_open_meteo_request()`
  - `fetcher.py` — retry logic for hourly data
  - `formatter.py` — formatting helpers

## Code reuse from sibling repos 🔗

### From `weather-mcp-server`:
```python
# Adapt make_open_meteo_request() from weather_mcp_server/client.py
# Adapt retry logic from weather_mcp_server/fetcher.py
# Adapt formatting helpers from weather_mcp_server/formatter.py
```

### From `lat-long-mcp-server`:
```python
# Adapt forward_geocode() and _get_json() from lat_long_mcp_server/server.py
# Requires OPENWEATHERMAP_API_KEY environment variable
```

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

async def test_app_loads():
    app = AppTest(WeatherApp)
    async with app.run_test():
        assert app.query_one("#location-input")
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
