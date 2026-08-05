"""
Unified Communications System
SIP, Intercom, Paging, Audio/Video Doorbells, Access Control, Seamless Call Handoff

Features:
- SIP VoIP phone system (room extensions, external calls)
- Intercom system (room-to-room, zone-call, all-call)
- Paging system (zone paging, emergency announcements, TTS)
- Multi-door doorbell system (audio/video, multiple doors per location)
- Access control integration (smart locks, door strikes, gates)
- KVM audio integration (unified audio for all communication types)
- Seamless call handoff (hold/resume calls when moving between rooms)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import asyncio


# ========== Data Models ==========

class CallType(Enum):
    """Type of communication call"""
    SIP = "sip"
    INTERCOM = "intercom"
    DOORBELL = "doorbell"
    PAGING = "paging"


class CallStatus(Enum):
    """Call status"""
    IDLE = "idle"
    RINGING = "ringing"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    TRANSFERRING = "transferring"
    ENDED = "ended"


class DoorbellType(Enum):
    """Doorbell type"""
    VIDEO = "video"
    AUDIO = "audio"


class LockType(Enum):
    """Access control lock type"""
    SMART_LOCK = "smart_lock"
    DOOR_STRIKE = "door_strike"
    MAGLOCK = "maglock"
    GARAGE_DOOR = "garage_door"
    GATE = "gate"


@dataclass
class UnifiedCall:
    """Unified communication call"""
    call_id: str
    call_type: CallType
    status: CallStatus
    
    # Participants
    from_room: str
    to_room: Optional[str] = None
    to_zone: Optional[str] = None  # For zone-call/paging
    
    # Timing
    started_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    
    # Call details
    caller_name: Optional[str] = None
    caller_number: Optional[str] = None
    
    # Audio
    muted: bool = False
    
    # Handoff
    on_hold_for_transfer: bool = False
    transfer_target_room: Optional[str] = None


@dataclass
class Doorbell:
    """Doorbell device"""
    doorbell_id: str
    name: str
    doorbell_type: DoorbellType
    location: str  # Physical location (e.g., "front_entrance")
    
    # Hardware
    hardware_type: str  # "ring", "nest", "arlo", "unifi", "generic_rtsp", "sip"
    stream_url: Optional[str] = None
    
    # Access control
    associated_lock_id: Optional[str] = None
    
    # Routing
    notify_rooms: List[str] = field(default_factory=list)
    default_room: Optional[str] = None
    
    # Behavior
    auto_popup: bool = True
    pip_mode: bool = True
    record_on_press: bool = True
    record_on_motion: bool = False
    
    # Status
    online: bool = True
    last_activity: Optional[datetime] = None


@dataclass
class AccessControlLock:
    """Access control lock/door"""
    lock_id: str
    name: str
    lock_type: LockType
    
    # Hardware
    protocol: str  # "zwave", "zigbee", "wifi", "ip", "relay"
    device_id: Optional[str] = None
    
    # Behavior
    auto_lock: bool = True
    auto_lock_delay: int = 30  # seconds
    unlock_duration: int = 5  # seconds (for door strikes)
    
    # Associated doorbell
    doorbell_id: Optional[str] = None
    
    # Status
    locked: bool = True
    online: bool = True


# ========== SIP Phone Controller ==========

class SIPPhoneController:
    """
    SIP VoIP phone system
    Manages room extensions, external calls
    """
    
    def __init__(self, pbx_server: str, kvm_audio_enabled: bool = True):
        self.pbx_server = pbx_server
        self.kvm_audio_enabled = kvm_audio_enabled
        
        self.extensions: Dict[str, Dict[str, Any]] = {}  # extension_id -> config
        self.active_calls: Dict[str, UnifiedCall] = {}
        
        print(f"SIP Phone Controller initialized")
        print(f"  PBX Server: {pbx_server}")
        print(f"  KVM Audio: {kvm_audio_enabled}")
    
    def register_extension(self, extension_id: str, room_id: str, display_name: str, password: str):
        """Register SIP extension for room"""
        self.extensions[extension_id] = {
            "extension_id": extension_id,
            "room_id": room_id,
            "display_name": display_name,
            "password": password,
            "registered": False
        }
        
        print(f"Registered SIP extension: {extension_id} ({display_name})")
        
        # In real implementation: Register with PBX
        self.extensions[extension_id]["registered"] = True
    
    async def make_call(self, from_room: str, destination: str) -> Optional[UnifiedCall]:
        """Make outbound SIP call"""
        import uuid
        call_id = f"sip_{uuid.uuid4().hex[:8]}"
        
        call = UnifiedCall(
            call_id=call_id,
            call_type=CallType.SIP,
            status=CallStatus.RINGING,
            from_room=from_room,
            caller_number=destination,
            started_at=datetime.now()
        )
        
        self.active_calls[call_id] = call
        
        print(f"SIP call from {from_room} to {destination}")
        print(f"  Call ID: {call_id}")
        print(f"  Audio: {'KVM' if self.kvm_audio_enabled else 'Fallback'}")
        
        return call
    
    async def answer_call(self, call_id: str, room_id: str) -> bool:
        """Answer incoming SIP call"""
        if call_id not in self.active_calls:
            return False
        
        call = self.active_calls[call_id]
        call.status = CallStatus.ACTIVE
        call.answered_at = datetime.now()
        call.to_room = room_id
        
        print(f"SIP call answered in {room_id}")
        return True
    
    async def hold_call(self, call_id: str) -> bool:
        """Put call on hold"""
        if call_id not in self.active_calls:
            return False
        
        call = self.active_calls[call_id]
        call.status = CallStatus.ON_HOLD
        
        print(f"SIP call {call_id} on hold")
        # In real implementation: Send SIP HOLD, play music on hold
        return True
    
    async def resume_call(self, call_id: str, room_id: str) -> bool:
        """Resume held call in different room"""
        if call_id not in self.active_calls:
            return False
        
        call = self.active_calls[call_id]
        call.status = CallStatus.ACTIVE
        call.to_room = room_id
        
        print(f"SIP call {call_id} resumed in {room_id}")
        return True


# ========== Intercom Controller ==========

class IntercomController:
    """
    Intercom system
    Room-to-room, zone-call, all-call communication
    """
    
    def __init__(self, kvm_audio_enabled: bool = True):
        self.kvm_audio_enabled = kvm_audio_enabled
        
        self.stations: Dict[str, Dict[str, Any]] = {}  # station_id -> config
        self.zones: Dict[str, List[str]] = {}  # zone_id -> list of station_ids
        self.active_calls: Dict[str, UnifiedCall] = {}
        
        print("Intercom Controller initialized")
    
    def register_station(self, station_id: str, room_id: str, name: str, auto_answer: bool = False):
        """Register intercom station"""
        self.stations[station_id] = {
            "station_id": station_id,
            "room_id": room_id,
            "name": name,
            "auto_answer": auto_answer,
            "privacy_mode": False
        }
        
        print(f"Registered intercom station: {station_id} ({name})")
    
    def register_zone(self, zone_id: str, name: str, station_ids: List[str]):
        """Register intercom zone"""
        self.zones[zone_id] = station_ids
        print(f"Registered intercom zone: {zone_id} ({name}) with {len(station_ids)} stations")
    
    async def call_room(self, from_room: str, to_room: str) -> Optional[UnifiedCall]:
        """Call another room via intercom"""
        import uuid
        call_id = f"intercom_{uuid.uuid4().hex[:8]}"
        
        call = UnifiedCall(
            call_id=call_id,
            call_type=CallType.INTERCOM,
            status=CallStatus.RINGING,
            from_room=from_room,
            to_room=to_room,
            started_at=datetime.now()
        )
        
        self.active_calls[call_id] = call
        
        print(f"Intercom call: {from_room} → {to_room}")
        print(f"  Call ID: {call_id}")
        
        # Check if target room has auto-answer
        for station_id, station in self.stations.items():
            if station["room_id"] == to_room and station["auto_answer"]:
                await self.answer_call(call_id, to_room)
                print(f"  Auto-answered (station has auto_answer enabled)")
        
        return call
    
    async def zone_call(self, from_room: str, zone_id: str, message: str) -> Optional[UnifiedCall]:
        """Broadcast to zone via intercom"""
        import uuid
        call_id = f"intercom_zone_{uuid.uuid4().hex[:8]}"
        
        call = UnifiedCall(
            call_id=call_id,
            call_type=CallType.INTERCOM,
            status=CallStatus.ACTIVE,  # Zone calls are immediately active
            from_room=from_room,
            to_zone=zone_id,
            started_at=datetime.now()
        )
        
        self.active_calls[call_id] = call
        
        station_count = len(self.zones.get(zone_id, []))
        print(f"Intercom zone-call: {from_room} → Zone '{zone_id}' ({station_count} stations)")
        print(f"  Message: {message}")
        
        return call
    
    async def all_call(self, from_room: str, message: str) -> Optional[UnifiedCall]:
        """Broadcast to all rooms via intercom"""
        return await self.zone_call(from_room, "all", message)
    
    async def answer_call(self, call_id: str, room_id: str) -> bool:
        """Answer intercom call"""
        if call_id not in self.active_calls:
            return False
        
        call = self.active_calls[call_id]
        call.status = CallStatus.ACTIVE
        call.answered_at = datetime.now()
        
        print(f"Intercom call answered in {room_id}")
        return True


# ========== Paging Controller ==========

class PagingController:
    """
    Paging/PA system
    Zone paging, emergency announcements, text-to-speech
    """
    
    def __init__(self, kvm_audio_enabled: bool = True):
        self.kvm_audio_enabled = kvm_audio_enabled
        
        self.zones: Dict[str, List[str]] = {}  # zone_id -> list of speaker_ids
        self.speakers: Dict[str, Dict[str, Any]] = {}
        
        print("Paging Controller initialized")
    
    def register_zone(self, zone_id: str, name: str, speaker_ids: List[str]):
        """Register paging zone"""
        self.zones[zone_id] = speaker_ids
        print(f"Registered paging zone: {zone_id} ({name}) with {len(speaker_ids)} speakers")
    
    def register_speaker(self, speaker_id: str, name: str, ip_address: Optional[str] = None):
        """Register paging speaker"""
        self.speakers[speaker_id] = {
            "speaker_id": speaker_id,
            "name": name,
            "ip_address": ip_address,
            "online": True
        }
        print(f"Registered paging speaker: {speaker_id} ({name})")
    
    async def announce(self, zone_ids: List[str], message: str, priority: int = 60) -> bool:
        """Live paging announcement"""
        print(f"Paging announcement (priority {priority}):")
        print(f"  Zones: {', '.join(zone_ids)}")
        print(f"  Message: {message}")
        
        # Calculate total speakers
        total_speakers = 0
        for zone_id in zone_ids:
            total_speakers += len(self.zones.get(zone_id, []))
        
        print(f"  Broadcasting to {total_speakers} speakers")
        
        # In real implementation: Send audio to all speakers in zones
        return True
    
    async def tts_announce(self, zone_ids: List[str], text: str, voice: str = "en-US-female") -> bool:
        """Text-to-speech paging announcement"""
        print(f"Paging TTS announcement:")
        print(f"  Zones: {', '.join(zone_ids)}")
        print(f"  Text: {text}")
        print(f"  Voice: {voice}")
        
        # In real implementation: Convert text to speech, then broadcast
        return True
    
    async def emergency_page(self, message: str) -> bool:
        """Emergency paging (highest priority, all zones)"""
        print(f"🚨 EMERGENCY PAGING 🚨")
        return await self.announce(["all"], message, priority=100)


# ========== Doorbell Controller ==========

class DoorbellController:
    """
    Multi-door doorbell system
    Audio/video doorbells, multiple doors per location
    """
    
    def __init__(self):
        self.doorbells: Dict[str, Doorbell] = {}
        self.active_calls: Dict[str, UnifiedCall] = {}
        
        print("Doorbell Controller initialized")
    
    def register_doorbell(self, doorbell: Doorbell):
        """Register doorbell"""
        self.doorbells[doorbell.doorbell_id] = doorbell
        print(f"Registered doorbell: {doorbell.doorbell_id} ({doorbell.name})")
        print(f"  Type: {doorbell.doorbell_type.value}")
        print(f"  Location: {doorbell.location}")
        print(f"  Notify rooms: {', '.join(doorbell.notify_rooms)}")
    
    async def on_doorbell_press(self, doorbell_id: str) -> Optional[UnifiedCall]:
        """Handle doorbell button press"""
        if doorbell_id not in self.doorbells:
            return None
        
        doorbell = self.doorbells[doorbell_id]
        doorbell.last_activity = datetime.now()
        
        import uuid
        call_id = f"doorbell_{uuid.uuid4().hex[:8]}"
        
        call = UnifiedCall(
            call_id=call_id,
            call_type=CallType.DOORBELL,
            status=CallStatus.RINGING,
            from_room=doorbell_id,  # Doorbell acts as "from"
            caller_name=f"Doorbell: {doorbell.name}",
            started_at=datetime.now()
        )
        
        self.active_calls[call_id] = call
        
        print(f"🔔 Doorbell pressed: {doorbell.name}")
        print(f"  Call ID: {call_id}")
        print(f"  Type: {doorbell.doorbell_type.value}")
        print(f"  Notifying rooms: {', '.join(doorbell.notify_rooms)}")
        
        if doorbell.auto_popup:
            print(f"  Auto-popup enabled (PiP mode: {doorbell.pip_mode})")
        
        if doorbell.record_on_press:
            print(f"  Recording started")
        
        return call
    
    async def answer_doorbell(self, call_id: str, room_id: str) -> bool:
        """Answer doorbell call from room"""
        if call_id not in self.active_calls:
            return False
        
        call = self.active_calls[call_id]
        call.status = CallStatus.ACTIVE
        call.answered_at = datetime.now()
        call.to_room = room_id
        
        doorbell_id = call.from_room
        doorbell = self.doorbells.get(doorbell_id)
        
        print(f"Doorbell call answered:")
        print(f"  Doorbell: {doorbell.name if doorbell else doorbell_id}")
        print(f"  Answered from: {room_id}")
        print(f"  Two-way audio: Active")
        
        return True
    
    def get_doorbells_for_location(self, location_id: str) -> List[Doorbell]:
        """Get all doorbells for a location"""
        return list(self.doorbells.values())


# ========== Access Control Controller ==========

class AccessControlController:
    """
    Access control system
    Smart locks, door strikes, garage doors, gates
    """
    
    def __init__(self):
        self.locks: Dict[str, AccessControlLock] = {}
        self.access_logs: List[Dict[str, Any]] = []
        
        print("Access Control Controller initialized")
    
    def register_lock(self, lock: AccessControlLock):
        """Register access control lock"""
        self.locks[lock.lock_id] = lock
        print(f"Registered lock: {lock.lock_id} ({lock.name})")
        print(f"  Type: {lock.lock_type.value}")
        print(f"  Protocol: {lock.protocol}")
    
    async def unlock(self, lock_id: str, duration: Optional[int] = None, user: str = "System", room: str = "Unknown") -> bool:
        """Unlock door"""
        if lock_id not in self.locks:
            return False
        
        lock = self.locks[lock_id]
        unlock_duration = duration or lock.unlock_duration
        
        print(f"🔓 Unlocking: {lock.name}")
        print(f"  Type: {lock.lock_type.value}")
        print(f"  Duration: {unlock_duration}s")
        print(f"  Requested by: {user} (from {room})")
        
        # Log access event
        self._log_event(lock_id, "unlock", user, room)
        
        # In real implementation: Send unlock command to lock
        lock.locked = False
        
        # Auto-lock after delay
        if lock.auto_lock:
            print(f"  Auto-lock in {lock.auto_lock_delay}s")
            # asyncio.create_task(self._auto_lock(lock_id, lock.auto_lock_delay))
        
        return True
    
    async def lock(self, lock_id: str, user: str = "System", room: str = "Unknown") -> bool:
        """Lock door"""
        if lock_id not in self.locks:
            return False
        
        lock = self.locks[lock_id]
        
        print(f"🔒 Locking: {lock.name}")
        
        # Log access event
        self._log_event(lock_id, "lock", user, room)
        
        lock.locked = True
        return True
    
    def _log_event(self, lock_id: str, event: str, user: str, room: str):
        """Log access control event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "lock_id": lock_id,
            "event": event,
            "user": user,
            "room": room
        }
        self.access_logs.append(log_entry)
    
    def get_access_logs(self, lock_id: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get access logs"""
        if lock_id:
            return [log for log in self.access_logs if log["lock_id"] == lock_id]
        return self.access_logs


# ========== Call Handoff Controller ==========

class CallHandoffController:
    """
    Seamless call handoff between rooms
    Hold calls during room transitions, resume in new room
    """
    
    def __init__(self):
        self.user_locations: Dict[str, str] = {}  # user_id -> current_room_id
        self.follow_me_enabled: Dict[str, bool] = {}  # user_id -> enabled
        
        print("Call Handoff Controller initialized")
    
    async def hold_and_transfer(self, call_id: str, from_room: str, to_room: str, 
                                unified_comms: 'UnifiedCommunicationsController') -> bool:
        """Hold call and prepare for transfer to new room"""
        print(f"Call handoff initiated:")
        print(f"  Call ID: {call_id}")
        print(f"  From: {from_room}")
        print(f"  To: {to_room}")
        
        # Find call in any controller
        call = self._find_call(call_id, unified_comms)
        if not call:
            print(f"  ❌ Call not found")
            return False
        
        # Put call on hold
        call.status = CallStatus.ON_HOLD
        call.on_hold_for_transfer = True
        call.transfer_target_room = to_room
        
        print(f"  ✓ Call on hold")
        print(f"  Playing music on hold...")
        
        # Notify target room
        print(f"  📱 Notifying {to_room}: Call waiting from {from_room}")
        
        return True
    
    async def pickup_transferred_call(self, call_id: str, room_id: str, 
                                      unified_comms: 'UnifiedCommunicationsController') -> bool:
        """Pick up held call in new room"""
        call = self._find_call(call_id, unified_comms)
        if not call:
            return False
        
        if not call.on_hold_for_transfer:
            print(f"Call {call_id} not in transfer state")
            return False
        
        # Resume call in new room
        call.status = CallStatus.ACTIVE
        call.on_hold_for_transfer = False
        call.to_room = room_id
        
        print(f"Call resumed:")
        print(f"  Call ID: {call_id}")
        print(f"  Now in: {room_id}")
        print(f"  Duration: {call.duration_seconds}s (seamless continuation)")
        
        return True
    
    def enable_follow_me(self, user_id: str, enabled: bool, badge_id: Optional[str] = None):
        """Enable Follow Me mode for user"""
        self.follow_me_enabled[user_id] = enabled
        print(f"Follow Me {'enabled' if enabled else 'disabled'} for user: {user_id}")
        if badge_id:
            print(f"  Badge ID: {badge_id}")
    
    def update_user_location(self, user_id: str, room_id: str):
        """Update user's current location (for automatic handoff)"""
        old_room = self.user_locations.get(user_id)
        self.user_locations[user_id] = room_id
        
        if old_room and old_room != room_id:
            print(f"User location updated: {user_id}")
            print(f"  From: {old_room}")
            print(f"  To: {room_id}")
            
            # If Follow Me enabled, automatically transfer active calls
            if self.follow_me_enabled.get(user_id, False):
                print(f"  Follow Me active: Will auto-transfer calls")
    
    def _find_call(self, call_id: str, unified_comms: 'UnifiedCommunicationsController') -> Optional[UnifiedCall]:
        """Find call across all controllers"""
        # Check SIP
        if call_id in unified_comms.sip.active_calls:
            return unified_comms.sip.active_calls[call_id]
        
        # Check Intercom
        if call_id in unified_comms.intercom.active_calls:
            return unified_comms.intercom.active_calls[call_id]
        
        # Check Doorbell
        if call_id in unified_comms.doorbell.active_calls:
            return unified_comms.doorbell.active_calls[call_id]
        
        return None


# ========== Unified Communications Controller ==========

class UnifiedCommunicationsController:
    """
    Main unified communications controller
    Integrates SIP, Intercom, Paging, Doorbells, Access Control, Call Handoff
    """
    
    def __init__(self, location_id: str, pbx_server: str = "pbx.local", 
                 kvm_audio_enabled: bool = True):
        self.location_id = location_id
        self.kvm_audio_enabled = kvm_audio_enabled
        
        # Sub-controllers
        self.sip = SIPPhoneController(pbx_server, kvm_audio_enabled)
        self.intercom = IntercomController(kvm_audio_enabled)
        self.paging = PagingController(kvm_audio_enabled)
        self.doorbell = DoorbellController()
        self.access_control = AccessControlController()
        self.handoff = CallHandoffController()
        
        print(f"\n{'='*60}")
        print(f"Unified Communications System Initialized")
        print(f"  Location: {location_id}")
        print(f"  KVM Audio: {kvm_audio_enabled}")
        print(f"{'='*60}\n")
    
    def get_all_active_calls(self) -> List[UnifiedCall]:
        """Get all active calls across all types"""
        calls = []
        calls.extend(self.sip.active_calls.values())
        calls.extend(self.intercom.active_calls.values())
        calls.extend(self.doorbell.active_calls.values())
        return calls
    
    def get_status(self) -> Dict[str, Any]:
        """Get unified communications system status"""
        return {
            "location_id": self.location_id,
            "kvm_audio_enabled": self.kvm_audio_enabled,
            "active_calls": {
                "sip": len(self.sip.active_calls),
                "intercom": len(self.intercom.active_calls),
                "doorbell": len(self.doorbell.active_calls),
                "total": len(self.get_all_active_calls())
            },
            "devices": {
                "sip_extensions": len(self.sip.extensions),
                "intercom_stations": len(self.intercom.stations),
                "paging_zones": len(self.paging.zones),
                "doorbells": len(self.doorbell.doorbells),
                "access_control_locks": len(self.access_control.locks)
            }
        }


# Example usage
if __name__ == "__main__":
    print("=== Unified Communications System Demo ===\n")
    
    # Initialize system
    uc = UnifiedCommunicationsController(
        location_id="headquarters",
        pbx_server="pbx.company.com",
        kvm_audio_enabled=True
    )
    
    # Configure SIP extensions
    print("\n--- Configuring SIP Extensions ---\n")
    uc.sip.register_extension("301", "conference_room_a", "Conference Room A", "pass301")
    uc.sip.register_extension("302", "conference_room_b", "Conference Room B", "pass302")
    uc.sip.register_extension("303", "executive_office", "Executive Office", "pass303")
    
    # Configure Intercom
    print("\n--- Configuring Intercom ---\n")
    uc.intercom.register_station("ic_301", "conference_room_a", "Conference Room A")
    uc.intercom.register_station("ic_302", "conference_room_b", "Conference Room B")
    uc.intercom.register_station("ic_reception", "reception", "Reception", auto_answer=True)
    uc.intercom.register_zone("all", "Entire Building", ["ic_301", "ic_302", "ic_reception"])
    
    # Configure Paging
    print("\n--- Configuring Paging ---\n")
    uc.paging.register_speaker("speaker_101", "Lobby Speaker", "192.168.1.101")
    uc.paging.register_speaker("speaker_102", "Hallway Speaker", "192.168.1.102")
    uc.paging.register_zone("all", "Entire Building", ["speaker_101", "speaker_102"])
    
    # Configure Doorbells
    print("\n--- Configuring Doorbells ---\n")
    front_door = Doorbell(
        doorbell_id="front_door",
        name="Front Door",
        doorbell_type=DoorbellType.VIDEO,
        location="front_entrance",
        hardware_type="ring",
        stream_url="rtsp://192.168.1.50/live",
        notify_rooms=["reception", "conference_room_a"],
        default_room="reception",
        auto_popup=True,
        pip_mode=True,
        record_on_press=True
    )
    uc.doorbell.register_doorbell(front_door)
    
    back_door = Doorbell(
        doorbell_id="back_door",
        name="Back Door (Deliveries)",
        doorbell_type=DoorbellType.AUDIO,
        location="back_entrance",
        hardware_type="sip",
        notify_rooms=["warehouse"],
        default_room="warehouse"
    )
    uc.doorbell.register_doorbell(back_door)
    
    # Configure Access Control
    print("\n--- Configuring Access Control ---\n")
    front_lock = AccessControlLock(
        lock_id="front_door_lock",
        name="Front Door Lock",
        lock_type=LockType.SMART_LOCK,
        protocol="zwave",
        device_id="zwave_node_5",
        auto_lock=True,
        auto_lock_delay=30,
        doorbell_id="front_door"
    )
    uc.access_control.register_lock(front_lock)
    
    back_strike = AccessControlLock(
        lock_id="back_door_strike",
        name="Back Door Strike",
        lock_type=LockType.DOOR_STRIKE,
        protocol="relay",
        device_id="relay_1",
        unlock_duration=3,
        doorbell_id="back_door"
    )
    uc.access_control.register_lock(back_strike)
    
    # Simulate usage scenarios
    print("\n" + "="*60)
    print("SCENARIO SIMULATIONS")
    print("="*60)
    
    async def run_scenarios():
        # Scenario 1: Doorbell rings, answered, unlock door
        print("\n--- Scenario 1: Front Doorbell ---\n")
        call = await uc.doorbell.on_doorbell_press("front_door")
        await asyncio.sleep(1)
        await uc.doorbell.answer_doorbell(call.call_id, "reception")
        await asyncio.sleep(2)
        await uc.access_control.unlock("front_door_lock", user="Receptionist", room="reception")
        
        # Scenario 2: Intercom call
        print("\n--- Scenario 2: Intercom Call ---\n")
        intercom_call = await uc.intercom.call_room("conference_room_a", "reception")
        await asyncio.sleep(1)
        await uc.intercom.answer_call(intercom_call.call_id, "reception")
        
        # Scenario 3: SIP call with handoff
        print("\n--- Scenario 3: SIP Call with Handoff ---\n")
        sip_call = await uc.sip.make_call("conference_room_a", "+1-555-123-4567")
        await asyncio.sleep(1)
        await uc.sip.answer_call(sip_call.call_id, "conference_room_a")
        print("\n  User starts walking to Conference Room B...")
        await asyncio.sleep(2)
        await uc.handoff.hold_and_transfer(sip_call.call_id, "conference_room_a", "conference_room_b", uc)
        await asyncio.sleep(1)
        print("\n  User arrives at Conference Room B...")
        await uc.handoff.pickup_transferred_call(sip_call.call_id, "conference_room_b", uc)
        
        # Scenario 4: Emergency paging
        print("\n--- Scenario 4: Emergency Paging ---\n")
        await uc.paging.emergency_page("Fire drill in progress. Evacuate building immediately.")
        
        # Scenario 5: Zone intercom call
        print("\n--- Scenario 5: Zone Intercom Call ---\n")
        await uc.intercom.all_call("reception", "Attention all rooms: Town hall meeting in 10 minutes")
    
    # Run scenarios
    asyncio.run(run_scenarios())
    
    # Print final status
    print("\n" + "="*60)
    print("SYSTEM STATUS")
    print("="*60 + "\n")
    status = uc.get_status()
    print(f"Location: {status['location_id']}")
    print(f"KVM Audio: {status['kvm_audio_enabled']}")
    print(f"\nActive Calls:")
    print(f"  SIP: {status['active_calls']['sip']}")
    print(f"  Intercom: {status['active_calls']['intercom']}")
    print(f"  Doorbell: {status['active_calls']['doorbell']}")
    print(f"  Total: {status['active_calls']['total']}")
    print(f"\nDevices:")
    print(f"  SIP Extensions: {status['devices']['sip_extensions']}")
    print(f"  Intercom Stations: {status['devices']['intercom_stations']}")
    print(f"  Paging Zones: {status['devices']['paging_zones']}")
    print(f"  Doorbells: {status['devices']['doorbells']}")
    print(f"  Access Control Locks: {status['devices']['access_control_locks']}")
