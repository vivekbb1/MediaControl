"""
SIP Telephony, Doorbell, Picture-in-Picture, Multi-Source Grid Layouts
VoIP phone system, doorbell camera integration, advanced display layouts

Features:
- SIP IP phone/extension (VoIP calls)
- Doorbell camera integration (Ring, Nest, Arlo, UniFi)
- Picture-in-Picture (PiP) mode
- Multi-source grid layouts (2×2, 3×3, custom)
- Touch-based source resizing with visual feedback
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import asyncio


# ========== SIP Telephony ==========

class SIPCallStatus(Enum):
    """SIP call status"""
    IDLE = "idle"
    RINGING = "ringing"
    ANSWERED = "answered"
    ON_HOLD = "on_hold"
    TRANSFERRING = "transferring"
    ENDED = "ended"


@dataclass
class SIPCall:
    """SIP call"""
    call_id: str
    direction: str  # "inbound", "outbound"
    remote_number: str
    remote_name: str
    local_extension: str
    
    status: SIPCallStatus = SIPCallStatus.IDLE
    started_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    
    video_enabled: bool = False
    muted: bool = False
    on_hold: bool = False


class SIPPhoneController:
    """
    SIP IP Phone controller
    Manages VoIP calls, extensions, audio routing
    """
    
    def __init__(self):
        self.extension = None
        self.sip_server = None
        self.registered = False
        
        self.active_calls: Dict[str, SIPCall] = {}
        self.call_history: List[SIPCall] = []
        
        # SIP client (would use pjsip or linphone)
        self.sip_client = None
    
    async def register(self, username: str, password: str, domain: str):
        """Register SIP extension"""
        self.extension = username
        self.sip_server = domain
        
        # In real implementation:
        # 1. Initialize SIP client (pjsip, linphone, etc.)
        # 2. Set credentials
        # 3. Register with PBX
        # 4. Listen for incoming calls
        
        print(f"Registering SIP extension {username}@{domain}...")
        print("  Protocol: SIP/2.0")
        print("  Transport: UDP/5060")
        print("  Codecs: OPUS, G.722, PCMU, PCMA")
        
        self.registered = True
        return True
    
    async def make_call(self, destination: str, video: bool = False) -> Optional[SIPCall]:
        """Make outbound call"""
        if not self.registered:
            print("Not registered to SIP server")
            return None
        
        import uuid
        call_id = f"call_{uuid.uuid4().hex[:8]}"
        
        call = SIPCall(
            call_id=call_id,
            direction="outbound",
            remote_number=destination,
            remote_name=destination,
            local_extension=self.extension,
            status=SIPCallStatus.RINGING,
            started_at=datetime.now(),
            video_enabled=video
        )
        
        self.active_calls[call_id] = call
        
        print(f"Making call to {destination}")
        print(f"  Call ID: {call_id}")
        print(f"  Video: {video}")
        
        # In real implementation:
        # 1. Send SIP INVITE
        # 2. Negotiate SDP (audio/video codecs)
        # 3. Establish RTP streams
        
        return call
    
    async def answer_call(self, call_id: str) -> bool:
        """Answer incoming call"""
        if call_id not in self.active_calls:
            return False
        
        call = self.active_calls[call_id]
        call.status = SIPCallStatus.ANSWERED
        call.answered_at = datetime.now()
        
        print(f"Answering call from {call.remote_name}")
        
        # In real implementation:
        # 1. Send SIP 200 OK
        # 2. Establish RTP audio/video streams
        # 3. Route audio to room speakers/microphone
        
        return True
    
    async def hangup_call(self, call_id: str) -> bool:
        """Hang up call"""
        if call_id not in self.active_calls:
            return False
        
        call = self.active_calls[call_id]
        call.status = SIPCallStatus.ENDED
        call.ended_at = datetime.now()
        
        if call.answered_at:
            call.duration_seconds = int((call.ended_at - call.answered_at).total_seconds())
        
        print(f"Ending call with {call.remote_name}")
        print(f"  Duration: {call.duration_seconds}s")
        
        # Move to history
        self.call_history.append(call)
        del self.active_calls[call_id]
        
        return True
    
    async def mute_toggle(self, call_id: str) -> bool:
        """Toggle mute"""
        if call_id not in self.active_calls:
            return False
        
        call = self.active_calls[call_id]
        call.muted = not call.muted
        
        print(f"Call {call_id}: {'Muted' if call.muted else 'Unmuted'}")
        return True


# ========== Doorbell Integration ==========

class DoorbellType(Enum):
    """Doorbell camera type"""
    RING = "ring"
    NEST = "nest"
    ARLO = "arlo"
    UNIFI = "unifi"
    GENERIC_RTSP = "generic_rtsp"


@dataclass
class DoorbellEvent:
    """Doorbell event"""
    event_id: str
    doorbell_id: str
    event_type: str  # "button_press", "motion", "package_detected"
    timestamp: datetime
    visitor_name: Optional[str] = None
    snapshot_url: Optional[str] = None
    video_url: Optional[str] = None
    answered: bool = False


class DoorbellController:
    """
    Doorbell camera controller
    Manages doorbell events, video streams, access control
    """
    
    def __init__(self):
        self.doorbells: Dict[str, Dict[str, Any]] = {}
        self.events: List[DoorbellEvent] = []
    
    def register_doorbell(self, doorbell_id: str, name: str, doorbell_type: DoorbellType, stream_url: str):
        """Register doorbell camera"""
        self.doorbells[doorbell_id] = {
            "doorbell_id": doorbell_id,
            "name": name,
            "type": doorbell_type,
            "stream_url": stream_url,
            "online": True
        }
        
        print(f"Registered doorbell: {name}")
        print(f"  Type: {doorbell_type.value}")
        print(f"  Stream: {stream_url}")
    
    async def on_doorbell_press(self, doorbell_id: str, visitor_name: Optional[str] = None):
        """Handle doorbell button press"""
        import uuid
        event_id = f"event_{uuid.uuid4().hex[:8]}"
        
        event = DoorbellEvent(
            event_id=event_id,
            doorbell_id=doorbell_id,
            event_type="button_press",
            timestamp=datetime.now(),
            visitor_name=visitor_name
        )
        
        self.events.append(event)
        
        doorbell = self.doorbells[doorbell_id]
        print(f"🔔 Doorbell pressed: {doorbell['name']}")
        if visitor_name:
            print(f"  Visitor: {visitor_name}")
        
        # In real implementation:
        # 1. Show doorbell video in PiP
        # 2. Play chime sound
        # 3. Send notification
        # 4. Start recording
        
        return event
    
    async def answer_doorbell(self, doorbell_id: str) -> bool:
        """Answer doorbell (start two-way audio)"""
        if doorbell_id not in self.doorbells:
            return False
        
        doorbell = self.doorbells[doorbell_id]
        print(f"Answering doorbell: {doorbell['name']}")
        
        # In real implementation:
        # 1. Establish two-way audio stream
        # 2. Route room microphone to doorbell speaker
        # 3. Route doorbell microphone to room speakers
        
        return True
    
    async def unlock_door(self, doorbell_id: str) -> bool:
        """Unlock door (access control)"""
        if doorbell_id not in self.doorbells:
            return False
        
        doorbell = self.doorbells[doorbell_id]
        print(f"Unlocking door: {doorbell['name']}")
        
        # In real implementation:
        # 1. Send unlock command to smart lock API
        # 2. Wait for confirmation
        # 3. Log access event
        
        return True


# ========== Picture-in-Picture ==========

@dataclass
class PiPWindow:
    """Picture-in-Picture window"""
    pip_id: str
    source_id: str
    source_name: str
    
    # Position (percent of screen)
    x: float  # 0-100
    y: float  # 0-100
    width: float  # 0-100
    height: float  # 0-100
    
    # Behavior
    movable: bool = True
    resizable: bool = True
    closable: bool = True
    
    # Visual
    opacity: float = 1.0
    z_index: int = 100  # Higher = on top
    
    # State
    active: bool = True


class PictureInPictureController:
    """
    Picture-in-Picture controller
    Manages PiP windows overlaid on main content
    """
    
    def __init__(self):
        self.pip_windows: Dict[str, PiPWindow] = {}
        self.max_pip_windows = 4
    
    def show_pip(self, source_id: str, source_name: str, position: str = "bottom_right", 
                 width: float = 25.0, height: float = 25.0) -> Optional[PiPWindow]:
        """Show source in PiP"""
        if len(self.pip_windows) >= self.max_pip_windows:
            print(f"Max PiP windows reached ({self.max_pip_windows})")
            return None
        
        import uuid
        pip_id = f"pip_{uuid.uuid4().hex[:8]}"
        
        # Position presets
        positions = {
            "top_left": (2, 2),
            "top_right": (73, 2),
            "bottom_left": (2, 73),
            "bottom_right": (73, 73)
        }
        
        x, y = positions.get(position, (73, 73))
        
        pip = PiPWindow(
            pip_id=pip_id,
            source_id=source_id,
            source_name=source_name,
            x=x,
            y=y,
            width=width,
            height=height
        )
        
        self.pip_windows[pip_id] = pip
        
        print(f"Showing PiP: {source_name}")
        print(f"  Position: {position} ({x}%, {y}%)")
        print(f"  Size: {width}% × {height}%")
        
        return pip
    
    def close_pip(self, pip_id: str) -> bool:
        """Close PiP window"""
        if pip_id not in self.pip_windows:
            return False
        
        pip = self.pip_windows[pip_id]
        print(f"Closing PiP: {pip.source_name}")
        
        del self.pip_windows[pip_id]
        return True
    
    def move_pip(self, pip_id: str, x: float, y: float) -> bool:
        """Move PiP window"""
        if pip_id not in self.pip_windows:
            return False
        
        pip = self.pip_windows[pip_id]
        if not pip.movable:
            return False
        
        pip.x = max(0, min(100 - pip.width, x))
        pip.y = max(0, min(100 - pip.height, y))
        
        return True
    
    def resize_pip(self, pip_id: str, width: float, height: float) -> bool:
        """Resize PiP window"""
        if pip_id not in self.pip_windows:
            return False
        
        pip = self.pip_windows[pip_id]
        if not pip.resizable:
            return False
        
        pip.width = max(10, min(50, width))  # 10-50%
        pip.height = max(10, min(50, height))
        
        return True


# ========== Multi-Source Grid Layouts ==========

@dataclass
class GridLayout:
    """Multi-source grid layout"""
    layout_id: str
    name: str
    rows: int
    columns: int
    sources: List[str]
    gap: int = 10  # pixels
    
    # Behavior
    auto_scale: bool = True
    maintain_aspect_ratio: bool = True
    show_labels: bool = True
    show_borders: bool = True


@dataclass
class SourceZone:
    """Source display zone (for asymmetric layouts)"""
    zone_id: str
    source_id: str
    x: float  # percent
    y: float
    width: float
    height: float


class MultiSourceLayoutController:
    """
    Multi-source grid layout controller
    Manages quad view, nine-up, custom grids
    """
    
    def __init__(self):
        self.active_layout: Optional[GridLayout] = None
        self.custom_zones: List[SourceZone] = []
        
        # Grid presets
        self.presets: Dict[str, GridLayout] = {}
        self._init_presets()
    
    def _init_presets(self):
        """Initialize default grid presets"""
        # 2×2 Quad View
        self.presets["quad_view"] = GridLayout(
            layout_id="quad_view",
            name="Quad View (2×2)",
            rows=2,
            columns=2,
            sources=["hdmi_1", "hdmi_2", "hdmi_3", "hdmi_4"]
        )
        
        # 3×3 Nine-Up
        self.presets["nine_up"] = GridLayout(
            layout_id="nine_up",
            name="Nine-Up (3×3)",
            rows=3,
            columns=3,
            sources=["hdmi_1", "hdmi_2", "hdmi_3", "hdmi_4", "hdmi_5", 
                    "hdmi_6", "hdmi_7", "hdmi_8", "hdmi_9"]
        )
        
        # 1×4 Horizontal Strip
        self.presets["horizontal_strip"] = GridLayout(
            layout_id="horizontal_strip",
            name="Horizontal Strip (1×4)",
            rows=1,
            columns=4,
            sources=["hdmi_1", "hdmi_2", "hdmi_3", "hdmi_4"]
        )
    
    def activate_grid(self, preset_id: str) -> bool:
        """Activate grid preset"""
        if preset_id not in self.presets:
            print(f"Preset not found: {preset_id}")
            return False
        
        self.active_layout = self.presets[preset_id]
        print(f"Activated grid: {self.active_layout.name}")
        print(f"  Layout: {self.active_layout.rows}×{self.active_layout.columns}")
        print(f"  Sources: {len(self.active_layout.sources)}")
        
        return True
    
    def create_custom_grid(self, rows: int, columns: int, sources: List[str], 
                          save_as: Optional[str] = None) -> GridLayout:
        """Create custom grid layout"""
        import uuid
        layout_id = save_as or f"custom_{uuid.uuid4().hex[:8]}"
        
        layout = GridLayout(
            layout_id=layout_id,
            name=f"Custom {rows}×{columns}",
            rows=rows,
            columns=columns,
            sources=sources
        )
        
        if save_as:
            self.presets[layout_id] = layout
            print(f"Saved custom grid: {save_as}")
        
        self.active_layout = layout
        return layout
    
    def create_asymmetric_layout(self, zones: List[SourceZone], save_as: Optional[str] = None):
        """Create asymmetric layout with custom zones"""
        self.custom_zones = zones
        
        print(f"Created asymmetric layout: {len(zones)} zones")
        for zone in zones:
            print(f"  {zone.source_id}: ({zone.x}%, {zone.y}%) {zone.width}%×{zone.height}%")
        
        if save_as:
            # Save to presets
            pass
        
        return True


# ========== Touch-Based Source Resizing ==========

class TouchGesture(Enum):
    """Touch gesture type"""
    TAP = "tap"
    DRAG = "drag"
    PINCH = "pinch"
    DOUBLE_TAP = "double_tap"
    THREE_FINGER_SWIPE = "three_finger_swipe"


@dataclass
class ResizeHandle:
    """Resize handle for touch resize"""
    handle_id: str
    position: str  # "top", "bottom", "left", "right", "top_left", etc.
    x: float  # pixels
    y: float
    size: float = 30  # pixels


class TouchResizeController:
    """
    Touch-based source resizing controller
    Handles touch gestures for resizing sources
    """
    
    def __init__(self):
        self.selected_source: Optional[str] = None
        self.resize_handles: List[ResizeHandle] = []
        
        self.snap_to_grid = True
        self.grid_size = 20  # pixels
        
        self.min_width_percent = 10
        self.min_height_percent = 10
    
    def select_source(self, source_id: str):
        """Select source for resizing"""
        self.selected_source = source_id
        
        # Create resize handles
        self.resize_handles = self._create_resize_handles(source_id)
        
        print(f"Selected source: {source_id}")
        print(f"  Resize handles: {len(self.resize_handles)}")
    
    def _create_resize_handles(self, source_id: str) -> List[ResizeHandle]:
        """Create resize handles for source"""
        # In real implementation, calculate handle positions based on source bounds
        handles = [
            ResizeHandle("top", "top", 50, 0),
            ResizeHandle("bottom", "bottom", 50, 100),
            ResizeHandle("left", "left", 0, 50),
            ResizeHandle("right", "right", 100, 50),
            ResizeHandle("top_left", "top_left", 0, 0),
            ResizeHandle("top_right", "top_right", 100, 0),
            ResizeHandle("bottom_left", "bottom_left", 0, 100),
            ResizeHandle("bottom_right", "bottom_right", 100, 100)
        ]
        return handles
    
    def resize_source(self, source_id: str, width: float, height: float, 
                     x: float, y: float) -> bool:
        """Resize source"""
        # Apply constraints
        width = max(self.min_width_percent, min(100, width))
        height = max(self.min_height_percent, min(100, height))
        
        # Snap to grid
        if self.snap_to_grid:
            width = round(width / self.grid_size) * self.grid_size
            height = round(height / self.grid_size) * self.grid_size
            x = round(x / self.grid_size) * self.grid_size
            y = round(y / self.grid_size) * self.grid_size
        
        print(f"Resizing {source_id}:")
        print(f"  Position: ({x}%, {y}%)")
        print(f"  Size: {width}% × {height}%")
        
        # In real implementation:
        # 1. Update source video scaling
        # 2. Reposition on display
        # 3. Trigger visual feedback
        
        return True
    
    def handle_pinch_gesture(self, source_id: str, scale: float) -> bool:
        """Handle pinch-to-zoom gesture"""
        print(f"Pinch gesture on {source_id}: scale={scale}")
        
        # Scale source proportionally
        # In real implementation, calculate new width/height based on scale
        
        return True
    
    def handle_double_tap(self, source_id: str) -> bool:
        """Handle double-tap to maximize"""
        print(f"Double-tap on {source_id}: maximizing to full screen")
        
        # Maximize source to 100%×100%
        return self.resize_source(source_id, 100, 100, 0, 0)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    # SIP Phone
    print("=== SIP IP Phone ===\n")
    sip = SIPPhoneController()
    asyncio.run(sip.register("301", "password", "pbx.company.com"))
    
    call = asyncio.run(sip.make_call("102", video=False))
    if call:
        asyncio.run(asyncio.sleep(1))
        asyncio.run(sip.answer_call(call.call_id))
        asyncio.run(asyncio.sleep(2))
        asyncio.run(sip.hangup_call(call.call_id))
    
    # Doorbell
    print("\n=== Doorbell Camera ===\n")
    doorbell = DoorbellController()
    doorbell.register_doorbell("front_door", "Front Door", DoorbellType.RING, 
                              "rtsp://doorbell.local/live")
    
    event = asyncio.run(doorbell.on_doorbell_press("front_door", visitor_name="John Smith"))
    asyncio.run(doorbell.answer_doorbell("front_door"))
    asyncio.run(doorbell.unlock_door("front_door"))
    
    # Picture-in-Picture
    print("\n=== Picture-in-Picture ===\n")
    pip = PictureInPictureController()
    pip_window = pip.show_pip("doorbell_front", "Front Door Camera", 
                              position="bottom_right", width=25, height=25)
    if pip_window:
        pip.move_pip(pip_window.pip_id, 70, 70)
        pip.resize_pip(pip_window.pip_id, 30, 30)
        pip.close_pip(pip_window.pip_id)
    
    # Multi-Source Grid
    print("\n=== Multi-Source Grid ===\n")
    grid = MultiSourceLayoutController()
    grid.activate_grid("quad_view")
    
    # Custom 2×3 grid
    custom = grid.create_custom_grid(2, 3, 
                                    ["hdmi_1", "hdmi_2", "hdmi_3", "hdmi_4", "hdmi_5", "hdmi_6"],
                                    save_as="custom_2x3")
    
    # Touch Resize
    print("\n=== Touch-Based Resize ===\n")
    touch = TouchResizeController()
    touch.select_source("hdmi_1")
    touch.resize_source("hdmi_1", width=50, height=50, x=0, y=0)
    touch.handle_double_tap("hdmi_2")
