"""
Touch Panel Integration Module
Supports USB, IP/Ethernet, Serial, and Web-based touch panels for room control

Supported panel types:
- Microsoft Teams Room controllers (Logitech Tap, Crestron Flex, Poly G100)
- Enterprise control panels (Crestron, Extron, AMX)
- KNX touch visualizations
- Custom web panels (iPad, Android tablets)
- Interactive touch displays
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
import json
from datetime import datetime


class TouchPanelType(Enum):
    """Type of touch panel connection"""
    USB_HID = "usb_hid"              # USB Human Interface Device (touch monitors, Logitech Tap)
    IP_ETHERNET = "ip_ethernet"       # Network-based (Crestron, Extron, AMX)
    SERIAL_RS232 = "serial_rs232"     # RS232 serial connection
    WEB_BROWSER = "web_browser"       # Browser-based control (iPad, tablets)
    HYBRID = "hybrid"                 # Multiple connection methods (e.g., Crestron Flex)


class ControlProtocol(Enum):
    """Control protocol for IP panels"""
    CRESTRON_CH5 = "crestron_ch5"     # Crestron CH5 (port 41794)
    EXTRON_SIS = "extron_sis"         # Extron Simple Instruction Set (port 23)
    AMX_NATIVE = "amx_native"         # AMX NetLinx (port 1319)
    HTTP = "http"                     # HTTP REST API
    WEBSOCKET = "websocket"           # WebSocket connection
    KNX_IP = "knx_ip"                 # KNX/IP protocol


class RoutingMode(Enum):
    """How touch input is routed between sources"""
    FOLLOW_ACTIVE_SOURCE = "follow_active_source"  # Route to active source on display
    MANUAL = "manual"                               # Explicit API routing
    DEDICATED = "dedicated"                         # Always route to specific source


class TouchPanelStatus(Enum):
    """Touch panel connection status"""
    ACTIVE = "active"
    IDLE = "idle"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class TouchPanelCapabilities:
    """Capabilities of a touch panel"""
    touch_input: bool = True
    multi_touch: bool = False
    max_touch_points: int = 1
    display: bool = False              # Panel has built-in display
    display_resolution: Optional[str] = None
    audio_output: bool = False
    microphone_input: bool = False
    call_controls: bool = False        # Teams Room call controls
    volume_controls: bool = False
    camera_controls: bool = False      # PTZ camera control
    content_sharing: bool = False
    roster_display: bool = False       # Show meeting participants


@dataclass
class USBConnection:
    """USB connection details"""
    port: str                          # e.g., "usb_a_1", "usb_c_2"
    vendor_id: Optional[str] = None   # USB VID (e.g., "0x046d" for Logitech)
    product_id: Optional[str] = None  # USB PID
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    serial_number: Optional[str] = None


@dataclass
class IPConnection:
    """IP/Ethernet connection details"""
    ip_address: str
    protocol: ControlProtocol
    port: int = 41794
    ssl: bool = False
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class SerialConnection:
    """Serial connection details"""
    port: str                          # e.g., "/dev/ttyUSB0", "COM1"
    baud_rate: int = 9600
    data_bits: int = 8
    parity: str = "N"                  # N, E, O
    stop_bits: int = 1
    flow_control: str = "none"         # none, rts_cts, xon_xoff


@dataclass
class WebConnection:
    """Web browser connection details"""
    url: str
    authentication: str = "token"      # token, basic, oauth
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class TouchRoutingConfig:
    """Configuration for touch input routing"""
    mode: RoutingMode = RoutingMode.FOLLOW_ACTIVE_SOURCE
    follow_display: Optional[str] = None  # Display ID to follow
    dedicated_source: Optional[str] = None  # Source ID for dedicated mode
    switch_delay_ms: int = 100              # Delay before routing switch


@dataclass
class TouchPanel:
    """Touch panel device"""
    panel_id: str
    name: str
    panel_type: TouchPanelType
    
    # Connection details (one of these will be populated)
    usb_connection: Optional[USBConnection] = None
    ip_connection: Optional[IPConnection] = None
    serial_connection: Optional[SerialConnection] = None
    web_connection: Optional[WebConnection] = None
    
    # Capabilities
    capabilities: TouchPanelCapabilities = field(default_factory=TouchPanelCapabilities)
    
    # Routing configuration
    routing: TouchRoutingConfig = field(default_factory=TouchRoutingConfig)
    
    # Current state
    status: TouchPanelStatus = TouchPanelStatus.DISCONNECTED
    connected: bool = False
    routed_to: Optional[str] = None      # Source ID currently receiving touch input
    last_activity: Optional[datetime] = None
    input_events_last_minute: int = 0
    
    # Settings
    shared: bool = False                  # Can be shared between sources
    auto_wake_display: bool = True        # Wake display on touch
    idle_timeout: int = 300               # Seconds before dimming
    
    # Custom settings
    settings: Dict[str, Any] = field(default_factory=dict)


class TouchPanelController:
    """
    Manages touch panels for room control
    Supports USB HID, IP/Ethernet, Serial, and Web-based panels
    """
    
    def __init__(self):
        self.panels: Dict[str, TouchPanel] = {}
        self.event_handlers: List[Callable] = []
        
        # Protocol servers (for IP panels to connect)
        self.crestron_server = None
        self.extron_server = None
        self.amx_server = None
        self.websocket_server = None
        
    async def start_protocol_servers(self):
        """Start protocol servers for IP panels"""
        # Crestron CH5 server (port 41794)
        self.crestron_server = await self._start_crestron_server()
        
        # Extron SIS server (port 23, telnet-based)
        self.extron_server = await self._start_extron_server()
        
        # AMX NetLinx server (port 1319)
        self.amx_server = await self._start_amx_server()
        
        # WebSocket server (for web panels)
        self.websocket_server = await self._start_websocket_server()
    
    def register_panel(self, panel: TouchPanel) -> bool:
        """Register a touch panel"""
        if panel.panel_id in self.panels:
            print(f"Panel {panel.panel_id} already registered")
            return False
        
        self.panels[panel.panel_id] = panel
        
        # Initialize connection based on panel type
        if panel.panel_type == TouchPanelType.USB_HID:
            self._init_usb_panel(panel)
        elif panel.panel_type == TouchPanelType.IP_ETHERNET:
            self._init_ip_panel(panel)
        elif panel.panel_type == TouchPanelType.SERIAL_RS232:
            self._init_serial_panel(panel)
        elif panel.panel_type == TouchPanelType.WEB_BROWSER:
            self._init_web_panel(panel)
        
        print(f"Registered touch panel: {panel.name} ({panel.panel_id})")
        return True
    
    def unregister_panel(self, panel_id: str) -> bool:
        """Unregister a touch panel"""
        if panel_id not in self.panels:
            return False
        
        panel = self.panels[panel_id]
        
        # Cleanup connection
        if panel.panel_type == TouchPanelType.USB_HID:
            self._cleanup_usb_panel(panel)
        elif panel.panel_type == TouchPanelType.IP_ETHERNET:
            self._cleanup_ip_panel(panel)
        
        del self.panels[panel_id]
        return True
    
    def route_panel_to_source(self, panel_id: str, source_id: str) -> bool:
        """Route touch panel input to specific source"""
        if panel_id not in self.panels:
            print(f"Panel {panel_id} not found")
            return False
        
        panel = self.panels[panel_id]
        
        # Check if panel is dedicated to another source
        if (panel.routing.mode == RoutingMode.DEDICATED and 
            panel.routing.dedicated_source != source_id):
            print(f"Panel {panel_id} is dedicated to {panel.routing.dedicated_source}")
            return False
        
        # Perform routing based on panel type
        if panel.panel_type == TouchPanelType.USB_HID:
            success = self._route_usb_panel(panel, source_id)
        else:
            # IP/Serial/Web panels don't need routing (they control gateway, not sources)
            success = True
        
        if success:
            panel.routed_to = source_id
            print(f"Routed panel {panel_id} to source {source_id}")
            
            # Trigger event
            self._trigger_event({
                "type": "panel_routed",
                "panel_id": panel_id,
                "source_id": source_id,
                "timestamp": datetime.now().isoformat()
            })
        
        return success
    
    def _route_usb_panel(self, panel: TouchPanel, source_id: str) -> bool:
        """Route USB HID panel to source"""
        if not panel.usb_connection:
            return False
        
        # Apply switch delay
        if panel.routing.switch_delay_ms > 0:
            import time
            time.sleep(panel.routing.switch_delay_ms / 1000.0)
        
        # Send USB routing command to hardware
        # This would interface with the USB hub controller
        # For now, simulate success
        print(f"Routing USB panel {panel.panel_id} from port {panel.usb_connection.port} to source {source_id}")
        
        return True
    
    def get_panel_status(self, panel_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a touch panel"""
        if panel_id not in self.panels:
            return None
        
        panel = self.panels[panel_id]
        
        return {
            "id": panel.panel_id,
            "name": panel.name,
            "type": panel.panel_type.value,
            "connected": panel.connected,
            "status": panel.status.value,
            "routed_to": panel.routed_to,
            "last_activity": panel.last_activity.isoformat() if panel.last_activity else None,
            "input_events_last_minute": panel.input_events_last_minute,
            "capabilities": {
                "touch_input": panel.capabilities.touch_input,
                "multi_touch": panel.capabilities.multi_touch,
                "max_touch_points": panel.capabilities.max_touch_points,
                "display": panel.capabilities.display,
                "display_resolution": panel.capabilities.display_resolution,
                "call_controls": panel.capabilities.call_controls,
                "volume_controls": panel.capabilities.volume_controls
            }
        }
    
    def list_panels(self) -> List[Dict[str, Any]]:
        """List all registered touch panels"""
        return [
            self.get_panel_status(panel_id)
            for panel_id in self.panels.keys()
        ]
    
    async def send_command_to_panel(self, panel_id: str, command: str, parameters: Dict[str, Any] = None) -> bool:
        """Send command to IP/Serial/Web panel"""
        if panel_id not in self.panels:
            return False
        
        panel = self.panels[panel_id]
        
        if panel.panel_type == TouchPanelType.IP_ETHERNET:
            return await self._send_ip_command(panel, command, parameters)
        elif panel.panel_type == TouchPanelType.SERIAL_RS232:
            return await self._send_serial_command(panel, command, parameters)
        elif panel.panel_type == TouchPanelType.WEB_BROWSER:
            return await self._send_websocket_command(panel, command, parameters)
        
        return False
    
    async def _send_ip_command(self, panel: TouchPanel, command: str, parameters: Dict[str, Any]) -> bool:
        """Send command to IP panel"""
        if not panel.ip_connection:
            return False
        
        protocol = panel.ip_connection.protocol
        
        if protocol == ControlProtocol.CRESTRON_CH5:
            # Crestron CH5 join commands
            # Format: Digital join, analog join, serial join
            return await self._send_crestron_command(panel, command, parameters)
        
        elif protocol == ControlProtocol.EXTRON_SIS:
            # Extron SIS commands (telnet-based)
            return await self._send_extron_command(panel, command, parameters)
        
        elif protocol == ControlProtocol.AMX_NATIVE:
            # AMX NetLinx commands
            return await self._send_amx_command(panel, command, parameters)
        
        elif protocol == ControlProtocol.WEBSOCKET:
            # WebSocket JSON commands
            return await self._send_websocket_command(panel, command, parameters)
        
        return False
    
    async def _send_crestron_command(self, panel: TouchPanel, command: str, parameters: Dict[str, Any]) -> bool:
        """Send Crestron CH5 command to panel"""
        # Crestron CH5 uses joins: digital (buttons), analog (sliders), serial (text)
        
        if command == "UPDATE_SOURCE_INDICATOR":
            # Set digital join high/low for source button feedback
            join_id = parameters.get("button_id", 1)
            state = parameters.get("state", "inactive")
            
            # Digital join command (simplified)
            cmd = f"DIG:{join_id}:{1 if state == 'active' else 0}"
            print(f"Crestron CH5 command: {cmd}")
            
        elif command == "UPDATE_VOLUME_SLIDER":
            # Set analog join value for volume slider
            join_id = parameters.get("slider_id", 1)
            value = parameters.get("value", 0)
            
            cmd = f"ANA:{join_id}:{value}"
            print(f"Crestron CH5 command: {cmd}")
        
        elif command == "UPDATE_TEXT_DISPLAY":
            # Set serial join for text display
            join_id = parameters.get("text_id", 1)
            text = parameters.get("text", "")
            
            cmd = f"SER:{join_id}:{text}"
            print(f"Crestron CH5 command: {cmd}")
        
        # In real implementation, send via socket to panel.ip_connection.ip_address:port
        return True
    
    async def _send_extron_command(self, panel: TouchPanel, command: str, parameters: Dict[str, Any]) -> bool:
        """Send Extron SIS command to panel"""
        # Extron uses ASCII-based commands
        
        if command == "UPDATE_SOURCE_INDICATOR":
            # Extron button feedback
            button_id = parameters.get("button_id", 1)
            state = parameters.get("state", "inactive")
            
            # Extron command (example)
            cmd = f"{button_id}*{1 if state == 'active' else 0}CPLD\r\n"
            print(f"Extron SIS command: {cmd}")
        
        return True
    
    async def _send_amx_command(self, panel: TouchPanel, command: str, parameters: Dict[str, Any]) -> bool:
        """Send AMX NetLinx command to panel"""
        # AMX uses button/level/channel commands
        
        if command == "UPDATE_SOURCE_INDICATOR":
            button_id = parameters.get("button_id", 1)
            state = parameters.get("state", "inactive")
            
            # AMX button feedback
            cmd = f"^{'BMF' if state == 'active' else 'BMT'}-{panel.panel_id},{button_id},1"
            print(f"AMX command: {cmd}")
        
        return True
    
    async def _send_websocket_command(self, panel: TouchPanel, command: str, parameters: Dict[str, Any]) -> bool:
        """Send WebSocket command to web panel"""
        # Send JSON message via WebSocket
        
        message = {
            "type": command,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
        
        # In real implementation, send via WebSocket connection
        print(f"WebSocket message: {json.dumps(message)}")
        
        return True
    
    def _init_usb_panel(self, panel: TouchPanel):
        """Initialize USB HID panel"""
        print(f"Initializing USB panel: {panel.name}")
        
        # Detect USB device
        if panel.usb_connection:
            # In real implementation:
            # 1. Enumerate USB devices
            # 2. Find device by VID/PID
            # 3. Open HID interface
            # 4. Start listening for touch events
            
            panel.connected = True
            panel.status = TouchPanelStatus.ACTIVE
    
    def _init_ip_panel(self, panel: TouchPanel):
        """Initialize IP/Ethernet panel"""
        print(f"Initializing IP panel: {panel.name}")
        
        # Panel connects to gateway's protocol server
        # Gateway waits for incoming connection
        
        panel.status = TouchPanelStatus.IDLE
    
    def _init_serial_panel(self, panel: TouchPanel):
        """Initialize serial panel"""
        print(f"Initializing serial panel: {panel.name}")
        
        # Open serial port
        if panel.serial_connection:
            # In real implementation:
            # 1. Open serial port
            # 2. Configure baud rate, parity, etc.
            # 3. Start listening for commands
            
            panel.connected = True
            panel.status = TouchPanelStatus.ACTIVE
    
    def _init_web_panel(self, panel: TouchPanel):
        """Initialize web browser panel"""
        print(f"Initializing web panel: {panel.name}")
        
        # Web panel connects via WebSocket
        # Gateway waits for WebSocket connection
        
        panel.status = TouchPanelStatus.IDLE
    
    def _cleanup_usb_panel(self, panel: TouchPanel):
        """Cleanup USB panel connection"""
        print(f"Cleaning up USB panel: {panel.name}")
        panel.connected = False
        panel.status = TouchPanelStatus.DISCONNECTED
    
    def _cleanup_ip_panel(self, panel: TouchPanel):
        """Cleanup IP panel connection"""
        print(f"Cleaning up IP panel: {panel.name}")
        panel.connected = False
        panel.status = TouchPanelStatus.DISCONNECTED
    
    async def _start_crestron_server(self):
        """Start Crestron CH5 server on port 41794"""
        print("Starting Crestron CH5 server on port 41794...")
        # In real implementation, start TCP server
        return True
    
    async def _start_extron_server(self):
        """Start Extron SIS server on port 23"""
        print("Starting Extron SIS server on port 23...")
        # In real implementation, start telnet server
        return True
    
    async def _start_amx_server(self):
        """Start AMX NetLinx server on port 1319"""
        print("Starting AMX NetLinx server on port 1319...")
        # In real implementation, start TCP server
        return True
    
    async def _start_websocket_server(self):
        """Start WebSocket server for web panels"""
        print("Starting WebSocket server on port 8765...")
        # In real implementation, start WebSocket server
        return True
    
    def on_event(self, callback: Callable):
        """Register event handler"""
        self.event_handlers.append(callback)
    
    def _trigger_event(self, event: Dict[str, Any]):
        """Trigger event to all handlers"""
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    def auto_route_on_source_change(self, active_source_id: str, display_id: str):
        """Automatically route touch panels when source changes"""
        for panel_id, panel in self.panels.items():
            # Only auto-route panels in FOLLOW_ACTIVE_SOURCE mode
            if panel.routing.mode != RoutingMode.FOLLOW_ACTIVE_SOURCE:
                continue
            
            # Check if panel follows this display
            if panel.routing.follow_display != display_id:
                continue
            
            # Route panel to new source
            self.route_panel_to_source(panel_id, active_source_id)


# Example usage
if __name__ == "__main__":
    # Initialize controller
    controller = TouchPanelController()
    
    # Register Logitech Tap (USB, dedicated to Teams Room)
    logitech_tap = TouchPanel(
        panel_id="logitech_tap",
        name="Logitech Tap",
        panel_type=TouchPanelType.USB_HID,
        usb_connection=USBConnection(
            port="usb_a_1",
            vendor_id="0x046d",
            product_id="0x0893",
            manufacturer="Logitech",
            product="Logi Tap"
        ),
        capabilities=TouchPanelCapabilities(
            touch_input=True,
            multi_touch=True,
            max_touch_points=10,
            display=True,
            display_resolution="1280x800",
            audio_output=True,
            call_controls=True,
            volume_controls=True,
            content_sharing=True,
            roster_display=True
        ),
        routing=TouchRoutingConfig(
            mode=RoutingMode.DEDICATED,
            dedicated_source="teams_room"
        )
    )
    
    controller.register_panel(logitech_tap)
    
    # Register Crestron wall panel (IP, Ethernet)
    crestron_panel = TouchPanel(
        panel_id="crestron_wall",
        name="Crestron TSW-770",
        panel_type=TouchPanelType.IP_ETHERNET,
        ip_connection=IPConnection(
            ip_address="192.168.1.60",
            protocol=ControlProtocol.CRESTRON_CH5,
            port=41794,
            ssl=True
        ),
        capabilities=TouchPanelCapabilities(
            touch_input=True,
            display=True,
            display_resolution="1024x600"
        ),
        shared=True  # Can control multiple sources
    )
    
    controller.register_panel(crestron_panel)
    
    # Register touch monitor (USB, follows active source)
    touch_monitor = TouchPanel(
        panel_id="touch_monitor",
        name="32\" Touch Display",
        panel_type=TouchPanelType.USB_HID,
        usb_connection=USBConnection(
            port="usb_a_3"
        ),
        capabilities=TouchPanelCapabilities(
            touch_input=True,
            multi_touch=True,
            max_touch_points=10
        ),
        routing=TouchRoutingConfig(
            mode=RoutingMode.FOLLOW_ACTIVE_SOURCE,
            follow_display="main_display",
            switch_delay_ms=200
        )
    )
    
    controller.register_panel(touch_monitor)
    
    # Route Logitech Tap to Teams Room
    controller.route_panel_to_source("logitech_tap", "teams_room")
    
    # List all panels
    print("\nRegistered touch panels:")
    for panel_status in controller.list_panels():
        print(f"  - {panel_status['name']}: {panel_status['status']} (routed to: {panel_status['routed_to']})")
    
    # Simulate source change (auto-route touch monitor)
    print("\nSwitching active source to 'laptop'...")
    controller.auto_route_on_source_change("laptop", "main_display")
    
    # Send command to Crestron panel (update source indicator)
    import asyncio
    asyncio.run(controller.send_command_to_panel(
        "crestron_wall",
        "UPDATE_SOURCE_INDICATOR",
        {"button_id": 2, "state": "active"}
    ))
