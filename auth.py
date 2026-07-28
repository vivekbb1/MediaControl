"""Session auth — admin (full access) and per-room credentials."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
AUTH_PATH = ROOT / "auth.yaml"
SESSION_COOKIE = "flip_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def _load_auth() -> dict[str, Any]:
    if not AUTH_PATH.exists():
        data = _bootstrap_auth()
        save_auth(data)
        return data
    return yaml.safe_load(AUTH_PATH.read_text()) or {}


def _bootstrap_auth() -> dict[str, Any]:
    secret = secrets.token_hex(32)
    return {
        "secret": secret,
        "admin": {
            "username": "admin",
            "password_hash": hash_password("changeme", secret),
        },
        "rooms": {},
    }


def save_auth(data: dict[str, Any]) -> None:
    AUTH_PATH.write_text(yaml.safe_dump(data, sort_keys=False, default_flow_style=False))


def get_secret() -> str:
    return str(_load_auth().get("secret", ""))


def hash_password(password: str, secret: str | None = None) -> str:
    secret = secret or get_secret()
    return hashlib.sha256(f"{secret}:{password}".encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    secret = get_secret()
    return hmac.compare_digest(hash_password(password, secret), password_hash)


def set_admin_credentials(username: str, password: str) -> None:
    data = _load_auth()
    data["admin"] = {"username": username, "password_hash": hash_password(password)}
    save_auth(data)


def change_admin_password(
    current_password: str,
    new_password: str,
    *,
    new_username: str | None = None,
) -> str:
    data = _load_auth()
    admin = data.get("admin") or {}
    if not verify_password(current_password, admin.get("password_hash", "")):
        raise ValueError("Current password is incorrect")
    username = (new_username or admin.get("username") or "admin").strip()
    if not username:
        raise ValueError("Username is required")
    if not new_password:
        raise ValueError("New password is required")
    set_admin_credentials(username, new_password)
    return username


def set_room_credentials(display_id: str, username: str, password: str) -> None:
    data = _load_auth()
    rooms = data.setdefault("rooms", {})
    rooms[display_id] = {
        "username": username,
        "password_hash": hash_password(password),
    }
    save_auth(data)


def remove_room_credentials(display_id: str) -> None:
    data = _load_auth()
    rooms = data.get("rooms") or {}
    rooms.pop(display_id, None)
    data["rooms"] = rooms
    save_auth(data)


def rename_room_credentials(old_id: str, new_id: str) -> None:
    if old_id == new_id:
        return
    data = _load_auth()
    rooms = data.get("rooms") or {}
    if old_id in rooms:
        rooms[new_id] = rooms.pop(old_id)
        save_auth(data)


def get_room_username(display_id: str) -> str | None:
    room = (_load_auth().get("rooms") or {}).get(display_id)
    return room.get("username") if room else None


def authenticate(username: str, password: str) -> dict[str, Any] | None:
    data = _load_auth()
    admin = data.get("admin") or {}
    if username == admin.get("username") and verify_password(password, admin.get("password_hash", "")):
        return {"role": "admin", "username": username, "scope": "master"}

    for location_id, loc_admin in (data.get("location_admins") or {}).items():
        if username == loc_admin.get("username") and verify_password(
            password, loc_admin.get("password_hash", "")
        ):
            return {
                "role": "location_admin",
                "username": username,
                "location_id": location_id,
                "scope": "location",
            }

    for display_id, room in (data.get("rooms") or {}).items():
        if username == room.get("username") and verify_password(password, room.get("password_hash", "")):
            return {"role": "room", "username": username, "display_id": display_id, "scope": "room"}
    return None


def create_session(user: dict[str, Any]) -> str:
    secret = get_secret()
    payload = base64.urlsafe_b64encode(json.dumps(user, separators=(",", ":")).encode()).decode().rstrip("=")
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def parse_session(token: str | None) -> dict[str, Any] | None:
    if not token or "." not in token:
        return None
    payload, sig = token.rsplit(".", 1)
    secret = get_secret()
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return None
    pad = "=" * (-len(payload) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(payload + pad))
    except (json.JSONDecodeError, ValueError):
        return None
    if data.get("role") not in ("admin", "location_admin", "room"):
        return None
    if data.get("role") == "room" and not data.get("display_id"):
        return None
    if data.get("role") == "location_admin" and not data.get("location_id"):
        return None
    return data


def is_master(user: dict[str, Any] | None) -> bool:
    return bool(user and user.get("role") == "admin")


def is_location_admin(user: dict[str, Any] | None) -> bool:
    return bool(user and user.get("role") == "location_admin")


def user_location_id(user: dict[str, Any] | None) -> str | None:
    if not user:
        return None
    if user.get("role") == "location_admin":
        return str(user.get("location_id") or "")
    return None


def can_access_display(user: dict[str, Any] | None, display_id: str) -> bool:
    if not user:
        return False
    if user.get("role") == "admin":
        return True
    if user.get("role") == "location_admin":
        from display_manager import get_display

        display = get_display(display_id)
        if not display:
            return False
        return str(display.get("location") or "") == str(user.get("location_id") or "")
    return user.get("role") == "room" and user.get("display_id") == display_id


def can_access_location(user: dict[str, Any] | None, location_id: str) -> bool:
    if not user:
        return False
    if user.get("role") == "admin":
        return True
    return user.get("role") == "location_admin" and user.get("location_id") == location_id


def can_manage_site(user: dict[str, Any] | None) -> bool:
    return is_master(user)


def set_location_admin_credentials(location_id: str, username: str, password: str) -> None:
    data = _load_auth()
    admins = data.setdefault("location_admins", {})
    admins[location_id] = {
        "username": username,
        "password_hash": hash_password(password),
    }
    save_auth(data)


def remove_location_admin(location_id: str) -> None:
    data = _load_auth()
    admins = data.get("location_admins") or {}
    admins.pop(location_id, None)
    data["location_admins"] = admins
    save_auth(data)


def list_location_admins() -> dict[str, str]:
    data = _load_auth()
    return {
        lid: str(entry.get("username") or "")
        for lid, entry in (data.get("location_admins") or {}).items()
    }


def is_admin(user: dict[str, Any] | None) -> bool:
    """Master or location admin — can open management UI within their scope."""
    return is_master(user) or is_location_admin(user)


def session_cookie_header(token: str, max_age: int = SESSION_MAX_AGE) -> str:
    return f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}"


def clear_session_cookie_header() -> str:
    return f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"
