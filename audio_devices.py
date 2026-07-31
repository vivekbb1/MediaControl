"""
Audio Device Support - AirPlay and Sonos
Multi-room audio with grouping/ungrouping capabilities
"""

from typing import Dict, Optional, Any, List, Set
from enum import Enum
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

# Try to import pyatv (for AirPlay)
try:
    import pyatv
    PYATV_AVAILABLE = True
except ImportError:
    PYATV_AVAILABLE = False
    logger.warning("pyatv not installed. AirPlay control will be limited.")

# Try to import soco (for Sonos)
try:
    import soco
    SOCO_AVAILABLE = True
except ImportError:
    SOCO_AVAILABLE = False
    logger.warning("soco not installed. Sonos control will not be available.")
    logger.warning("Install with: pip install soco")


class AudioDeviceType(Enum):
    """Audio device types"""
    AIRPLAY = "airplay"
    AIRPLAY2 = "airplay2"
    SONOS = "sonos"
    CHROMECAST_AUDIO = "chromecast_audio"


@dataclass
class AudioGroup:
    """
    Audio group (zone) for synchronized playback
    """
    id: str
    name: str
    coordinator_device_id: str  # Main device controlling the group
    member_device_ids: List[str] = field(default_factory=list)
    volume: int = 50
    is_playing: bool = False
    current_source: Optional[str] = None


class AirPlaySpeaker:
    """
    AirPlay/AirPlay 2 speaker
    Works with Apple devices, HomePod, etc.
    """
    
    def __init__(
        self,
        device_id: str,
        name: str,
        ip: str,
        password: Optional[str] = None,
    ):
        if not PYATV_AVAILABLE:
            logger.warning("pyatv not available, AirPlay support limited")
        
        self.id = device_id
        self.name = name
        self.ip = ip
        self.password = password
        self._device = None
        self._volume = 50
        self._is_playing = False
    
    async def connect(self) -> bool:
        """Connect to AirPlay device"""
        if not PYATV_AVAILABLE:
            return False
        
        try:
            # Scan for AirPlay device
            atvs = await pyatv.scan(hosts=[self.ip], timeout=5)
            if not atvs:
                logger.error(f"No AirPlay device found at {self.ip}")
                return False
            
            conf = atvs[0]
            self._device = await pyatv.connect(conf, loop=None)
            logger.info(f"Connected to AirPlay device: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to AirPlay device: {e}")
            return False
    
    async def play(self) -> bool:
        """Start playback"""
        if not self._device:
            return False
        try:
            await self._device.remote_control.play()
            self._is_playing = True
            return True
        except Exception as e:
            logger.error(f"AirPlay play failed: {e}")
            return False
    
    async def pause(self) -> bool:
        """Pause playback"""
        if not self._device:
            return False
        try:
            await self._device.remote_control.pause()
            self._is_playing = False
            return True
        except Exception as e:
            logger.error(f"AirPlay pause failed: {e}")
            return False
    
    async def set_volume(self, volume: int) -> bool:
        """Set volume (0-100)"""
        if not self._device:
            return False
        try:
            # AirPlay volume is 0-100
            await self._device.audio.set_volume(volume)
            self._volume = volume
            return True
        except Exception as e:
            logger.error(f"AirPlay set_volume failed: {e}")
            return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get device state"""
        return {
            "id": self.id,
            "name": self.name,
            "type": "airplay",
            "volume": self._volume,
            "is_playing": self._is_playing,
        }


class SonosDevice:
    """
    Sonos speaker
    Supports multi-room audio with native grouping
    """
    
    def __init__(
        self,
        device_id: str,
        name: str,
        ip: str,
    ):
        if not SOCO_AVAILABLE:
            raise RuntimeError("soco library not installed")
        
        self.id = device_id
        self.name = name
        self.ip = ip
        self._device: Optional[soco.SoCo] = None
        self._group_coordinator = None
    
    def connect(self) -> bool:
        """Connect to Sonos device"""
        try:
            self._device = soco.SoCo(self.ip)
            # Test connection
            _ = self._device.player_name
            logger.info(f"Connected to Sonos: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Sonos: {e}")
            return False
    
    def play(self) -> bool:
        """Start playback"""
        if not self._device:
            return False
        try:
            self._device.play()
            return True
        except Exception as e:
            logger.error(f"Sonos play failed: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause playback"""
        if not self._device:
            return False
        try:
            self._device.pause()
            return True
        except Exception as e:
            logger.error(f"Sonos pause failed: {e}")
            return False
    
    def set_volume(self, volume: int) -> bool:
        """Set volume (0-100)"""
        if not self._device:
            return False
        try:
            self._device.volume = volume
            return True
        except Exception as e:
            logger.error(f"Sonos set_volume failed: {e}")
            return False
    
    def join_group(self, coordinator_ip: str) -> bool:
        """Join another Sonos device's group"""
        if not self._device:
            return False
        try:
            coordinator = soco.SoCo(coordinator_ip)
            self._device.join(coordinator)
            self._group_coordinator = coordinator_ip
            logger.info(f"{self.name} joined group led by {coordinator_ip}")
            return True
        except Exception as e:
            logger.error(f"Sonos join failed: {e}")
            return False
    
    def leave_group(self) -> bool:
        """Leave current group"""
        if not self._device:
            return False
        try:
            self._device.unjoin()
            self._group_coordinator = None
            logger.info(f"{self.name} left group")
            return True
        except Exception as e:
            logger.error(f"Sonos unjoin failed: {e}")
            return False
    
    def get_group_members(self) -> List[str]:
        """Get all members in this device's group"""
        if not self._device:
            return []
        try:
            group = self._device.group
            return [member.ip_address for member in group.members]
        except Exception as e:
            logger.error(f"Failed to get group members: {e}")
            return []
    
    def is_coordinator(self) -> bool:
        """Check if this device is the group coordinator"""
        if not self._device:
            return False
        try:
            return self._device.is_coordinator
        except Exception as e:
            logger.error(f"Failed to check coordinator status: {e}")
            return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get device state"""
        if not self._device:
            return {
                "id": self.id,
                "name": self.name,
                "type": "sonos",
                "connected": False,
            }
        
        try:
            transport_info = self._device.get_current_transport_info()
            return {
                "id": self.id,
                "name": self.name,
                "type": "sonos",
                "volume": self._device.volume,
                "is_playing": transport_info['current_transport_state'] == 'PLAYING',
                "is_coordinator": self.is_coordinator(),
                "group_coordinator": self._group_coordinator,
                "group_members": self.get_group_members(),
            }
        except Exception as e:
            logger.error(f"Failed to get state: {e}")
            return {
                "id": self.id,
                "name": self.name,
                "type": "sonos",
                "error": str(e),
            }


class AudioGroupManager:
    """
    Manages audio groups (zones) for synchronized playback
    Works with AirPlay, Sonos, and other multi-room audio systems
    """
    
    def __init__(self):
        self.groups: Dict[str, AudioGroup] = {}
        self.devices: Dict[str, Any] = {}  # device_id → device instance
        logger.info("AudioGroupManager initialized")
    
    def register_device(self, device_id: str, device: Any):
        """Register an audio device"""
        self.devices[device_id] = device
        logger.info(f"Registered audio device: {device_id}")
    
    def create_group(
        self,
        group_name: str,
        coordinator_id: str,
        member_ids: Optional[List[str]] = None,
    ) -> Optional[AudioGroup]:
        """
        Create a new audio group
        
        Args:
            group_name: Name of the group
            coordinator_id: Device ID of the coordinator
            member_ids: List of member device IDs (optional)
        """
        if coordinator_id not in self.devices:
            logger.error(f"Coordinator device not found: {coordinator_id}")
            return None
        
        group_id = f"group_{len(self.groups) + 1}"
        group = AudioGroup(
            id=group_id,
            name=group_name,
            coordinator_device_id=coordinator_id,
            member_device_ids=member_ids or [],
        )
        
        self.groups[group_id] = group
        
        # For Sonos, perform actual grouping
        coordinator = self.devices[coordinator_id]
        if isinstance(coordinator, SonosDevice) and member_ids:
            for member_id in member_ids:
                member = self.devices.get(member_id)
                if isinstance(member, SonosDevice):
                    member.join_group(coordinator.ip)
        
        logger.info(f"Created audio group: {group_name} ({group_id})")
        return group
    
    def add_to_group(self, group_id: str, device_id: str) -> bool:
        """Add a device to an existing group"""
        group = self.groups.get(group_id)
        if not group:
            logger.error(f"Group not found: {group_id}")
            return False
        
        if device_id in group.member_device_ids:
            logger.warning(f"Device {device_id} already in group")
            return True
        
        device = self.devices.get(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            return False
        
        # For Sonos, perform actual join
        if isinstance(device, SonosDevice):
            coordinator = self.devices[group.coordinator_device_id]
            if isinstance(coordinator, SonosDevice):
                if device.join_group(coordinator.ip):
                    group.member_device_ids.append(device_id)
                    logger.info(f"Added {device_id} to group {group_id}")
                    return True
        else:
            # For other devices, just track in group
            group.member_device_ids.append(device_id)
            return True
        
        return False
    
    def remove_from_group(self, group_id: str, device_id: str) -> bool:
        """Remove a device from a group"""
        group = self.groups.get(group_id)
        if not group:
            logger.error(f"Group not found: {group_id}")
            return False
        
        if device_id not in group.member_device_ids:
            logger.warning(f"Device {device_id} not in group")
            return False
        
        device = self.devices.get(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            return False
        
        # For Sonos, perform actual unjoin
        if isinstance(device, SonosDevice):
            if device.leave_group():
                group.member_device_ids.remove(device_id)
                logger.info(f"Removed {device_id} from group {group_id}")
                return True
        else:
            group.member_device_ids.remove(device_id)
            return True
        
        return False
    
    def delete_group(self, group_id: str) -> bool:
        """Delete a group (ungroups all devices)"""
        group = self.groups.get(group_id)
        if not group:
            logger.error(f"Group not found: {group_id}")
            return False
        
        # Ungroup all members
        for device_id in group.member_device_ids[:]:  # Copy list
            self.remove_from_group(group_id, device_id)
        
        del self.groups[group_id]
        logger.info(f"Deleted group: {group_id}")
        return True
    
    def set_group_volume(self, group_id: str, volume: int) -> bool:
        """Set volume for entire group"""
        group = self.groups.get(group_id)
        if not group:
            return False
        
        success = True
        # Set coordinator volume
        coordinator = self.devices.get(group.coordinator_device_id)
        if coordinator:
            if isinstance(coordinator, SonosDevice):
                success &= coordinator.set_volume(volume)
            # AirPlay would need async
        
        # Set all member volumes
        for device_id in group.member_device_ids:
            device = self.devices.get(device_id)
            if device and isinstance(device, SonosDevice):
                success &= device.set_volume(volume)
        
        if success:
            group.volume = volume
        
        return success
    
    def play_group(self, group_id: str) -> bool:
        """Start playback on entire group"""
        group = self.groups.get(group_id)
        if not group:
            return False
        
        # Only need to play on coordinator for Sonos
        coordinator = self.devices.get(group.coordinator_device_id)
        if coordinator:
            if isinstance(coordinator, SonosDevice):
                success = coordinator.play()
                if success:
                    group.is_playing = True
                return success
        
        return False
    
    def pause_group(self, group_id: str) -> bool:
        """Pause playback on entire group"""
        group = self.groups.get(group_id)
        if not group:
            return False
        
        coordinator = self.devices.get(group.coordinator_device_id)
        if coordinator:
            if isinstance(coordinator, SonosDevice):
                success = coordinator.pause()
                if success:
                    group.is_playing = False
                return success
        
        return False
    
    def get_all_groups(self) -> List[AudioGroup]:
        """Get all audio groups"""
        return list(self.groups.values())
    
    def get_group_state(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get state of a group"""
        group = self.groups.get(group_id)
        if not group:
            return None
        
        return {
            "id": group.id,
            "name": group.name,
            "coordinator": group.coordinator_device_id,
            "members": group.member_device_ids,
            "volume": group.volume,
            "is_playing": group.is_playing,
            "current_source": group.current_source,
        }


# Configuration example
AUDIO_CONFIG_EXAMPLE = """
# audio_devices.yaml

audio_devices:
  # Sonos speakers
  - id: "sonos-living-room"
    type: "sonos"
    name: "Living Room Sonos"
    room_id: "living-room"
    ip: "192.168.1.70"
  
  - id: "sonos-kitchen"
    type: "sonos"
    name: "Kitchen Sonos"
    room_id: "kitchen"
    ip: "192.168.1.71"
  
  - id: "sonos-bedroom"
    type: "sonos"
    name: "Bedroom Sonos"
    room_id: "bedroom"
    ip: "192.168.1.72"
  
  # AirPlay speakers
  - id: "homepod-office"
    type: "airplay2"
    name: "Office HomePod"
    room_id: "office"
    ip: "192.168.1.80"
  
  - id: "homepod-mini-bathroom"
    type: "airplay2"
    name: "Bathroom HomePod Mini"
    room_id: "bathroom"
    ip: "192.168.1.81"

# Audio groups (zones)
audio_groups:
  - id: "downstairs"
    name: "Downstairs"
    coordinator: "sonos-living-room"
    members:
      - "sonos-kitchen"
    
  - id: "whole-house"
    name: "Whole House"
    coordinator: "sonos-living-room"
    members:
      - "sonos-kitchen"
      - "sonos-bedroom"
      - "homepod-office"
"""
