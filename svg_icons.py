"""
High-Resolution Vector SVG Icons for MLACW Campus Navigator
Provides scalable, razor-sharp SVG vector icons across all browsers and devices.
Replaces pixelated or inconsistent OS emojis with a cohesive modern design system.
"""

from typing import Dict, Optional

# Standard Feather / Lucide inspired vector paths (viewBox 0 0 24 24)
SVG_PATHS: Dict[str, str] = {
    # Institutional & Navigation
    "campus": (
        '<path d="M3 21h18M3 10h18M5 6l7-3 7 3M4 10v11M20 10v11M8 14v3M12 14v3M16 14v3" />'
    ),
    "building": (
        '<rect x="4" y="2" width="16" height="20" rx="2" ry="2" />'
        '<line x1="9" y1="6" x2="9" y2="6.01" />'
        '<line x1="15" y1="6" x2="15" y2="6.01" />'
        '<line x1="9" y1="10" x2="9" y2="10.01" />'
        '<line x1="15" y1="10" x2="15" y2="10.01" />'
        '<line x1="9" y1="14" x2="9" y2="14.01" />'
        '<line x1="15" y1="14" x2="15" y2="14.01" />'
        '<path d="M10 22v-4h4v4" />'
    ),
    "compass": (
        '<circle cx="12" cy="12" r="10" />'
        '<polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" fill="currentColor" fill-opacity="0.2" />'
    ),
    "map": (
        '<polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />'
        '<line x1="8" y1="2" x2="8" y2="18" />'
        '<line x1="16" y1="6" x2="16" y2="22" />'
    ),
    "map_pin": (
        '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />'
        '<circle cx="12" cy="10" r="3" />'
    ),
    "flag": (
        '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />'
        '<line x1="4" y1="22" x2="4" y2="15" />'
    ),
    "target": (
        '<circle cx="12" cy="12" r="10" />'
        '<circle cx="12" cy="12" r="6" />'
        '<circle cx="12" cy="12" r="2" fill="currentColor" />'
    ),
    "swap": (
        '<path d="M16 3l4 4-4 4" />'
        '<path d="M20 7H4" />'
        '<path d="M8 21l-4-4 4-4" />'
        '<path d="M4 17h16" />'
    ),
    "route": (
        '<circle cx="6" cy="19" r="3" />'
        '<path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15" />'
        '<polyline points="18 8 21 5 18 2" />'
    ),

    # Accessibility
    "wheelchair": (
        '<circle cx="15.5" cy="5.5" r="2" />'
        '<path d="M7 10h5l1 7h4" />'
        '<path d="M12 17l-3 4" />'
        '<path d="M5 19a4 4 0 1 0 4-4H7" />'
    ),

    # Pedestrian Movement & Actions
    "walk": (
        '<circle cx="13" cy="4" r="2" fill="currentColor" />'
        '<path d="m9 20 3-6-3-2V8h4l2 4 3 1" />'
        '<path d="M6 14l3-2" />'
        '<path d="M15 16l3 5" />'
    ),
    "arrow_straight": (
        '<line x1="12" y1="19" x2="12" y2="5" />'
        '<polyline points="5 12 12 5 19 12" />'
    ),
    "arrow_up": (
        '<line x1="12" y1="19" x2="12" y2="5" />'
        '<polyline points="5 12 12 5 19 12" />'
    ),
    "turn_right": (
        '<path d="M5 19v-6a4 4 0 0 1 4-4h10" />'
        '<polyline points="15 5 19 9 15 13" />'
    ),
    "turn_left": (
        '<path d="M19 19v-6a4 4 0 0 0-4-4H5" />'
        '<polyline points="9 5 5 9 9 13" />'
    ),
    "slight_right": (
        '<path d="M6 19c2-6 5-9 10-10" />'
        '<polyline points="11 7 16 9 14 14" />'
    ),
    "slight_left": (
        '<path d="M18 19c-2-6-5-9-10-10" />'
        '<polyline points="13 7 8 9 10 14" />'
    ),
    "stairs": (
        '<polyline points="4 20 8 20 8 16 12 16 12 12 16 12 16 8 20 8 20 4" />'
    ),
    "stairs_up": (
        '<polyline points="4 20 8 20 8 16 12 16 12 12 16 12 16 8 20 8 20 4" />'
        '<polyline points="8 4 4 4 4 8" />'
        '<line x1="4" y1="4" x2="11" y2="11" />'
    ),
    "stairs_down": (
        '<polyline points="4 4 8 4 8 8 12 8 12 12 16 12 16 16 20 16 20 20" />'
        '<polyline points="16 20 20 20 20 16" />'
        '<line x1="13" y1="13" x2="20" y2="20" />'
    ),
    "elevator": (
        '<rect x="4" y="3" width="16" height="18" rx="2" />'
        '<line x1="12" y1="3" x2="12" y2="21" />'
        '<polyline points="7 10 8.5 7 10 10" />'
        '<polyline points="14 14 15.5 17 17 14" />'
    ),
    "trophy": (
        '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" />'
        '<path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" />'
        '<path d="M4 22h16" />'
        '<path d="M10 14.66V17c0 .55-.45 1-1 1H7v2h10v-2h-2c-.55 0-1-.45-1-1v-2.34" />'
        '<path d="M6 4h12v7a6 6 0 0 1-12 0V4z" />'
    ),

    # Floors & Academic Divisions
    "layers": (
        '<polygon points="12 2 2 7 12 12 22 7 12 2" />'
        '<polyline points="2 17 12 22 22 17" />'
        '<polyline points="2 12 12 17 22 12" />'
    ),
    "leaf": (
        '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />'
        '<path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />'
    ),
    "microscope": (
        '<path d="M6 18h8M3 22h18M14 22a7 7 0 1 0 0-14h-1M9 14h2M9 12a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2Z" />'
        '<path d="M10 6h4" />'
    ),
    "laptop": (
        '<path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45L4 16" />'
    ),
    "book": (
        '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />'
        '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />'
    ),
    "folder": (
        '<path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />'
    ),

    # Voice & Audio
    "mic": (
        '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />'
        '<path d="M19 10v2a7 7 0 0 1-14 0v-2" />'
        '<line x1="12" y1="19" x2="12" y2="23" />'
        '<line x1="8" y1="23" x2="16" y2="23" />'
    ),
    "mic_active": (
        '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" fill="currentColor" />'
        '<path d="M19 10v2a7 7 0 0 1-14 0v-2" />'
        '<line x1="12" y1="19" x2="12" y2="23" />'
        '<line x1="8" y1="23" x2="16" y2="23" />'
    ),
    "speaker": (
        '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />'
        '<path d="M19.07 4.93a10 10 0 0 1 0 14.14" />'
        '<path d="M15.54 8.46a5 5 0 0 1 0 7.07" />'
    ),
    "play": (
        '<polygon points="5 3 19 12 5 21 5 3" fill="currentColor" />'
    ),
    "pause": (
        '<rect x="6" y="4" width="4" height="16" fill="currentColor" />'
        '<rect x="14" y="4" width="4" height="16" fill="currentColor" />'
    ),
    "stop": (
        '<rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" />'
    ),
    "skip_back": (
        '<polygon points="19 20 9 12 19 4 19 20" fill="currentColor" />'
        '<line x1="5" y1="19" x2="5" y2="5" />'
    ),
    "skip_forward": (
        '<polygon points="5 4 15 12 5 20 5 4" fill="currentColor" />'
        '<line x1="19" y1="5" x2="19" y2="19" />'
    ),
    "repeat": (
        '<polyline points="23 4 23 10 17 10" />'
        '<polyline points="1 20 1 14 7 14" />'
        '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />'
    ),

    # Search & Input
    "search": (
        '<circle cx="11" cy="11" r="8" />'
        '<line x1="21" y1="21" x2="16.65" y2="16.65" />'
    ),
    "keyboard": (
        '<rect x="2" y="4" width="20" height="16" rx="2" ry="2" />'
        '<line x1="6" y1="8" x2="6.01" y2="8" />'
        '<line x1="10" y1="8" x2="10.01" y2="8" />'
        '<line x1="14" y1="8" x2="14.01" y2="8" />'
        '<line x1="18" y1="8" x2="18.01" y2="8" />'
        '<line x1="6" y1="12" x2="6.01" y2="12" />'
        '<line x1="18" y1="12" x2="18.01" y2="12" />'
        '<line x1="10" y1="16" x2="14" y2="16" />'
    ),

    # Status, Orientation & Verification
    "globe": (
        '<circle cx="12" cy="12" r="10" />'
        '<line x1="2" y1="12" x2="22" y2="12" />'
        '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />'
    ),
    "landmark": (
        '<path d="M4 21h16M5 21V7M19 21V7M9 21V7M15 21V7M3 7h18M12 3L3 7h18l-9-4z" />'
    ),
    "clock": (
        '<circle cx="12" cy="12" r="10" />'
        '<polyline points="12 6 12 12 16 14" />'
    ),
    "ruler": (
        '<path d="M21.3 8.7 8.7 21.3a1 1 0 0 1-1.4 0l-4.6-4.6a1 1 0 0 1 0-1.4L15.3 2.7a1 1 0 0 1 1.4 0l4.6 4.6a1 1 0 0 1 0 1.4z" />'
        '<path d="m14.5 4.5 2 2M11.5 7.5l3 3M8.5 10.5l2 2M5.5 13.5l3 3" />'
    ),
    "check": (
        '<polyline points="20 6 9 17 4 12" />'
    ),
    "check_circle": (
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />'
        '<polyline points="22 4 12 14.01 9 11.01" />'
    ),
    "circle": (
        '<circle cx="12" cy="12" r="9" />'
    ),
    "alert": (
        '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />'
        '<line x1="12" y1="9" x2="12" y2="13" />'
        '<line x1="12" y1="17" x2="12.01" y2="17" />'
    ),
    "lifebuoy": (
        '<circle cx="12" cy="12" r="10" />'
        '<circle cx="12" cy="12" r="4" />'
        '<line x1="4.93" y1="4.93" x2="9.17" y2="9.17" />'
        '<line x1="14.83" y1="14.83" x2="19.07" y2="19.07" />'
        '<line x1="14.83" y1="9.17" x2="19.07" y2="4.93" />'
        '<line x1="4.93" y1="19.07" x2="9.17" y2="14.83" />'
    ),
    "help": (
        '<circle cx="12" cy="12" r="10" />'
        '<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />'
        '<line x1="12" y1="17" x2="12.01" y2="17" />'
    ),
    "arrow_right": (
        '<line x1="5" y1="12" x2="19" y2="12" />'
        '<polyline points="12 5 19 12 12 19" />'
    ),
    "arrow_left": (
        '<line x1="19" y1="12" x2="5" y2="12" />'
        '<polyline points="12 19 5 12 12 5" />'
    ),
    "chevron_right": (
        '<polyline points="9 18 15 12 9 6" />'
    ),
    "chevron_left": (
        '<polyline points="15 18 9 12 15 6" />'
    ),
    "info": (
        '<circle cx="12" cy="12" r="10" />'
        '<line x1="12" y1="16" x2="12" y2="12" />'
        '<line x1="12" y1="8" x2="12.01" y2="8" />'
    ),
    "list": (
        '<line x1="8" y1="6" x2="21" y2="6" />'
        '<line x1="8" y1="12" x2="21" y2="12" />'
        '<line x1="8" y1="18" x2="21" y2="18" />'
        '<line x1="3" y1="6" x2="3.01" y2="6" />'
        '<line x1="3" y1="12" x2="3.01" y2="12" />'
        '<line x1="3" y1="18" x2="3.01" y2="18" />'
    )
}

# Mapping of common emojis to SVG icon keys
EMOJI_TO_SVG: Dict[str, str] = {
    "🚶": "walk",
    "🏃": "walk",
    "🎯": "target",
    "🚩": "flag",
    "📍": "map_pin",
    "🧭": "compass",
    "🗺️": "map",
    "🛗": "elevator",
    "🪜": "stairs",
    "⬆️": "arrow_straight",
    "➡️": "turn_right",
    "⬅️": "turn_left",
    "↗️": "slight_right",
    "↖️": "slight_left",
    "🌿": "leaf",
    "🔬": "microscope",
    "💻": "laptop",
    "🛋️": "book",
    "📚": "book",
    "📖": "book",
    "🏛️": "landmark",
    "🏢": "building",
    "🏫": "campus",
    "♿": "wheelchair",
    "🎙️": "mic",
    "🗣️": "speaker",
    "🔊": "speaker",
    "⌨️": "keyboard",
    "🔍": "search",
    "🔄": "repeat",
    "✓": "check",
    "✅": "check_circle",
    "⭕": "circle",
    "⚠️": "alert",
    "🆘": "lifebuoy",
    "🏆": "trophy",
    "🎉": "trophy",
    "🌐": "globe",
    "⏱️": "clock",
    "📏": "ruler",
    "📂": "folder",
    "📋": "list",
    "➔": "arrow_right",
    "→": "arrow_right",
    "⇄": "swap",
    "▶": "play",
    "▶️": "play",
    "⏸": "pause",
    "⏸️": "pause",
    "⏹": "stop",
    "⏹️": "stop",
    "⏮": "skip_back",
    "⏮️": "skip_back",
    "⏭": "skip_forward",
    "⏭️": "skip_forward"
}


def get_svg_icon(
    name: str,
    size: int = 18,
    color: str = "currentColor",
    extra_classes: str = "",
    stroke_width: float = 2.0,
    filled: bool = False,
    style: str = ""
) -> str:
    """
    Returns an inline SVG HTML element for the requested icon name or emoji.
    If the name matches an emoji or alias, it is automatically resolved.
    """
    clean_name = name.strip()
    icon_key = EMOJI_TO_SVG.get(clean_name, clean_name.lower())

    # Fallback to campus/compass if not found
    path_data = SVG_PATHS.get(icon_key)
    if not path_data:
        # Check sub-words
        for k, v in SVG_PATHS.items():
            if k in icon_key:
                path_data = v
                break
    if not path_data:
        path_data = SVG_PATHS.get("compass")

    fill_val = color if filled else "none"
    class_attr = f' class="svg-icon {extra_classes.strip()}"' if extra_classes else ' class="svg-icon"'
    style_attr = f' style="{style}"' if style else ''

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="{fill_val}" stroke="{color}" '
        f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"'
        f'{class_attr}{style_attr}>{path_data}</svg>'
    )


def icon_text(
    name: str,
    text: str,
    size: int = 16,
    color: str = "currentColor",
    gap: int = 6,
    extra_classes: str = ""
) -> str:
    """
    Helper to render an icon neatly aligned with adjacent text.
    """
    svg = get_svg_icon(name, size=size, color=color, extra_classes=extra_classes)
    return (
        f'<span style="display:inline-flex; align-items:center; vertical-align:middle; gap:{gap}px;">'
        f'{svg}<span>{text}</span></span>'
    )


def icon_badge(
    name: str,
    text: str,
    bg: str = "#EFF6FF",
    color: str = "#0284C7",
    border: str = "#BFDBFE",
    size: int = 14
) -> str:
    """
    Returns a pre-styled pill badge with an aligned SVG icon.
    """
    svg = get_svg_icon(name, size=size, color=color)
    return (
        f'<span style="display:inline-flex; align-items:center; gap:5px; background:{bg}; '
        f'color:{color}; border:1px solid {border}; border-radius:10px; padding:3px 8px; '
        f'font-size:11px; font-weight:700; vertical-align:middle;">{svg}<span>{text}</span></span>'
    )
