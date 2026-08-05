"""
Extended API Integration for MediaControl
Adds new-feature API routes while keeping legacy Samsung Flip remote intact.
"""

from __future__ import annotations

import importlib
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

ROOT = Path(__file__).resolve().parent

FEATURE_CATALOG = [
    {
        "id": "samsung_mdc",
        "name": "Samsung Flip / MDC",
        "category": "Display",
        "module": None,
        "docs": None,
        "description": "Core display control via MDC/TCP (power, input, volume).",
        "ui_path": "/",
    },
    {
        "id": "broadlink_ir_rf",
        "name": "Broadlink IR/RF",
        "category": "Sources",
        "module": "broadlink_client",
        "docs": "docs/BROADLINK_SETUP.md",
        "description": "Control STBs and AV gear via RM4 Mini/Pro IR/RF.",
        "ui_path": "/features/broadlink",
    },
    {
        "id": "epg_guide",
        "name": "EPG / TV Guide",
        "category": "Sources",
        "module": "epg_client",
        "docs": "docs/EPG_GUIDE.md",
        "description": "Channel logos and program schedules with timezone conversion.",
        "ui_path": "/features/epg",
    },
    {
        "id": "apple_tv",
        "name": "Apple TV",
        "category": "Sources",
        "module": "appletv_device",
        "docs": "docs/MULTI_DEVICE_SETUP.md",
        "description": "Network control for Apple TV apps and remote.",
        "ui_path": "/features/sources",
    },
    {
        "id": "android_tv",
        "name": "Android TV / Fire TV",
        "category": "Sources",
        "module": "androidtv_device",
        "docs": "docs/MULTI_DEVICE_SETUP.md",
        "description": "ADB network control for Android TV sticks and boxes.",
        "ui_path": "/features/sources",
    },
    {
        "id": "hdmi_matrix",
        "name": "HDMI Matrix",
        "category": "Routing",
        "module": "hdmi_matrix",
        "docs": "docs/MULTI_DEVICE_SETUP.md",
        "description": "Route any source to any display via matrix switchers.",
        "ui_path": "/features/sources",
    },
    {
        "id": "audio_devices",
        "name": "AirPlay / Sonos",
        "category": "Audio",
        "module": "audio_devices",
        "docs": "docs/AUDIO_DEVICES.md",
        "description": "Speaker control with group/ungroup for AirPlay and Sonos.",
        "ui_path": "/features/audio",
    },
    {
        "id": "bluetooth_beacons",
        "name": "Bluetooth Beacons",
        "category": "Presence",
        "module": "bluetooth_beacon_presence",
        "docs": "docs/BLUETOOTH_BEACON_PRESENCE.md",
        "description": "Room proximity and presence detection with automation triggers.",
        "ui_path": "/features/beacons",
    },
    {
        "id": "guest_keys",
        "name": "Guest Keys & Staff Access",
        "category": "Hospitality",
        "module": "guest_key_staff_access",
        "docs": "docs/GUEST_KEY_STAFF_ACCESS.md",
        "description": "Check-in/out key lifecycle and staff master keys.",
        "ui_path": "/features/hospitality",
    },
    {
        "id": "hospitality",
        "name": "Hospitality Management",
        "category": "Hospitality",
        "module": "hospitality_management",
        "docs": "docs/HOSPITALITY_LUXURY_MANAGEMENT.md",
        "description": "Wallet keys, in-room dining, butler requests, laundry.",
        "ui_path": "/features/hospitality",
    },
    {
        "id": "access_control",
        "name": "Door Access Control",
        "category": "Access",
        "module": "door_access_control",
        "docs": "docs/DOOR_ACCESS_CONTROL.md",
        "description": "NFC, RFID, face, fingerprint, and PIN pad access.",
        "ui_path": "/features/access",
    },
    {
        "id": "passive_entry",
        "name": "Passive Entry",
        "category": "Access",
        "module": "passive_entry_system",
        "docs": "docs/PASSIVE_ENTRY_GUIDE.md",
        "description": "Hands-free unlock via BLE/UWB and digital wallets.",
        "ui_path": "/features/access",
    },
    {
        "id": "knx_integration",
        "name": "KNX Integration",
        "category": "Smart Home",
        "module": "knx_integration",
        "docs": "docs/KNX_INTEGRATION_CLOUD_BRIDGE.md",
        "description": "KNX/IP bridge with ETS import and cloud HTTPS access.",
        "ui_path": "/features/smarthome",
    },
    {
        "id": "smart_home_ecosystem",
        "name": "Smart Home Ecosystem",
        "category": "Smart Home",
        "module": "smart_home_ecosystem",
        "docs": "docs/SMART_HOME_ECOSYSTEM_INTEGRATION.md",
        "description": "Ubiquiti, Aqara, Nuki, Home Assistant, Matter, Zigbee.",
        "ui_path": "/features/smarthome",
    },
    {
        "id": "consumer_platforms",
        "name": "Consumer Platforms",
        "category": "Smart Home",
        "module": "consumer_platforms",
        "docs": "docs/CONSUMER_SMART_HOME_PLATFORMS.md",
        "description": "Apple Home, Google Home, Xiaomi, Alexa, SmartThings, IKEA.",
        "ui_path": "/features/smarthome",
    },
    {
        "id": "home_automation",
        "name": "Home Automation Devices",
        "category": "Smart Home",
        "module": "home_automation_devices",
        "docs": "docs/HOME_AUTOMATION_DEVICES.md",
        "description": "Garage, irrigation, pool, elevator, CCTV integrations.",
        "ui_path": "/features/smarthome",
    },
    {
        "id": "unified_comms",
        "name": "Unified Communications",
        "category": "Comms",
        "module": "unified_communications",
        "docs": "docs/UNIFIED_COMMUNICATIONS.md",
        "description": "SIP, intercom, paging, doorbells, call handoff.",
        "ui_path": "/features/comms",
    },
    {
        "id": "ai_studio",
        "name": "AI Studio Effects",
        "category": "Meetings",
        "module": "ai_studio_effects",
        "docs": "docs/AI_STUDIO_EFFECTS.md",
        "description": "Background blur, eye contact, noise suppression, Teams Premium.",
        "ui_path": "/features/meetings",
    },
    {
        "id": "wireless_presentation",
        "name": "Wireless Presentation",
        "category": "Meetings",
        "module": "wireless_presentation",
        "docs": "docs/WIRELESS_PRESENTATION.md",
        "description": "AirPlay, Chromecast, Miracast receiver on gateway.",
        "ui_path": "/features/meetings",
    },
    {
        "id": "legacy_devices",
        "name": "Legacy Devices / Gateways",
        "category": "Control",
        "module": "legacy_devices",
        "docs": "docs/LEGACY_DEVICES_GUIDE.md",
        "description": "IR/RF/RS232/RS485 sub-devices under intermediary gateways.",
        "ui_path": "/features/control",
    },
]


def _module_status(module_name: Optional[str]) -> Dict[str, Any]:
    if not module_name:
        return {"available": True, "error": None}
    try:
        importlib.import_module(module_name)
        return {"available": True, "error": None}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def handle_api_features_status(_request_data: Dict[str, Any]) -> Dict[str, Any]:
    features = []
    for item in FEATURE_CATALOG:
        status = _module_status(item["module"])
        features.append(
            {
                **item,
                "available": status["available"],
                "error": status["error"],
                "docs_exists": bool(item["docs"] and (ROOT / item["docs"]).is_file()),
            }
        )
    available = sum(1 for f in features if f["available"])
    return {
        "ok": True,
        "version": "2.0.0-extended",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(features),
            "available": available,
            "unavailable": len(features) - available,
        },
        "features": features,
    }


def handle_api_features_catalog(_request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Alias for status — used by Features hub UI."""
    return handle_api_features_status(_request_data)


def handle_api_broadlink_info(_request_data: Dict[str, Any]) -> Dict[str, Any]:
    status = _module_status("broadlink_client")
    return {
        "ok": True,
        "available": status["available"],
        "error": status["error"],
        "supported_devices": ["RM4 Mini", "RM4 Pro", "RM Mini 3", "RM Pro+"],
        "capabilities": ["IR learn/send", "RF learn/send", "device discovery"],
        "config_example": "BROADLINK_CONFIG_EXAMPLE.yaml",
        "docs": "docs/BROADLINK_SETUP.md",
        "note": "Configure a Broadlink host/MAC in room YAML to send live commands.",
    }


def handle_api_epg_info(_request_data: Dict[str, Any]) -> Dict[str, Any]:
    status = _module_status("epg_client")
    return {
        "ok": True,
        "available": status["available"],
        "error": status["error"],
        "providers": ["iptv-org", "custom XMLTV URL"],
        "capabilities": [
            "XMLTV fetch/parse",
            "channel logos",
            "timezone conversion (e.g. IST → GST)",
            "now/next listings",
        ],
        "config_examples": [
            "EPG_CONFIG_EXAMPLE.yaml",
            "CROSS_TIMEZONE_CONFIG.yaml",
            "INDIA_STB_CONFIG.yaml",
            "UAE_STB_CONFIG.yaml",
        ],
        "docs": "docs/EPG_GUIDE.md",
    }


def handle_api_beacon_info(_request_data: Dict[str, Any]) -> Dict[str, Any]:
    status = _module_status("bluetooth_beacon_presence")
    occupied_demo = [
        {"room": "2201", "occupied": True, "occupants": 1, "zone": "near"},
        {"room": "2202", "occupied": False, "occupants": 0, "zone": "unknown"},
        {"room": "lobby", "occupied": True, "occupants": 3, "zone": "far"},
    ]
    return {
        "ok": True,
        "available": status["available"],
        "error": status["error"],
        "protocols": ["iBeacon", "Eddystone", "AltBeacon"],
        "zones": ["immediate", "near", "far", "unknown"],
        "demo_occupancy": occupied_demo,
        "docs": "docs/BLUETOOTH_BEACON_PRESENCE.md",
        "note": "Demo occupancy shown until live gateways/beacons are configured.",
    }


def handle_api_hospitality_info(_request_data: Dict[str, Any]) -> Dict[str, Any]:
    guest = _module_status("guest_key_staff_access")
    hosp = _module_status("hospitality_management")
    return {
        "ok": True,
        "available": guest["available"] and hosp["available"],
        "modules": {
            "guest_key_staff_access": guest,
            "hospitality_management": hosp,
        },
        "capabilities": [
            "Guest key auto-activate at check-in",
            "Guest key auto-expire at check-out + grace",
            "Staff master keys (5 levels)",
            "Digital wallet keys",
            "In-room dining",
            "Staff call buttons",
        ],
        "docs": [
            "docs/GUEST_KEY_STAFF_ACCESS.md",
            "docs/HOSPITALITY_LUXURY_MANAGEMENT.md",
        ],
    }


def handle_api_access_info(_request_data: Dict[str, Any]) -> Dict[str, Any]:
    door = _module_status("door_access_control")
    passive = _module_status("passive_entry_system")
    return {
        "ok": True,
        "available": door["available"] and passive["available"],
        "modules": {
            "door_access_control": door,
            "passive_entry_system": passive,
        },
        "auth_methods": ["NFC", "RFID", "Face", "Fingerprint", "PIN"],
        "passive_entry": ["BLE", "UWB", "Apple Wallet", "Google Wallet"],
        "docs": ["docs/DOOR_ACCESS_CONTROL.md", "docs/PASSIVE_ENTRY_GUIDE.md"],
    }


def handle_api_sources_info(_request_data: Dict[str, Any]) -> Dict[str, Any]:
    modules = {
        "apple_tv": _module_status("appletv_device"),
        "android_tv": _module_status("androidtv_device"),
        "hdmi_matrix": _module_status("hdmi_matrix"),
        "input_router": _module_status("input_router"),
        "device_abstraction": _module_status("device_abstraction"),
    }
    return {
        "ok": True,
        "available": all(m["available"] for m in modules.values()),
        "modules": modules,
        "capabilities": [
            "App launch (Netflix, etc.)",
            "Contextual D-pad",
            "Auto input switching",
            "Source presets",
        ],
        "docs": "docs/MULTI_DEVICE_SETUP.md",
    }


def handle_api_smarthome_info(_request_data: Dict[str, Any]) -> Dict[str, Any]:
    modules = {
        "knx": _module_status("knx_integration"),
        "ecosystem": _module_status("smart_home_ecosystem"),
        "consumer": _module_status("consumer_platforms"),
        "home_automation": _module_status("home_automation_devices"),
    }
    return {
        "ok": True,
        "available": all(m["available"] for m in modules.values()),
        "modules": modules,
        "platforms": [
            "KNX",
            "Apple Home",
            "Google Home",
            "Xiaomi",
            "Alexa",
            "SmartThings",
            "IKEA",
            "Ubiquiti",
            "Aqara",
            "Nuki",
            "Home Assistant",
            "Matter",
            "Zigbee",
        ],
        "docs": [
            "docs/KNX_INTEGRATION_CLOUD_BRIDGE.md",
            "docs/SMART_HOME_ECOSYSTEM_INTEGRATION.md",
            "docs/CONSUMER_SMART_HOME_PLATFORMS.md",
            "docs/HOME_AUTOMATION_DEVICES.md",
        ],
    }


EXTENDED_API_ROUTES: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "/api/features/status": handle_api_features_status,
    "/api/features/catalog": handle_api_features_catalog,
    "/api/features/broadlink": handle_api_broadlink_info,
    "/api/features/epg": handle_api_epg_info,
    "/api/features/beacons": handle_api_beacon_info,
    "/api/features/hospitality": handle_api_hospitality_info,
    "/api/features/access": handle_api_access_info,
    "/api/features/sources": handle_api_sources_info,
    "/api/features/smarthome": handle_api_smarthome_info,
    # Back-compat aliases used earlier
    "/api/broadlink/discover": handle_api_broadlink_info,
    "/api/epg/channels": handle_api_epg_info,
    "/api/beacons/status": handle_api_beacon_info,
    "/api/guest-keys/status": handle_api_hospitality_info,
    "/api/staff-access/status": handle_api_hospitality_info,
}


def handle_extended_api(
    path: str, method: str, request_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Return response dict if path is handled; otherwise None."""
    handler = EXTENDED_API_ROUTES.get(path)
    if handler is None:
        return None
    try:
        return handler(request_data or {})
    except Exception as exc:
        return {"ok": False, "error": f"Internal server error: {exc}"}
