"""
STB Device Implementation
Wraps Broadlink IR/RF control for set-top boxes
"""

from typing import Dict, Optional, Any
import logging
from device_abstraction import (
    SourceDevice, DeviceType, DeviceState, DeviceCapabilities,
    DeviceConnection, HDMIConnection, App
)
from broadlink_client import BroadlinkClient, BroadlinkConfig, load_ir_codes

logger = logging.getLogger(__name__)


class STBDevice(SourceDevice):
    """
    Set-Top Box controlled via Broadlink IR/RF
    """
    
    def __init__(
        self,
        device_id: str,
        name: str,
        connection: DeviceConnection,
        hdmi_connection: Optional[HDMIConnection] = None,
        channels: Optional[Dict[str, Any]] = None,
        epg_config: Optional[Dict[str, Any]] = None,
    ):
        capabilities = DeviceCapabilities(
            power_control=True,
            navigation=True,
            channel_tuning=True,
            transport_control=True,
            app_launching=False,  # STBs don't launch "apps" in the modern sense
            status_query=False,  # IR is one-way
        )
        
        super().__init__(
            device_id=device_id,
            device_type=DeviceType.STB,
            name=name,
            connection=connection,
            hdmi_connection=hdmi_connection,
            capabilities=capabilities,
        )
        
        self.channels = channels or {}
        self.epg_config = epg_config or {}
        self._broadlink_client: Optional[BroadlinkClient] = None
        self._ir_codes: Dict[str, str] = {}
    
    def connect(self) -> bool:
        """Connect to Broadlink device"""
        try:
            if not self.connection.broadlink_device or not self.connection.ir_codes_file:
                logger.error(f"{self.name}: Missing Broadlink config")
                return False
            
            # Load IR codes
            self._ir_codes = load_ir_codes(self.connection.ir_codes_file)
            if not self._ir_codes:
                logger.error(f"{self.name}: No IR codes loaded")
                return False
            
            # Initialize Broadlink client
            config = BroadlinkConfig(
                device_ip=self.connection.broadlink_device,
                timeout=self.connection.config.get("timeout", 5),
            )
            self._broadlink_client = BroadlinkClient(config)
            
            if self._broadlink_client.connect():
                self._connected = True
                self._state = DeviceState.UNKNOWN  # Can't query STB state via IR
                logger.info(f"{self.name}: Connected via Broadlink")
                return True
            else:
                logger.error(f"{self.name}: Broadlink connection failed")
                return False
                
        except Exception as e:
            logger.error(f"{self.name}: Connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Broadlink"""
        self._connected = False
        self._broadlink_client = None
        return True
    
    def power_on(self) -> bool:
        """Turn STB on"""
        return self.send_command("power_on")
    
    def power_off(self) -> bool:
        """Turn STB off"""
        return self.send_command("power_off")
    
    def send_command(self, command: str, params: Optional[Dict] = None) -> bool:
        """Send IR command to STB"""
        if not self._connected or not self._broadlink_client:
            logger.error(f"{self.name}: Not connected")
            return False
        
        # Get IR code for command
        ir_code = self._ir_codes.get(command)
        if not ir_code:
            logger.error(f"{self.name}: Unknown command '{command}'")
            return False
        
        # Send via Broadlink
        try:
            success = self._broadlink_client.send_code(ir_code)
            if success:
                logger.info(f"{self.name}: Sent command '{command}'")
            return success
        except Exception as e:
            logger.error(f"{self.name}: Failed to send '{command}': {e}")
            return False
    
    def tune_channel(self, channel_number: int) -> bool:
        """Tune to a specific channel number"""
        if not self.capabilities.channel_tuning:
            return False
        
        # Send digit sequence: e.g., 109 = digit_1, digit_0, digit_9
        digits = str(channel_number)
        for digit in digits:
            command = f"digit_{digit}"
            if not self.send_command(command):
                logger.error(f"{self.name}: Failed to send digit {digit}")
                return False
        
        logger.info(f"{self.name}: Tuned to channel {channel_number}")
        return True
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get info about a channel"""
        return self.channels.get(channel_id)
    
    def get_all_channels(self) -> Dict[str, Any]:
        """Get all configured channels"""
        return self.channels
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize STB device"""
        base = super().to_dict()
        base.update({
            "channel_count": len(self.channels),
            "has_epg": bool(self.epg_config),
            "ir_commands": list(self._ir_codes.keys()) if self._ir_codes else [],
        })
        return base
