"""Color utility functions for weather visualization.

Temperature scale: -20°C (blue) → 10°C (green) → 35°C (red)
Precipitation scale: 0mm (gray) → 20mm+ (purple)
"""

# Temperature scale bounds
TEMP_MIN = -20.0
TEMP_MAX = 35.0

# Precipitation scale bound
PRECIP_MAX = 20.0


def temp_to_rgb(temp: float) -> tuple[int, int, int]:
    """Convert temperature to RGB color tuple.

    Scale: -20°C = blue, 10°C = green, 35°C = red
    """
    normalized = (temp - TEMP_MIN) / (TEMP_MAX - TEMP_MIN)
    normalized = max(0.0, min(1.0, normalized))

    if normalized < 0.5:
        # Blue to green
        factor = normalized * 2
        r = 0
        g = int(255 * factor)
        b = int(255 * (1 - factor))
    else:
        # Green to red
        factor = (normalized - 0.5) * 2
        r = int(255 * factor)
        g = int(255 * (1 - factor))
        b = 0

    return (r, g, b)


def temp_to_color(temp: float) -> str:
    """Convert temperature to hex color string.

    Scale: -20°C = blue, 10°C = green, 35°C = red
    """
    r, g, b = temp_to_rgb(temp)
    return f"#{r:02x}{g:02x}{b:02x}"


def precip_to_rgb(precip: float) -> tuple[int, int, int]:
    """Convert precipitation to RGB color tuple.

    Scale: 0mm = gray (#888888), 20mm+ = purple (#0000ff)
    """
    normalized = min(1.0, precip / PRECIP_MAX)

    # Gray to purple gradient
    r = int(136 - 136 * normalized)  # 136 -> 0
    g = int(136 - 136 * normalized)  # 136 -> 0
    b = int(136 + 119 * normalized)  # 136 -> 255

    return (r, g, b)


def precip_to_color(precip: float) -> str:
    """Convert precipitation to hex color string.

    Scale: 0mm = gray (#888888), 20mm+ = purple (#0000ff)
    """
    r, g, b = precip_to_rgb(precip)
    return f"#{r:02x}{g:02x}{b:02x}"
