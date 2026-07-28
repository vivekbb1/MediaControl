#!/usr/bin/env python3
"""Samsung MDC client for Flip Pro WM55B over RJ45 (TCP port 1515)."""

from __future__ import annotations

import argparse
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class MdcConfig:
    host: str
    port: int = 1515
    device_id: int = 0
    timeout_sec: float = 3.0
    retry_count: int = 3
    retry_delay_sec: float = 2.0
    reconnect_after_power_on_sec: float = 10.0


def checksum(command: int, device_id: int, data: bytes) -> int:
    return (command + device_id + len(data) + sum(data)) & 0xFF


def build_packet(command: int, device_id: int, data: bytes = b"") -> bytes:
    return bytes([0xAA, command, device_id, len(data), *data, checksum(command, device_id, data)])


def parse_hex(value: str) -> bytes:
    cleaned = value.replace(" ", "").replace("0x", "").replace("\\x", "")
    if len(cleaned) % 2:
        raise ValueError(f"Invalid hex string: {value!r}")
    return bytes.fromhex(cleaned)


def format_hex(data: bytes) -> str:
    return " ".join(f"{b:02X}" for b in data)


class MdcClient:
    def __init__(self, config: MdcConfig):
        self.config = config

    def send_raw(self, payload: bytes, expect_response: bool = True) -> bytes | None:
        with socket.create_connection((self.config.host, self.config.port), timeout=self.config.timeout_sec) as sock:
            sock.sendall(payload)
            if not expect_response:
                return None
            sock.settimeout(self.config.timeout_sec)
            chunks: list[bytes] = []
            try:
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    if len(chunk) < 4096:
                        break
            except socket.timeout:
                pass
            return b"".join(chunks) if chunks else None

    def send_command(self, command: int, data: bytes = b"", *, expect_response: bool | None = None) -> bytes | None:
        if expect_response is None:
            expect_response = self.config.device_id != 0xFE
        packet = build_packet(command, self.config.device_id, data)
        return self.send_raw(packet, expect_response=expect_response)

    def send_named(self, name: str, commands: dict[str, str]) -> bytes | None:
        if name not in commands:
            raise KeyError(f"Unknown command {name!r}. Available: {', '.join(sorted(commands))}")
        payload = parse_hex(commands[name])
        expect = self.config.device_id != 0xFE
        return self.send_raw(payload, expect_response=expect)

    def power_on(self) -> bytes | None:
        response = self._retry_command(0x11, b"\x01")
        time.sleep(self.config.reconnect_after_power_on_sec)
        return response

    def power_off(self) -> bytes | None:
        return self._retry_command(0x11, b"\x00")

    def reboot(self) -> tuple[bytes | None, str]:
        """Reboot via MDC 0x11/0x02; fall back to power cycle when the panel NAKs."""
        response = self._retry_command(0x11, b"\x02")
        if response and len(response) >= 5 and response[4] == 0x41:
            return response, "mdc"
        self.power_off()
        time.sleep(3.0)
        response = self.power_on()
        return response, "power_cycle"

    def set_input(self, source: int) -> bytes | None:
        return self.send_command(0x14, bytes([source]))

    def status(self) -> bytes | None:
        return self.send_command(0x00)

    def connection_type(self) -> bytes | None:
        return self.send_command(0x1D)

    def _retry_command(self, command: int, data: bytes) -> bytes | None:
        last: bytes | None = None
        for attempt in range(self.config.retry_count):
            last = self.send_command(command, data)
            if last and len(last) >= 5 and last[4] == 0x41:
                return last
            if attempt + 1 < self.config.retry_count:
                time.sleep(self.config.retry_delay_sec)
        return last


def load_config(path: Path) -> tuple[MdcConfig, dict[str, str], dict[str, int]]:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    raw = yaml.safe_load(path.read_text())
    display = raw["display"]
    cfg = MdcConfig(
        host=display["ip"],
        port=int(display.get("port", 1515)),
        device_id=int(display.get("device_id", 0)),
        timeout_sec=float(display.get("timeout_sec", 3)),
        retry_count=int(display.get("retry_count", 3)),
        retry_delay_sec=float(display.get("retry_delay_sec", 2)),
        reconnect_after_power_on_sec=float(display.get("reconnect_after_power_on_sec", 10)),
    )
    commands = {k: v.replace(" ", "") for k, v in raw.get("commands", {}).items()}
    inputs = {k: int(v) if isinstance(v, int) else int(str(v), 0) for k, v in raw.get("inputs", {}).items()}
    return cfg, commands, inputs


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Control Samsung Flip Pro via MDC/RJ45")
    parser.add_argument("-c", "--config", type=Path, default=Path(__file__).with_name("config.yaml"))
    parser.add_argument("command", nargs="?", help="Command name from config.yaml commands section")
    parser.add_argument("--input", dest="input_name", help="Input alias from config inputs section, e.g. hdmi1")
    parser.add_argument("--hex", dest="hex_payload", help="Send raw hex packet")
    parser.add_argument("--host", help="Override display IP")
    parser.add_argument("--id", type=lambda x: int(x, 0), help="Override device ID (decimal or 0xFE)")
    args = parser.parse_args(list(argv) if argv is not None else None)

    cfg, commands, inputs = load_config(args.config)
    if args.host:
        cfg.host = args.host
    if args.id is not None:
        cfg.device_id = args.id

    client = MdcClient(cfg)

    if args.hex_payload:
        payload = parse_hex(args.hex_payload)
        response = client.send_raw(payload)
    elif args.input_name:
        if args.input_name not in inputs:
            print(f"Unknown input {args.input_name!r}", file=sys.stderr)
            return 2
        response = client.set_input(inputs[args.input_name])
    elif args.command == "power_on":
        response = client.power_on()
    elif args.command == "power_off":
        response = client.power_off()
    elif args.command:
        response = client.send_named(args.command, commands)
    else:
        parser.print_help()
        return 1

    if response:
        print(format_hex(response))
    else:
        print("(no response)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
