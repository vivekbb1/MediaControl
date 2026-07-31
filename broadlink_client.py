#!/usr/bin/env python3
"""Broadlink RM4 Mini/Pro client for IR/RF control of set-top boxes and AV equipment."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import broadlink
    from broadlink.exceptions import BroadlinkException
    BROADLINK_AVAILABLE = True
except ImportError:
    BROADLINK_AVAILABLE = False
    broadlink = None
    BroadlinkException = Exception

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class BroadlinkConfig:
    """Configuration for a Broadlink IR/RF device."""
    host: str
    port: int = 80
    mac: str = ""  # MAC address in hex format (e.g., "24DFA7F94D84")
    device_type: int = 0x61A2  # RM4 Mini: 0x61A2, RM4 Pro: 0x648D
    timeout_sec: float = 5.0
    name: str = "Broadlink Device"

    @property
    def mac_bytes(self) -> bytes:
        """Convert MAC string to bytes."""
        if not self.mac:
            return b"\x00\x00\x00\x00\x00\x00"
        clean = self.mac.replace(":", "").replace("-", "").replace(" ", "")
        return bytes.fromhex(clean)


class BroadlinkClient:
    """Client for controlling Broadlink RM4 Mini/Pro IR/RF devices."""

    def __init__(self, config: BroadlinkConfig):
        if not BROADLINK_AVAILABLE:
            raise RuntimeError(
                "Broadlink library not installed. Install with: pip3 install broadlink"
            )
        
        self.config = config
        self.device = None
        self.authenticated = False
        self.logger = logging.getLogger(f"broadlink.{config.name}")

    def connect(self) -> bool:
        """Connect and authenticate with the Broadlink device."""
        try:
            # Create device instance
            self.device = broadlink.gendevice(
                self.config.device_type,
                (self.config.host, self.config.port),
                self.config.mac_bytes
            )
            
            # Authenticate
            self.device.auth()
            self.authenticated = True
            self.logger.info(f"Connected to {self.config.name} at {self.config.host}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.config.name}: {e}")
            self.authenticated = False
            return False

    def ensure_connected(self) -> bool:
        """Ensure device is connected, reconnecting if necessary."""
        if not self.authenticated or not self.device:
            return self.connect()
        return True

    def send_code(self, ir_code: str) -> dict[str, Any]:
        """
        Send an IR/RF code to the device.
        
        Args:
            ir_code: Hex string of the IR/RF code (e.g., "2600...")
            
        Returns:
            Dict with status and any error messages
        """
        if not self.ensure_connected():
            return {"ok": False, "error": "Not connected to Broadlink device"}

        try:
            # Convert hex string to bytes
            code_bytes = bytes.fromhex(ir_code.replace(" ", "").replace("0x", ""))
            
            # Send the code
            self.device.send_data(code_bytes)
            self.logger.debug(f"Sent IR code: {ir_code[:20]}...")
            
            return {"ok": True, "message": "IR code sent successfully"}
            
        except Exception as e:
            self.logger.error(f"Failed to send IR code: {e}")
            return {"ok": False, "error": str(e)}

    def learn_code(self, timeout: int = 10) -> dict[str, Any]:
        """
        Enter learning mode and capture an IR/RF code.
        
        Args:
            timeout: Seconds to wait for a code
            
        Returns:
            Dict with captured code or error
        """
        if not self.ensure_connected():
            return {"ok": False, "error": "Not connected to Broadlink device"}

        try:
            self.logger.info("Entering learning mode...")
            self.device.enter_learning()
            
            # Poll for captured data
            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(0.5)
                try:
                    learned_data = self.device.check_data()
                    if learned_data:
                        ir_code = learned_data.hex()
                        self.logger.info(f"Captured IR code: {ir_code[:20]}...")
                        return {
                            "ok": True,
                            "code": ir_code,
                            "message": "IR code captured successfully"
                        }
                except Exception:
                    continue
            
            return {"ok": False, "error": "Timeout: No IR code captured"}
            
        except Exception as e:
            self.logger.error(f"Failed to learn IR code: {e}")
            return {"ok": False, "error": str(e)}

    def get_temperature(self) -> float:
        """
        Get temperature reading (requires HTS2 sensor cable on RM4 Pro).
        
        Returns:
            Temperature in Celsius, or 0.0 if not available
        """
        if not self.ensure_connected():
            return 0.0

        try:
            temp = self.device.check_temperature()
            return temp if temp else 0.0
        except Exception as e:
            self.logger.debug(f"Temperature not available: {e}")
            return 0.0

    @staticmethod
    def discover(timeout: int = 5, local_ip: str | None = None) -> list[dict[str, Any]]:
        """
        Discover Broadlink devices on the network.
        
        Args:
            timeout: Discovery timeout in seconds
            local_ip: Local IP address to bind to (optional)
            
        Returns:
            List of discovered devices with their details
        """
        if not BROADLINK_AVAILABLE:
            return []

        try:
            kwargs = {"timeout": timeout}
            if local_ip:
                kwargs["local_ip_address"] = local_ip
            
            devices = broadlink.discover(**kwargs)
            
            result = []
            for dev in devices:
                result.append({
                    "type": f"{dev.type:04X}",
                    "host": dev.host[0],
                    "port": dev.host[1],
                    "mac": dev.mac.hex().upper(),
                    "name": dev.__class__.__name__,
                    "is_locked": getattr(dev, 'is_locked', False)
                })
            
            return result
            
        except Exception as e:
            logging.error(f"Discovery failed: {e}")
            return []


def load_ir_codes(yaml_file: Path) -> dict[str, str]:
    """Load IR codes from a YAML file."""
    if not yaml or not yaml_file.exists():
        return {}
    
    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("ir_codes", {}) if data else {}
    except Exception as e:
        logging.error(f"Failed to load IR codes from {yaml_file}: {e}")
        return {}


def save_ir_code(yaml_file: Path, command_name: str, ir_code: str) -> bool:
    """Save a learned IR code to a YAML file."""
    if not yaml:
        return False
    
    try:
        # Load existing codes
        codes = load_ir_codes(yaml_file)
        
        # Add/update the code
        codes[command_name] = ir_code
        
        # Save back
        yaml_file.parent.mkdir(parents=True, exist_ok=True)
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump({"ir_codes": codes}, f, default_flow_style=False)
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to save IR code: {e}")
        return False


# Convenience function for CLI testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Broadlink IR/RF controller")
    parser.add_argument("--discover", action="store_true", help="Discover devices")
    parser.add_argument("--learn", action="store_true", help="Learn an IR code")
    parser.add_argument("--send", help="Send IR code (hex string)")
    parser.add_argument("--host", help="Device IP address")
    parser.add_argument("--mac", help="Device MAC address")
    parser.add_argument("--type", default="0x61A2", help="Device type (default: RM4 Mini)")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    if args.discover:
        print("Discovering Broadlink devices...")
        devices = BroadlinkClient.discover()
        if devices:
            print(f"\nFound {len(devices)} device(s):")
            for dev in devices:
                print(f"  Type: {dev['type']}, Host: {dev['host']}, MAC: {dev['mac']}")
        else:
            print("No devices found")
    
    elif args.learn or args.send:
        if not args.host:
            print("Error: --host required")
            exit(1)
        
        config = BroadlinkConfig(
            host=args.host,
            mac=args.mac or "",
            device_type=int(args.type, 16) if args.type.startswith("0x") else int(args.type)
        )
        
        client = BroadlinkClient(config)
        
        if args.learn:
            print("Point remote at Broadlink and press button...")
            result = client.learn_code(timeout=15)
            if result["ok"]:
                print(f"\nCaptured code:\n{result['code']}")
            else:
                print(f"Error: {result['error']}")
        
        elif args.send:
            result = client.send_code(args.send)
            if result["ok"]:
                print("Code sent successfully")
            else:
                print(f"Error: {result['error']}")
    
    else:
        parser.print_help()
