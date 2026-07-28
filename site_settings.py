"""Site-wide UI and navigation settings stored in displays.yaml."""

from __future__ import annotations

from typing import Any

from display_manager import default_location_id, get_display, load_displays, rooms_for_location, save_displays

DEFAULT_HOMEPAGE_TITLE = "TV Remotes"
DEFAULT_HOMEPAGE_LEAD = (
    "Locations group rooms by site. Each room has its own display IP for local control."
)


def get_site_settings() -> dict[str, Any]:
    data = load_displays()
    raw = data.get("site") or {}
    default_loc = default_location_id()
    default_room = str(raw.get("default_room") or "").strip().lower()
    if not default_room:
        rooms = rooms_for_location(default_loc)
        default_room = rooms[0] if rooms else ""
    return {
        "homepage_title": str(raw.get("homepage_title") or DEFAULT_HOMEPAGE_TITLE).strip(),
        "homepage_lead": str(raw.get("homepage_lead") or DEFAULT_HOMEPAGE_LEAD).strip(),
        "default_location": str(raw.get("default_location") or default_loc).strip().lower(),
        "default_room": default_room,
        "show_default_remote": bool(raw.get("show_default_remote", True)),
    }


def default_remote_path() -> str | None:
    from display_manager import get_location, room_path

    settings = get_site_settings()
    loc = settings["default_location"]
    room = settings["default_room"]
    if not loc or not room:
        return None
    if not get_location(loc) or not get_display(room):
        return None
    display = get_display(room)
    if not display or str(display.get("location") or default_location_id()) != loc:
        return None
    return room_path(loc, room)


def save_site_settings(payload: dict[str, Any]) -> dict[str, Any]:
    data = load_displays()
    current = get_site_settings()
    merged = {**current, **{k: v for k, v in payload.items() if k in current}}
    merged["homepage_title"] = str(merged.get("homepage_title") or DEFAULT_HOMEPAGE_TITLE).strip()
    merged["homepage_lead"] = str(merged.get("homepage_lead") or DEFAULT_HOMEPAGE_LEAD).strip()
    merged["default_location"] = str(merged.get("default_location") or default_location_id()).strip().lower()
    merged["default_room"] = str(merged.get("default_room") or "").strip().lower()
    merged["show_default_remote"] = bool(merged.get("show_default_remote"))
    data["site"] = merged
    save_displays(data)
    return get_site_settings()
