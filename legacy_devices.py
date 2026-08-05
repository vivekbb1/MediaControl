"""
Legacy Device Controller with Gateway/Sub-Device Architecture
Support for analog/digital legacy devices via IR/RF/RS232/RS485
Gateways: Broadlink, RS232 controllers (count toward subscription)
Sub-devices: ACs, fans, switches, etc. (count toward device limit)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class GatewayType(Enum):
    """Types of control gateways"""
    BROADLINK_IR = "broadlink_ir"  # Broadlink RM4 Mini (IR only)
    BROADLINK_RF = "broadlink_rf"  # Broadlink RM4 Pro (IR + RF 433MHz)
    RS232_CONTROLLER = "rs232_controller"  # Serial/RS232 controller
    RS485_CONTROLLER = "rs485_controller"  # RS485 controller
    TCP_IP_GATEWAY = "tcp_ip_gateway"  # Generic TCP/IP gateway
    KNX_GATEWAY = "knx_gateway"  # KNX IP gateway


class LegacyDeviceType(Enum):
    """Types of legacy devices"""
    AIR_CONDITIONER = "air_conditioner"
    FAN = "fan"
    SWITCH = "switch"              # Power switch, scene switch
    PROJECTOR = "projector"
    AUDIO_AMPLIFIER = "audio_amplifier"
    AUDIO_RECEIVER = "audio_receiver"
    SCREEN = "screen"              # Projection screen
    BLINDS = "blinds"              # Motorized blinds/curtains
    LIGHTS = "lights"              # IR-controlled lights
    RS232_DEVICE = "rs232_device"  # RS232/serial controlled devices
    RS485_DEVICE = "rs485_device"  # RS485 device
    GENERIC_IR = "generic_ir"      # Any IR device
    GENERIC_RF = "generic_rf"      # Any RF device (433MHz, etc.)


class ControlProtocol(Enum):
    """Control protocols for legacy devices"""
    INFRARED = "infrared"      # IR (Broadlink RM4)
    RADIO_FREQUENCY = "radio_frequency"  # RF 433MHz (Broadlink RM4 Pro)
    RS232 = "rs232"            # Serial communication
    RS485 = "rs485"            # RS485 communication
    TCP_IP = "tcp_ip"          # Network-based control
    UDP = "udp"                # UDP control


@dataclass
class Gateway:
    """
    Control gateway (counts toward gateway limit in subscription)
    Examples: Broadlink RM4, RS232 controller, KNX gateway
    """
    gateway_id: str
    name: str
    gateway_type: GatewayType
    
    # Connection details
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    serial_port: Optional[str] = None  # For RS232/RS485
    tcp_port: int = 23
    
    # Gateway-specific settings
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Sub-devices connected to this gateway
    sub_devices: List[str] = field(default_factory=list)  # List of device_ids
    
    def add_sub_device(self, device_id: str):
        """Add a sub-device to this gateway"""
        if device_id not in self.sub_devices:
            self.sub_devices.append(device_id)
    
    def remove_sub_device(self, device_id: str):
        """Remove a sub-device from this gateway"""
        if device_id in self.sub_devices:
            self.sub_devices.remove(device_id)


class ACMode(Enum):
    """Air conditioner modes"""
    AUTO = "auto"
    COOL = "cool"
    HEAT = "heat"
    DRY = "dry"
    FAN = "fan"
    OFF = "off"


class FanSpeed(Enum):
    """Fan speed levels"""
    OFF = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    AUTO = 99


@dataclass
class ACState:
    """Air conditioner state"""
    power: bool = False
    mode: ACMode = ACMode.OFF
    temperature: int = 24  # Celsius
    fan_speed: FanSpeed = FanSpeed.AUTO
    swing: bool = False


@dataclass
class FanState:
    """Fan state"""
    power: bool = False
    speed: FanSpeed = FanSpeed.OFF
    oscillation: bool = False
    timer: Optional[int] = None  # minutes


@dataclass
class Gateway:
    """
    Control gateway (counts toward gateway limit in subscription)
    Examples: Broadlink RM4, RS232 controller, KNX gateway
    """
    gateway_id: str
    name: str
    gateway_type: GatewayType
    
    # Connection details
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    serial_port: Optional[str] = None  # For RS232/RS485
    tcp_port: int = 23
    
    # Gateway-specific settings
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Sub-devices connected to this gateway
    sub_devices: List[str] = field(default_factory=list)  # List of device_ids
    
    def add_sub_device(self, device_id: str):
        """Add a sub-device to this gateway"""
        if device_id not in self.sub_devices:
            self.sub_devices.append(device_id)
    
    def remove_sub_device(self, device_id: str):
        """Remove a sub-device from this gateway"""
        if device_id in self.sub_devices:
            self.sub_devices.remove(device_id)


@dataclass
class LegacyDeviceConfig:
    """
    Configuration for a legacy sub-device (counts toward device limit)
    Must be attached to a Gateway
    """
    device_id: str
    name: str
    device_type: LegacyDeviceType
    control_protocol: ControlProtocol
    gateway_id: str  # Which gateway controls this device
    
    # Command codes (IR/RF hex codes, RS232 strings, etc.)
    commands: Dict[str, str] = field(default_factory=dict)
    
    # Device-specific settings
    settings: Dict[str, Any] = field(default_factory=dict)


class LegacyDeviceController:
    """
    Universal controller for legacy analog/digital devices
    Manages both gateways and sub-devices
    
    Subscription Tracking:
    - Gateways count toward gateway_limit
    - Sub-devices count toward device_limit
    """
    
    def __init__(self, subscription_manager=None):
        self.gateways: Dict[str, Gateway] = {}
        self.devices: Dict[str, LegacyDeviceConfig] = {}
        self.device_states: Dict[str, Any] = {}
        self.broadlink_clients: Dict[str, Any] = {}  # Broadlink device instances
        self.subscription_manager = subscription_manager
        logger.info("LegacyDeviceController initialized")
    
    def register_gateway(
        self,
        gateway: Gateway,
        organization_id: Optional[str] = None
    ) -> bool:
        """
        Register a gateway (counts toward gateway limit)
        
        Args:
            gateway: Gateway configuration
            organization_id: Organization ID for subscription check
            
        Returns:
            True if registered successfully
        """
        # Check gateway limit if subscription manager provided
        if self.subscription_manager and organization_id:
            if not self.subscription_manager.check_gateway_limit(organization_id):
                logger.error(f"Gateway limit reached for organization {organization_id}")
                return False
            
            # Register with subscription
            if not self.subscription_manager.register_gateway(organization_id):
                return False
        
        self.gateways[gateway.gateway_id] = gateway
        logger.info(f"Registered gateway: {gateway.name} ({gateway.gateway_type.value})")
        return True
    
    def unregister_gateway(
        self,
        gateway_id: str,
        organization_id: Optional[str] = None
    ) -> bool:
        """Unregister a gateway"""
        if gateway_id not in self.gateways:
            return False
        
        # Remove all sub-devices first
        gateway = self.gateways[gateway_id]
        for device_id in list(gateway.sub_devices):
            self.unregister_device(device_id, organization_id)
        
        del self.gateways[gateway_id]
        
        # Update subscription
        if self.subscription_manager and organization_id:
            self.subscription_manager.unregister_gateway(organization_id)
        
        logger.info(f"Unregistered gateway: {gateway_id}")
        return True
    
    def register_device(
        self,
        config: LegacyDeviceConfig,
        organization_id: Optional[str] = None
    ) -> bool:
        """
        Register a legacy sub-device (counts toward device limit)
        
        Args:
            config: Device configuration
            organization_id: Organization ID for subscription check
            
        Returns:
            True if registered successfully
        """
        # Check if gateway exists
        if config.gateway_id not in self.gateways:
            logger.error(f"Gateway not found: {config.gateway_id}")
            return False
        
        # Check device limit if subscription manager provided
        if self.subscription_manager and organization_id:
            if not self.subscription_manager.check_device_limit(organization_id):
                logger.error(f"Device limit reached for organization {organization_id}")
                return False
            
            # Register with subscription
            if not self.subscription_manager.register_device(organization_id):
                return False
        
        self.devices[config.device_id] = config
        
        # Add to gateway's sub-device list
        self.gateways[config.gateway_id].add_sub_device(config.device_id)
        
        # Initialize device state
        if config.device_type == LegacyDeviceType.AIR_CONDITIONER:
            self.device_states[config.device_id] = ACState()
        elif config.device_type == LegacyDeviceType.FAN:
            self.device_states[config.device_id] = FanState()
        
        logger.info(f"Registered legacy device: {config.name} ({config.device_type.value}) via gateway {config.gateway_id}")
        return True
    
    def unregister_device(
        self,
        device_id: str,
        organization_id: Optional[str] = None
    ) -> bool:
        """Unregister a sub-device"""
        if device_id not in self.devices:
            return False
        
        config = self.devices[device_id]
        
        # Remove from gateway
        if config.gateway_id in self.gateways:
            self.gateways[config.gateway_id].remove_sub_device(device_id)
        
        del self.devices[device_id]
        
        # Update subscription
        if self.subscription_manager and organization_id:
            self.subscription_manager.unregister_device(organization_id)
        
        logger.info(f"Unregistered device: {device_id}")
        return True
    
    def send_command(
        self,
        device_id: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send command to legacy device
        
        Args:
            device_id: Device identifier
            command: Command name (e.g., "power_on", "set_temp_24")
            parameters: Optional parameters for the command
            
        Returns:
            True if command sent successfully
        """
        if device_id not in self.devices:
            logger.error(f"Device not found: {device_id}")
            return False
        
        config = self.devices[device_id]
        
        if config.control_protocol == ControlProtocol.INFRARED:
            return self._send_ir_command(config, command, parameters)
        
        elif config.control_protocol == ControlProtocol.RADIO_FREQUENCY:
            return self._send_rf_command(config, command, parameters)
        
        elif config.control_protocol == ControlProtocol.RS232:
            return self._send_rs232_command(config, command, parameters)
        
        elif config.control_protocol == ControlProtocol.TCP_IP:
            return self._send_tcp_command(config, command, parameters)
        
        else:
            logger.error(f"Unsupported protocol: {config.control_protocol}")
            return False
    
    def _send_ir_command(
        self,
        config: LegacyDeviceConfig,
        command: str,
        parameters: Optional[Dict[str, Any]]
    ) -> bool:
        """Send IR command via Broadlink gateway"""
        try:
            import broadlink
            
            # Get gateway
            if config.gateway_id not in self.gateways:
                logger.error(f"Gateway not found: {config.gateway_id}")
                return False
            
            gateway = self.gateways[config.gateway_id]
            
            # Get or create Broadlink client
            device_key = f"{gateway.ip_address}_{gateway.mac_address}"
            
            if device_key not in self.broadlink_clients:
                device = broadlink.discover(timeout=5)
                if not device:
                    logger.error(f"Broadlink device not found: {gateway.ip_address}")
                    return False
                
                device.auth()
                self.broadlink_clients[device_key] = device
            
            broadlink_device = self.broadlink_clients[device_key]
            
            # Get IR code for command
            if command not in config.commands:
                logger.error(f"Command not configured: {command} for device {config.device_id}")
                return False
            
            ir_code = config.commands[command]
            
            # Convert hex string to bytes
            if isinstance(ir_code, str):
                ir_code = bytes.fromhex(ir_code)
            
            # Send IR command
            broadlink_device.send_data(ir_code)
            
            logger.info(f"Sent IR command '{command}' to {config.name} via gateway {gateway.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send IR command: {e}")
            return False
    
    def _send_rf_command(
        self,
        config: LegacyDeviceConfig,
        command: str,
        parameters: Optional[Dict[str, Any]]
    ) -> bool:
        """Send RF command via Broadlink RM4 Pro gateway"""
        try:
            import broadlink
            
            # Get gateway
            if config.gateway_id not in self.gateways:
                logger.error(f"Gateway not found: {config.gateway_id}")
                return False
            
            gateway = self.gateways[config.gateway_id]
            
            device_key = f"{gateway.ip_address}_{gateway.mac_address}"
            
            if device_key not in self.broadlink_clients:
                device = broadlink.discover(timeout=5)
                if not device:
                    logger.error(f"Broadlink device not found")
                    return False
                
                device.auth()
                self.broadlink_clients[device_key] = device
            
            broadlink_device = self.broadlink_clients[device_key]
            
            # Get RF code
            if command not in config.commands:
                logger.error(f"Command not configured: {command}")
                return False
            
            rf_code = config.commands[command]
            
            if isinstance(rf_code, str):
                rf_code = bytes.fromhex(rf_code)
            
            # Send RF command
            broadlink_device.send_data(rf_code)
            
            logger.info(f"Sent RF command '{command}' to {config.name} via gateway {gateway.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send RF command: {e}")
            return False
    
    def _send_rs232_command(
        self,
        config: LegacyDeviceConfig,
        command: str,
        parameters: Optional[Dict[str, Any]]
    ) -> bool:
        """Send RS232 serial command via gateway"""
        try:
            import serial
            
            # Get gateway
            if config.gateway_id not in self.gateways:
                logger.error(f"Gateway not found: {config.gateway_id}")
                return False
            
            gateway = self.gateways[config.gateway_id]
            
            # Open serial port
            ser = serial.Serial(
                port=gateway.serial_port,
                baudrate=gateway.settings.get('baud_rate', 9600),
                bytesize=gateway.settings.get('data_bits', 8),
                stopbits=gateway.settings.get('stop_bits', 1),
                parity=gateway.settings.get('parity', 'N'),
                timeout=1
            )
            
            # Get command string
            if command not in config.commands:
                logger.error(f"Command not configured: {command}")
                return False
            
            cmd_string = config.commands[command]
            
            # Format command with parameters if provided
            if parameters:
                cmd_string = cmd_string.format(**parameters)
            
            # Send command
            ser.write(cmd_string.encode('utf-8'))
            
            # Read response (optional)
            response = ser.readline().decode('utf-8').strip()
            
            ser.close()
            
            logger.info(f"Sent RS232 command '{command}' to {config.name}, response: {response}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send RS232 command: {e}")
            return False
    
    def _send_tcp_command(
        self,
        config: LegacyDeviceConfig,
        command: str,
        parameters: Optional[Dict[str, Any]]
    ) -> bool:
        """Send TCP/IP command via gateway"""
        try:
            import socket
            
            # Get gateway
            if config.gateway_id not in self.gateways:
                logger.error(f"Gateway not found: {config.gateway_id}")
                return False
            
            gateway = self.gateways[config.gateway_id]
            
            # Get command string
            if command not in config.commands:
                logger.error(f"Command not configured: {command}")
                return False
            
            cmd_string = config.commands[command]
            
            # Format command with parameters
            if parameters:
                cmd_string = cmd_string.format(**parameters)
            
            # Send TCP command
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((gateway.ip_address, gateway.tcp_port))
            sock.send(cmd_string.encode('utf-8'))
            
            # Read response (optional)
            response = sock.recv(1024).decode('utf-8')
            
            sock.close()
            
            logger.info(f"Sent TCP command '{command}' to {config.name} via gateway {gateway.name}, response: {response}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send TCP command: {e}")
            return False
    
    # High-level device control methods
    
    def control_ac(
        self,
        device_id: str,
        power: Optional[bool] = None,
        mode: Optional[ACMode] = None,
        temperature: Optional[int] = None,
        fan_speed: Optional[FanSpeed] = None,
        swing: Optional[bool] = None
    ) -> bool:
        """
        Control air conditioner
        
        Args:
            device_id: AC device ID
            power: Turn on/off
            mode: AC mode (cool, heat, fan, etc.)
            temperature: Target temperature (Celsius)
            fan_speed: Fan speed
            swing: Enable/disable swing
            
        Returns:
            True if successful
        """
        if device_id not in self.devices:
            return False
        
        config = self.devices[device_id]
        if config.device_type != LegacyDeviceType.AIR_CONDITIONER:
            logger.error(f"Device {device_id} is not an AC")
            return False
        
        state = self.device_states.get(device_id, ACState())
        
        # Update state
        if power is not None:
            state.power = power
        if mode is not None:
            state.mode = mode
        if temperature is not None:
            state.temperature = temperature
        if fan_speed is not None:
            state.fan_speed = fan_speed
        if swing is not None:
            state.swing = swing
        
        # Build and send command
        if power == False:
            command = "power_off"
        else:
            # Many ACs use single command with all parameters
            # e.g., "cool_24_high_swing"
            command = f"{state.mode.value}_{state.temperature}_{state.fan_speed.value}"
            if state.swing:
                command += "_swing"
        
        success = self.send_command(device_id, command)
        
        if success:
            self.device_states[device_id] = state
        
        return success
    
    def control_fan(
        self,
        device_id: str,
        power: Optional[bool] = None,
        speed: Optional[FanSpeed] = None,
        oscillation: Optional[bool] = None,
        timer: Optional[int] = None
    ) -> bool:
        """
        Control fan
        
        Args:
            device_id: Fan device ID
            power: Turn on/off
            speed: Fan speed
            oscillation: Enable/disable oscillation
            timer: Timer in minutes
            
        Returns:
            True if successful
        """
        if device_id not in self.devices:
            return False
        
        config = self.devices[device_id]
        if config.device_type != LegacyDeviceType.FAN:
            logger.error(f"Device {device_id} is not a fan")
            return False
        
        state = self.device_states.get(device_id, FanState())
        
        # Update state
        if power is not None:
            state.power = power
        if speed is not None:
            state.speed = speed
        if oscillation is not None:
            state.oscillation = oscillation
        if timer is not None:
            state.timer = timer
        
        # Build command
        if power == False:
            command = "power_off"
        elif speed is not None:
            command = f"speed_{speed.value}"
        else:
            command = "power_on"
        
        success = self.send_command(device_id, command)
        
        if success:
            self.device_states[device_id] = state
        
        return success
    
    def control_switch(self, device_id: str, state: bool) -> bool:
        """Control power switch"""
        command = "on" if state else "off"
        return self.send_command(device_id, command)
    
    def control_projector(
        self,
        device_id: str,
        power: Optional[bool] = None,
        input_source: Optional[str] = None
    ) -> bool:
        """Control projector"""
        if power is not None:
            command = "power_on" if power else "power_off"
            if not self.send_command(device_id, command):
                return False
        
        if input_source is not None:
            command = f"input_{input_source}"
            return self.send_command(device_id, command)
        
        return True
    
    def learn_command(
        self,
        device_id: str,
        command_name: str,
        timeout: int = 10
    ) -> Optional[str]:
        """
        Learn IR/RF command from remote
        
        Args:
            device_id: Device to learn command for
            command_name: Name for the command
            timeout: Learning timeout in seconds
            
        Returns:
            Hex string of learned command, or None if failed
        """
        if device_id not in self.devices:
            return None
        
        config = self.devices[device_id]
        
        try:
            import broadlink
            
            device_key = f"{config.broadlink_device_ip}_{config.broadlink_device_mac}"
            
            if device_key not in self.broadlink_clients:
                device = broadlink.discover(timeout=5)
                if not device:
                    return None
                device.auth()
                self.broadlink_clients[device_key] = device
            
            broadlink_device = self.broadlink_clients[device_key]
            
            # Enter learning mode
            logger.info(f"Entering learning mode for {command_name}. Press remote button...")
            broadlink_device.enter_learning()
            
            # Wait for button press
            import time
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    data = broadlink_device.check_data()
                    if data:
                        # Convert to hex string
                        hex_code = data.hex()
                        
                        # Save to config
                        config.commands[command_name] = hex_code
                        
                        logger.info(f"Learned command '{command_name}': {hex_code[:20]}...")
                        return hex_code
                
                except Exception:
                    pass
                
                time.sleep(0.5)
            
            logger.error(f"Learning timeout for command '{command_name}'")
            return None
        
        except Exception as e:
            logger.error(f"Failed to learn command: {e}")
            return None


# Pre-configured device templates
DEVICE_TEMPLATES = {
    "generic_ac": {
        "commands": {
            "power_on": "...",
            "power_off": "...",
            "cool_24_auto": "...",
            "cool_24_high": "...",
            # ... more commands
        }
    },
    "generic_fan": {
        "commands": {
            "power_on": "...",
            "power_off": "...",
            "speed_1": "...",
            "speed_2": "...",
            "speed_3": "...",
            "oscillation_on": "...",
            "oscillation_off": "...",
        }
    },
    "projector_rs232": {
        "control_protocol": ControlProtocol.RS232,
        "commands": {
            "power_on": "PON\\r",
            "power_off": "POF\\r",
            "input_hdmi1": "SOURCE 60\\r",
            "input_hdmi2": "SOURCE 61\\r",
            "input_vga": "SOURCE 11\\r",
        }
    }
}


# Usage examples
LEGACY_DEVICE_EXAMPLES = """
# Example 1: Configure AC with Broadlink IR

from legacy_devices import (
    LegacyDeviceController, LegacyDeviceConfig,
    LegacyDeviceType, ControlProtocol, ACMode, FanSpeed
)

controller = LegacyDeviceController()

# Register AC
ac_config = LegacyDeviceConfig(
    device_id="bedroom_ac",
    name="Bedroom AC",
    device_type=LegacyDeviceType.AIR_CONDITIONER,
    control_protocol=ControlProtocol.INFRARED,
    broadlink_device_ip="192.168.1.50",
    broadlink_device_mac="34:ea:34:12:34:56",
    commands={
        "power_off": "26001234567890abcdef...",
        "cool_24_auto": "26001234567890abcdef...",
        "cool_22_high": "26001234567890abcdef...",
    }
)

controller.register_device(ac_config)

# Control AC
controller.control_ac(
    device_id="bedroom_ac",
    power=True,
    mode=ACMode.COOL,
    temperature=24,
    fan_speed=FanSpeed.AUTO
)

# Learn new command
hex_code = controller.learn_command("bedroom_ac", "cool_18_turbo", timeout=10)
# Press remote button now...


# Example 2: Configure projector with RS232

projector_config = LegacyDeviceConfig(
    device_id="conference_projector",
    name="Conference Room Projector",
    device_type=LegacyDeviceType.PROJECTOR,
    control_protocol=ControlProtocol.RS232,
    serial_port="/dev/ttyUSB0",
    baud_rate=9600,
    commands={
        "power_on": "PON\\r",
        "power_off": "POF\\r",
        "input_hdmi1": "SOURCE 60\\r",
        "input_hdmi2": "SOURCE 61\\r",
    }
)

controller.register_device(projector_config)

# Control projector
controller.control_projector(
    device_id="conference_projector",
    power=True,
    input_source="hdmi1"
)


# Example 3: RF-controlled blinds

blinds_config = LegacyDeviceConfig(
    device_id="living_room_blinds",
    name="Living Room Blinds",
    device_type=LegacyDeviceType.BLINDS,
    control_protocol=ControlProtocol.RADIO_FREQUENCY,
    broadlink_device_ip="192.168.1.50",
    commands={
        "open": "b2001234567890abcdef...",
        "close": "b2001234567890abcdef...",
        "stop": "b2001234567890abcdef...",
    }
)

controller.register_device(blinds_config)

# Control blinds
controller.send_command("living_room_blinds", "open")


# Example 4: TCP/IP controlled audio amplifier

amp_config = LegacyDeviceConfig(
    device_id="audio_amp",
    name="Yamaha RX-V6A",
    device_type=LegacyDeviceType.AUDIO_RECEIVER,
    control_protocol=ControlProtocol.TCP_IP,
    tcp_ip="192.168.1.100",
    tcp_port=50000,
    commands={
        "power_on": "PWON\\r\\n",
        "power_off": "PWSTANDBY\\r\\n",
        "volume_up": "VOLUP\\r\\n",
        "volume_down": "VOLDOWN\\r\\n",
        "input_hdmi1": "SIHDMI1\\r\\n",
    }
)

controller.register_device(amp_config)

# Control amplifier
controller.send_command("audio_amp", "power_on")
controller.send_command("audio_amp", "input_hdmi1")
"""
