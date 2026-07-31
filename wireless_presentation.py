"""
Wireless Presentation Module
Supports AirPlay, Chromecast, Miracast - Universal wireless presentation receiver

Features:
- AirPlay receiver (iOS/macOS devices)
- Chromecast Built-in (Android/Chrome)
- Miracast receiver (Windows PC, Android)
- Multi-user presentation (up to 4 simultaneous presenters)
- Whiteboard integration
- Security (PIN, device whitelist)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import asyncio


class PresentationProtocol(Enum):
    """Wireless presentation protocol"""
    AIRPLAY = "airplay"
    CHROMECAST = "chromecast"
    MIRACAST = "miracast"
    WEBRTC = "webrtc"  # Browser-based


class PresentationStatus(Enum):
    """Presentation session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"


class MultiUserLayout(Enum):
    """Multi-user presentation layout"""
    GRID = "grid"  # 2×2 or 3×3 grid
    SPOTLIGHT = "spotlight"  # Main presenter + thumbnails
    SIDEBAR = "sidebar"  # Main + side panel


@dataclass
class PresentationSession:
    """Active wireless presentation session"""
    session_id: str
    protocol: PresentationProtocol
    device_name: str
    device_mac: str
    device_ip: str
    
    # Video/audio
    resolution: str
    fps: int
    audio_enabled: bool
    
    # Session info
    started_at: datetime
    duration_seconds: int = 0
    status: PresentationStatus = PresentationStatus.ACTIVE
    
    # User info
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WhiteboardAnnotation:
    """Whiteboard annotation data"""
    annotation_id: str
    session_id: str
    user_name: str
    
    # Drawing data
    type: str  # "pen", "marker", "highlighter", "shape", "text"
    color: str
    width: int
    points: List[Dict[str, float]]  # [{"x": 100, "y": 200}, ...]
    
    # Metadata
    created_at: datetime
    layer: int = 0


class WirelessPresentationController:
    """
    Controller for wireless presentation features
    Manages AirPlay, Chromecast, Miracast connections
    """
    
    def __init__(self):
        self.sessions: Dict[str, PresentationSession] = {}
        self.whiteboard_annotations: List[WhiteboardAnnotation] = []
        
        # Services
        self.airplay_service = None
        self.chromecast_service = None
        self.miracast_service = None
        
        # Settings
        self.max_sessions = 4
        self.multi_user_enabled = True
        self.layout = MultiUserLayout.GRID
        self.moderation_enabled = False
        self.moderator_pin = "9999"
        
        # Security
        self.pin_required = True
        self.dynamic_pin = True
        self.current_pin = self._generate_pin()
        self.allowed_devices = []  # MAC addresses
    
    async def start_services(self):
        """Start all wireless presentation services"""
        # Start AirPlay receiver (shairport-sync)
        self.airplay_service = await self._start_airplay_service()
        
        # Start Chromecast receiver (Cast SDK)
        self.chromecast_service = await self._start_chromecast_service()
        
        # Start Miracast receiver (Wi-Fi Direct)
        self.miracast_service = await self._start_miracast_service()
        
        print("Wireless presentation services started")
        print(f"Connection PIN: {self.current_pin}")
    
    async def _start_airplay_service(self):
        """Start AirPlay receiver service"""
        # In real implementation:
        # 1. Start shairport-sync daemon
        # 2. Configure as AirPlay 2 receiver
        # 3. Set device name, password (PIN)
        # 4. Enable video mirroring
        # 5. Listen for incoming connections
        
        print("Starting AirPlay receiver...")
        print("  Device name: Conference Room A Display")
        print(f"  Password: {self.current_pin}")
        print("  Video: 1920x1080@30fps")
        print("  Audio: 48kHz stereo")
        
        return {"status": "running", "port": 5000}
    
    async def _start_chromecast_service(self):
        """Start Chromecast receiver service"""
        # In real implementation:
        # 1. Start Cast Receiver SDK
        # 2. Register device with Google Cast protocol
        # 3. Configure mDNS for device discovery
        # 4. Listen for Cast connections
        
        print("Starting Chromecast receiver...")
        print("  Device name: Conference Room A Display")
        print(f"  PIN: {self.current_pin}")
        print("  Video: 1920x1080@60fps (H.264/VP9)")
        print("  Audio: AAC/Opus")
        
        return {"status": "running", "port": 8008}
    
    async def _start_miracast_service(self):
        """Start Miracast receiver service"""
        # In real implementation:
        # 1. Enable Wi-Fi Direct (P2P mode)
        # 2. Start WFD (Wi-Fi Display) service
        # 3. Advertise as Miracast sink
        # 4. Listen for incoming connections
        
        print("Starting Miracast receiver...")
        print("  Device name: Conference Room A Display")
        print(f"  PIN: {self.current_pin}")
        print("  Wi-Fi Direct SSID: DIRECT-MCG-ConfRoomA")
        print("  Video: 1920x1080@60fps (H.264)")
        
        return {"status": "running"}
    
    def on_connection_request(self, device_info: Dict[str, Any]) -> bool:
        """Handle incoming wireless presentation connection request"""
        device_mac = device_info.get("mac_address")
        device_name = device_info.get("device_name")
        protocol = device_info.get("protocol")
        
        # Check device whitelist
        if self.allowed_devices and device_mac not in self.allowed_devices:
            print(f"Connection denied: {device_name} ({device_mac}) not in whitelist")
            return False
        
        # Check max sessions
        if len(self.sessions) >= self.max_sessions:
            print(f"Connection denied: Max sessions ({self.max_sessions}) reached")
            return False
        
        # Check PIN (if required)
        if self.pin_required:
            provided_pin = device_info.get("pin")
            if provided_pin != self.current_pin:
                print(f"Connection denied: Invalid PIN from {device_name}")
                return False
        
        # Check moderation
        if self.moderation_enabled and not device_info.get("approved_by_moderator"):
            print(f"Connection pending: {device_name} waiting for moderator approval")
            return False
        
        # Accept connection
        session = self._create_session(device_info)
        self.sessions[session.session_id] = session
        
        print(f"Connection accepted: {device_name} ({protocol})")
        print(f"  Session ID: {session.session_id}")
        print(f"  Resolution: {session.resolution}")
        
        # Update multi-user layout
        self._update_layout()
        
        return True
    
    def _create_session(self, device_info: Dict[str, Any]) -> PresentationSession:
        """Create presentation session"""
        import uuid
        
        session_id = f"{device_info['protocol']}_{uuid.uuid4().hex[:8]}"
        
        return PresentationSession(
            session_id=session_id,
            protocol=PresentationProtocol(device_info["protocol"]),
            device_name=device_info["device_name"],
            device_mac=device_info["mac_address"],
            device_ip=device_info.get("ip_address", ""),
            resolution=device_info.get("resolution", "1920x1080"),
            fps=device_info.get("fps", 30),
            audio_enabled=device_info.get("audio_enabled", True),
            started_at=datetime.now(),
            user_name=device_info.get("user_name"),
            user_email=device_info.get("user_email")
        )
    
    def disconnect_session(self, session_id: str, reason: str = "user_request"):
        """Disconnect wireless presentation session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.status = PresentationStatus.DISCONNECTED
        
        print(f"Disconnecting session: {session.device_name}")
        print(f"  Reason: {reason}")
        print(f"  Duration: {session.duration_seconds}s")
        
        # Remove session
        del self.sessions[session_id]
        
        # Update layout
        self._update_layout()
        
        return True
    
    def _update_layout(self):
        """Update multi-user presentation layout"""
        active_count = len(self.sessions)
        
        if active_count == 0:
            print("No active presentations")
            return
        
        if active_count == 1:
            print("Layout: Full screen (1 presenter)")
            return
        
        if self.layout == MultiUserLayout.GRID:
            if active_count == 2:
                print("Layout: 2×1 grid")
            elif active_count <= 4:
                print("Layout: 2×2 grid")
            else:
                print("Layout: 3×3 grid (truncated to 4)")
        
        elif self.layout == MultiUserLayout.SPOTLIGHT:
            print(f"Layout: Spotlight (1 main + {active_count - 1} thumbnails)")
        
        elif self.layout == MultiUserLayout.SIDEBAR:
            print(f"Layout: Sidebar (1 main + {active_count - 1} side panel)")
    
    def change_layout(self, layout: MultiUserLayout, spotlight_session: Optional[str] = None):
        """Change multi-user presentation layout"""
        self.layout = layout
        
        if layout == MultiUserLayout.SPOTLIGHT and spotlight_session:
            # Promote session to spotlight
            print(f"Promoting session {spotlight_session} to spotlight")
        
        self._update_layout()
    
    # Whiteboard methods
    
    def add_whiteboard_annotation(self, annotation: WhiteboardAnnotation):
        """Add whiteboard annotation"""
        self.whiteboard_annotations.append(annotation)
        print(f"Whiteboard annotation added: {annotation.type} by {annotation.user_name}")
    
    def clear_whiteboard(self):
        """Clear all whiteboard annotations"""
        count = len(self.whiteboard_annotations)
        self.whiteboard_annotations.clear()
        print(f"Cleared {count} whiteboard annotations")
    
    def save_whiteboard(self, filename: str, format: str = "png"):
        """Save whiteboard to file"""
        # In real implementation:
        # 1. Render all annotations to image
        # 2. Apply to base presentation image
        # 3. Save as PNG/PDF/SVG
        
        print(f"Saving whiteboard to {filename}.{format}")
        print(f"  Annotations: {len(self.whiteboard_annotations)}")
        
        return True
    
    # Utility methods
    
    def _generate_pin(self) -> str:
        """Generate random 4-digit PIN"""
        import random
        return f"{random.randint(1000, 9999)}"
    
    def rotate_pin(self):
        """Rotate PIN (for dynamic PIN mode)"""
        if self.dynamic_pin:
            self.current_pin = self._generate_pin()
            print(f"PIN rotated: {self.current_pin}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get wireless presentation status"""
        return {
            "services": {
                "airplay": self.airplay_service is not None,
                "chromecast": self.chromecast_service is not None,
                "miracast": self.miracast_service is not None
            },
            "active_sessions": len(self.sessions),
            "max_sessions": self.max_sessions,
            "layout": self.layout.value,
            "current_pin": self.current_pin if self.pin_required else None,
            "sessions": [
                {
                    "session_id": s.session_id,
                    "protocol": s.protocol.value,
                    "device_name": s.device_name,
                    "resolution": s.resolution,
                    "duration_seconds": s.duration_seconds,
                    "status": s.status.value
                }
                for s in self.sessions.values()
            ]
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Initialize controller
    controller = WirelessPresentationController()
    
    # Configure settings
    controller.max_sessions = 4
    controller.multi_user_enabled = True
    controller.layout = MultiUserLayout.GRID
    controller.pin_required = True
    controller.dynamic_pin = True
    
    # Start services
    asyncio.run(controller.start_services())
    
    # Simulate connection from iPhone (AirPlay)
    device_info_iphone = {
        "protocol": "airplay",
        "device_name": "John's iPhone",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.1.100",
        "resolution": "1920x1080",
        "fps": 30,
        "audio_enabled": True,
        "pin": controller.current_pin,
        "user_name": "John Doe",
        "user_email": "john@company.com"
    }
    
    controller.on_connection_request(device_info_iphone)
    
    # Simulate connection from Android (Chromecast)
    device_info_android = {
        "protocol": "chromecast",
        "device_name": "Jane's Pixel",
        "mac_address": "11:22:33:44:55:66",
        "ip_address": "192.168.1.101",
        "resolution": "1920x1080",
        "fps": 60,
        "audio_enabled": True,
        "pin": controller.current_pin,
        "user_name": "Jane Smith",
        "user_email": "jane@company.com"
    }
    
    controller.on_connection_request(device_info_android)
    
    # Change layout to spotlight
    first_session = list(controller.sessions.keys())[0]
    controller.change_layout(MultiUserLayout.SPOTLIGHT, spotlight_session=first_session)
    
    # Add whiteboard annotation
    annotation = WhiteboardAnnotation(
        annotation_id="annot_001",
        session_id=first_session,
        user_name="John Doe",
        type="pen",
        color="#FF0000",
        width=3,
        points=[
            {"x": 100, "y": 200},
            {"x": 150, "y": 250},
            {"x": 200, "y": 200}
        ],
        created_at=datetime.now()
    )
    
    controller.add_whiteboard_annotation(annotation)
    
    # Get status
    status = controller.get_status()
    print("\nWireless Presentation Status:")
    print(f"  Active sessions: {status['active_sessions']}")
    print(f"  Layout: {status['layout']}")
    print(f"  PIN: {status['current_pin']}")
    
    # Save whiteboard
    controller.save_whiteboard("meeting_notes_2026-07-31", format="pdf")
    
    # Disconnect session
    controller.disconnect_session(first_session, reason="presentation_ended")
