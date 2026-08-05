#!/usr/bin/env python3
"""Multi-cabin Samsung Flip Pro remote server with auth."""

from __future__ import annotations

import importlib
import json
import mimetypes
import re
import sys
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from auth import (
    SESSION_COOKIE,
    authenticate,
    can_access_display,
    can_access_location,
    can_manage_site,
    change_admin_password,
    clear_session_cookie_header,
    create_session,
    get_room_username,
    is_admin,
    is_master,
    is_location_admin,
    list_location_admins,
    parse_session,
    remove_location_admin,
    remove_room_credentials,
    session_cookie_header,
    set_location_admin_credentials,
    set_room_credentials,
    user_location_id,
)
from button_icons import icon_catalog as button_icon_catalog
from display_manager import (
    apply_layout_template,
    build_commands_for_display,
    category_labels,
    create_display,
    create_location,
    delete_display,
    delete_location,
    display_location_id,
    enrich_auth_user,
    find_duplicate_remote_url,
    get_layout,
    get_layout_template,
    get_location,
    list_layout_template_summaries,
    location_id_available,
    location_payload,
    list_locations,
    normalize_layout,
    parse_remote_host_port,
    rename_display,
    rename_location,
    room_id_available,
    sync_source_orders_from_layout,
    get_display,
    input_aliases,
    input_packet,
    legacy_room_redirect,
    list_display_ids,
    load_display_map,
    mdc_config,
    normalize_sources_for_save,
    remote_payload,
    resolve_room_route,
    room_path,
    room_setup_path,
    save_display_map,
    section_labels,
    send_room_command,
    set_location_order,
    set_room_order,
    setup_candidates,
    source_label_map,
    source_title_for_id,
    template_from_display,
    unstable_codes,
    upsert_display,
    upsert_layout_template,
    upsert_location,
    wireless_source_ids,
)
from discover import discover, parse_response, summary
from mdc_client import MdcClient, format_hex, parse_hex
from site_settings import default_remote_path, get_site_settings, save_site_settings

# Import extended API features
try:
    from api_integration import handle_extended_api, EXTENDED_API_ROUTES
    EXTENDED_API_AVAILABLE = True
    print("[INFO] Extended API features loaded successfully")
except ImportError as e:
    EXTENDED_API_AVAILABLE = False
    print(f"[WARNING] Extended API features not available: {e}")

ROOT = Path(__file__).resolve().parent
FRONTEND_DIST = ROOT / "frontend" / "dist"
DISPLAY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

PUBLIC_PATHS = {"/login", "/login.html"}
PUBLIC_API = {"/api/auth/login"}


def _display_context(display_id: str) -> dict:
    display = get_display(display_id)
    if not display:
        raise KeyError(f"Unknown display: {display_id}")
    discovered = load_display_map(display_id)
    commands = build_commands_for_display(display, discovered)
    return {
        "display": display,
        "discovered": discovered,
        "commands": commands,
        "labels": source_label_map(display, discovered),
        "aliases": input_aliases(display),
        "unstable": unstable_codes(discovered),
        "wireless_ids": wireless_source_ids(display),
    }


def _send(display_id: str, cmd: str) -> dict:
    try:
        result = send_room_command(display_id, cmd)
    except KeyError as exc:
        return {"ok": False, "error": str(exc)}
    ctx = _display_context(display_id)
    if cmd in ctx["aliases"] and "query_after" in result:
        code = ctx["aliases"][cmd]
        query_parsed = result["query_after"]
        query_val = query_parsed.get("value_dec")
        if query_val is not None:
            result["input_code_queried"] = f"0x{query_val:02X}"
            queried_label = ctx["labels"].get(query_val)
            if queried_label and (cmd not in ctx["wireless_ids"] or query_val != 0x64):
                result["input_label"] = queried_label
        parsed = result.get("parsed") or {}
        result["input_stable"] = parsed.get("value") == query_parsed.get("value")
        result["input_unstable"] = code in ctx["unstable"]
    return result


def _send_code(display_id: str, code: str) -> dict:
    ctx = _display_context(display_id)
    display = ctx["display"]
    device_id = int(display.get("device_id", 0))
    code_int = int(str(code), 16)
    packet = parse_hex(input_packet(code_int, device_id))
    client = MdcClient(mdc_config(display))
    response = client.send_raw(packet)
    parsed = parse_response(response) if response else {"status": "no_response"}
    time.sleep(0.8)
    query_resp = client.send_raw(parse_hex(ctx["commands"]["query_input"]))
    query_parsed = parse_response(query_resp) if query_resp else {"status": "no_response"}
    return {
        "ok": True,
        "display_id": display_id,
        "code": f"0x{code_int:02X}",
        "sent": format_hex(packet),
        "response": format_hex(response) if response else None,
        "parsed": parsed,
        "ack": parsed.get("ack", False),
        "query_after": query_parsed,
        "input_stable": parsed.get("value") == query_parsed.get("value"),
    }


def _status(display_id: str) -> dict:
    ctx = _display_context(display_id)
    display = ctx["display"]
    host = str(display.get("ip") or "")
    # Demo / unbound rooms should not hard-fail status polling
    if host in ("", "0.0.0.0", "127.0.0.1", "dry-run"):
        return {
            "ok": True,
            "display_id": display_id,
            "title": display.get("title") or display_id,
            "host": host or None,
            "port": display.get("port", 1515),
            "device_id": display.get("device_id", 0),
            "power": "Demo",
            "input_code": None,
            "input_label": "No live display",
            "muted": False,
            "volume": None,
            "demo": True,
        }
    try:
        client = MdcClient(mdc_config(display))
        commands = ctx["commands"]
        power = client.send_raw(parse_hex(commands["query_power"]))
        input_r = client.send_raw(parse_hex(commands["query_input"]))
        mute = client.send_raw(parse_hex(commands["query_mute"]))
        volume = client.send_raw(parse_hex(commands["query_volume"]))
    except OSError as exc:
        return {
            "ok": True,
            "display_id": display_id,
            "title": display.get("title") or display_id,
            "host": host,
            "port": display.get("port", 1515),
            "device_id": display.get("device_id", 0),
            "power": "Offline",
            "input_label": "Unreachable",
            "muted": False,
            "volume": None,
            "error": str(exc),
        }

    def val(resp: bytes | None, idx: int = 6):
        return resp[idx] if resp and len(resp) > idx else None

    inp = val(input_r)
    labels = ctx["labels"]
    power_val = val(power)
    power_str = "On" if power_val == 1 else "Off" if power_val == 0 else "Unknown"
    if power_val == 0:
        return {
            "ok": True,
            "display_id": display_id,
            "title": display.get("title") or display_id,
            "host": display.get("ip"),
            "port": display.get("port", 1515),
            "device_id": display.get("device_id", 0),
            "power": power_str,
            "input_code": None,
            "input_label": "None",
            "muted": False,
            "volume": None,
            "volume_label": "Off",
            "parsed_input": parse_response(input_r) if input_r else None,
        }
    return {
        "ok": True,
        "display_id": display_id,
        "title": display.get("title") or display_id,
        "host": display.get("ip"),
        "port": display.get("port", 1515),
        "device_id": display.get("device_id", 0),
        "power": power_str,
        "input_code": f"0x{inp:02X}" if inp is not None else None,
        "input_label": labels.get(inp, f"Source 0x{inp:02X}" if inp is not None else "—"),
        "muted": val(mute) == 1,
        "volume": val(volume),
        "parsed_input": parse_response(input_r) if input_r else None,
    }


def _run_discover(display_id: str, quick: bool = False) -> dict:
    display = get_display(display_id)
    if not display:
        raise KeyError(display_id)
    data = discover(
        str(display["ip"]),
        int(display.get("port", 1515)),
        full_scan=not quick,
        device_id=int(display.get("device_id", 0)),
    )
    path = save_display_map(display_id, data)
    return {
        "ok": True,
        "display_id": display_id,
        "saved": str(path),
        "summary": summary(data),
        "stable_count": sum(1 for i in data.get("inputs", []) if i.get("stable")),
        "unstable_count": sum(1 for i in data.get("inputs", []) if not i.get("stable")),
        "candidates": setup_candidates(display, data),
    }


class RemoteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[remote] {self.address_string()} - {fmt % args}\n")

    def end_headers(self):
        path = urlparse(self.path).path
        if path.endswith((".html", ".js", ".css")):
            self.send_header("Cache-Control", "no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
        super().end_headers()

    @staticmethod
    def _live_icon_svgs() -> dict[str, str]:
        import button_svgs as button_svgs_module

        importlib.reload(button_svgs_module)
        return button_svgs_module.icon_svgs()

    def _session_user(self) -> dict | None:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            part = part.strip()
            if part.startswith(f"{SESSION_COOKIE}="):
                return parse_session(part.split("=", 1)[1])
        return None

    def _redirect(self, location: str, code: int = 302):
        self.send_response(code)
        self.send_header("Location", location)
        self.end_headers()

    def _json(self, code: int, payload: dict, extra_headers: list[tuple[str, str]] | None = None):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        if extra_headers:
            for k, v in extra_headers:
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        return json.loads(self.rfile.read(length) or b"{}")

    def _unauthorized_api(self):
        self._json(401, {"ok": False, "error": "Unauthorized"})

    def _forbidden_api(self):
        self._json(403, {"ok": False, "error": "Forbidden"})

    def _serve_frontend(self, path: str) -> bool:
        """Serve Vite build at /app/ when frontend/dist exists."""
        if not FRONTEND_DIST.is_dir():
            return False
        if path == "/app":
            self._redirect("/app/")
            return True
        if not path.startswith("/app/"):
            return False
        sub = path[5:].lstrip("/")
        if sub:
            target = (FRONTEND_DIST / sub).resolve()
            root = FRONTEND_DIST.resolve()
            if not str(target).startswith(str(root)):
                self.send_error(403)
                return True
            if target.is_file():
                ctype, _ = mimetypes.guess_type(str(target))
                body = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", ctype or "application/octet-stream")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return True
        index = FRONTEND_DIST / "index.html"
        if not index.is_file():
            self.send_error(404, "New UI not built — run: cd frontend && npm install && npm run build")
            return True
        body = index.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return True

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _match_display_api(self, path: str) -> tuple[str, str] | None:
        m = re.match(r"^/api/displays/([a-z0-9][a-z0-9_-]*)(?:/(.+))?$", path)
        if not m:
            return None
        return m.group(1), m.group(2) or ""

    def _admin_only_actions(self) -> frozenset[str]:
        """Actions that always require admin (any HTTP method)."""
        return frozenset({"map", "discover", "send-code", "layout", "sources", "credentials", "apply-template"})

    def _admin_write_actions(self) -> frozenset[str]:
        """Actions that require admin for writes; GET may be allowed for room users."""
        return frozenset({"config"})

    def _check_api_auth(self, path: str, display_id: str | None, action: str = "") -> dict | None:
        user = self._session_user()
        if path in PUBLIC_API:
            return user
        if path == "/api/auth/me":
            return user
        if path == "/api/auth/logout":
            return user
        if path == "/api/displays" and self.command == "GET":
            if not is_admin(user):
                self._unauthorized_api()
                return None
            return user
        if path == "/api/displays" and self.command == "POST":
            if not is_admin(user):
                self._unauthorized_api()
                return None
            return user
        if path == "/api/displays/order" or path.startswith("/api/layout-templates"):
            if not is_admin(user):
                self._unauthorized_api()
                return None
            return user
        if path.startswith("/api/locations"):
            if not is_admin(user):
                self._unauthorized_api()
                return None
            if self.command != "GET" and not is_master(user):
                self._unauthorized_api()
                return None
            return user
        if path.startswith("/api/site-settings") or path.startswith("/api/location-admins"):
            if not is_admin(user):
                self._unauthorized_api()
                return None
            return user
        if path.startswith("/api/displays/check-id"):
            if not is_admin(user):
                self._unauthorized_api()
                return None
            return user
        if display_id:
            if self.command == "DELETE":
                if not is_admin(user):
                    self._forbidden_api()
                    return None
                return user
            if action in self._admin_only_actions():
                if not is_admin(user):
                    self._forbidden_api()
                    return None
                return user
            if action in self._admin_write_actions() and self.command != "GET":
                if not is_admin(user):
                    self._forbidden_api()
                    return None
                return user
            if not can_access_display(user, display_id):
                self._unauthorized_api()
                return None
            return user
        if not user:
            self._unauthorized_api()
            return None
        return user

    def _check_page_auth(self, path: str, display_id: str | None = None, setup: bool = False) -> bool:
        if path in PUBLIC_PATHS or path.startswith("/login"):
            return True
        user = self._session_user()
        if path in ("/", "/index.html"):
            return bool(user)
        if path in ("/add", "/add.html"):
            return is_admin(user)
        if path in ("/locations", "/locations.html"):
            return is_master(user)
        if path in ("/settings", "/settings.html"):
            return is_admin(user)
        if display_id:
            if setup and not is_admin(user):
                return False
            return can_access_display(user, display_id)
        return bool(user)

    def do_GET(self):
        path = urlparse(self.path).path

        # Try extended API first (new features)
        if EXTENDED_API_AVAILABLE and path.startswith("/api/"):
            query_params = parse_qs(urlparse(self.path).query)
            # Flatten single-value lists
            request_data = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
            extended_result = handle_extended_api(path, "GET", request_data)
            if extended_result is not None:
                self._json(200 if extended_result.get("ok") else 400, extended_result)
                return

        if path == "/api/auth/me":
            user = self._session_user()
            if not user:
                self._json(200, {"ok": True, "user": None})
                return
            enriched = enrich_auth_user(user)
            payload = {
                "role": enriched["role"],
                "username": enriched.get("username"),
                "scope": enriched.get("scope") or enriched.get("role"),
                "is_master": is_master(enriched),
            }
            if enriched.get("display_id"):
                payload["display_id"] = enriched["display_id"]
            if enriched.get("location_id"):
                payload["location_id"] = enriched["location_id"]
            if enriched.get("remote_url"):
                payload["remote_url"] = enriched["remote_url"]
            self._json(200, {"ok": True, "user": payload})
            return

        if path == "/login" or path == "/login.html":
            self.path = "/login.html"
            return super().do_GET()

        if path == "/button_svgs.js":
            import button_svgs as button_svgs_module

            importlib.reload(button_svgs_module)
            svgs = button_svgs_module.icon_svgs()
            revision = button_svgs_module.icon_revision()
            body = (
                "window.BUTTON_SVGS = "
                + json.dumps(svgs)
                + ";\nwindow.BUTTON_SVG_REVISION = "
                + json.dumps(revision)
                + ";\n"
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/displays":
            if not self._check_api_auth(path, None):
                return
            displays = []
            loc_filter = user_location_id(self._session_user())
            for did in list_display_ids():
                d = get_display(did)
                if not d:
                    continue
                if loc_filter and str(d.get("location") or "") != loc_filter:
                    continue
                displays.append(remote_payload(d, load_display_map(did)))
            self._json(
                200,
                {
                    "ok": True,
                    "displays": displays,
                    "order": [d["id"] for d in displays],
                    "locations": [
                        loc
                        for loc in list_locations()
                        if not loc_filter or loc["id"] == loc_filter
                    ],
                    "site": get_site_settings(),
                    "default_remote_url": default_remote_path(),
                },
            )
            return

        if path == "/api/site-settings":
            if not self._check_api_auth(path, None):
                return
            settings = get_site_settings()
            self._json(
                200,
                {
                    "ok": True,
                    "settings": settings,
                    "default_remote_url": default_remote_path(),
                    "location_admins": list_location_admins() if is_master(self._session_user()) else {},
                },
            )
            return

        if path == "/api/location-admins":
            if not self._check_api_auth(path, None):
                return
            if not is_master(self._session_user()):
                self._forbidden_api()
                return
            self._json(200, {"ok": True, "location_admins": list_location_admins()})
            return

        if path == "/api/displays/check-id":
            if not self._check_api_auth(path, None):
                return
            qs = parse_qs(urlparse(self.path).query)
            rid = str(qs.get("id", [""])[0]).strip().lower()
            exclude = str(qs.get("exclude", [""])[0]).strip().lower() or None
            valid = bool(DISPLAY_ID_RE.match(rid)) if rid else False
            available = room_id_available(rid, exclude=exclude) if valid else False
            self._json(200, {"ok": True, "id": rid, "valid": valid, "available": available})
            return

        if path == "/api/locations":
            if not self._check_api_auth(path, None):
                return
            loc_filter = user_location_id(self._session_user())
            locs = [
                loc for loc in list_locations()
                if not loc_filter or loc["id"] == loc_filter
            ]
            self._json(200, {"ok": True, "locations": locs})
            return

        if path == "/api/locations/check-id":
            if not self._check_api_auth(path, None):
                return
            qs = parse_qs(urlparse(self.path).query)
            lid = str(qs.get("id", [""])[0]).strip().lower()
            exclude = str(qs.get("exclude", [""])[0]).strip().lower() or None
            valid = bool(DISPLAY_ID_RE.match(lid)) if lid else False
            available = location_id_available(lid, exclude=exclude) if valid else False
            self._json(200, {"ok": True, "id": lid, "valid": valid, "available": available})
            return

        if path == "/api/locations/check-url":
            if not self._check_api_auth(path, None):
                return
            qs = parse_qs(urlparse(self.path).query)
            host = str(qs.get("host", [""])[0]).strip()
            port = int(qs.get("port", ["8080"])[0] or 8080)
            exclude = str(qs.get("exclude", [""])[0]).strip().lower() or None
            parsed_host, parsed_port = parse_remote_host_port(host, port)
            dup = find_duplicate_remote_url(parsed_host, parsed_port, exclude_id=exclude) if parsed_host else None
            dup_title = None
            if dup:
                other = get_location(dup)
                dup_title = (other or {}).get("title") or dup
            self._json(
                200,
                {
                    "ok": True,
                    "host": parsed_host,
                    "port": parsed_port,
                    "duplicate": dup,
                    "duplicate_title": dup_title,
                    "available": dup is None,
                },
            )
            return

        if path.startswith("/api/locations/"):
            if not self._check_api_auth(path, None):
                return
            location_id = path.split("/api/locations/", 1)[1].strip("/")
            if location_id == "order":
                self._json(405, {"ok": False, "error": "Use PUT"})
                return
            if not DISPLAY_ID_RE.match(location_id):
                self._json(400, {"ok": False, "error": "Invalid location id"})
                return
            from display_manager import location_payload
            try:
                self._json(200, {"ok": True, "location": location_payload(location_id)})
            except KeyError:
                self._json(404, {"ok": False, "error": "Location not found"})
            return

        if path == "/api/displays/order":
            if not self._check_api_auth(path, None):
                return
            self._json(405, {"ok": False, "error": "Use PUT"})
            return

        if path == "/api/layout-templates" or path.startswith("/api/layout-templates/"):
            if not self._check_api_auth(path, None):
                return
            if path == "/api/layout-templates":
                self._json(200, {"ok": True, "templates": list_layout_template_summaries()})
                return
            template_id = path.split("/api/layout-templates/", 1)[1].strip("/")
            if not DISPLAY_ID_RE.match(template_id):
                self._json(400, {"ok": False, "error": "Invalid template id"})
                return
            tpl = get_layout_template(template_id)
            if not tpl:
                self._json(404, {"ok": False, "error": "Template not found"})
                return
            self._json(200, {"ok": True, "id": template_id, "template": tpl})
            return

        api = self._match_display_api(path)
        if api:
            display_id, action = api
            if not self._check_api_auth(path, display_id, action):
                return
            try:
                if action in ("", "config"):
                    display = get_display(display_id)
                    if not display:
                        self._json(404, {"ok": False, "error": "Not found"})
                        return
                    discovered = load_display_map(display_id)
                    user = self._session_user()
                    payload = remote_payload(display, discovered)
                    resp = {
                        "ok": True,
                        "display": payload,
                        "icon_catalog": payload.get("icon_catalog") or button_icon_catalog(),
                        "categories": category_labels(),
                        "layout": get_layout(display),
                        "section_labels": section_labels(),
                    }
                    if is_admin(user):
                        resp["candidates"] = setup_candidates(display, discovered)
                        resp["room_username"] = get_room_username(display_id)
                        resp["layout_templates"] = list_layout_template_summaries()
                        resp["locations"] = list_locations()
                    self._json(200, resp)
                    return
                if action == "status":
                    self._json(200, _status(display_id))
                    return
                if action == "features":
                    from room_features import room_feature_summary

                    display = get_display(display_id)
                    if not display:
                        self._json(404, {"ok": False, "error": "Not found"})
                        return
                    self._json(200, {"ok": True, "display_id": display_id, **room_feature_summary(display)})
                    return
                if action == "epg":
                    from room_features import fetch_epg_guide

                    qs = parse_qs(urlparse(self.path).query)
                    use_live = str(qs.get("live", ["1"])[0]).lower() not in ("0", "false", "no")
                    self._json(200, fetch_epg_guide(display_id, use_live=use_live))
                    return
                if action == "beacons":
                    from room_features import get_beacon_presence

                    self._json(200, get_beacon_presence(display_id))
                    return
                if action == "map":
                    discovered = load_display_map(display_id)
                    if not discovered:
                        self._json(404, {"ok": False, "error": "No map — run discover first"})
                        return
                    self._json(200, {"ok": True, "map": discovered, "summary": summary(discovered)})
                    return
            except KeyError:
                self._json(404, {"ok": False, "error": "Display not found"})
                return
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
                return

        if path in ("/", "/index.html"):
            # Classic HTML remote is the default day-to-day UI.
            # React lives at /app/ (Channels tabs, Features catalog).
            if not self._check_page_auth(path):
                return self._redirect("/login")
            self.path = "/index.html"
            return super().do_GET()

        if self._serve_frontend(path):
            return

        if path in ("/add", "/add.html"):
            if not self._check_page_auth(path):
                return self._redirect("/login?next=/add")
            self.path = "/add.html"
            return super().do_GET()

        if path in ("/locations", "/locations.html"):
            if not self._check_page_auth(path):
                return self._redirect("/login?next=/locations")
            self.path = "/locations.html"
            return super().do_GET()

        if path in ("/settings", "/settings.html"):
            if not self._check_page_auth(path):
                return self._redirect("/login?next=/settings")
            self.path = "/settings.html"
            return super().do_GET()

        legacy = re.match(r"^/d/([a-z0-9][a-z0-9_-]*)(/setup)?$", path)
        if legacy:
            display_id = legacy.group(1)
            setup = bool(legacy.group(2))
            target = legacy_room_redirect(display_id, setup=setup)
            if target:
                return self._redirect(target)

        m = re.match(r"^/d/([a-z0-9][a-z0-9_-]*)/([a-z0-9][a-z0-9_-]*)(/setup)?$", path)
        if m:
            location_id = m.group(1)
            display_id = m.group(2)
            setup = bool(m.group(3))
            if not resolve_room_route(location_id, display_id):
                self.send_error(404)
                return
            if not self._check_page_auth(path, display_id, setup=setup):
                return self._redirect(f"/login?next={path}")
            self.path = "/setup.html" if setup else "/remote.html"
            return super().do_GET()

        if not self._session_user() and path.endswith(".html"):
            return self._redirect("/login")
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()

        # Try extended API first (new features)
        if EXTENDED_API_AVAILABLE and path.startswith("/api/"):
            extended_result = handle_extended_api(path, "POST", body or {})
            if extended_result is not None:
                self._json(200 if extended_result.get("ok") else 400, extended_result)
                return

        if path == "/api/auth/login":
            username = str(body.get("username", "")).strip()
            password = str(body.get("password", ""))
            user = authenticate(username, password)
            if not user:
                self._json(401, {"ok": False, "error": "Invalid username or password"})
                return
            token = create_session(user)
            self._json(
                200,
                {"ok": True, "user": enrich_auth_user(user)},
                [("Set-Cookie", session_cookie_header(token))],
            )
            return

        if path == "/api/auth/logout":
            self._json(200, {"ok": True}, [("Set-Cookie", clear_session_cookie_header())])
            return

        api = self._match_display_api(path)
        if api:
            display_id, action = api
            if not self._check_api_auth(path, display_id, action):
                return
            try:
                if action == "send":
                    cmd = body.get("command") or body.get("cmd")
                    if not cmd:
                        self._json(400, {"ok": False, "error": "Missing command"})
                        return
                    self._json(200, _send(display_id, str(cmd)))
                    return
                if action == "ir":
                    from room_features import send_ir

                    cmd = body.get("command") or body.get("cmd")
                    if not cmd:
                        self._json(400, {"ok": False, "error": "Missing command"})
                        return
                    self._json(200, send_ir(display_id, str(cmd)))
                    return
                if action == "tune":
                    from room_features import tune_channel

                    channel = body.get("channel") or body.get("channel_number")
                    ir_seq = body.get("ir_command") or body.get("ir_sequence")
                    if channel is None and not ir_seq:
                        self._json(400, {"ok": False, "error": "Missing channel or ir_command"})
                        return
                    self._json(200, tune_channel(display_id, channel if channel is not None else "", ir_seq))
                    return
                if action == "beacons":
                    from room_features import report_beacon_scan

                    user_id = str(body.get("user_id") or "anonymous")
                    zone = str(body.get("zone") or "near")
                    self._json(
                        200,
                        report_beacon_scan(
                            display_id,
                            user_id=user_id,
                            zone=zone,
                            rssi=body.get("rssi"),
                            name=body.get("name"),
                        ),
                    )
                    return
                if action == "send-code":
                    code = body.get("code")
                    if not code:
                        self._json(400, {"ok": False, "error": "Missing code"})
                        return
                    self._json(200, _send_code(display_id, str(code)))
                    return
                if action == "discover":
                    self._json(200, _run_discover(display_id, quick=bool(body.get("quick"))))
                    return
                if action == "apply-template":
                    template_id = str(body.get("template") or body.get("template_id") or "").strip()
                    if not template_id:
                        self._json(400, {"ok": False, "error": "Missing template id"})
                        return
                    include_sources = bool(body.get("include_sources", True))
                    saved = apply_layout_template(display_id, template_id, include_sources=include_sources)
                    discovered = load_display_map(display_id)
                    self._json(200, {"ok": True, "display": remote_payload(saved, discovered)})
                    return
            except ValueError as exc:
                self._json(400, {"ok": False, "error": str(exc)})
                return
            except KeyError:
                self._json(404, {"ok": False, "error": "Display not found"})
                return
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
                return

        if path == "/api/locations":
            if not self._check_api_auth(path, None):
                return
            location_id = str(body.get("id", "")).strip().lower()
            if not location_id:
                self._json(400, {"ok": False, "error": "Location id is required"})
                return
            try:
                from display_manager import location_payload
                create_location(location_id, body)
                self._json(201, {"ok": True, "location": location_payload(location_id)})
            except ValueError as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
            return

        if path == "/api/displays":
            if not self._check_api_auth(path, None):
                return
            try:
                display_id = str(body.get("id", "")).strip().lower()
                if not display_id:
                    self._json(400, {"ok": False, "error": "Room id is required"})
                    return
                if not DISPLAY_ID_RE.match(display_id):
                    self._json(400, {"ok": False, "error": "Invalid room id"})
                    return
                if get_display(display_id):
                    self._json(409, {"ok": False, "error": f"Room already exists: {display_id}"})
                    return
                password = body.get("password")
                if not password:
                    self._json(400, {"ok": False, "error": "Room password is required"})
                    return
                username = str(body.get("username") or display_id).strip()
                user = self._session_user()
                loc_scope = user_location_id(user)
                if loc_scope:
                    body = dict(body)
                    body["location"] = loc_scope
                saved = create_display(display_id, body)
                set_room_credentials(display_id, username, str(password))
                self._json(201, {"ok": True, "display": remote_payload(saved, None)})
            except ValueError as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
            return

        self._json(404, {"ok": False, "error": "Not found"})

    def do_PUT(self):
        path = urlparse(self.path).path
        body = self._read_json()

        if path == "/api/auth/admin-password":
            user = self._session_user()
            if not is_admin(user):
                self._unauthorized_api()
                return
            current = str(body.get("current_password", ""))
            new_pass = str(body.get("new_password", ""))
            new_user = str(body.get("username", "")).strip() or None
            try:
                saved_username = change_admin_password(
                    current, new_pass, new_username=new_user
                )
            except ValueError as exc:
                self._json(400, {"ok": False, "error": str(exc)})
                return
            self._json(200, {"ok": True, "username": saved_username})
            return

        if path == "/api/site-settings":
            user = self._session_user()
            if not is_admin(user):
                self._unauthorized_api()
                return
            if not is_master(user):
                self._forbidden_api()
                return
            try:
                saved = save_site_settings(body)
                self._json(
                    200,
                    {
                        "ok": True,
                        "settings": saved,
                        "default_remote_url": default_remote_path(),
                    },
                )
            except ValueError as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path.startswith("/api/location-admins/"):
            user = self._session_user()
            if not is_master(user):
                self._forbidden_api()
                return
            location_id = path.split("/api/location-admins/", 1)[1].strip("/")
            if not DISPLAY_ID_RE.match(location_id):
                self._json(400, {"ok": False, "error": "Invalid location id"})
                return
            if body.get("remove"):
                remove_location_admin(location_id)
                self._json(200, {"ok": True, "removed": location_id})
                return
            username = str(body.get("username", "")).strip()
            password = body.get("password")
            if not username or not password:
                self._json(400, {"ok": False, "error": "Username and password required"})
                return
            set_location_admin_credentials(location_id, username, str(password))
            self._json(200, {"ok": True, "location_id": location_id, "username": username})
            return

        if path == "/api/displays/order":
            if not self._check_api_auth(path, None):
                return
            order = body.get("order")
            if not isinstance(order, list):
                self._json(400, {"ok": False, "error": "order must be a list"})
                return
            try:
                saved = set_room_order(order)
                self._json(200, {"ok": True, "order": saved})
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
            return

        if path == "/api/locations/order":
            if not self._check_api_auth(path, None):
                return
            order = body.get("order")
            if not isinstance(order, list):
                self._json(400, {"ok": False, "error": "order must be a list"})
                return
            try:
                saved = set_location_order(order)
                self._json(200, {"ok": True, "order": saved, "locations": list_locations()})
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
            return

        if path.startswith("/api/locations/"):
            if not self._check_api_auth(path, None):
                return
            location_id = path.split("/api/locations/", 1)[1].strip("/")
            if not DISPLAY_ID_RE.match(location_id):
                self._json(400, {"ok": False, "error": "Invalid location id"})
                return
            try:
                from display_manager import location_payload
                new_id = str(body.get("new_id") or "").strip().lower()
                payload = {k: v for k, v in body.items() if k != "new_id"}
                if new_id and new_id != location_id:
                    rename_location(location_id, new_id)
                    location_id = new_id
                saved = upsert_location(location_id, payload)
                self._json(200, {"ok": True, "location": location_payload(location_id)})
            except ValueError as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
            return

        if path.startswith("/api/layout-templates/"):
            if not self._check_api_auth(path, None):
                return
            template_id = path.split("/api/layout-templates/", 1)[1].strip("/")
            if not DISPLAY_ID_RE.match(template_id):
                self._json(400, {"ok": False, "error": "Invalid template id"})
                return
            try:
                payload: dict[str, Any] = {
                    "title": str(body.get("title") or template_id),
                    "description": str(body.get("description") or ""),
                }
                if body.get("set_default"):
                    payload["set_default"] = True
                if body.get("layout"):
                    payload["layout"] = body["layout"]
                    if body.get("sources") is not None:
                        payload["sources"] = body["sources"]
                    elif body.get("include_sources"):
                        from_room = str(body.get("from_room") or "").strip()
                        display = get_display(from_room) if from_room else None
                        if display:
                            payload["sources"] = template_from_display(
                                display, include_sources=True
                            ).get("sources")
                else:
                    from_room = str(body.get("from_room") or "").strip()
                    display = get_display(from_room) if from_room else None
                    if not display:
                        raise ValueError("layout or from_room required")
                    derived = template_from_display(
                        display, include_sources=bool(body.get("include_sources", True))
                    )
                    payload.update(derived)
                    payload["title"] = str(body.get("title") or template_id)
                    payload["description"] = str(body.get("description") or "")
                    if body.get("set_default"):
                        payload["set_default"] = True
                saved = upsert_layout_template(template_id, payload)
                self._json(200, {"ok": True, "id": template_id, "template": saved})
            except ValueError as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
            return

        api = self._match_display_api(path)
        if not api:
            self._json(404, {"ok": False, "error": "Not found"})
            return
        display_id, action = api
        if not self._check_api_auth(path, display_id, action):
            return
        try:
            if action == "config":
                new_id = str(body.get("new_id") or "").strip().lower()
                payload = {k: v for k, v in body.items() if k != "new_id"}
                if new_id and new_id != display_id:
                    if not room_id_available(new_id, exclude=display_id):
                        self._json(409, {"ok": False, "error": f"Room already exists: {new_id}"})
                        return
                    rename_display(display_id, new_id)
                    display_id = new_id
                saved = upsert_display(display_id, payload)
                discovered = load_display_map(display_id)
                self._json(200, {"ok": True, "display": remote_payload(saved, discovered)})
                return
            if action == "layout":
                layout = normalize_layout(body.get("layout") or body)
                display = get_display(display_id)
                if not display:
                    self._json(404, {"ok": False, "error": "Display not found"})
                    return
                sources = sync_source_orders_from_layout(display, layout)
                saved = upsert_display(display_id, {"layout": layout, "sources": sources})
                discovered = load_display_map(display_id)
                self._json(200, {"ok": True, "display": remote_payload(saved, discovered)})
                return
            if action == "credentials":
                username = str(body.get("username", "")).strip()
                password = body.get("password")
                if not username or not password:
                    self._json(400, {"ok": False, "error": "Username and password required"})
                    return
                set_room_credentials(display_id, username, str(password))
                self._json(200, {"ok": True, "username": username})
                return
            if action == "sources":
                display = get_display(display_id)
                if not display:
                    self._json(404, {"ok": False, "error": "Display not found"})
                    return
                sources = body.get("sources")
                if not isinstance(sources, list):
                    self._json(400, {"ok": False, "error": "sources must be a list"})
                    return
                sources = normalize_sources_for_save(sources)
                saved = upsert_display(display_id, {"sources": sources})
                discovered = load_display_map(display_id)
                self._json(
                    200,
                    {
                        "ok": True,
                        "display": remote_payload(saved, discovered),
                        "candidates": setup_candidates(saved, discovered),
                    },
                )
                return
        except Exception as exc:
            self._json(500, {"ok": False, "error": str(exc)})
            return
        self._json(404, {"ok": False, "error": "Not found"})

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/api/locations/"):
            if not self._check_api_auth(path, None):
                return
            location_id = path.split("/api/locations/", 1)[1].strip("/")
            if location_id == "order":
                self._json(405, {"ok": False, "error": "Use PUT"})
                return
            if not DISPLAY_ID_RE.match(location_id):
                self._json(400, {"ok": False, "error": "Invalid location id"})
                return
            try:
                reassign_to = str(body.get("reassign_to") or "").strip().lower() or None
                if not delete_location(location_id, reassign_to=reassign_to):
                    self._json(404, {"ok": False, "error": "Location not found"})
                    return
                self._json(200, {"ok": True, "deleted": location_id})
            except ValueError as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)})
            return

        api = self._match_display_api(path)
        if not api:
            self._json(404, {"ok": False, "error": "Not found"})
            return
        display_id, action = api
        if not self._check_api_auth(path, display_id, action or "delete"):
            return
        if action not in ("", "delete"):
            self._json(404, {"ok": False, "error": "Not found"})
            return
        if not delete_display(display_id):
            self._json(404, {"ok": False, "error": "Room not found"})
            return
        remove_room_credentials(display_id)
        self._json(200, {"ok": True, "deleted": display_id})


def _ensure_room_credentials() -> None:
    """Create default room logins for displays missing credentials."""
    for did in list_display_ids():
        if not get_room_username(did):
            set_room_credentials(did, did, did)
            print(f"  [auth] Default login for {did}: username={did} password={did}  (change in Setup)")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    _ensure_room_credentials()
    server = ThreadingHTTPServer(("0.0.0.0", port), RemoteHandler)
    ids = list_display_ids()
    print(f"Samsung Flip Remote → http://localhost:{port}")
    print(f"Default admin: admin / changeme  (auth.yaml — change on first deploy)")
    print(f"Cabins configured: {len(ids)}")
    for did in ids:
        d = get_display(did)
        if d:
            loc = display_location_id(d)
            print(f"  /d/{loc}/{did}  →  {d.get('title')}  ({d.get('ip')}:{d.get('port')})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
