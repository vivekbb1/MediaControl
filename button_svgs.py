"""Inline SVG markup for built-in remote utility icons (non-brand)."""

from __future__ import annotations

import hashlib
import json

ICON_ALIASES: dict[str, str] = {
    "menu": "settings",
}

SVG_NS = ' xmlns="http://www.w3.org/2000/svg"'


def _svg(svg: str) -> str:
    if "xmlns=" not in svg:
        return svg.replace("<svg ", f"<svg{SVG_NS} ", 1)
    return svg


ICON_SVGS: dict[str, str] = {
    "whiteboard": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="5" width="18" height="11" rx="1.5"/>'
        '<path d="M9 20h6"/><path d="M12 16v4"/>'
        '<path d="M7 13h10"/>'
        "</svg>"
    ),
    "stb": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="9" width="18" height="7" rx="1.5"/>'
        '<path d="M6 9V7.5A1.5 1.5 0 0 1 7.5 6h9A1.5 1.5 0 0 1 18 7.5V9"/>'
        '<circle cx="17" cy="12.5" r="1"/>'
        "</svg>"
    ),
    "usb_c": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="5" y="9" width="14" height="6" rx="3"/>'
        '<path d="M12 9.5v5"/>'
        "</svg>"
    ),
    "hdmi": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="7" width="14" height="10" rx="2"/><path d="M17 10h4v4h-4zM7 20h6"/></svg>'),
    "flip": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 21h8"/></svg>'),
    "usb": _svg('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 2v3H6v3h2v8.8c0 1.5 1.2 2.7 2.7 2.7H13v2h2v-2h2.3c1.5 0 2.7-1.2 2.7-2.7V8h2V5h-2V2h-2v3h-2V2h-2v3H10V2H8Zm2 6h4v7.8c0 .5-.4.9-.9.9H10.9c-.5 0-.9-.4-.9-.9V8Z"/></svg>'),
    "pc": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>'),
    "power": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v8"/><path d="M8.5 5.8a7 7 0 1 0 7 0"/></svg>'),
    "reboot": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 12a9 9 0 1 1-2.64-6.36"/>'
        '<path d="M21 3v6h-6"/>'
        "</svg>"
    ),
    "mute": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="m16 9 4 4M20 9l-4 4"/></svg>'),
    "unmute": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="M15.5 9.5a4.5 4.5 0 0 1 0 5M18 7a7.5 7.5 0 0 1 0 10"/></svg>'),
    "volume": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="M15.5 9.5a4.5 4.5 0 0 1 0 5M18 7a7.5 7.5 0 0 1 0 10"/></svg>'),
    "volume_up": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
        '<path d="M11 5 6 9H3v6h3l5 4V5Z"/>'
        '<path d="M18 9v6M15 12h6"/>'
        "</svg>"
    ),
    "volume_down": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
        '<path d="M11 5 6 9H3v6h3l5 4V5Z"/>'
        '<path d="M15 12h6"/>'
        "</svg>"
    ),
    "home": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m4 10 8-6 8 6"/><path d="M6 10v9h12v-9"/></svg>'),
    "settings": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/>'
        '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>'
        "</svg>"
    ),
    "info": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01" stroke-linecap="round"/></svg>'),
    "back": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 6 8 12l6 6"/>'
        '<path d="M8 12h11"/>'
        "</svg>"
    ),
    "arrow_up": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M6 10 12 4 18 10"/>'
        "</svg>"
    ),
    "arrow_down": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M6 14 12 20 18 14"/>'
        "</svg>"
    ),
    "arrow_left": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M10 6 4 12 10 18"/>'
        "</svg>"
    ),
    "arrow_right": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 6 20 12 14 18"/>'
        "</svg>"
    ),
    "enter": _svg(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
        '<circle cx="12" cy="12" r="8"/>'
        '<circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/>'
        "</svg>"
    ),
    "exit": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/></svg>'),
    "screen_fit": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/><rect x="7.5" y="7.5" width="9" height="9" rx="1"/></svg>'),
    "aspect_16_9": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="7.5" width="16" height="9" rx="1"/></svg>'),
    "aspect_4_3": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="6" width="14" height="10.5" rx="1"/></svg>'),
    "refresh": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12a8 8 0 0 1 13.4-5.9L20 8"/><path d="M20 4v4h-4"/><path d="M20 12a8 8 0 0 1-13.4 5.9L4 16"/><path d="M4 20v-4h4"/></svg>'),
    "source": _svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M8 10h8M8 14h5"/></svg>'),
}


def normalize_icon_key(key: str | None) -> str | None:
    if not key:
        return None
    text = str(key).strip()
    return ICON_ALIASES.get(text, text)


def icon_svgs() -> dict[str, str]:
    """Return utility icon SVG markup. Regenerate button_svgs.js after edits."""
    merged = dict(ICON_SVGS)
    for alias, target in ICON_ALIASES.items():
        if target in merged:
            merged[alias] = merged[target]
    return merged


def icon_revision() -> str:
    """Short hash for cache-busting icon bundles."""
    payload = json.dumps(icon_svgs(), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def live_icon_bundle() -> tuple[dict[str, str], str]:
    """Reload this module and return fresh SVGs + revision (dev-friendly)."""
    import importlib
    import sys

    mod = sys.modules[__name__]
    importlib.reload(mod)
    return mod.icon_svgs(), mod.icon_revision()
