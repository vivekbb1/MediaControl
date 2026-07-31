# AUDIO DEVICES GUIDE

Complete guide for integrating and controlling AirPlay speakers and Sonos devices

## Overview

This guide covers integration of audio devices:
- **AirPlay/AirPlay 2 Speakers**: Network-based control via `pyatv`
- **Sonos Devices**: Control and grouping via `soco` library
- **Audio Grouping**: Create synchronized multi-room audio zones

## Supported Features

### AirPlay Speakers
- ✅ Play/pause/stop
- ✅ Volume control
- ✅ Track information
- ✅ Next/previous track
- ✅ Discovery via Bonjour/mDNS
- ✅ Multiple speaker support
- ⚠️ Grouping (AirPlay 2 only, limited support)

### Sonos Devices
- ✅ Play/pause/stop
- ✅ Volume control
- ✅ Track information
- ✅ Queue management
- ✅ Favorite playlists
- ✅ Native Sonos grouping/ungrouping
- ✅ Multi-room sync
- ✅ Discovery via SSDP

## Installation

### Python Dependencies

```bash
# Install pyatv for AirPlay support
pip install pyatv>=0.14.0

# Install soco for Sonos support
pip install soco>=0.30.0
```

### System Requirements

**For AirPlay:**
- Network access to AirPlay devices
- mDNS/Bonjour enabled on network
- Same subnet as AirPlay devices (or mDNS reflector configured)

**For Sonos:**
- Network access to Sonos devices
- SSDP/UPnP enabled on network
- Same subnet as Sonos devices

## Configuration

### YAML Configuration Example

```yaml
# displays.yaml

audio_devices:
  # AirPlay Speakers
  living_room_homepod:
    device_type: airplay
    name: "Living Room HomePod"
    identifier: "AA:BB:CC:DD:EE:FF"  # MAC address or device ID
    # Optional: IP address (for faster connection)
    host: "192.168.1.150"
    
  bedroom_airplay:
    device_type: airplay
    name: "Bedroom AirPlay 2"
    identifier: "11:22:33:44:55:66"
    host: "192.168.1.151"
  
  # Sonos Devices
  kitchen_sonos:
    device_type: sonos
    name: "Kitchen Sonos One"
    host: "192.168.1.160"  # Required for Sonos
    
  dining_sonos:
    device_type: sonos
    name: "Dining Room Sonos"
    host: "192.168.1.161"
    
  patio_sonos:
    device_type: sonos
    name: "Patio Sonos Move"
    host: "192.168.1.162"

# Audio Groups (presets)
audio_groups:
  whole_house:
    name: "Whole House Audio"
    devices:
      - living_room_homepod
      - bedroom_airplay
      - kitchen_sonos
      - dining_sonos
      - patio_sonos
      
  indoor_only:
    name: "Indoor Audio"
    devices:
      - living_room_homepod
      - bedroom_airplay
      - kitchen_sonos
      - dining_sonos
      
  sonos_only:
    name: "Sonos Group"
    devices:
      - kitchen_sonos
      - dining_sonos
      - patio_sonos
```

### Python Configuration

```python
from audio_devices import AirPlaySpeaker, SonosDevice, AudioGroupManager

# Initialize audio manager
audio_mgr = AudioGroupManager()

# Add AirPlay speakers
living_room = AirPlaySpeaker(
    device_id="living_room_homepod",
    name="Living Room HomePod",
    identifier="AA:BB:CC:DD:EE:FF"
)
audio_mgr.register_device(living_room)

# Add Sonos devices
kitchen_sonos = SonosDevice(
    device_id="kitchen_sonos",
    name="Kitchen Sonos One",
    host="192.168.1.160"
)
audio_mgr.register_device(kitchen_sonos)

dining_sonos = SonosDevice(
    device_id="dining_sonos",
    name="Dining Room Sonos",
    host="192.168.1.161"
)
audio_mgr.register_device(dining_sonos)
```

## Usage

### Individual Device Control

#### AirPlay Speaker
```python
import asyncio
from audio_devices import AirPlaySpeaker

async def control_airplay():
    speaker = AirPlaySpeaker(
        device_id="living_room",
        name="Living Room HomePod",
        identifier="AA:BB:CC:DD:EE:FF"
    )
    
    # Connect
    await speaker.connect()
    
    # Play
    await speaker.play()
    
    # Pause
    await speaker.pause()
    
    # Set volume (0-100)
    await speaker.set_volume(50)
    
    # Skip track
    await speaker.next_track()
    
    # Disconnect
    await speaker.disconnect()

asyncio.run(control_airplay())
```

#### Sonos Device
```python
from audio_devices import SonosDevice

# Create device
sonos = SonosDevice(
    device_id="kitchen",
    name="Kitchen Sonos",
    host="192.168.1.160"
)

# Connect
sonos.connect()

# Play
sonos.play()

# Pause
sonos.pause()

# Set volume (0-100)
sonos.set_volume(60)

# Play favorite
sonos.play_favorite("My Spotify Playlist")

# Disconnect
sonos.disconnect()
```

### Audio Grouping

#### Create a Group (Sonos-only)
```python
# Create Sonos group
group_id = audio_mgr.create_group(
    group_name="Kitchen + Dining",
    device_ids=["kitchen_sonos", "dining_sonos"]
)

# Control the group
audio_mgr.play_group(group_id)
audio_mgr.set_group_volume(group_id, 70)
audio_mgr.pause_group(group_id)
```

#### Add Device to Existing Group
```python
# Add patio to the group
audio_mgr.add_to_group(group_id, "patio_sonos")
```

#### Remove Device from Group
```python
# Remove patio from the group
audio_mgr.remove_from_group(group_id, "patio_sonos")
```

#### Ungroup All
```python
# Break up the group
audio_mgr.ungroup(group_id)
```

### Mixed Groups (AirPlay + Sonos)
```python
# Mixed groups control devices independently
# (No native sync, but commands sent to all devices)

group_id = audio_mgr.create_group(
    group_name="Whole House",
    device_ids=[
        "living_room_homepod",
        "bedroom_airplay",
        "kitchen_sonos",
        "dining_sonos"
    ]
)

# Play on all devices
# Note: No audio sync between AirPlay and Sonos
audio_mgr.play_group(group_id)
```

## API Integration

### REST API Endpoints

```python
# Flask/FastAPI example

@app.post("/api/v1/audio/{device_id}/play")
async def play_audio(device_id: str):
    """Play audio on device"""
    device = audio_mgr.get_device(device_id)
    if not device:
        return {"error": "Device not found"}, 404
    
    if isinstance(device, AirPlaySpeaker):
        await device.play()
    else:
        device.play()
    
    return {"success": True}

@app.post("/api/v1/audio/{device_id}/volume")
async def set_volume(device_id: str, volume: int):
    """Set device volume"""
    device = audio_mgr.get_device(device_id)
    if not device:
        return {"error": "Device not found"}, 404
    
    if isinstance(device, AirPlaySpeaker):
        await device.set_volume(volume)
    else:
        device.set_volume(volume)
    
    return {"success": True, "volume": volume}

@app.post("/api/v1/audio/groups")
def create_audio_group(group_name: str, device_ids: List[str]):
    """Create audio group"""
    group_id = audio_mgr.create_group(group_name, device_ids)
    return {"group_id": group_id, "devices": device_ids}

@app.post("/api/v1/audio/groups/{group_id}/play")
def play_group(group_id: str):
    """Play audio group"""
    audio_mgr.play_group(group_id)
    return {"success": True}

@app.delete("/api/v1/audio/groups/{group_id}")
def ungroup(group_id: str):
    """Ungroup audio devices"""
    audio_mgr.ungroup(group_id)
    return {"success": True}
```

## Frontend Integration

### React Component Example

```typescript
// AudioControls.tsx
import React, { useState } from 'react';

interface AudioDevice {
  id: string;
  name: string;
  type: 'airplay' | 'sonos';
  playing: boolean;
  volume: number;
}

export const AudioControls: React.FC<{ device: AudioDevice }> = ({ device }) => {
  const [volume, setVolume] = useState(device.volume);
  
  const playPause = async () => {
    const endpoint = device.playing ? 'pause' : 'play';
    await fetch(`/api/v1/audio/${device.id}/${endpoint}`, { method: 'POST' });
  };
  
  const changeVolume = async (newVolume: number) => {
    setVolume(newVolume);
    await fetch(`/api/v1/audio/${device.id}/volume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ volume: newVolume })
    });
  };
  
  return (
    <div className="audio-device">
      <h3>{device.name}</h3>
      <button onClick={playPause}>
        {device.playing ? '⏸ Pause' : '▶ Play'}
      </button>
      <input
        type="range"
        min="0"
        max="100"
        value={volume}
        onChange={(e) => changeVolume(parseInt(e.target.value))}
      />
      <span>{volume}%</span>
    </div>
  );
};

// AudioGroupManager.tsx
export const AudioGroupManager: React.FC = () => {
  const [devices, setDevices] = useState<AudioDevice[]>([]);
  const [selectedDevices, setSelectedDevices] = useState<string[]>([]);
  
  const createGroup = async () => {
    const response = await fetch('/api/v1/audio/groups', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        group_name: "Custom Group",
        device_ids: selectedDevices
      })
    });
    
    const data = await response.json();
    console.log('Group created:', data.group_id);
  };
  
  return (
    <div className="audio-group-manager">
      <h2>Create Audio Group</h2>
      {devices.map(device => (
        <label key={device.id}>
          <input
            type="checkbox"
            checked={selectedDevices.includes(device.id)}
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedDevices([...selectedDevices, device.id]);
              } else {
                setSelectedDevices(selectedDevices.filter(id => id !== device.id));
              }
            }}
          />
          {device.name}
        </label>
      ))}
      <button onClick={createGroup}>Create Group</button>
    </div>
  );
};
```

## Troubleshooting

### AirPlay Issues

**Device not discovered:**
- Ensure devices are on same network/subnet
- Check mDNS/Bonjour is enabled
- Verify firewall allows UDP port 5353 (mDNS)
- Try manual IP address configuration

**Connection timeouts:**
- Verify network connectivity
- Check AirPlay device is powered on
- Ensure no VLANs blocking traffic
- Try restarting the device

**Authentication errors:**
- Some AirPlay 2 devices require pairing
- Use `pyatv` CLI to pair: `atvremote --scan`
- Store pairing credentials in configuration

### Sonos Issues

**Device not found:**
- Verify IP address is correct
- Check SSDP/UPnP is enabled on network
- Ensure firewall allows TCP port 1400
- Try discovery: `soco.discovery.any_soco()`

**Grouping fails:**
- Only Sonos devices can be grouped together
- Ensure all devices are on same Sonos system
- Check devices have latest firmware
- Try ungrouping all first, then regroup

**Playback not synchronized:**
- This is expected for mixed AirPlay + Sonos groups
- Use Sonos-only groups for perfect sync
- Consider Sonos Port for connecting AirPlay sources

## Best Practices

1. **Device Discovery:**
   - Cache discovered devices
   - Refresh periodically (every 5-10 minutes)
   - Allow manual IP configuration as fallback

2. **Error Handling:**
   - Implement retries for network failures
   - Handle device offline gracefully
   - Show user-friendly error messages

3. **Performance:**
   - Keep connections open for frequently used devices
   - Use async for AirPlay operations
   - Batch group operations when possible

4. **User Experience:**
   - Show device status (online/offline, playing/paused)
   - Display current track information
   - Provide visual feedback for volume changes
   - Auto-refresh device list

## Integration with Room Presets

```yaml
# displays.yaml
presets:
  movie_night:
    name: "Movie Night"
    actions:
      - type: display_power
        device: main_tv
        state: on
      - type: display_input
        device: main_tv
        input: HDMI1
      - type: source_power
        device: apple_tv
        state: on
      - type: source_app
        device: apple_tv
        app: Netflix
      # Audio actions
      - type: audio_group
        name: "Living Room Audio"
        devices: [soundbar_sonos, rear_speakers_sonos]
      - type: audio_play
        group: "Living Room Audio"
      - type: audio_volume
        group: "Living Room Audio"
        volume: 60
        
  party_mode:
    name: "Party Mode"
    actions:
      - type: audio_group
        name: "Whole House"
        devices: [kitchen_sonos, living_room_sonos, patio_sonos, bedroom_homepod]
      - type: audio_play
        group: "Whole House"
      - type: audio_volume
        group: "Whole House"
        volume: 70
```

## Advanced Features

### Dynamic Volume Leveling
```python
# Automatically balance volume across grouped devices
async def level_group_volumes(group_id: str, target_volume: int):
    group = audio_mgr.get_group(group_id)
    
    for device_id in group.device_ids:
        device = audio_mgr.get_device(device_id)
        
        # AirPlay devices might need async
        if isinstance(device, AirPlaySpeaker):
            await device.set_volume(target_volume)
        else:
            device.set_volume(target_volume)
```

### Playlist Management (Sonos)
```python
# Play Sonos playlist
sonos = audio_mgr.get_device("kitchen_sonos")
sonos.play_favorite("Dinner Jazz")

# Add to queue
sonos.add_to_queue("spotify:track:123456")
```

### Track Information
```python
# Get what's playing (Sonos)
track_info = sonos.get_current_track_info()
print(f"Now playing: {track_info['title']} by {track_info['artist']}")

# Get what's playing (AirPlay)
await airplay.update()
print(f"Now playing: {airplay.metadata}")
```

## Summary

The audio integration provides:
- ✅ Unified control for AirPlay and Sonos
- ✅ Native Sonos grouping for perfect sync
- ✅ Mixed groups for whole-house control
- ✅ REST API for remote control
- ✅ Integration with room presets
- ✅ Volume management across devices
- ✅ Playback control (play/pause/next/previous)

This enables complete audio control alongside video/display management for a truly integrated smart multimedia system.
