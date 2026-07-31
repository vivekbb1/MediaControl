"""
Device Abstraction Layer for Multi-Device Control
Supports: STBs, Apple TV, Android TV, HDMI Matrix, and more
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Types of controllable devices"""
    STB = "stb"
    APPLE_TV = "apple_tv"
    ANDROID_TV = "android_tv"
    FIRE_TV = "fire_tv"
    ROKU = "roku"
    GAME_CONSOLE = "game_console"
    HDMI_MATRIX = "hdmi_matrix"
    DISPLAY = "display"
    AUDIO_RECEIVER = "audio_receiver"
    ENCODER = "encoder"


class ControlProtocol(Enum):
    """Control protocols for devices"""
    IR = "ir"  # Infrared via Broadlink
    RF = "rf"  # Radio Frequency via Broadlink
    CEC = "cec"  # HDMI-CEC
    NETWORK_API = "network_api"  # RESTful API
    PYATV = "pyatv"  # Apple TV protocol
    ADB = "adb"  # Android Debug Bridge
    RS232 = "rs232"  # Serial
    TCP = "tcp"  # Raw TCP
    MDC = "mdc"  # Samsung MDC protocol


class DeviceState(Enum):
    """Device power states"""
    ON = "on"
    OFF = "off"
    STANDBY = "standby"
    UNKNOWN = "unknown"


@dataclass
class DeviceConnection:
    """Physical/network connection details"""
    protocol: ControlProtocol
    ip: Optional[str] = None
    port: Optional[int] = None
    mac: Optional[str] = None
    serial_port: Optional[str] = None
    broadlink_device: Optional[str] = None
    credentials_file: Optional[str] = None
    ir_codes_file: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HDMIConnection:
    """HDMI physical connection"""
    display_id: str
    input_port: str  # "hdmi1", "hdmi2", etc.
    via_matrix: bool = False
    matrix_input: Optional[int] = None
    matrix_output: Optional[int] = None


@dataclass
class App:
    """Streamable app or channel"""
    id: str  # app bundle ID or package name
    name: str
    icon: str
    category: Optional[str] = None
    deep_link: Optional[str] = None


@dataclass
class DeviceCapabilities:
    """What a device can do"""
    power_control: bool = True
    input_switching: bool = False
    volume_control: bool = False
    navigation: bool = False
    app_launching: bool = False
    channel_tuning: bool = False
    transport_control: bool = False  # play/pause/ff/rw
    status_query: bool = False
    text_input: bool = False


class SourceDevice:
    """
    Abstract base for all source devices (STB, Apple TV, Android TV, etc.)
    """
    
    def __init__(
        self,
        device_id: str,
        device_type: DeviceType,
        name: str,
        connection: DeviceConnection,
        hdmi_connection: Optional[HDMIConnection] = None,
        capabilities: Optional[DeviceCapabilities] = None,
        apps: Optional[List[App]] = None,
    ):
        self.id = device_id
        self.type = device_type
        self.name = name
        self.connection = connection
        self.hdmi_connection = hdmi_connection
        self.capabilities = capabilities or DeviceCapabilities()
        self.apps = apps or []
        self._state = DeviceState.UNKNOWN
        self._current_app = None
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to the device. Override in subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement connect()")
    
    def disconnect(self) -> bool:
        """Disconnect from device. Override in subclasses."""
        self._connected = False
        return True
    
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self._connected
    
    def power_on(self) -> bool:
        """Turn device on. Override in subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement power_on()")
    
    def power_off(self) -> bool:
        """Turn device off. Override in subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement power_off()")
    
    def send_command(self, command: str, params: Optional[Dict] = None) -> bool:
        """Send generic command. Override in subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement send_command()")
    
    def launch_app(self, app_id: str) -> bool:
        """Launch an app by ID. Override in subclasses if supported."""
        if not self.capabilities.app_launching:
            logger.warning(f"{self.name} does not support app launching")
            return False
        raise NotImplementedError(f"{self.__class__.__name__} must implement launch_app()")
    
    def get_state(self) -> DeviceState:
        """Get current power state"""
        return self._state
    
    def get_current_app(self) -> Optional[str]:
        """Get currently running app ID"""
        return self._current_app
    
    def get_apps(self) -> List[App]:
        """Get list of available apps"""
        return self.apps
    
    def get_app_by_id(self, app_id: str) -> Optional[App]:
        """Find app by ID"""
        for app in self.apps:
            if app.id == app_id:
                return app
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize device to dict"""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "state": self._state.value,
            "connected": self._connected,
            "current_app": self._current_app,
            "apps": [
                {
                    "id": app.id,
                    "name": app.name,
                    "icon": app.icon,
                    "category": app.category,
                }
                for app in self.apps
            ],
            "capabilities": {
                "power_control": self.capabilities.power_control,
                "input_switching": self.capabilities.input_switching,
                "volume_control": self.capabilities.volume_control,
                "navigation": self.capabilities.navigation,
                "app_launching": self.capabilities.app_launching,
                "channel_tuning": self.capabilities.channel_tuning,
                "transport_control": self.capabilities.transport_control,
                "status_query": self.capabilities.status_query,
                "text_input": self.capabilities.text_input,
            },
            "hdmi_connection": {
                "display_id": self.hdmi_connection.display_id,
                "input_port": self.hdmi_connection.input_port,
                "via_matrix": self.hdmi_connection.via_matrix,
            } if self.hdmi_connection else None,
        }


class SourceManager:
    """
    Manages all source devices in a room
    """
    
    def __init__(self):
        self.devices: Dict[str, SourceDevice] = {}
        logger.info("SourceManager initialized")
    
    def add_device(self, device: SourceDevice):
        """Register a source device"""
        self.devices[device.id] = device
        logger.info(f"Added device: {device.name} ({device.id})")
    
    def remove_device(self, device_id: str) -> bool:
        """Unregister a source device"""
        if device_id in self.devices:
            device = self.devices[device_id]
            device.disconnect()
            del self.devices[device_id]
            logger.info(f"Removed device: {device_id}")
            return True
        return False
    
    def get_device(self, device_id: str) -> Optional[SourceDevice]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[SourceDevice]:
        """Get all devices of a specific type"""
        return [d for d in self.devices.values() if d.type == device_type]
    
    def get_all_devices(self) -> List[SourceDevice]:
        """Get all registered devices"""
        return list(self.devices.values())
    
    def connect_all(self) -> Dict[str, bool]:
        """Connect to all devices. Returns dict of device_id: success"""
        results = {}
        for device_id, device in self.devices.items():
            try:
                results[device_id] = device.connect()
            except Exception as e:
                logger.error(f"Failed to connect to {device.name}: {e}")
                results[device_id] = False
        return results
    
    def disconnect_all(self):
        """Disconnect from all devices"""
        for device in self.devices.values():
            try:
                device.disconnect()
            except Exception as e:
                logger.error(f"Failed to disconnect from {device.name}: {e}")
    
    def find_app(self, app_id: str) -> Optional[tuple[SourceDevice, App]]:
        """Find which device has a specific app"""
        for device in self.devices.values():
            app = device.get_app_by_id(app_id)
            if app:
                return (device, app)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize all devices"""
        return {
            "devices": {
                device_id: device.to_dict()
                for device_id, device in self.devices.items()
            }
        }


class ContextManager:
    """
    Tracks which source is active on each display
    Routes contextual commands (D-pad, etc.) to the correct device
    """
    
    def __init__(self):
        self.active_sources: Dict[str, str] = {}  # display_id → source_device_id
        logger.info("ContextManager initialized")
    
    def set_active_source(self, display_id: str, source_id: str):
        """Set which source is currently active on a display"""
        self.active_sources[display_id] = source_id
        logger.info(f"Display {display_id} active source: {source_id}")
    
    def get_active_source(self, display_id: str) -> Optional[str]:
        """Get currently active source for a display"""
        return self.active_sources.get(display_id)
    
    def clear_active_source(self, display_id: str):
        """Clear active source for a display"""
        if display_id in self.active_sources:
            del self.active_sources[display_id]
            logger.info(f"Cleared active source for display {display_id}")
    
    def get_all_active(self) -> Dict[str, str]:
        """Get all active sources"""
        return self.active_sources.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize context state"""
        return {
            "active_sources": self.active_sources.copy()
        }
