"""Load and manage per-cabin display configuration."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

import yaml

from broadlink_client import BroadlinkClient, BroadlinkConfig, BROADLINK_AVAILABLE, load_ir_codes
from button_icons import (
    DEFAULT_ICONS_BY_ID,
    MUTE_TOGGLE_BUTTON,
    POWER_TOGGLE_BUTTON,
    VALID_BUTTON_STYLES,
    VALID_MUTE_MODES,
    VALID_POWER_MODES,
    button_style_for,
    enrich_remote_button,
    icon_catalog,
)
from button_svgs import live_icon_bundle
from mdc_client import MdcConfig, MdcClient, build_packet, format_hex, parse_hex

ROOT = Path(__file__).resolve().parent
DISPLAYS_PATH = ROOT / "displays.yaml"
TEMPLATES_PATH = ROOT / "layout_templates.yaml"
MAPS_DIR = ROOT / "maps"
CATALOG_PATH = ROOT / "source_catalog.yaml"

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
VALID_CATEGORIES = frozenset({"sources", "wireless", "builtin", "other"})
DEFAULT_CATEGORY_ORDER = ["sources", "wireless", "builtin", "other"]
DEFAULT_SECTION_ORDER = [
    "master",
    "sources",
    "wireless",
    "builtin",
    "other",
    "volume",
    "navigation",
    "picture",
    "status",
    "power",
]
VALID_SECTIONS = frozenset(DEFAULT_SECTION_ORDER)
VALID_BUTTON_SIZES = frozenset({"sm", "md", "lg"})
STATIC_BUTTON_SECTIONS = frozenset({"master", "power", "volume", "navigation", "picture", "status"})
DEFAULT_GRID_SIZE: dict[str, dict[str, int]] = {
    "master": {"cols": 4, "rows": 1},
    "power": {"cols": 3, "rows": 1},
    "volume": {"cols": 4, "rows": 1},
    "volume_presets": {"cols": 5, "rows": 1},
    "navigation_actions": {"cols": 5, "rows": 1},
    "picture": {"cols": 3, "rows": 1},
    "status": {"cols": 4, "rows": 1},
}
MAX_GRID_COLS = 6
MAX_GRID_ROWS = 12

# Built-in remote buttons (non-source grids). zone drives layout on the remote page.
STATIC_BUTTON_CATALOG: dict[str, list[dict[str, Any]]] = {
    "master": [
        {"id": "power_toggle", "title": "Power", "variant": "primary"},
        {"id": "mute_toggle", "title": "Mute"},
        {"id": "vol_down", "title": "−", "aria_label": "Volume down"},
        {"id": "vol_up", "title": "+", "aria_label": "Volume up"},
    ],
    "power": [
        {"id": "power_on", "title": "Power On", "variant": "success"},
        {"id": "power_off", "title": "Power Off", "variant": "danger"},
        {"id": "reboot", "title": "Reboot"},
    ],
    "volume": [
        {"id": "vol_0", "title": "0%", "zone": "presets"},
        {"id": "vol_25", "title": "25%", "zone": "presets"},
        {"id": "vol_50", "title": "50%", "zone": "presets"},
        {"id": "vol_75", "title": "75%", "zone": "presets"},
        {"id": "vol_100", "title": "100%", "zone": "presets"},
    ],
    "navigation": [
        {"id": "up", "title": "Up", "aria_label": "Up", "zone": "dpad"},
        {"id": "left", "title": "Left", "aria_label": "Left", "zone": "dpad"},
        {"id": "ok", "title": "OK", "aria_label": "OK", "zone": "dpad", "variant": "primary"},
        {"id": "right", "title": "Right", "aria_label": "Right", "zone": "dpad"},
        {"id": "down", "title": "Down", "aria_label": "Down", "zone": "dpad"},
        {"id": "menu", "title": "Menu", "zone": "actions"},
        {"id": "home", "title": "Home", "zone": "actions"},
        {"id": "back", "title": "Back", "zone": "actions"},
        {"id": "exit", "title": "Exit", "zone": "actions"},
        {"id": "info", "title": "Info", "zone": "actions"},
    ],
    "picture": [
        {"id": "screen_fit", "title": "Screen Fit"},
        {"id": "aspect_16_9", "title": "16:9"},
        {"id": "aspect_4_3", "title": "4:3"},
    ],
    "status": [
        {"id": "refresh", "title": "Refresh", "action": "refresh"},
        {"id": "reboot", "title": "Reboot"},
        {"id": "query_power", "title": "Query Power"},
        {"id": "query_input", "title": "Query Input"},
    ],
}


def _ensure_maps_dir() -> Path:
    MAPS_DIR.mkdir(exist_ok=True)
    return MAPS_DIR


def load_displays() -> dict[str, Any]:
    if not DISPLAYS_PATH.exists():
        return {"displays": {}, "locations": {}, "location_order": []}
    data = yaml.safe_load(DISPLAYS_PATH.read_text()) or {"displays": {}}
    return _ensure_locations(data)


def _ensure_locations(data: dict[str, Any]) -> dict[str, Any]:
    """Ensure every room belongs to a location; bootstrap default site if missing."""
    displays = data.setdefault("displays", {})
    locations = data.setdefault("locations", {})
    order = list(data.get("location_order") or [])
    if not locations:
        locations["main"] = {"title": "Main site", "host": "", "port": 8080, "note": ""}
        order = ["main"]
    order = [lid for lid in order if lid in locations]
    for lid in locations:
        if lid not in order:
            order.append(lid)
    default_loc = order[0] if order else "main"
    for rid, entry in displays.items():
        if not entry.get("location"):
            entry["location"] = default_loc
    data["locations"] = locations
    data["location_order"] = order
    return data


def save_displays(data: dict[str, Any]) -> None:
    data = _ensure_locations(data)
    DISPLAYS_PATH.write_text(yaml.safe_dump(data, sort_keys=False, default_flow_style=False))


def default_location_id() -> str:
    data = load_displays()
    order = data.get("location_order") or []
    return order[0] if order else "main"


def list_location_ids() -> list[str]:
    data = load_displays()
    return list(data.get("location_order") or [])


def get_location(location_id: str) -> dict[str, Any] | None:
    data = load_displays()
    entry = (data.get("locations") or {}).get(location_id)
    if not entry:
        return None
    return {"id": location_id, **entry}


def parse_remote_host_port(host: str, port: int = 8080) -> tuple[str, int]:
    """Normalize host input; extract port from pasted URLs like http://host:8080."""
    raw = str(host or "").strip()
    if not raw:
        return "", max(1, min(65535, int(port)))
    if raw.startswith("https://"):
        raw = raw[8:]
    elif raw.startswith("http://"):
        raw = raw[7:]
    raw = raw.rstrip("/")
    if "/" in raw:
        raw = raw.split("/")[0]
    if ":" in raw:
        if raw.startswith("["):
            end = raw.find("]")
            if end != -1 and len(raw) > end + 1 and raw[end + 1] == ":":
                port_str = raw[end + 2 :]
                if port_str.isdigit():
                    port = int(port_str)
                    raw = raw[: end + 1]
        else:
            host_part, port_str = raw.rsplit(":", 1)
            if port_str.isdigit():
                raw = host_part
                port = int(port_str)
    port = max(1, min(65535, int(port)))
    return raw.strip(), port


def remote_url_key(host: str, port: int = 8080) -> str | None:
    host, port = parse_remote_host_port(host, port)
    if not host:
        return None
    return f"{host.lower()}:{port}"


def normalize_location(raw: dict[str, Any]) -> dict[str, Any]:
    port = int(raw.get("port", 8080))
    host, port = parse_remote_host_port(str(raw.get("host") or "").strip(), port)
    return {
        "title": str(raw.get("title") or "").strip(),
        "host": host,
        "port": port,
        "note": str(raw.get("note") or "").strip(),
    }


def location_remote_url(location: dict[str, Any]) -> str | None:
    host = str(location.get("host") or "").strip()
    if not host:
        return None
    port = int(location.get("port", 8080))
    return f"http://{host}:{port}"


def room_id_available(room_id: str, *, exclude: str | None = None) -> bool:
    room_id = str(room_id or "").strip().lower()
    if not _SLUG_RE.match(room_id):
        return False
    if exclude and room_id == exclude:
        return True
    return get_display(room_id) is None


def location_id_available(location_id: str, *, exclude: str | None = None) -> bool:
    location_id = str(location_id or "").strip().lower()
    if not _SLUG_RE.match(location_id):
        return False
    if exclude and location_id == exclude:
        return True
    return get_location(location_id) is None


def find_duplicate_remote_url(
    host: str, port: int = 8080, *, exclude_id: str | None = None
) -> str | None:
    key = remote_url_key(host, port)
    if not key:
        return None
    for lid in list_location_ids():
        if exclude_id and lid == exclude_id:
            continue
        loc = get_location(lid)
        if not loc:
            continue
        other = remote_url_key(loc.get("host", ""), int(loc.get("port", 8080)))
        if other == key:
            return lid
    return None


def rooms_for_location(location_id: str) -> list[str]:
    data = load_displays()
    displays = data.get("displays") or {}
    order = list(data.get("room_order") or [])
    ordered = [rid for rid in order if rid in displays]
    for rid in displays:
        if rid not in ordered:
            ordered.append(rid)
    default_loc = default_location_id()
    return [rid for rid in ordered if (displays.get(rid) or {}).get("location", default_loc) == location_id]


def location_payload(location_id: str) -> dict[str, Any]:
    loc = get_location(location_id)
    if not loc:
        raise KeyError(location_id)
    remote = location_remote_url(loc)
    room_ids = rooms_for_location(location_id)
    return {
        "id": location_id,
        "title": loc.get("title") or location_id,
        "host": loc.get("host") or "",
        "port": int(loc.get("port", 8080)),
        "note": loc.get("note") or "",
        "remote_url": remote,
        "room_count": len(room_ids),
        "room_ids": room_ids,
    }


def list_locations() -> list[dict[str, Any]]:
    return [location_payload(lid) for lid in list_location_ids()]


def create_location(location_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not _SLUG_RE.match(location_id):
        raise ValueError("Location id must be lowercase letters, numbers, - or _")
    data = load_displays()
    locations = data.setdefault("locations", {})
    if location_id in locations:
        raise ValueError(f"Location already exists: {location_id}")
    entry = normalize_location(payload)
    if not entry["title"]:
        entry["title"] = location_id
    dup = find_duplicate_remote_url(entry["host"], entry["port"])
    if dup:
        other = get_location(dup)
        title = (other or {}).get("title") or dup
        raise ValueError(f'Remote URL already used by location "{title}" ({dup})')
    locations[location_id] = entry
    order = data.setdefault("location_order", [])
    if location_id not in order:
        order.append(location_id)
    save_displays(data)
    return get_location(location_id)  # type: ignore[return-value]


def upsert_location(location_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not _SLUG_RE.match(location_id):
        raise ValueError("Location id must be lowercase letters, numbers, - or _")
    data = load_displays()
    locations = data.setdefault("locations", {})
    current = normalize_location({**(locations.get(location_id) or {}), **payload})
    if not current["title"]:
        current["title"] = location_id
    dup = find_duplicate_remote_url(current["host"], current["port"], exclude_id=location_id)
    if dup:
        other = get_location(dup)
        title = (other or {}).get("title") or dup
        raise ValueError(f'Remote URL already used by location "{title}" ({dup})')
    locations[location_id] = current
    order = data.setdefault("location_order", [])
    if location_id not in order:
        order.append(location_id)
    save_displays(data)
    return get_location(location_id)  # type: ignore[return-value]


def set_location_order(location_ids: list[str]) -> list[str]:
    data = load_displays()
    locations = data.get("locations") or {}
    cleaned: list[str] = []
    seen: set[str] = set()
    for lid in location_ids:
        lid = str(lid).strip().lower()
        if lid in locations and lid not in seen:
            cleaned.append(lid)
            seen.add(lid)
    for lid in locations:
        if lid not in seen:
            cleaned.append(lid)
    data["location_order"] = cleaned
    save_displays(data)
    return cleaned


def delete_location(location_id: str, *, reassign_to: str | None = None) -> bool:
    data = load_displays()
    locations = data.get("locations") or {}
    if location_id not in locations:
        return False
    displays = data.get("displays") or {}
    affected = [rid for rid, entry in displays.items() if entry.get("location") == location_id]
    if affected:
        target = reassign_to or default_location_id()
        if target == location_id or target not in locations:
            raise ValueError("Cannot delete location with rooms unless reassign_to is set")
        for rid in affected:
            displays[rid]["location"] = target
    del locations[location_id]
    order = [lid for lid in (data.get("location_order") or []) if lid != location_id]
    data["location_order"] = order
    save_displays(data)
    return True


def resolve_display_location(display: dict[str, Any]) -> dict[str, Any] | None:
    loc_id = str(display.get("location") or default_location_id())
    return get_location(loc_id)


def display_location_id(display: dict[str, Any]) -> str:
    return str(display.get("location") or default_location_id())


def room_path(location_id: str, display_id: str) -> str:
    return f"/d/{location_id}/{display_id}"


def room_setup_path(location_id: str, display_id: str) -> str:
    return f"/d/{location_id}/{display_id}/setup"


def resolve_room_route(location_id: str, display_id: str) -> dict[str, Any] | None:
    if not get_location(location_id):
        return None
    display = get_display(display_id)
    if not display:
        return None
    if display_location_id(display) != location_id:
        return None
    return display


def legacy_room_redirect(display_id: str, *, setup: bool = False) -> str | None:
    display = get_display(display_id)
    if not display:
        return None
    loc_id = display_location_id(display)
    return room_setup_path(loc_id, display_id) if setup else room_path(loc_id, display_id)


def enrich_auth_user(user: dict[str, Any]) -> dict[str, Any]:
    """Add location_id and remote_url for room users."""
    payload = dict(user)
    if payload.get("role") == "location_admin" and payload.get("location_id"):
        payload["scope"] = "location"
    if payload.get("role") == "admin":
        payload["scope"] = "master"
    if payload.get("role") == "room" and payload.get("display_id"):
        display = get_display(str(payload["display_id"]))
        if display:
            loc_id = display_location_id(display)
            payload["location_id"] = loc_id
            payload["remote_url"] = room_path(loc_id, display["id"])
            payload["setup_url"] = room_setup_path(loc_id, display["id"])
            payload["scope"] = "room"
    return payload


def list_display_ids() -> list[str]:
    data = load_displays()
    displays = data.get("displays") or {}
    order = list(data.get("room_order") or [])
    order = [rid for rid in order if rid in displays]
    for rid in displays:
        if rid not in order:
            order.append(rid)
    return order


def set_room_order(display_ids: list[str]) -> list[str]:
    data = load_displays()
    displays = data.get("displays") or {}
    cleaned = []
    seen: set[str] = set()
    for rid in display_ids:
        rid = str(rid).strip().lower()
        if rid in displays and rid not in seen:
            cleaned.append(rid)
            seen.add(rid)
    for rid in displays:
        if rid not in seen:
            cleaned.append(rid)
    data["room_order"] = cleaned
    save_displays(data)
    return cleaned


def get_display(display_id: str) -> dict[str, Any] | None:
    displays = load_displays().get("displays") or {}
    entry = displays.get(display_id)
    if not entry:
        return None
    return {"id": display_id, **entry}


def create_display(display_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not _SLUG_RE.match(display_id):
        raise ValueError("Room id must be lowercase letters, numbers, - or _")
    data = load_displays()
    displays = data.setdefault("displays", {})
    if display_id in displays:
        raise ValueError(f"Room already exists: {display_id}")

    title = str(payload.get("title", "")).strip()
    ip = str(payload.get("ip", "")).strip()
    if not title:
        raise ValueError("TV name is required")
    if not ip:
        raise ValueError("IP address is required")

    displays[display_id] = {
        "title": title,
        "model": str(payload.get("model") or "WM55B"),
        "ip": ip,
        "port": int(payload.get("port", 1515)),
        "device_id": int(payload.get("device_id", 0)),
        "location": str(payload.get("location") or default_location_id()).strip().lower(),
        "sources": payload.get("sources") or [],
    }
    order = data.setdefault("room_order", [])
    if display_id not in order:
        order.append(display_id)
    save_displays(data)
    template_id = str(payload.get("template") or "").strip()
    if not template_id:
        template_id = str(load_layout_templates().get("default_template") or "").strip()
    if template_id:
        include_sources = payload.get("template_sources", True)
        if not isinstance(include_sources, bool):
            include_sources = bool(include_sources)
        apply_layout_template(display_id, template_id, include_sources=include_sources)
    return get_display(display_id)  # type: ignore[return-value]


def upsert_display(display_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not _SLUG_RE.match(display_id):
        raise ValueError("Display id must be lowercase alphanumeric with - or _")
    data = load_displays()
    displays = data.setdefault("displays", {})
    current = displays.get(display_id, {})
    for key in ("title", "model", "ip", "port", "device_id", "location"):
        if key in payload and payload[key] is not None:
            current[key] = payload[key]
    if "layout" in payload and payload["layout"] is not None:
        current["layout"] = normalize_layout(payload["layout"])
    if "sources" in payload and payload["sources"] is not None:
        current["sources"] = payload["sources"]
    displays[display_id] = current
    save_displays(data)
    return get_display(display_id)  # type: ignore[return-value]


def delete_display(display_id: str) -> bool:
    data = load_displays()
    displays = data.get("displays") or {}
    if display_id not in displays:
        return False
    del displays[display_id]
    order = data.get("room_order") or []
    data["room_order"] = [rid for rid in order if rid != display_id]
    save_displays(data)
    map_file = map_path(display_id)
    if map_file.exists():
        map_file.unlink()
    return True


def rename_display(old_id: str, new_id: str) -> dict[str, Any]:
    new_id = str(new_id or "").strip().lower()
    if not _SLUG_RE.match(new_id):
        raise ValueError("Room id must be lowercase letters, numbers, - or _")
    if new_id == old_id:
        display = get_display(old_id)
        if not display:
            raise KeyError(f"Unknown display: {old_id}")
        return display
    if get_display(new_id):
        raise ValueError(f"Room already exists: {new_id}")
    data = load_displays()
    displays = data.get("displays") or {}
    if old_id not in displays:
        raise KeyError(f"Unknown display: {old_id}")
    displays[new_id] = displays.pop(old_id)
    order = data.get("room_order") or []
    data["room_order"] = [new_id if rid == old_id else rid for rid in order]
    save_displays(data)
    old_map = map_path(old_id)
    new_map = map_path(new_id)
    if old_map.exists():
        if new_map.exists():
            new_map.unlink()
        old_map.rename(new_map)
    from auth import rename_room_credentials

    rename_room_credentials(old_id, new_id)
    display = get_display(new_id)
    if not display:
        raise KeyError(f"Unknown display: {new_id}")
    return display


def rename_location(old_id: str, new_id: str) -> dict[str, Any]:
    new_id = str(new_id or "").strip().lower()
    if not _SLUG_RE.match(new_id):
        raise ValueError("Location id must be lowercase letters, numbers, - or _")
    if new_id == old_id:
        loc = get_location(old_id)
        if not loc:
            raise KeyError(f"Unknown location: {old_id}")
        return loc
    data = load_displays()
    locations = data.get("locations") or {}
    if old_id not in locations:
        raise KeyError(f"Unknown location: {old_id}")
    if new_id in locations:
        raise ValueError(f"Location already exists: {new_id}")
    locations[new_id] = locations.pop(old_id)
    order = data.get("location_order") or []
    data["location_order"] = [new_id if lid == old_id else lid for lid in order]
    displays = data.get("displays") or {}
    for entry in displays.values():
        if entry.get("location") == old_id:
            entry["location"] = new_id
    save_displays(data)
    loc = get_location(new_id)
    if not loc:
        raise KeyError(f"Unknown location: {new_id}")
    return loc


def slug_from_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "room"


def load_source_catalog() -> dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {"categories": {}, "catalog": []}
    return yaml.safe_load(CATALOG_PATH.read_text()) or {"categories": {}, "catalog": []}


def category_labels() -> dict[str, str]:
    data = load_source_catalog()
    return dict(data.get("categories") or {})


def normalize_category(value: str | None, fallback: str = "sources") -> str:
    cat = (value or "").strip().lower()
    if cat in VALID_CATEGORIES:
        return cat
    if value is True or str(value).lower() == "true":
        return "builtin"
    return fallback


def source_category(src: dict[str, Any], catalog_entry: dict[str, Any] | None = None) -> str:
    if src.get("category"):
        return normalize_category(src["category"])
    if src.get("builtin"):
        return "builtin"
    if catalog_entry:
        return normalize_category(catalog_entry.get("default_category"), "sources")
    return "sources"


def default_button_order() -> dict[str, list[str]]:
    return {section: [b["id"] for b in buttons] for section, buttons in STATIC_BUTTON_CATALOG.items()}


def static_button_catalog() -> dict[str, list[dict[str, Any]]]:
    return {k: [dict(b) for b in v] for k, v in STATIC_BUTTON_CATALOG.items()}


def _normalize_button_order(raw_order: dict[str, Any] | None) -> dict[str, list[str]]:
    raw_order = raw_order or {}
    defaults = default_button_order()
    normalized: dict[str, list[str]] = {}
    for section, default_ids in defaults.items():
        custom = list(raw_order.get(section) or [])
        valid = set(default_ids)
        if section == "power":
            valid.add("power_toggle")
        if section in ("volume", "master"):
            valid.add("mute_toggle")
        if section == "master":
            valid.add("power_toggle")
        ordered = [str(bid) for bid in custom if str(bid) in valid]
        for bid in default_ids:
            if bid not in ordered:
                ordered.append(bid)
        normalized[section] = ordered
    for section, custom in raw_order.items():
        if section in VALID_CATEGORIES and section not in normalized:
            normalized[section] = [str(bid) for bid in custom if str(bid).strip()]
    return normalized


def _normalize_button_labels(raw_labels: dict[str, Any] | None) -> dict[str, str]:
    labels: dict[str, str] = {}
    for key, value in (raw_labels or {}).items():
        text = str(value).strip()
        if text:
            labels[str(key)] = text
    return labels


def _layout_mode_to_grid(mode: str, fallback_cols: int = 2) -> dict[str, int]:
    mode = str(mode or "").strip().lower()
    if mode in ("stack", "cols-1", "grid-1"):
        return {"cols": 1, "rows": 0}
    if mode == "row":
        return {"cols": max(1, min(MAX_GRID_COLS, fallback_cols)), "rows": 1}
    if mode.startswith("cols-"):
        try:
            cols = int(mode.split("-", 1)[1])
        except ValueError:
            cols = fallback_cols
        return {"cols": max(1, min(MAX_GRID_COLS, cols)), "rows": 0}
    if mode.startswith("grid-"):
        try:
            cols = int(mode.split("-", 1)[1])
        except ValueError:
            cols = fallback_cols
        return {"cols": max(1, min(MAX_GRID_COLS, cols)), "rows": 0}
    return {"cols": max(1, min(MAX_GRID_COLS, fallback_cols)), "rows": 0}


def _normalize_grid_spec(raw: Any, fallback_cols: int = 2) -> dict[str, int]:
    fallback_cols = max(1, min(MAX_GRID_COLS, int(fallback_cols)))
    if isinstance(raw, dict):
        cols = int(raw.get("cols", fallback_cols))
        rows = int(raw.get("rows", 0))
    elif isinstance(raw, str):
        return _layout_mode_to_grid(raw, fallback_cols)
    else:
        return {"cols": fallback_cols, "rows": 0}
    return {
        "cols": max(1, min(MAX_GRID_COLS, cols)),
        "rows": max(0, min(MAX_GRID_ROWS, rows)),
    }


def _normalize_grid_size(raw_size: dict[str, Any] | None, default_cols: int = 2) -> dict[str, dict[str, int]]:
    raw_size = raw_size or {}
    default_cols = max(1, min(MAX_GRID_COLS, int(default_cols)))
    normalized: dict[str, dict[str, int]] = {}
    for key, value in raw_size.items():
        normalized[str(key)] = _normalize_grid_spec(value, default_cols)
    for section, default in DEFAULT_GRID_SIZE.items():
        normalized.setdefault(section, dict(default))
    for cat in VALID_CATEGORIES:
        normalized.setdefault(cat, {"cols": default_cols, "rows": 0})
    return normalized


def resolve_section_grid(section: str, layout: dict[str, Any], button_count: int = 0) -> dict[str, int]:
    grids = layout.get("grid_size") or {}
    default_cols = int(layout.get("columns", 2))
    if section in grids:
        spec = dict(grids[section])
    elif section in DEFAULT_GRID_SIZE:
        spec = dict(DEFAULT_GRID_SIZE[section])
    elif section in VALID_CATEGORIES:
        spec = {"cols": max(1, min(MAX_GRID_COLS, default_cols)), "rows": 0}
    else:
        spec = {"cols": max(1, min(MAX_GRID_COLS, default_cols)), "rows": 0}
    return effective_grid(spec, button_count)


def resolve_zone_grid(section: str, zone: str, layout: dict[str, Any], button_count: int = 0) -> dict[str, int]:
    grids = layout.get("grid_size") or {}
    key = f"{section}_{zone}"
    default_cols = int(layout.get("columns", 2))
    if key in grids:
        return effective_grid(grids[key], button_count)
    if zone == "presets" and section == "volume":
        if key not in grids and section in grids:
            return effective_grid(grids[section], button_count)
        return effective_grid(grids.get(key, DEFAULT_GRID_SIZE.get("volume_presets", {"cols": 5, "rows": 1})), button_count)
    if zone == "actions" and section == "navigation":
        return effective_grid(
            grids.get(key, DEFAULT_GRID_SIZE.get("navigation_actions", {"cols": 5, "rows": 1})),
            button_count,
        )
    return resolve_section_grid(section, layout, button_count)


def effective_grid(spec: dict[str, int], button_count: int) -> dict[str, int | bool]:
    cols = max(1, int(spec.get("cols", 1)))
    stored_rows = int(spec.get("rows", 0))
    count = max(0, int(button_count))
    fixed = stored_rows > 0
    if count > 0 and cols > count:
        cols = count
    if stored_rows <= 0:
        rows = max(1, (count + cols - 1) // cols) if count else 1
    elif count > cols * stored_rows:
        rows = max(stored_rows, (count + cols - 1) // cols)
        fixed = False
    else:
        rows = stored_rows
    return {"cols": cols, "rows": rows, "fixed": fixed}


def _normalize_hidden_buttons(raw: Any) -> list[str]:
    hidden: list[str] = []
    seen: set[str] = set()
    if isinstance(raw, dict):
        for key, value in raw.items():
            if value and str(key).strip() and str(key) not in seen:
                seen.add(str(key))
                hidden.append(str(key))
        return hidden
    for item in raw or []:
        bid = str(item).strip()
        if bid and bid not in seen:
            seen.add(bid)
            hidden.append(bid)
    return hidden


def hidden_button_ids(layout: dict[str, Any]) -> set[str]:
    return set(layout.get("hidden_buttons") or [])


def normalize_layout(raw: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw or {}
    size = str(raw.get("button_size", "md")).lower()
    if size not in VALID_BUTTON_SIZES:
        size = "md"
    columns = int(raw.get("columns", 2))
    columns = max(1, min(MAX_GRID_COLS, columns))

    section_order = list(raw.get("section_order") or DEFAULT_SECTION_ORDER)
    section_order = [s for s in section_order if s in VALID_SECTIONS]
    for cat in DEFAULT_CATEGORY_ORDER:
        if cat not in section_order:
            section_order.append(cat)

    category_order = list(raw.get("category_order") or DEFAULT_CATEGORY_ORDER)
    category_order = [c for c in category_order if c in VALID_CATEGORIES]
    for c in DEFAULT_CATEGORY_ORDER:
        if c not in category_order:
            category_order.append(c)

    legacy_layout = raw.get("button_layout") or {}
    grid_raw = dict(raw.get("grid_size") or {})
    for key, value in legacy_layout.items():
        grid_raw.setdefault(key, value)

    power_mode = str(raw.get("power_mode", "split")).lower()
    if power_mode not in VALID_POWER_MODES:
        power_mode = "split"

    mute_mode = str(raw.get("mute_mode", "split")).lower()
    if mute_mode not in VALID_MUTE_MODES:
        mute_mode = "split"

    button_style = raw.get("button_style") or {"default": "both"}
    if isinstance(button_style, str):
        button_style = {"default": button_style if button_style in VALID_BUTTON_STYLES else "both"}
    else:
        normalized_style: dict[str, str] = {}
        for key, value in button_style.items():
            style = str(value).lower()
            if style in VALID_BUTTON_STYLES:
                normalized_style[str(key)] = style
        button_style = normalized_style or {"default": "both"}

    button_icons = {}
    for key, value in (raw.get("button_icons") or {}).items():
        icon = str(value).strip()
        if icon:
            button_icons[str(key)] = icon

    return {
        "button_size": size,
        "columns": columns,
        "section_order": section_order,
        "category_order": category_order,
        "button_order": _normalize_button_order(raw.get("button_order")),
        "button_labels": _normalize_button_labels(raw.get("button_labels")),
        "grid_size": _normalize_grid_size(grid_raw, columns),
        "power_mode": power_mode,
        "mute_mode": mute_mode,
        "button_style": button_style,
        "button_icons": button_icons,
        "hidden_buttons": _normalize_hidden_buttons(raw.get("hidden_buttons")),
    }


def resolve_static_buttons(section: str, layout: dict[str, Any]) -> list[dict[str, Any]]:
    catalog = {b["id"]: dict(b) for b in STATIC_BUTTON_CATALOG.get(section, [])}
    labels = layout.get("button_labels") or {}
    order = list((layout.get("button_order") or {}).get(section) or default_button_order().get(section, []))

    if section == "master":
        order = [bid for bid in order if bid not in ("power_on", "power_off", "mute_on", "mute_off")]
        if "power_toggle" not in order:
            order.insert(0, "power_toggle")
        if "mute_toggle" not in order:
            up_idx = order.index("vol_up") if "vol_up" in order else len(order)
            order.insert(up_idx, "mute_toggle")
        catalog["power_toggle"] = dict(POWER_TOGGLE_BUTTON)
        catalog["mute_toggle"] = dict(MUTE_TOGGLE_BUTTON)

    if section == "power" and layout.get("power_mode") == "toggle":
        order = [bid for bid in order if bid not in ("power_on", "power_off")]
        if "power_toggle" not in order:
            order.insert(0, "power_toggle")
        catalog["power_toggle"] = dict(POWER_TOGGLE_BUTTON)

    if section == "volume" and layout.get("mute_mode") == "toggle" and "master" not in (layout.get("section_order") or []):
        order = [bid for bid in order if bid not in ("mute_on", "mute_off")]
        if "mute_toggle" not in order:
            const_idx = next((i for i, bid in enumerate(order) if bid == "vol_up"), 1)
            order.insert(const_idx, "mute_toggle")
        catalog["mute_toggle"] = dict(MUTE_TOGGLE_BUTTON)

    hidden = hidden_button_ids(layout)
    resolved: list[dict[str, Any]] = []
    for bid in order:
        if bid in hidden:
            continue
        base = catalog.get(bid)
        if not base:
            continue
        if bid in labels:
            base["title"] = labels[bid]
        resolved.append(enrich_remote_button(base, section, layout))
    return resolved


def sort_items_by_button_order(
    items: list[dict[str, Any]],
    section: str,
    layout: dict[str, Any],
    *,
    id_key: str = "id",
) -> list[dict[str, Any]]:
    order_list = (layout.get("button_order") or {}).get(section) or []
    order_map = {str(item_id): idx for idx, item_id in enumerate(order_list)}
    return sorted(
        items,
        key=lambda x: (
            order_map.get(str(x.get(id_key)), 999),
            int(x.get("order", 999)),
            str(x.get("title", "")),
        ),
    )


def sync_source_orders_from_layout(display: dict[str, Any], layout: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply per-grid button order from layout onto source entries."""
    button_order = layout.get("button_order") or {}
    sources = [dict(src) for src in display.get("sources") or []]
    for section in VALID_CATEGORIES:
        ids = button_order.get(section) or []
        order_map = {str(item_id): idx for idx, item_id in enumerate(ids)}
        for src in sources:
            if source_category(src) != section:
                continue
            src_id = str(src.get("id") or "")
            if src_id in order_map:
                src["order"] = order_map[src_id]
    return sources


def build_remote_sections(
    display: dict[str, Any],
    layout: dict[str, Any],
    by_category: dict[str, list[dict[str, Any]]],
    labels: dict[str, str],
) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    for key in layout.get("section_order") or DEFAULT_SECTION_ORDER:
        if key in STATIC_BUTTON_SECTIONS:
            buttons = resolve_static_buttons(key, layout)
            if not buttons:
                continue
            sections.append(
                {
                    "id": key,
                    "type": "static",
                    "label": labels.get(key, key),
                    "span": 2 if key == "navigation" else 1,
                    "buttons": buttons,
                    "grid": resolve_section_grid(key, layout, len(buttons)),
                    "button_style": button_style_for(key, layout),
                    "zone_grids": {
                        "presets": resolve_zone_grid(
                            key,
                            "presets",
                            layout,
                            len([b for b in buttons if b.get("zone") == "presets"]),
                        ),
                        "actions": resolve_zone_grid(
                            key,
                            "actions",
                            layout,
                            len([b for b in buttons if b.get("zone") == "actions"]),
                        ),
                    },
                }
            )
        elif key in VALID_CATEGORIES:
            items = sort_items_by_button_order(by_category.get(key) or [], key, layout)
            if not items:
                continue
            section_buttons = [
                enrich_remote_button(
                    {
                        "id": item["id"],
                        "title": item.get("title") or item["id"],
                        "variant": "warn" if item.get("unstable") or item.get("provision") else "",
                        "hint": "Provisioned"
                        if item.get("provision")
                        else ("Unstable query" if item.get("unstable") else item.get("title")),
                    },
                    key,
                    layout,
                )
                for item in items
            ]
            sections.append(
                {
                    "id": key,
                    "type": "sources",
                    "label": labels.get(key, key),
                    "span": 1,
                    "grid": resolve_section_grid(key, layout, len(section_buttons)),
                    "button_style": button_style_for(key, layout),
                    "buttons": section_buttons,
                }
            )
    return sections


def get_layout(display: dict[str, Any]) -> dict[str, Any]:
    return normalize_layout(display.get("layout"))


def section_labels() -> dict[str, str]:
    cats = category_labels()
    return {
        "master": "Master",
        "power": "Power",
        "volume": "Volume",
        "navigation": "Navigation",
        "picture": "Picture",
        "status": "Status",
        **cats,
    }


def map_path(display_id: str) -> Path:
    return _ensure_maps_dir() / f"{display_id}.json"


def load_display_map(display_id: str) -> dict[str, Any] | None:
    path = map_path(display_id)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def save_display_map(display_id: str, data: dict[str, Any]) -> Path:
    path = map_path(display_id)
    path.write_text(json.dumps(data, indent=2))
    return path


def mdc_config(display: dict[str, Any]) -> MdcConfig:
    return MdcConfig(
        host=str(display["ip"]),
        port=int(display.get("port", 1515)),
        device_id=int(display.get("device_id", 0)),
    )


def broadlink_config(display: dict[str, Any]) -> BroadlinkConfig | None:
    """Create Broadlink config from display if it has broadlink settings."""
    broadlink_cfg = display.get("broadlink")
    if not broadlink_cfg or not isinstance(broadlink_cfg, dict):
        return None
    
    host = broadlink_cfg.get("host") or broadlink_cfg.get("ip")
    if not host:
        return None
    
    return BroadlinkConfig(
        host=str(host),
        port=int(broadlink_cfg.get("port", 80)),
        mac=str(broadlink_cfg.get("mac", "")),
        device_type=int(str(broadlink_cfg.get("device_type", "0x61A2")), 16) 
            if isinstance(broadlink_cfg.get("device_type"), str) 
            else int(broadlink_cfg.get("device_type", 0x61A2)),
        name=display.get("title", "Broadlink Device"),
    )


def has_broadlink(display: dict[str, Any]) -> bool:
    """Check if display has Broadlink IR/RF configuration."""
    return broadlink_config(display) is not None


def _send_broadlink_command(
    display_id: str, cmd: str, bl_cfg: BroadlinkConfig, display: dict[str, Any]
) -> dict[str, Any]:
    """Send IR/RF command via Broadlink device."""
    # Load IR codes from display config or external file
    ir_codes = display.get("ir_codes", {})
    
    # Also try loading from external file if specified
    ir_codes_file = display.get("ir_codes_file")
    if ir_codes_file:
        external_codes = load_ir_codes(ROOT / ir_codes_file)
        ir_codes = {**external_codes, **ir_codes}  # Display config takes precedence
    
    if cmd not in ir_codes:
        known = ", ".join(sorted(ir_codes.keys()))
        raise KeyError(f"Unknown IR command {cmd!r}. Available: {known}")
    
    # Send the IR code
    client = BroadlinkClient(bl_cfg)
    ir_code = ir_codes[cmd]
    send_result = client.send_code(ir_code)
    
    return {
        "ok": send_result.get("ok", False),
        "display_id": display_id,
        "command": cmd,
        "method": "broadlink_ir",
        "device": bl_cfg.host,
        "error": send_result.get("error"),
        "message": send_result.get("message"),
    }


def parse_code(value: str | int) -> int:
    if isinstance(value, int):
        return value
    return int(str(value), 16)


def input_packet(code: str | int, device_id: int = 0) -> str:
    c = parse_code(code)
    return format_hex(build_packet(0x14, device_id, bytes([c]))).replace(" ", "")


def volume_packet(level: int, device_id: int = 0) -> str:
    return format_hex(build_packet(0x12, device_id, bytes([level]))).replace(" ", "")


def command_packet(command: int, data: bytes, device_id: int = 0) -> str:
    return format_hex(build_packet(command, device_id, data)).replace(" ", "")


def build_static_commands(device_id: int = 0) -> dict[str, str]:
    d = device_id
    key = lambda k: command_packet(0xC1, bytes([k]), d)
    return {
        "power_on": command_packet(0x11, bytes([1]), d),
        "power_off": command_packet(0x11, bytes([0]), d),
        "reboot": command_packet(0x11, bytes([2]), d),
        "vol_up": command_packet(0x62, bytes([0]), d),
        "vol_down": command_packet(0x62, bytes([1]), d),
        "mute_on": command_packet(0x13, bytes([1]), d),
        "mute_off": command_packet(0x13, bytes([0]), d),
        "menu": command_packet(0x34, bytes([1]), d),
        "info": command_packet(0x17, bytes([1]), d),
        "home": command_packet(0x34, bytes([0]), d),
        "up": key(0x06),
        "down": key(0x08),
        "left": key(0x12),
        "right": key(0x14),
        "ok": key(0x11),
        "enter": key(0x11),
        "back": key(0x15),
        "return": key(0x15),
        "screen_fit": key(0xB5),
        "aspect_16_9": command_packet(0x15, bytes([1]), d),
        "aspect_4_3": command_packet(0x15, bytes([0x0B]), d),
        "exit": command_packet(0xB2, bytes([1, 0, 0, 0x40, 0x09, 0x04, 0x0A]), d),
        "query_power": command_packet(0x11, b"", d),
        "query_input": command_packet(0x14, b"", d),
        "query_mute": command_packet(0x13, b"", d),
        "query_volume": command_packet(0x12, b"", d),
        "query_status": command_packet(0x00, b"", d),
        "vol_0": volume_packet(0, d),
        "vol_25": volume_packet(25, d),
        "vol_50": volume_packet(50, d),
        "vol_75": volume_packet(75, d),
        "vol_100": volume_packet(100, d),
    }


def build_commands_for_display(display: dict[str, Any], discovered: dict[str, Any] | None = None) -> dict[str, str]:
    device_id = int(display.get("device_id", 0))
    commands = build_static_commands(device_id)

    if discovered:
        for item in discovered.get("inputs", []):
            packet = item.get("packet", "").lower()
            code = item.get("code", "")
            if packet:
                commands[f"input_{code}"] = packet
        for vol in discovered.get("volumes", []):
            level = vol.get("level")
            packet = vol.get("packet", "").lower()
            if level is not None and packet and vol.get("ok"):
                commands[f"vol_{level}"] = packet

    for src in display.get("sources") or []:
        if not src.get("enabled", True):
            continue
        slug = src.get("id") or src.get("slug")
        code = src.get("code")
        if slug and code:
            commands[str(slug)] = input_packet(code, device_id).lower()

    return commands


def source_label_map(display: dict[str, Any], discovered: dict[str, Any] | None = None) -> dict[int, str]:
    labels: dict[int, str] = {}
    sources_by_code: dict[int, dict[str, Any]] = {}
    for src in display.get("sources") or []:
        if not src.get("enabled", True):
            continue
        code = parse_code(src["code"])
        title = str(src.get("title") or src.get("id") or f"0x{code:02X}")
        labels[code] = title
        sources_by_code[code] = src

    if discovered:
        for item in discovered.get("inputs", []):
            set_code = item.get("code_dec")
            if set_code is None:
                continue
            qa = item.get("query_after") or {}
            query_val = qa.get("value_dec")
            if query_val is None or query_val == set_code:
                continue
            src = sources_by_code.get(set_code)
            if not src:
                continue
            title = str(src.get("title") or src.get("id") or f"0x{set_code:02X}")
            existing = labels.get(query_val)
            if existing is None or source_category(src) == "wireless":
                labels[query_val] = title

    return labels


def source_title_for_id(display: dict[str, Any], source_id: str) -> str | None:
    for src in display.get("sources") or []:
        if str(src.get("id")) == source_id and src.get("enabled", True):
            return str(src.get("title") or source_id)
    return None


def wireless_source_ids(display: dict[str, Any]) -> set[str]:
    return {
        str(src.get("id"))
        for src in display.get("sources") or []
        if src.get("enabled", True) and source_category(src) == "wireless"
    }


def input_aliases(display: dict[str, Any]) -> dict[str, int]:
    aliases: dict[str, int] = {}
    for src in display.get("sources") or []:
        if not src.get("enabled", True):
            continue
        slug = src.get("id")
        if slug:
            aliases[str(slug)] = parse_code(src["code"])
    return aliases


def unstable_codes(discovered: dict[str, Any] | None) -> set[int]:
    if not discovered:
        return set()
    return {item["code_dec"] for item in discovered.get("inputs", []) if not item.get("stable")}


def remote_payload(display: dict[str, Any], discovered: dict[str, Any] | None = None) -> dict[str, Any]:
    unstable = unstable_codes(discovered)
    labels = category_labels()
    layout = get_layout(display)
    by_category: dict[str, list[dict[str, Any]]] = {k: [] for k in labels}
    sources_flat = []
    for src in display.get("sources") or []:
        if not src.get("enabled", True):
            continue
        code = parse_code(src["code"])
        cat = source_category(src)
        item = {
            "id": src.get("id"),
            "code": f"0x{code:02X}",
            "title": src.get("title") or src.get("id"),
            "category": cat,
            "order": int(src.get("order", 999)),
            "provision": bool(src.get("provision")),
            "unstable": code in unstable,
        }
        sources_flat.append(item)
        by_category.setdefault(cat, []).append(item)

    for cat in by_category:
        by_category[cat] = sort_items_by_button_order(by_category[cat], cat, layout)

    section_label_map = section_labels()
    remote_sections = build_remote_sections(display, layout, by_category, section_label_map)
    icon_svgs_map, icon_rev = live_icon_bundle()
    import importlib
    import button_icons as button_icons_module

    importlib.reload(button_icons_module)

    loc_id = display_location_id(display)
    loc = resolve_display_location(display)
    loc_title = (loc or {}).get("title") or loc_id
    loc_remote = location_remote_url(loc) if loc else None

    return {
        "id": display["id"],
        "title": display.get("title") or display["id"],
        "location": loc_id,
        "location_title": loc_title,
        "location_remote_url": loc_remote,
        "ip": display.get("ip"),
        "port": display.get("port", 1515),
        "device_id": display.get("device_id", 0),
        "sources": sources_flat,
        "categories": labels,
        "sources_by_category": by_category,
        "layout": layout,
        "section_labels": section_label_map,
        "remote_sections": remote_sections,
        "static_button_catalog": static_button_catalog(),
        "icon_catalog": icon_catalog(),
        "default_icons": dict(button_icons_module.DEFAULT_ICONS_BY_ID),
        "icon_svgs": icon_svgs_map,
        "icon_revision": icon_rev,
        "remote_url": room_path(loc_id, display["id"]),
        "setup_url": room_setup_path(loc_id, display["id"]),
    }


def setup_candidates(display: dict[str, Any], discovered: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Full catalog + discovery + saved config for the setup UI."""
    catalog_data = load_source_catalog()
    catalog = catalog_data.get("catalog") or []
    cat_labels = category_labels()
    device_id = int(display.get("device_id", 0))
    by_code: dict[str, dict[str, Any]] = {}

    for entry in catalog:
        code = str(entry["code"]).lower()
        by_code[code] = {
            "code": code,
            "id": entry.get("id") or code.replace("0x", "src_"),
            "title": entry.get("title") or code,
            "category": normalize_category(entry.get("default_category"), "sources"),
            "catalog": True,
            "note": entry.get("note"),
            "enabled": False,
            "provision": False,
            "discovered": False,
            "stable": None,
            "packet": input_packet(code, device_id),
        }

    if discovered:
        for item in discovered.get("inputs", []):
            code = str(item.get("code", "")).lower()
            row = by_code.setdefault(
                code,
                {
                    "code": code,
                    "id": code.replace("0x", "src_"),
                    "title": f"Source {code}",
                    "category": "other",
                    "catalog": False,
                    "enabled": False,
                    "provision": False,
                    "discovered": True,
                    "packet": item.get("packet") or input_packet(code, device_id),
                },
            )
            row["discovered"] = True
            row["stable"] = item.get("stable", False)
            row["set_value"] = (item.get("set") or {}).get("value")
            row["query_value"] = (item.get("query_after") or {}).get("value")
            row["packet"] = item.get("packet") or row.get("packet")

    for src in display.get("sources") or []:
        code = str(src.get("code", "")).lower()
        if not code.startswith("0x"):
            code = f"0x{parse_code(code):02X}".lower()
        row = by_code.setdefault(
            code,
            {
                "code": code,
                "id": src.get("id") or code.replace("0x", "src_"),
                "title": src.get("title") or code,
                "category": "sources",
                "catalog": False,
                "enabled": False,
                "provision": False,
                "packet": input_packet(code, device_id),
            },
        )
        row["id"] = src.get("id") or row["id"]
        row["title"] = src.get("title") or row["title"]
        row["enabled"] = bool(src.get("enabled", True))
        row["provision"] = bool(src.get("provision"))
        row["category"] = source_category(src, row if row.get("catalog") else None)
        if "order" in src:
            row["order"] = int(src["order"])

    result = list(by_code.values())
    for row in result:
        row["category_label"] = cat_labels.get(row["category"], row["category"])
    return sorted(result, key=lambda x: (x.get("category", ""), x.get("order", 999), x.get("code", "")))


def normalize_sources_for_save(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Persist sources shown on remote or marked provision."""
    cleaned: list[dict[str, Any]] = []
    for idx, src in enumerate(sources):
        if not src.get("enabled") and not src.get("provision"):
            continue
        code = str(src.get("code", "")).lower()
        if not code.startswith("0x"):
            code = f"0x{parse_code(code):02X}".lower()
        item = {
            "id": str(src.get("id") or code.replace("0x", "src_")),
            "code": code,
            "title": str(src.get("title") or code),
            "enabled": bool(src.get("enabled", True)),
            "category": normalize_category(src.get("category"), "sources"),
            "order": int(src.get("order", idx)),
        }
        if src.get("provision"):
            item["provision"] = True
        cleaned.append(item)
    return cleaned


def load_layout_templates() -> dict[str, Any]:
    if not TEMPLATES_PATH.exists():
        return {"default_template": "", "templates": {}}
    return yaml.safe_load(TEMPLATES_PATH.read_text()) or {"templates": {}}


def save_layout_templates(data: dict[str, Any]) -> None:
    TEMPLATES_PATH.write_text(yaml.safe_dump(data, sort_keys=False, default_flow_style=False))


def list_layout_template_summaries() -> list[dict[str, Any]]:
    data = load_layout_templates()
    templates = data.get("templates") or {}
    default_id = str(data.get("default_template") or "")
    return [
        {
            "id": tid,
            "title": str(tpl.get("title") or tid),
            "description": str(tpl.get("description") or ""),
            "default": tid == default_id,
        }
        for tid, tpl in templates.items()
    ]


def get_layout_template(template_id: str) -> dict[str, Any] | None:
    templates = load_layout_templates().get("templates") or {}
    tpl = templates.get(template_id)
    return dict(tpl) if tpl else None


def template_from_display(display: dict[str, Any], *, include_sources: bool = True) -> dict[str, Any]:
    payload: dict[str, Any] = {"layout": copy.deepcopy(get_layout(display))}
    if include_sources:
        payload["sources"] = [
            {k: src[k] for k in ("id", "enabled", "category", "order", "title", "provision") if k in src}
            for src in display.get("sources") or []
        ]
    return payload


def _catalog_code_by_id() -> dict[str, str]:
    catalog = load_source_catalog().get("catalog") or []
    return {str(entry.get("id")): str(entry.get("code")).lower() for entry in catalog if entry.get("id") and entry.get("code")}


def merge_source_template(
    existing: list[dict[str, Any]],
    template_sources: list[dict[str, Any]],
    display: dict[str, Any],
) -> list[dict[str, Any]]:
    by_id = {str(s.get("id")): dict(s) for s in existing if s.get("id")}
    code_by_id = _catalog_code_by_id()
    for pref in template_sources:
        sid = str(pref.get("id") or "").strip()
        if not sid:
            continue
        row = by_id.get(sid)
        if not row:
            code = code_by_id.get(sid)
            if not code:
                continue
            row = {"id": sid, "code": code, "title": str(pref.get("title") or sid)}
            by_id[sid] = row
        for key in ("enabled", "category", "order", "title", "provision"):
            if key in pref:
                row[key] = pref[key]
    return normalize_sources_for_save(list(by_id.values()))


def apply_layout_template(display_id: str, template_id: str, *, include_sources: bool = False) -> dict[str, Any]:
    display = get_display(display_id)
    if not display:
        raise KeyError(f"Unknown display: {display_id}")
    template = get_layout_template(template_id)
    if not template:
        raise ValueError(f"Unknown template: {template_id}")

    payload: dict[str, Any] = {}
    if template.get("layout"):
        layout = normalize_layout(copy.deepcopy(template["layout"]))
        payload["layout"] = layout
        merged = {**display, **payload}
        payload["sources"] = sync_source_orders_from_layout(merged, layout)

    if include_sources and template.get("sources"):
        payload["sources"] = merge_source_template(
            display.get("sources") or payload.get("sources") or [],
            template["sources"],
            display,
        )
    return upsert_display(display_id, payload)


def upsert_layout_template(template_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not _SLUG_RE.match(template_id):
        raise ValueError("Template id must be lowercase letters, numbers, - or _")
    data = load_layout_templates()
    templates = data.setdefault("templates", {})
    entry: dict[str, Any] = {
        "title": str(body.get("title") or template_id),
        "description": str(body.get("description") or ""),
        "layout": normalize_layout(body.get("layout") or {}),
    }
    if body.get("sources"):
        entry["sources"] = body["sources"]
    templates[template_id] = entry
    if body.get("set_default"):
        data["default_template"] = template_id
    save_layout_templates(data)
    return entry


def send_room_command(display_id: str, cmd: str) -> dict[str, Any]:
    """Send a named command to a room (MDC for displays, or IR/RF via Broadlink for STBs)."""
    import time

    from discover import parse_response

    display = get_display(display_id)
    if not display:
        raise KeyError(f"Unknown display: {display_id}")
    
    # Check if this display uses Broadlink for IR/RF control
    bl_cfg = broadlink_config(display)
    if bl_cfg and BROADLINK_AVAILABLE:
        return _send_broadlink_command(display_id, cmd, bl_cfg, display)
    
    # Original MDC-based logic for Samsung displays
    discovered = load_display_map(display_id)
    commands = build_commands_for_display(display, discovered)
    if cmd not in commands:
        known = ", ".join(sorted(commands))
        raise KeyError(f"Unknown command {cmd!r}. Available: {known}")

    client = MdcClient(mdc_config(display))
    payload = parse_hex(commands[cmd])
    reboot_method = None
    if cmd == "power_on":
        response = client.power_on()
    elif cmd == "power_off":
        response = client.power_off()
    elif cmd == "reboot":
        response, reboot_method = client.reboot()
    else:
        response = client.send_raw(payload)
    parsed = parse_response(response) if response else {"status": "no_response"}
    ack = bool(parsed.get("ack"))
    if cmd == "reboot":
        ack = reboot_method == "power_cycle" or ack
    result: dict[str, Any] = {
        "ok": True,
        "display_id": display_id,
        "command": cmd,
        "sent": format_hex(payload),
        "response": format_hex(response) if response else None,
        "parsed": parsed,
        "ack": ack,
    }
    if reboot_method:
        result["reboot_method"] = reboot_method
        if reboot_method == "power_cycle":
            result["note"] = "Panel rejected MDC reboot; performed power cycle instead."
    aliases = input_aliases(display)
    if cmd in aliases:
        code = aliases[cmd]
        wireless = wireless_source_ids(display)
        unstable = unstable_codes(discovered)
        delay = 2.0 if cmd in wireless or code in unstable else 0.8
        time.sleep(delay)
        query_resp = client.send_raw(parse_hex(commands["query_input"]))
        query_parsed = parse_response(query_resp) if query_resp else {"status": "no_response"}
        result["query_after"] = query_parsed
        result["input_code"] = f"0x{code:02X}"
        result["input_label"] = source_title_for_id(display, cmd)
    return result
