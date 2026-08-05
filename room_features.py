"""
Room-scoped AV feature helpers: Broadlink IR, EPG guide, beacon presence.
Used by server.py display API routes and the React remote UI.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from display_manager import (
    broadlink_config,
    get_display,
    has_broadlink,
    send_room_command,
)

ROOT = Path(__file__).resolve().parent
logger = logging.getLogger("room_features")

# In-memory beacon presence for demo / gateway reports
_BEACON_PRESENCE: dict[str, list[dict[str, Any]]] = {}


def _ir_codes_for(display: dict[str, Any]) -> dict[str, Any]:
    from broadlink_client import load_ir_codes

    codes = dict(display.get("ir_codes") or {})
    ir_file = display.get("ir_codes_file")
    if ir_file:
        external = load_ir_codes(ROOT / str(ir_file))
        codes = {**external, **codes}
    return codes


def is_dry_run(display: dict[str, Any]) -> bool:
    bl = display.get("broadlink") or {}
    if isinstance(bl, dict) and bl.get("dry_run"):
        return True
    host = (bl.get("host") or bl.get("ip") or "") if isinstance(bl, dict) else ""
    return host in ("", "0.0.0.0", "127.0.0.1", "dry-run")


def room_feature_summary(display: dict[str, Any]) -> dict[str, Any]:
    """Capability flags + channel list for the remote UI."""
    ir_codes = _ir_codes_for(display)
    epg = display.get("epg") if isinstance(display.get("epg"), dict) else {}
    beacons = display.get("beacons") if isinstance(display.get("beacons"), dict) else {}
    channels = list(epg.get("channels") or [])

    channel_cmds = [k for k in ir_codes if k.startswith("num_") or k in ("ch_up", "ch_down", "last", "guide")]
    nav_cmds = [k for k in ("up", "down", "left", "right", "ok", "back", "menu", "exit", "info") if k in ir_codes]
    transport_cmds = [
        k for k in ("play", "pause", "stop", "rewind", "forward", "record") if k in ir_codes
    ]

    return {
        "broadlink": {
            "configured": has_broadlink(display),
            "dry_run": is_dry_run(display) if has_broadlink(display) else False,
            "host": (display.get("broadlink") or {}).get("host") if has_broadlink(display) else None,
            "ir_command_count": len(ir_codes),
            "channel_commands": channel_cmds,
            "navigation_commands": nav_cmds,
            "transport_commands": transport_cmds,
            "has_number_pad": all(f"num_{i}" in ir_codes for i in range(10)),
        },
        "epg": {
            "enabled": bool(epg.get("enabled")),
            "timezone": epg.get("timezone") or "UTC",
            "country_code": epg.get("country_code") or "us",
            "channel_count": len(channels),
            "channels": [
                {
                    "name": c.get("name"),
                    "epg_id": c.get("epg_id"),
                    "channel_number": c.get("channel_number"),
                    "ir_command": c.get("ir_command"),
                    "logo": c.get("logo_override"),
                }
                for c in channels
            ],
            "sources": [
                {"url": s.get("url"), "priority": s.get("priority", 99)}
                for s in (epg.get("sources") or [])
                if isinstance(s, dict) and s.get("url")
            ],
        },
        "beacons": {
            "enabled": bool(beacons.get("enabled")),
            "room_beacon_id": beacons.get("beacon_id") or f"room_{display.get('id')}_beacon",
            "protocols": beacons.get("protocols") or ["ibeacon"],
            "zones": ["immediate", "near", "far", "unknown"],
        },
    }


def send_ir(display_id: str, command: str) -> dict[str, Any]:
    """Send a single IR/RF command (or dry-run)."""
    display = get_display(display_id)
    if not display:
        raise KeyError(f"Unknown display: {display_id}")

    ir_codes = _ir_codes_for(display)
    if command not in ir_codes:
        raise KeyError(f"Unknown IR command {command!r}")

    if is_dry_run(display) or not has_broadlink(display):
        return {
            "ok": True,
            "display_id": display_id,
            "command": command,
            "method": "broadlink_ir_dry_run",
            "dry_run": True,
            "message": f"Dry-run IR send: {command}",
        }

    return send_room_command(display_id, command)


def tune_channel(display_id: str, channel_number: int | str, ir_sequence: str | None = None) -> dict[str, Any]:
    """
    Tune STB to a channel by sending digit IR commands.
    ir_sequence e.g. "num_2,num_0,num_2" or channel_number 202 → num_2,num_0,num_2
    """
    display = get_display(display_id)
    if not display:
        raise KeyError(f"Unknown display: {display_id}")

    if ir_sequence:
        parts = [p.strip() for p in str(ir_sequence).split(",") if p.strip()]
    else:
        digits = str(channel_number).strip()
        if not digits.isdigit():
            raise ValueError("channel_number must be digits or provide ir_command sequence")
        parts = [f"num_{d}" for d in digits]

    results = []
    for part in parts:
        result = send_ir(display_id, part)
        results.append(result)
        if not result.get("ok"):
            return {"ok": False, "display_id": display_id, "channel": channel_number, "steps": results}
        time.sleep(0.25)

    return {
        "ok": True,
        "display_id": display_id,
        "channel": channel_number,
        "sequence": parts,
        "dry_run": any(r.get("dry_run") for r in results),
        "steps": results,
    }


def _demo_programmes(channels: list[dict[str, Any]], tz_name: str) -> list[dict[str, Any]]:
    """Fallback guide when live XMLTV cannot be fetched."""
    try:
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc

    now = datetime.now(tz)
    slot_start = now.replace(minute=(now.minute // 30) * 30, second=0, microsecond=0)
    titles = [
        "Morning News",
        "World Briefing",
        "Sports Center",
        "Documentary Hour",
        "Prime Drama",
        "Late Night",
    ]
    out: list[dict[str, Any]] = []
    for ch in channels:
        cid = ch.get("epg_id") or ch.get("name") or "unknown"
        for i in range(6):
            start = slot_start + timedelta(hours=i - 1)
            stop = start + timedelta(minutes=60)
            out.append(
                {
                    "channel": cid,
                    "channel_name": ch.get("name"),
                    "channel_number": ch.get("channel_number"),
                    "title": titles[i % len(titles)],
                    "desc": f"Demo listing for {ch.get('name')} ({tz_name})",
                    "start": start.isoformat(),
                    "stop": stop.isoformat(),
                    "is_live": start <= now < stop,
                    "demo": True,
                }
            )
    return out


def fetch_epg_guide(display_id: str, use_live: bool = True) -> dict[str, Any]:
    """Fetch EPG for a room (live XMLTV when possible, else demo)."""
    display = get_display(display_id)
    if not display:
        raise KeyError(f"Unknown display: {display_id}")

    epg = display.get("epg") if isinstance(display.get("epg"), dict) else {}
    if not epg.get("enabled"):
        return {"ok": False, "error": "EPG not enabled for this room", "display_id": display_id}

    channels = list(epg.get("channels") or [])
    tz_name = str(epg.get("timezone") or "UTC")
    sources = [s for s in (epg.get("sources") or []) if isinstance(s, dict) and s.get("url")]
    sources.sort(key=lambda s: int(s.get("priority", 99)))

    programmes: list[dict[str, Any]] = []
    source_used = None
    mode = "demo"

    if use_live and sources:
        try:
            from epg_client import EPGClient
            from zoneinfo import ZoneInfo

            client = EPGClient(cache_dir=ROOT / "epg_cache")
            url = str(sources[0]["url"])
            path = client.fetch_xmltv(url, use_cache=True)
            wanted = {c.get("epg_id") for c in channels if c.get("epg_id")}
            try:
                target_tz = ZoneInfo(tz_name)
            except Exception:
                target_tz = timezone.utc
            _parsed_channels, parsed_programmes = client.parse_xmltv(
                path, target_timezone=target_tz, filter_channels=wanted if wanted else None
            )
            for prog in parsed_programmes:
                if wanted and prog.channel not in wanted:
                    continue
                programmes.append(
                    {
                        "channel": prog.channel,
                        "title": prog.title,
                        "desc": prog.desc,
                        "start": prog.start.isoformat() if prog.start else None,
                        "stop": prog.stop.isoformat() if prog.stop else None,
                        "category": prog.category,
                        "is_live": False,
                        "demo": False,
                    }
                )
            # Mark live
            now = datetime.now(timezone.utc)
            for p in programmes:
                try:
                    start = datetime.fromisoformat(p["start"]) if p["start"] else None
                    stop = datetime.fromisoformat(p["stop"]) if p["stop"] else None
                    if start and stop and start <= now.astimezone(start.tzinfo) < stop:
                        p["is_live"] = True
                except Exception:
                    pass
            # Enrich with channel metadata
            by_id = {c.get("epg_id"): c for c in channels}
            for p in programmes:
                meta = by_id.get(p["channel"]) or {}
                p["channel_name"] = meta.get("name")
                p["channel_number"] = meta.get("channel_number")
                p["ir_command"] = meta.get("ir_command")
            source_used = url
            mode = "live"
        except Exception as exc:
            logger.warning("Live EPG fetch failed, using demo: %s", exc)
            programmes = _demo_programmes(channels, tz_name)
            mode = "demo_fallback"
    else:
        programmes = _demo_programmes(channels, tz_name)

    now_list = [p for p in programmes if p.get("is_live")]
    return {
        "ok": True,
        "display_id": display_id,
        "mode": mode,
        "timezone": tz_name,
        "source": source_used,
        "channels": room_feature_summary(display)["epg"]["channels"],
        "now": now_list,
        "programmes": programmes[:200],
        "count": len(programmes),
    }


def get_beacon_presence(display_id: str) -> dict[str, Any]:
    display = get_display(display_id)
    if not display:
        raise KeyError(f"Unknown display: {display_id}")

    summary = room_feature_summary(display)
    beacons = summary["beacons"]
    occupants = list(_BEACON_PRESENCE.get(display_id) or [])

    if not occupants and beacons["enabled"]:
        # Seed a demo occupant so UI is usable without hardware
        occupants = [
            {
                "user_id": "demo_guest",
                "name": "Demo Guest",
                "zone": "near",
                "distance_meters": 1.8,
                "entered_at": (datetime.now(timezone.utc) - timedelta(minutes=12)).isoformat(),
                "demo": True,
            }
        ]

    return {
        "ok": True,
        "display_id": display_id,
        "enabled": beacons["enabled"],
        "beacon_id": beacons["room_beacon_id"],
        "occupied": len(occupants) > 0,
        "occupants": occupants,
        "zones": beacons["zones"],
        "protocols": beacons["protocols"],
    }


def report_beacon_scan(
    display_id: str,
    user_id: str,
    zone: str,
    rssi: int | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """Gateway/app reports a beacon sighting (updates in-memory presence)."""
    display = get_display(display_id)
    if not display:
        raise KeyError(f"Unknown display: {display_id}")

    occupants = [o for o in _BEACON_PRESENCE.get(display_id, []) if o.get("user_id") != user_id]
    if zone != "unknown":
        occupants.append(
            {
                "user_id": user_id,
                "name": name or user_id,
                "zone": zone,
                "rssi": rssi,
                "entered_at": datetime.now(timezone.utc).isoformat(),
                "demo": False,
            }
        )
    _BEACON_PRESENCE[display_id] = occupants
    return get_beacon_presence(display_id)
