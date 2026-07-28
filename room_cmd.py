#!/usr/bin/env python3
"""Send MDC commands to a room by id — for Home Assistant, scripts, and switches."""

from __future__ import annotations

import argparse
import json
import sys

from display_manager import get_display, list_display_ids, send_room_command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Control a Samsung Flip room by id")
    parser.add_argument("room", nargs="?", help="Room id from displays.yaml (e.g. cabin-1)")
    parser.add_argument("command", nargs="?", help="Command name (power_on, teams, apple, …)")
    parser.add_argument("--list-rooms", action="store_true", help="List configured room ids")
    parser.add_argument("--json", action="store_true", help="Print full JSON result")
    args = parser.parse_args(argv)

    if args.list_rooms:
        for rid in list_display_ids():
            d = get_display(rid)
            title = d.get("title") if d else rid
            print(f"{rid}\t{title}")
        return 0

    if not args.room or not args.command:
        parser.print_help()
        return 1

    try:
        result = send_room_command(args.room, args.command)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        ack = "ACK" if result.get("ack") else "NAK"
        print(f"{result['display_id']}: {result['command']} → {ack}")
        if result.get("input_label"):
            print(f"  input: {result['input_label']}")
    return 0 if result.get("ack") else 3


if __name__ == "__main__":
    raise SystemExit(main())
