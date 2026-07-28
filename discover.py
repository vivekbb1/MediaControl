#!/usr/bin/env python3
"""Probe Samsung MDC commands and build a map from device responses."""

from __future__ import annotations

import json
import socket
import time
from pathlib import Path
from typing import Any

DEFAULT_HOST = "10.10.10.17"
DEFAULT_PORT = 1515
MAP_PATH = Path(__file__).with_name("discovered_map.json")


def checksum(command: int, device_id: int, data: bytes) -> int:
    return (command + device_id + len(data) + sum(data)) & 0xFF


def build_packet(command: int, device_id: int = 0, data: bytes = b"") -> bytes:
    return bytes([0xAA, command, device_id, len(data), *data, checksum(command, device_id, data)])


def send_recv(host: str, port: int, payload: bytes, timeout: float = 2.0) -> bytes:
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.send(payload)
        sock.settimeout(timeout)
        try:
            return sock.recv(4096)
        except socket.timeout:
            return b""


def parse_response(resp: bytes) -> dict[str, Any]:
    if not resp:
        return {"status": "no_response", "raw": ""}
    raw = resp.hex(" ").upper()
    if len(resp) < 5:
        return {"status": "short", "raw": raw}
    if resp[4] == 0x41:
        out: dict[str, Any] = {"status": "ACK", "raw": raw, "ack": True}
        if len(resp) >= 7:
            out["ref_cmd"] = f"0x{resp[5]:02X}"
            out["value"] = f"0x{resp[6]:02X}"
            out["value_dec"] = resp[6]
        return out
    if resp[4] == 0x4E:
        out = {"status": "NAK", "raw": raw, "ack": False}
        if len(resp) >= 7:
            out["ref_cmd"] = f"0x{resp[5]:02X}"
            out["error"] = f"0x{resp[6]:02X}"
        return out
    return {"status": "unknown", "raw": raw, "ack": False}


def query_input(host: str, port: int, device_id: int = 0) -> dict[str, Any]:
    return parse_response(send_recv(host, port, build_packet(0x14, device_id)))


def set_input(
    host: str, port: int, code: int, settle: float = 0.8, device_id: int = 0
) -> tuple[dict[str, Any], dict[str, Any]]:
    pkt = build_packet(0x14, device_id, bytes([code]))
    set_resp = parse_response(send_recv(host, port, pkt))
    time.sleep(settle)
    query_resp = query_input(host, port, device_id)
    return set_resp, query_resp


def set_volume(
    host: str, port: int, level: int, device_id: int = 0
) -> tuple[dict[str, Any], dict[str, Any]]:
    pkt = build_packet(0x12, device_id, bytes([level]))
    set_resp = parse_response(send_recv(host, port, pkt))
    time.sleep(0.3)
    query_resp = parse_response(send_recv(host, port, build_packet(0x12, device_id)))
    return set_resp, query_resp


def discover(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    full_scan: bool = True,
    device_id: int = 0,
) -> dict[str, Any]:
    results: dict[str, Any] = {
        "host": host,
        "port": port,
        "device_id": device_id,
        "inputs": [],
        "volumes": [],
        "queries": {},
    }

    for name, cmd, data in [
        ("power", 0x11, b""),
        ("input", 0x14, b""),
        ("volume", 0x12, b""),
        ("mute", 0x13, b""),
    ]:
        results["queries"][name] = parse_response(
            send_recv(host, port, build_packet(cmd, device_id, data))
        )

    codes = range(0x100) if full_scan else [0x21, 0x23, 0x25, 0x31, 0x61, 0x64, 0x65, 0x69, 0x6A]
    for code in codes:
        set_resp, query_resp = set_input(host, port, code, device_id=device_id)
        if set_resp.get("status") != "ACK":
            continue
        stable = query_resp.get("value") == set_resp.get("value")
        results["inputs"].append(
            {
                "code": f"0x{code:02X}",
                "code_dec": code,
                "packet": build_packet(0x14, device_id, bytes([code])).hex().upper(),
                "set": set_resp,
                "query_after": query_resp,
                "stable": stable,
            }
        )

    for level in [0, 1, 25, 50, 75, 100]:
        set_resp, query_resp = set_volume(host, port, level, device_id=device_id)
        results["volumes"].append(
            {
                "level": level,
                "packet": build_packet(0x12, device_id, bytes([level])).hex().upper(),
                "set": set_resp,
                "query_after": query_resp,
                "ok": set_resp.get("ack") and query_resp.get("value_dec") == level,
            }
        )

    return results


def save_map(data: dict[str, Any], path: Path = MAP_PATH) -> Path:
    path.write_text(json.dumps(data, indent=2))
    return path


def load_map(path: Path = MAP_PATH) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def summary(data: dict[str, Any]) -> str:
    lines = ["Stable inputs (SET ACK + query matches):"]
    for item in data.get("inputs", []):
        if item.get("stable"):
            lines.append(f"  {item['code']}  packet={item['packet']}")
    lines.append("Unstable inputs (ACK but query differs):")
    for item in data.get("inputs", []):
        if not item.get("stable"):
            s = item["set"].get("value", "?")
            q = item["query_after"].get("value", "?")
            lines.append(f"  {item['code']}  set={s} query={q}  packet={item['packet']}")
    lines.append("Volumes verified:")
    for v in data.get("volumes", []):
        if v.get("ok"):
            lines.append(f"  {v['level']}%  packet={v['packet']}")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Discover Samsung MDC command responses")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--device-id", type=int, default=0)
    parser.add_argument("--quick", action="store_true", help="Only probe known candidate codes")
    parser.add_argument("-o", "--output", type=Path, default=MAP_PATH)
    args = parser.parse_args()

    data = discover(args.host, args.port, full_scan=not args.quick, device_id=args.device_id)
    save_map(data, args.output)
    print(summary(data))
    print(f"\nSaved {args.output}")


if __name__ == "__main__":
    main()
