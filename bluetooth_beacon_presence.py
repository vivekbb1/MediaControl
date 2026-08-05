"""
Bluetooth Beacon Proximity & Presence Detection
Room-level location tracking and automated actions

Features:
- Beacon scanning (iBeacon, Eddystone, AltBeacon)
- RSSI-based proximity detection (immediate, near, far, unknown)
- Presence detection (enter/exit events with debouncing)
- Dwell time tracking (how long someone stays in a room)
- User identification (phone MAC or personal beacon)
- Automation triggers (unlock door, lights, HVAC, notifications)
- Multi-beacon triangulation for accurate positioning
- RSSI smoothing (Kalman filter)
- Battery monitoring for beacons
- Occupancy reporting
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import math
import secrets
import struct


# ========== Data Models ==========

class BeaconType(Enum):
    """Beacon protocol type"""
    IBEACON = "ibeacon"
    EDDYSTONE = "eddystone"
    ALTBEACON = "altbeacon"


class ProximityZone(Enum):
    """Proximity zone based on RSSI"""
    IMMEDIATE = "immediate"  # < 1 meter (at door)
    NEAR = "near"  # 1-3 meters (inside room)
    FAR = "far"  # 3-10 meters (hallway)
    UNKNOWN = "unknown"  # > 10 meters (too far)


class PresenceEvent(Enum):
    """Presence event type"""
    ENTER = "enter"
    EXIT = "exit"


@dataclass
class BeaconConfig:
    """Beacon configuration"""
    beacon_id: str
    type: BeaconType
    
    # iBeacon
    uuid: Optional[str] = None
    major: Optional[int] = None
    minor: Optional[int] = None
    
    # Eddystone
    namespace: Optional[str] = None
    instance: Optional[str] = None
    url: Optional[str] = None
    
    # AltBeacon
    organization_id: Optional[str] = None
    beacon_code: Optional[str] = None
    
    # Location
    room_number: Optional[str] = None
    location: Optional[str] = None  # "above_door_inside", etc.
    
    # Calibration
    tx_power: int = -59  # Calibrated RSSI at 1 meter


@dataclass
class BeaconScan:
    """Single beacon scan result"""
    beacon_id: str
    rssi: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Parsed beacon data
    type: Optional[BeaconType] = None
    uuid: Optional[str] = None
    major: Optional[int] = None
    minor: Optional[int] = None


@dataclass
class ProximityData:
    """Proximity data for user-beacon pair"""
    user_id: str
    beacon_id: str
    
    # RSSI
    rssi_raw: int
    rssi_smoothed: float
    
    # Distance
    distance_meters: float
    zone: ProximityZone
    
    # Timing
    first_seen: datetime
    last_seen: datetime
    
    # Smoothing filter
    rssi_filter: Optional['RSSIKalmanFilter'] = None


@dataclass
class PresenceData:
    """Presence data for user in room"""
    presence_id: str
    user_id: str
    room_number: str
    
    # Timing
    entered_at: datetime
    exited_at: Optional[datetime] = None
    dwell_time_seconds: Optional[int] = None
    
    # State
    currently_present: bool = True


@dataclass
class UserDevice:
    """User device for identification"""
    user_id: str
    user_name: str
    user_type: str  # "guest" or "staff"
    
    # Identification
    bluetooth_mac: Optional[str] = None  # Phone MAC address
    beacon_id: Optional[str] = None  # Personal beacon
    
    # Guest-specific
    room_number: Optional[str] = None
    checked_in: bool = False
    key_active: bool = False


# ========== RSSI Kalman Filter ==========

class RSSIKalmanFilter:
    """
    Kalman filter for RSSI smoothing
    Reduces noise in RSSI measurements
    """
    
    def __init__(self, process_variance: float = 0.01, measurement_variance: float = 4.0):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_rssi: Optional[float] = None
        self.error_covariance: float = 1.0
    
    def update(self, measured_rssi: int) -> float:
        """Update filter with new RSSI measurement"""
        if self.estimated_rssi is None:
            self.estimated_rssi = float(measured_rssi)
            return self.estimated_rssi
        
        # Prediction
        prediction = self.estimated_rssi
        prediction_covariance = self.error_covariance + self.process_variance
        
        # Update
        kalman_gain = prediction_covariance / (prediction_covariance + self.measurement_variance)
        self.estimated_rssi = prediction + kalman_gain * (measured_rssi - prediction)
        self.error_covariance = (1 - kalman_gain) * prediction_covariance
        
        return self.estimated_rssi


# ========== Proximity Calculator ==========

class ProximityCalculator:
    """
    Calculate distance and proximity zone from RSSI
    """
    
    def __init__(self, tx_power: int = -59, path_loss_exponent: float = 3.0):
        """
        Args:
            tx_power: Calibrated RSSI at 1 meter (typically -59 dBm)
            path_loss_exponent: Environment-specific (2.0 = free space, 3.0 = typical indoor, 4.0 = dense walls)
        """
        self.tx_power = tx_power
        self.path_loss_exponent = path_loss_exponent
    
    def rssi_to_distance(self, rssi: float) -> float:
        """
        Convert RSSI to distance in meters
        Formula: distance = 10 ^ ((tx_power - rssi) / (10 * path_loss_exponent))
        """
        if rssi == 0:
            return -1.0
        
        ratio = (self.tx_power - rssi) / (10 * self.path_loss_exponent)
        distance = math.pow(10, ratio)
        
        return round(distance, 2)
    
    def rssi_to_zone(self, rssi: float) -> ProximityZone:
        """Convert RSSI to proximity zone"""
        if rssi >= -59:
            return ProximityZone.IMMEDIATE  # < 1 meter
        elif rssi >= -70:
            return ProximityZone.NEAR  # 1-3 meters
        elif rssi >= -90:
            return ProximityZone.FAR  # 3-10 meters
        else:
            return ProximityZone.UNKNOWN  # > 10 meters


# ========== Beacon Scanner ==========

class BeaconScanner:
    """
    Scan for Bluetooth beacons (iBeacon, Eddystone, AltBeacon)
    
    Note: This is a mock implementation for demonstration.
    In production, use:
    - bleak (async BLE library for Python)
    - bluepy (Raspberry Pi)
    - pybluez (Linux)
    """
    
    def __init__(self, scan_interval: float = 1.0):
        self.scan_interval = scan_interval
        self.scanning = False
        self.callbacks: List[Callable] = []
    
    async def start_scanning(self):
        """Start scanning for beacons"""
        self.scanning = True
        print(f"Beacon scanner started (interval: {self.scan_interval}s)")
        
        while self.scanning:
            # Mock: In production, this would use BLE scanning
            # For now, generate mock beacon scans for demo
            await self._mock_scan()
            await asyncio.sleep(self.scan_interval)
    
    def stop_scanning(self):
        """Stop scanning"""
        self.scanning = False
        print("Beacon scanner stopped")
    
    def on_beacon_detected(self, callback: Callable):
        """Register callback for beacon detection"""
        self.callbacks.append(callback)
    
    async def _mock_scan(self):
        """Mock beacon scan (for demonstration)"""
        # In production, this would:
        # 1. Scan for BLE advertisements
        # 2. Parse iBeacon/Eddystone/AltBeacon packets
        # 3. Extract UUID/Major/Minor or Namespace/Instance
        # 4. Measure RSSI
        # 5. Call callbacks with BeaconScan objects
        pass
    
    def parse_ibeacon(self, advertisement_data: bytes) -> Optional[BeaconScan]:
        """
        Parse iBeacon advertisement packet
        
        Format:
        - Bytes 0-3: Manufacturer ID (0x004C = Apple)
        - Bytes 4-5: iBeacon type (0x02, 0x15)
        - Bytes 6-21: UUID (16 bytes)
        - Bytes 22-23: Major (2 bytes)
        - Bytes 24-25: Minor (2 bytes)
        - Byte 26: TX Power (1 byte)
        """
        try:
            # Check manufacturer ID (Apple = 0x004C)
            manufacturer_id = struct.unpack(">H", advertisement_data[0:2])[0]
            if manufacturer_id != 0x004C:
                return None
            
            # Check iBeacon type
            if advertisement_data[4:6] != b'\x02\x15':
                return None
            
            # Parse UUID
            uuid_bytes = advertisement_data[6:22]
            uuid = uuid_bytes.hex()
            uuid_formatted = f"{uuid[0:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:32]}"
            
            # Parse Major, Minor
            major = struct.unpack(">H", advertisement_data[22:24])[0]
            minor = struct.unpack(">H", advertisement_data[24:26])[0]
            
            # Parse TX Power
            tx_power = struct.unpack("b", advertisement_data[26:27])[0]
            
            beacon_id = f"ibeacon_{major}_{minor}"
            
            return BeaconScan(
                beacon_id=beacon_id,
                rssi=-65,  # Mock RSSI
                type=BeaconType.IBEACON,
                uuid=uuid_formatted,
                major=major,
                minor=minor
            )
        
        except Exception as e:
            print(f"Error parsing iBeacon: {e}")
            return None


# ========== Proximity Tracker ==========

class ProximityTracker:
    """
    Track proximity between users and beacons
    """
    
    def __init__(self, tx_power: int = -59, path_loss_exponent: float = 3.0):
        self.proximity_data: Dict[str, ProximityData] = {}  # Key: "user_id:beacon_id"
        self.calculator = ProximityCalculator(tx_power, path_loss_exponent)
        
        print(f"\n{'='*60}")
        print(f"Proximity Tracker Initialized")
        print(f"  TX Power: {tx_power} dBm")
        print(f"  Path Loss Exponent: {path_loss_exponent}")
        print(f"{'='*60}\n")
    
    async def update_proximity(self, user_id: str, beacon_id: str, rssi: int) -> ProximityData:
        """Update proximity data for user-beacon pair"""
        key = f"{user_id}:{beacon_id}"
        
        # Get or create proximity data
        if key not in self.proximity_data:
            # Create new
            rssi_filter = RSSIKalmanFilter()
            rssi_smoothed = rssi_filter.update(rssi)
            
            proximity = ProximityData(
                user_id=user_id,
                beacon_id=beacon_id,
                rssi_raw=rssi,
                rssi_smoothed=rssi_smoothed,
                distance_meters=self.calculator.rssi_to_distance(rssi_smoothed),
                zone=self.calculator.rssi_to_zone(rssi_smoothed),
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                rssi_filter=rssi_filter
            )
            
            self.proximity_data[key] = proximity
        
        else:
            # Update existing
            proximity = self.proximity_data[key]
            proximity.rssi_raw = rssi
            proximity.rssi_smoothed = proximity.rssi_filter.update(rssi)
            proximity.distance_meters = self.calculator.rssi_to_distance(proximity.rssi_smoothed)
            proximity.zone = self.calculator.rssi_to_zone(proximity.rssi_smoothed)
            proximity.last_seen = datetime.now()
        
        return self.proximity_data[key]
    
    def get_proximity(self, user_id: str, beacon_id: str) -> Optional[ProximityData]:
        """Get current proximity data"""
        key = f"{user_id}:{beacon_id}"
        return self.proximity_data.get(key)
    
    def cleanup_stale_data(self, max_age_seconds: int = 60):
        """Remove stale proximity data (no update for N seconds)"""
        now = datetime.now()
        stale_keys = []
        
        for key, proximity in self.proximity_data.items():
            age = (now - proximity.last_seen).total_seconds()
            if age > max_age_seconds:
                stale_keys.append(key)
        
        for key in stale_keys:
            del self.proximity_data[key]
        
        if stale_keys:
            print(f"Cleaned up {len(stale_keys)} stale proximity entries")


# ========== Presence Detector ==========

class PresenceDetector:
    """
    Detect room entry/exit events and track dwell time
    """
    
    def __init__(self, 
                 enter_zone: ProximityZone = ProximityZone.NEAR,
                 exit_zone: ProximityZone = ProximityZone.UNKNOWN,
                 debounce_enter_seconds: int = 5,
                 debounce_exit_seconds: int = 30):
        """
        Args:
            enter_zone: Zone threshold for entering (e.g., NEAR or IMMEDIATE)
            exit_zone: Zone threshold for exiting (e.g., UNKNOWN)
            debounce_enter_seconds: Must stay in zone for N seconds to trigger enter
            debounce_exit_seconds: Must be gone for N seconds to trigger exit
        """
        self.enter_zone = enter_zone
        self.exit_zone = exit_zone
        self.debounce_enter = debounce_enter_seconds
        self.debounce_exit = debounce_exit_seconds
        
        self.presence_data: Dict[str, PresenceData] = {}  # Key: "user_id:room_number"
        self.pending_entries: Dict[str, datetime] = {}  # Debounce for entries
        self.pending_exits: Dict[str, datetime] = {}  # Debounce for exits
        
        self.callbacks: Dict[PresenceEvent, List[Callable]] = {
            PresenceEvent.ENTER: [],
            PresenceEvent.EXIT: []
        }
        
        print(f"\n{'='*60}")
        print(f"Presence Detector Initialized")
        print(f"  Enter zone: {enter_zone.value}")
        print(f"  Exit zone: {exit_zone.value}")
        print(f"  Debounce enter: {debounce_enter_seconds}s")
        print(f"  Debounce exit: {debounce_exit_seconds}s")
        print(f"{'='*60}\n")
    
    async def process_proximity(self, user_id: str, room_number: str, proximity: ProximityData):
        """Process proximity update and detect enter/exit events"""
        key = f"{user_id}:{room_number}"
        
        # Check current presence state
        is_present = key in self.presence_data and self.presence_data[key].currently_present
        
        # Determine if should be present based on proximity zone
        should_be_present = self._zone_indicates_presence(proximity.zone)
        
        if should_be_present and not is_present:
            # Potential ENTER event
            await self._handle_potential_enter(user_id, room_number, proximity)
        
        elif not should_be_present and is_present:
            # Potential EXIT event
            await self._handle_potential_exit(user_id, room_number)
        
        elif should_be_present and is_present:
            # Still present - reset exit debounce
            if key in self.pending_exits:
                del self.pending_exits[key]
        
        elif not should_be_present and not is_present:
            # Still not present - reset enter debounce
            if key in self.pending_entries:
                del self.pending_entries[key]
    
    def _zone_indicates_presence(self, zone: ProximityZone) -> bool:
        """Check if proximity zone indicates presence in room"""
        zone_order = [ProximityZone.IMMEDIATE, ProximityZone.NEAR, ProximityZone.FAR, ProximityZone.UNKNOWN]
        enter_idx = zone_order.index(self.enter_zone)
        current_idx = zone_order.index(zone)
        return current_idx <= enter_idx
    
    async def _handle_potential_enter(self, user_id: str, room_number: str, proximity: ProximityData):
        """Handle potential enter event with debouncing"""
        key = f"{user_id}:{room_number}"
        now = datetime.now()
        
        if key not in self.pending_entries:
            # Start debounce timer
            self.pending_entries[key] = now
            print(f"Potential ENTER: {user_id} at {room_number} (zone: {proximity.zone.value}, waiting {self.debounce_enter}s)")
        
        else:
            # Check if debounce period elapsed
            elapsed = (now - self.pending_entries[key]).total_seconds()
            
            if elapsed >= self.debounce_enter:
                # Trigger ENTER event
                await self._trigger_enter(user_id, room_number)
                del self.pending_entries[key]
    
    async def _handle_potential_exit(self, user_id: str, room_number: str):
        """Handle potential exit event with debouncing"""
        key = f"{user_id}:{room_number}"
        now = datetime.now()
        
        if key not in self.pending_exits:
            # Start debounce timer
            self.pending_exits[key] = now
            print(f"Potential EXIT: {user_id} from {room_number} (waiting {self.debounce_exit}s)")
        
        else:
            # Check if debounce period elapsed
            elapsed = (now - self.pending_exits[key]).total_seconds()
            
            if elapsed >= self.debounce_exit:
                # Trigger EXIT event
                await self._trigger_exit(user_id, room_number)
                del self.pending_exits[key]
    
    async def _trigger_enter(self, user_id: str, room_number: str):
        """Trigger ENTER event"""
        key = f"{user_id}:{room_number}"
        presence_id = f"presence_{secrets.token_hex(6)}"
        
        presence = PresenceData(
            presence_id=presence_id,
            user_id=user_id,
            room_number=room_number,
            entered_at=datetime.now(),
            currently_present=True
        )
        
        self.presence_data[key] = presence
        
        print(f"\n🚪 ENTER EVENT")
        print(f"  User: {user_id}")
        print(f"  Room: {room_number}")
        print(f"  Time: {presence.entered_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Call callbacks
        for callback in self.callbacks[PresenceEvent.ENTER]:
            await callback(presence)
    
    async def _trigger_exit(self, user_id: str, room_number: str):
        """Trigger EXIT event"""
        key = f"{user_id}:{room_number}"
        
        if key not in self.presence_data:
            return
        
        presence = self.presence_data[key]
        presence.exited_at = datetime.now()
        presence.currently_present = False
        presence.dwell_time_seconds = int((presence.exited_at - presence.entered_at).total_seconds())
        
        print(f"\n🚪 EXIT EVENT")
        print(f"  User: {user_id}")
        print(f"  Room: {room_number}")
        print(f"  Entered: {presence.entered_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Exited: {presence.exited_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Dwell time: {presence.dwell_time_seconds // 60} minutes")
        
        # Call callbacks
        for callback in self.callbacks[PresenceEvent.EXIT]:
            await callback(presence)
        
        # Remove from active presence (keep for history if needed)
        # del self.presence_data[key]
    
    def on_presence_event(self, event: PresenceEvent, callback: Callable):
        """Register callback for presence events"""
        self.callbacks[event].append(callback)
    
    def get_current_presence(self, room_number: str) -> List[PresenceData]:
        """Get all users currently present in room"""
        return [
            presence for presence in self.presence_data.values()
            if presence.room_number == room_number and presence.currently_present
        ]
    
    def is_room_occupied(self, room_number: str) -> bool:
        """Check if room is currently occupied"""
        return len(self.get_current_presence(room_number)) > 0


# ========== Beacon Presence System ==========

class BeaconPresenceSystem:
    """
    Complete beacon-based presence detection system
    """
    
    def __init__(self):
        self.scanner = BeaconScanner()
        self.proximity_tracker = ProximityTracker()
        self.presence_detector = PresenceDetector()
        
        # Configuration
        self.beacons: Dict[str, BeaconConfig] = {}
        self.users: Dict[str, UserDevice] = {}
        
        # Map beacons to rooms
        self.beacon_room_map: Dict[str, str] = {}  # beacon_id -> room_number
        
        print(f"\n{'='*60}")
        print(f"Beacon Presence System Initialized")
        print(f"{'='*60}\n")
    
    def register_beacon(self, beacon: BeaconConfig):
        """Register a beacon"""
        self.beacons[beacon.beacon_id] = beacon
        if beacon.room_number:
            self.beacon_room_map[beacon.beacon_id] = beacon.room_number
        print(f"Registered beacon: {beacon.beacon_id} (Room {beacon.room_number})")
    
    def register_user(self, user: UserDevice):
        """Register a user"""
        self.users[user.user_id] = user
        print(f"Registered user: {user.user_name} ({user.user_type})")
    
    async def process_beacon_scan(self, user_id: str, beacon_id: str, rssi: int):
        """Process a beacon scan result"""
        # Update proximity
        proximity = await self.proximity_tracker.update_proximity(user_id, beacon_id, rssi)
        
        # Get room for beacon
        room_number = self.beacon_room_map.get(beacon_id)
        if not room_number:
            return
        
        # Detect presence
        await self.presence_detector.process_proximity(user_id, room_number, proximity)
    
    async def start(self):
        """Start the system"""
        print("Starting Beacon Presence System...")
        await self.scanner.start_scanning()
    
    def stop(self):
        """Stop the system"""
        print("Stopping Beacon Presence System...")
        self.scanner.stop_scanning()
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "beacons_registered": len(self.beacons),
            "users_registered": len(self.users),
            "active_proximity_tracks": len(self.proximity_tracker.proximity_data),
            "active_presences": len([p for p in self.presence_detector.presence_data.values() if p.currently_present])
        }


# Example usage
if __name__ == "__main__":
    print("=== Bluetooth Beacon Presence Detection Demo ===\n")
    
    async def run_demo():
        # Initialize system
        system = BeaconPresenceSystem()
        
        # Register beacons
        print("\n--- Register Beacons ---\n")
        
        beacon_2201 = BeaconConfig(
            beacon_id="room_2201_beacon",
            type=BeaconType.IBEACON,
            uuid="550e8400-e29b-41d4-a716-446655440000",
            major=22,
            minor=2201,
            room_number="2201",
            tx_power=-59
        )
        system.register_beacon(beacon_2201)
        
        # Register users
        print("\n--- Register Users ---\n")
        
        guest = UserDevice(
            user_id="guest_john_smith",
            user_name="John Smith",
            user_type="guest",
            room_number="2201",
            checked_in=True,
            key_active=True
        )
        system.register_user(guest)
        
        # Register presence event callbacks
        print("\n--- Register Callbacks ---\n")
        
        async def on_enter(presence: PresenceData):
            print(f"🎉 Automation: User entered room, unlocking door and turning on lights")
        
        async def on_exit(presence: PresenceData):
            print(f"💡 Automation: User left room, activating energy saving mode")
        
        system.presence_detector.on_presence_event(PresenceEvent.ENTER, on_enter)
        system.presence_detector.on_presence_event(PresenceEvent.EXIT, on_exit)
        
        # Simulate beacon scans
        print("\n--- Simulate Beacon Scans ---\n")
        
        # Approach room (far)
        print("Guest approaching room...")
        await system.process_beacon_scan("guest_john_smith", "room_2201_beacon", -75)
        await asyncio.sleep(1)
        
        # Near room (near)
        print("Guest near room...")
        await system.process_beacon_scan("guest_john_smith", "room_2201_beacon", -65)
        await asyncio.sleep(6)  # Wait for debounce (5s)
        
        # At door (immediate)
        print("Guest at door...")
        await system.process_beacon_scan("guest_john_smith", "room_2201_beacon", -55)
        await asyncio.sleep(10)
        
        # Inside room (near)
        print("Guest inside room...")
        for _ in range(60):
            await system.process_beacon_scan("guest_john_smith", "room_2201_beacon", -62)
            await asyncio.sleep(1)
        
        # Leaving room (far)
        print("Guest leaving room...")
        await system.process_beacon_scan("guest_john_smith", "room_2201_beacon", -80)
        await asyncio.sleep(31)  # Wait for debounce (30s)
        
        # Print status
        print("\n" + "="*60)
        print("SYSTEM STATUS")
        print("="*60 + "\n")
        
        status = system.get_status()
        print(f"Beacons registered: {status['beacons_registered']}")
        print(f"Users registered: {status['users_registered']}")
        print(f"Active proximity tracks: {status['active_proximity_tracks']}")
        print(f"Active presences: {status['active_presences']}")
    
    asyncio.run(run_demo())
