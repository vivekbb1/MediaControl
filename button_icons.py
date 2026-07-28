"""Built-in remote button icon keys and defaults."""

from __future__ import annotations

from typing import Any

from button_svgs import normalize_icon_key

ICON_CATALOG: list[dict[str, str]] = [
    {"id": "apple", "label": "Apple"},
    {"id": "teams", "label": "Teams"},
    {"id": "browser", "label": "Browser"},
    {"id": "airplay", "label": "AirPlay"},
    {"id": "smartview", "label": "SmartView"},
    {"id": "whiteboard", "label": "Whiteboard / markers"},
    {"id": "stb", "label": "Set-top box"},
    {"id": "hdmi", "label": "HDMI"},
    {"id": "usb_c", "label": "USB-C"},
    {"id": "flip", "label": "Flip"},
    {"id": "usb", "label": "USB-A"},
    {"id": "pc", "label": "PC"},
    {"id": "power", "label": "Power"},
    {"id": "reboot", "label": "Reboot"},
    {"id": "mute", "label": "Mute"},
    {"id": "unmute", "label": "Unmute"},
    {"id": "volume", "label": "Volume"},
    {"id": "volume_up", "label": "Volume up"},
    {"id": "volume_down", "label": "Volume down"},
    {"id": "home", "label": "Home"},
    {"id": "settings", "label": "Settings"},
    {"id": "info", "label": "Info"},
    {"id": "back", "label": "Back"},
    {"id": "arrow_up", "label": "Up"},
    {"id": "arrow_down", "label": "Down"},
    {"id": "arrow_left", "label": "Left"},
    {"id": "arrow_right", "label": "Right"},
    {"id": "enter", "label": "Enter / OK"},
    {"id": "exit", "label": "Exit"},
    {"id": "screen_fit", "label": "Fit to screen"},
    {"id": "aspect_16_9", "label": "16:9"},
    {"id": "aspect_4_3", "label": "4:3"},
    {"id": "refresh", "label": "Refresh"},
    {"id": "menu", "label": "Menu (gear)"},
    {"id": "source", "label": "Generic source"},
]

DEFAULT_ICONS_BY_ID: dict[str, str] = {
    "apple": "apple",
    "teams": "teams",
    "browser": "browser",
    "airplay": "airplay",
    "screen_mirror": "airplay",
    "touchscreen": "whiteboard",
    "stb": "stb",
    "hdmi1": "teams",
    "hdmi2": "hdmi",
    "hdmi3": "hdmi",
    "usb_c": "usb_c",
    "usb_c2": "flip",
    "pc": "pc",
    "dp": "hdmi",
    "power_on": "power",
    "power_off": "power",
    "power_toggle": "power",
    "reboot": "reboot",
    "mute_on": "mute",
    "mute_off": "unmute",
    "mute_toggle": "mute",
    "vol_up": "volume_up",
    "vol_down": "volume_down",
    "up": "arrow_up",
    "down": "arrow_down",
    "left": "arrow_left",
    "right": "arrow_right",
    "ok": "enter",
    "enter": "enter",
    "home": "home",
    "menu": "settings",
    "info": "info",
    "back": "back",
    "exit": "exit",
    "screen_fit": "screen_fit",
    "aspect_16_9": "aspect_16_9",
    "aspect_4_3": "aspect_4_3",
    "refresh": "refresh",
    "query_power": "power",
    "query_input": "source",
}

VALID_BUTTON_STYLES = frozenset({"text", "icon", "both"})
VALID_POWER_MODES = frozenset({"split", "toggle"})
VALID_MUTE_MODES = frozenset({"split", "toggle"})

POWER_TOGGLE_BUTTON: dict[str, Any] = {
    "id": "power_toggle",
    "title": "Power",
    "icon": "power",
    "toggle": "power",
    "variant": "primary",
}

MUTE_TOGGLE_BUTTON: dict[str, Any] = {
    "id": "mute_toggle",
    "title": "Mute",
    "icon": "mute",
    "toggle": "mute",
}


def icon_catalog() -> list[dict[str, str]]:
    return sorted(
        (dict(item) for item in ICON_CATALOG),
        key=lambda item: item["label"].casefold(),
    )


def default_icon_for(button_id: str, source_icon: str | None = None) -> str | None:
    if source_icon:
        return source_icon
    return DEFAULT_ICONS_BY_ID.get(button_id)


def resolve_icon(button_id: str, layout: dict[str, Any], source_icon: str | None = None) -> str | None:
    overrides = layout.get("button_icons") or {}
    if button_id in overrides and overrides[button_id]:
        return normalize_icon_key(str(overrides[button_id]))
    icon = default_icon_for(button_id, source_icon)
    return normalize_icon_key(icon) if icon else None


def button_style_for(section: str, layout: dict[str, Any]) -> str:
    styles = layout.get("button_style") or {}
    if isinstance(styles, str):
        style = styles
    else:
        style = styles.get(section) or styles.get("default") or "both"
    return style if style in VALID_BUTTON_STYLES else "both"


def enrich_remote_button(button: dict[str, Any], section: str, layout: dict[str, Any]) -> dict[str, Any]:
    import button_icons as bi

    item = dict(button)
    item["icon"] = bi.resolve_icon(str(item.get("id") or ""), layout, item.get("icon"))
    item["style"] = button_style_for(section, layout)
    return item
