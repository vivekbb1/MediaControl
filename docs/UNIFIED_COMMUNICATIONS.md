# Unified Communications System

**SIP, Intercom, Paging, Audio/Video Doorbells, Access Control, Seamless Call Handoff**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [SIP Phone System](#sip-phone-system)
4. [Intercom System](#intercom-system)
5. [Paging System](#paging-system)
6. [Doorbell System](#doorbell-system)
7. [Access Control](#access-control)
8. [KVM Audio Integration](#kvm-audio-integration)
9. [Seamless Call Handoff](#seamless-call-handoff)
10. [Configuration](#configuration)
11. [API Reference](#api-reference)

---

## Overview

**MediaControl Unified Communications** is a complete enterprise-grade telecommunications system that integrates:

- **SIP VoIP Phone** - Room extensions, external calls
- **Intercom** - Room-to-room, building-wide communication
- **Paging** - Public address announcements (zones, all-call)
- **Doorbells** - Audio/video doorbells (multiple doors per location)
- **Access Control** - Smart locks, door strikes, gates
- **KVM Audio** - Use room microphone/speakers for all communication
- **Call Handoff** - Move calls between rooms/devices seamlessly

### Key Features

✅ **Multi-door support** - Front, back, garage, side entrance per location  
✅ **Unified audio** - All calls use KVM microphone/speakers  
✅ **Seamless handoff** - Move active calls between rooms without dropping  
✅ **Access control integration** - Unlock doors from any room  
✅ **Zone paging** - Announce to specific areas or entire building  
✅ **Call hold/resume** - Hold calls during transitions  
✅ **Device failover** - Automatic fallback if device unavailable  
✅ **Multi-tenant** - Separate systems per organization/location

---

## Architecture

### System Hierarchy

```
Organization
  └── Location (Building/Site)
       ├── Room (Zone with MediaControl Gateway)
       │    ├── KVM Audio (Microphone + Speakers)
       │    └── Communication Devices
       │         ├── SIP Extension (e.g., 301)
       │         ├── Intercom Station
       │         └── Paging Speaker
       │
       ├── Doorbells (Multiple per Location)
       │    ├── Front Door (Video Doorbell)
       │    ├── Back Door (Audio Doorbell)
       │    ├── Garage (Video Doorbell)
       │    └── Side Entrance (Audio Doorbell)
       │
       └── Access Control (Locks)
            ├── Front Door Lock (Smart Lock)
            ├── Back Door Lock (Door Strike)
            ├── Garage Door (Opener)
            └── Gate (Electric Gate)
```

### Communication Flow

```
┌─────────────────────────────────────────────────┐
│         Unified Communications Flow             │
│                                                 │
│  ┌──────────────┐    ┌──────────────┐         │
│  │  Room 301    │───▶│ PBX Server   │         │
│  │  (Conference)│◀───│ (SIP/Intercom│         │
│  │  KVM Audio   │    │  Controller) │         │
│  └──────────────┘    └──────────────┘         │
│         │                    │                  │
│         │                    ▼                  │
│         │           ┌──────────────┐           │
│         │           │  Front Door  │           │
│         │           │  (Doorbell)  │           │
│         │           └──────────────┘           │
│         │                    │                  │
│         └────────────────────┼─────────────┐   │
│                              │             │   │
│                              ▼             ▼   │
│                     ┌─────────────┐  ┌──────────┐
│                     │ Smart Lock  │  │ Paging   │
│                     │ (Z-Wave)    │  │ Speaker  │
│                     └─────────────┘  └──────────┘
│                                                 │
│  Call Flow:                                    │
│  1. Front doorbell pressed                     │
│  2. Video appears on all room displays         │
│  3. User in Room 301 answers via touch panel  │
│  4. Audio routed to Room 301 KVM mic/speakers │
│  5. User moves to Room 302 (call on hold)     │
│  6. Room 302 picks up call (seamless resume)  │
│  7. User unlocks front door from Room 302     │
└─────────────────────────────────────────────────┘
```

---

## SIP Phone System

### Features

✅ **Room extensions** - Each room has dedicated SIP extension  
✅ **External calls** - Call external numbers via SIP trunk  
✅ **Call transfer** - Transfer calls between rooms  
✅ **Call forwarding** - Forward to mobile when away  
✅ **Voicemail** - Per-room or shared voicemail  
✅ **Call park** - Park call, pick up from any room  
✅ **Conference calling** - Multi-party calls  
✅ **Call recording** - Optional recording for compliance

### Configuration

```yaml
sip_phone:
  enabled: true
  
  # PBX server
  pbx:
    server: "pbx.company.com"
    port: 5060
    transport: "udp"  # or "tcp", "tls"
    
  # Extensions (one per room)
  extensions:
    - extension_id: "301"
      room_id: "conference_room_a"
      display_name: "Conference Room A"
      password: "secure_password_301"
      
    - extension_id: "302"
      room_id: "conference_room_b"
      display_name: "Conference Room B"
      password: "secure_password_302"
      
    - extension_id: "303"
      room_id: "executive_office"
      display_name: "Executive Office"
      password: "secure_password_303"
  
  # Audio routing (use KVM audio)
  audio:
    use_kvm_audio: true  # Use room KVM mic/speakers
    
    # Fallback if KVM not available
    fallback_mic: "usb_mic_1"
    fallback_speaker: "hdmi_audio_out"
    
  # Call behavior
  call_behavior:
    auto_answer: false
    ring_duration: 30  # seconds
    call_waiting: true
    call_forwarding: true
    voicemail: true
    call_recording: false
```

---

## Intercom System

### Overview

**Intercom** enables room-to-room communication within a location without using phone extensions.

### Features

✅ **Room-to-room** - Call any room directly ("Intercom Room 302")  
✅ **All-call** - Broadcast to all rooms in location  
✅ **Zone-call** - Call specific zones (e.g., all conference rooms)  
✅ **Auto-answer** - Optional auto-answer for urgent announcements  
✅ **Push-to-talk** - Hold button to talk, release to listen  
✅ **Hands-free** - Full duplex audio (both sides talk simultaneously)  
✅ **Privacy mode** - Disable incoming intercom calls

### Use Cases

1. **Office:** "Intercom Reception: Client has arrived"
2. **School:** "Intercom All Classrooms: Fire drill in 5 minutes"
3. **Hospital:** "Intercom Nurse Station: Doctor needed in Room 405"
4. **Hotel:** "Intercom Housekeeping: Room 512 ready for cleaning"

### Configuration

```yaml
intercom:
  enabled: true
  
  # Intercom stations (one per room)
  stations:
    - station_id: "ic_301"
      room_id: "conference_room_a"
      name: "Conference Room A"
      auto_answer: false
      privacy_mode: false
      
    - station_id: "ic_302"
      room_id: "conference_room_b"
      name: "Conference Room B"
      auto_answer: false
      privacy_mode: false
      
    - station_id: "ic_reception"
      room_id: "reception"
      name: "Reception Desk"
      auto_answer: true  # Always answer (receptionist)
      privacy_mode: false
  
  # Audio routing
  audio:
    use_kvm_audio: true
    codec: "opus"  # High-quality audio codec
    sample_rate: 48000
    
  # Zones (for zone-call)
  zones:
    - zone_id: "conference_rooms"
      name: "All Conference Rooms"
      stations: ["ic_301", "ic_302"]
      
    - zone_id: "offices"
      name: "All Offices"
      stations: ["ic_executive", "ic_manager"]
      
    - zone_id: "all"
      name: "Entire Building"
      stations: ["ic_301", "ic_302", "ic_reception", "ic_executive", "ic_manager"]
  
  # Behavior
  behavior:
    mode: "hands_free"  # or "push_to_talk"
    ring_tone: "/sounds/intercom_chime.mp3"
    timeout: 60  # seconds (no answer)
```

---

## Paging System

### Overview

**Paging** (Public Address) broadcasts audio announcements to speakers throughout the building.

### Features

✅ **Zone paging** - Page specific zones (Floor 1, Floor 2, etc.)  
✅ **All-call paging** - Broadcast to entire building  
✅ **Emergency paging** - High-priority announcements (fire, lockdown)  
✅ **Scheduled announcements** - Automated announcements (lunch, closing time)  
✅ **Pre-recorded messages** - Upload and play pre-recorded messages  
✅ **Text-to-speech** - Convert text to speech for announcements  
✅ **Music on hold** - Background music between announcements

### Use Cases

1. **Corporate:** "Attention all employees: Town hall meeting in 10 minutes"
2. **School:** "All students report to the gymnasium for assembly"
3. **Hospital:** "Code Blue, Emergency Room. Code Blue, Emergency Room"
4. **Retail:** "Attention shoppers: Store closing in 15 minutes"
5. **Industrial:** "Shift change in 5 minutes. All personnel to break areas"

### Configuration

```yaml
paging:
  enabled: true
  
  # Paging zones
  zones:
    - zone_id: "floor_1"
      name: "Floor 1"
      speakers: ["speaker_101", "speaker_102", "speaker_103"]
      
    - zone_id: "floor_2"
      name: "Floor 2"
      speakers: ["speaker_201", "speaker_202", "speaker_203"]
      
    - zone_id: "outdoor"
      name: "Outdoor Areas"
      speakers: ["speaker_parking", "speaker_courtyard"]
      
    - zone_id: "all"
      name: "Entire Building"
      speakers: ["all"]
  
  # Paging speakers (IP-based or analog via audio gateway)
  speakers:
    - speaker_id: "speaker_101"
      name: "Lobby Speaker"
      type: "ip"  # or "analog"
      ip_address: "192.168.1.101"
      volume: 80  # 0-100
      
    - speaker_id: "speaker_102"
      name: "Conference Room A Speaker"
      type: "ip"
      ip_address: "192.168.1.102"
      volume: 70
  
  # Audio source
  audio_source:
    use_kvm_audio: true  # Use room mic for live paging
    
  # Scheduled announcements
  scheduled:
    - schedule_id: "lunch_announcement"
      enabled: true
      zones: ["all"]
      time: "12:00"
      days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
      message: "Attention: Lunch break. Cafeteria is now open."
      tts: true  # Text-to-speech
      
    - schedule_id: "closing_announcement"
      enabled: true
      zones: ["all"]
      time: "17:45"
      days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
      message: "Attention: Building closes in 15 minutes."
      tts: true
  
  # Emergency paging
  emergency:
    enabled: true
    priority: 100  # Interrupts all other audio
    zones: ["all"]  # Always broadcast to all zones
```

---

## Doorbell System

### Overview

**Multi-door support:** Each location can have multiple audio/video doorbells at different entrances.

### Supported Doorbell Types

#### 1. **Video Doorbell**
- Full video + audio
- Motion detection
- Night vision
- Recording
- Examples: Ring, Nest Hello, Arlo, UniFi Protect

#### 2. **Audio Doorbell**
- Audio only (two-way)
- More affordable
- Lower bandwidth
- Examples: Doorbird, Aiphone, generic SIP doorbell

### Features per Doorbell

✅ **Auto-popup** - Video/caller info appears on all room displays  
✅ **Multi-room answer** - Any room can answer doorbell  
✅ **Call routing** - Route to specific rooms (e.g., back door → kitchen)  
✅ **Recording** - Save all doorbell interactions  
✅ **Motion alerts** - Notify on motion detection  
✅ **Do Not Disturb** - Schedule quiet hours  
✅ **Access control** - Unlock associated door from call

### Configuration

```yaml
doorbells:
  enabled: true
  
  # Doorbells (multiple per location)
  devices:
    # Front Door (Video Doorbell)
    - doorbell_id: "front_door"
      name: "Front Door"
      type: "video"  # or "audio"
      location: "front_entrance"
      
      # Hardware
      hardware_type: "ring"  # "ring", "nest", "arlo", "unifi", "generic_rtsp", "sip"
      
      # Ring-specific config
      ring:
        device_id: "abc123"
        auth_token: "ring_auth_token"
      
      # Video stream
      stream:
        url: "rtsp://192.168.1.50/live"
        resolution: "1280x720"
        fps: 30
      
      # Associated access control
      access_control:
        lock_id: "front_door_lock"
        auto_unlock: false
      
      # Call routing
      routing:
        # Notify these rooms when doorbell pressed
        notify_rooms: ["reception", "conference_room_a", "executive_office"]
        # Default room to ring (if no answer, try others)
        default_room: "reception"
        ring_duration: 30  # seconds
      
      # Behavior
      behavior:
        auto_popup: true
        pip_mode: true
        pip_position: "bottom_right"
        play_chime: true
        record_on_press: true
        record_on_motion: true
      
      # Do Not Disturb
      dnd:
        enabled: false
        schedule:
          days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
          start_time: "09:00"
          end_time: "17:00"
    
    # Back Door (Audio Doorbell - cheaper)
    - doorbell_id: "back_door"
      name: "Back Door (Deliveries)"
      type: "audio"
      location: "back_entrance"
      
      # SIP-based audio doorbell
      hardware_type: "sip"
      sip:
        extension: "8001"  # Dedicated extension for doorbell
        server: "pbx.company.com"
        password: "doorbell_password"
      
      # Associated access control
      access_control:
        lock_id: "back_door_strike"
        auto_unlock: false
      
      # Call routing
      routing:
        notify_rooms: ["kitchen", "warehouse"]
        default_room: "warehouse"
        ring_duration: 30
      
      # Behavior
      behavior:
        play_chime: true
        record_on_press: true
    
    # Garage (Video Doorbell)
    - doorbell_id: "garage"
      name: "Garage Entrance"
      type: "video"
      location: "garage"
      
      hardware_type: "generic_rtsp"
      stream:
        url: "rtsp://192.168.1.52/stream"
      
      access_control:
        lock_id: "garage_door_opener"
        auto_unlock: false
      
      routing:
        notify_rooms: ["security_office"]
        default_room: "security_office"
    
    # Side Entrance (Audio Doorbell)
    - doorbell_id: "side_entrance"
      name: "Side Entrance (Employees)"
      type: "audio"
      location: "side_entrance"
      
      hardware_type: "sip"
      sip:
        extension: "8002"
      
      access_control:
        lock_id: "side_door_lock"
        auto_unlock: false  # Employees use badge
      
      routing:
        notify_rooms: ["security_office"]
  
  # Global settings
  global:
    max_ring_duration: 60  # seconds
    missed_call_notification: true
    missed_call_recipients: ["security@company.com"]
```

---

## Access Control

### Overview

**Access Control** integrates smart locks, door strikes, garage doors, and gates with the doorbell and intercom systems.

### Supported Lock Types

1. **Smart Locks** (Z-Wave, Zigbee, Wi-Fi)
   - August, Schlage, Yale, Kwikset
   
2. **Electric Door Strikes** (12V/24V)
   - Fail-secure (locked when power off)
   - Fail-safe (unlocked when power off)
   
3. **Magnetic Locks** (Maglocks)
   - 600 lbs - 1200 lbs holding force
   
4. **Garage Door Openers**
   - MyQ, LiftMaster, Chamberlain
   
5. **Electric Gates**
   - Gate operators with dry contact relay

### Features

✅ **Remote unlock** - Unlock from any room via touch panel  
✅ **Temporary access** - Grant time-limited access  
✅ **Access logs** - Track all lock/unlock events  
✅ **PIN codes** - Keypad entry codes  
✅ **Badge access** - RFID/NFC badge readers  
✅ **Automatic lock** - Auto-lock after delay  
✅ **Integration** - Unlock via doorbell call, intercom, or SIP call

### Configuration

```yaml
access_control:
  enabled: true
  
  # Locks/doors
  locks:
    - lock_id: "front_door_lock"
      name: "Front Door Lock"
      type: "smart_lock"  # "smart_lock", "door_strike", "maglock", "garage_door", "gate"
      
      # Smart lock (Z-Wave)
      hardware:
        protocol: "zwave"  # "zwave", "zigbee", "wifi", "ip", "relay"
        device_id: "zwave_node_5"
        
      # Behavior
      behavior:
        auto_lock: true
        auto_lock_delay: 30  # seconds after unlock
        unlock_duration: 5  # seconds (for door strikes)
        
      # Access methods
      access_methods:
        - method: "remote"  # Unlock via app/touch panel
          enabled: true
        - method: "pin"  # Keypad PIN codes
          enabled: true
        - method: "badge"  # RFID badge
          enabled: true
      
      # Associated doorbell
      doorbell_id: "front_door"
      
    - lock_id: "back_door_strike"
      name: "Back Door Strike"
      type: "door_strike"
      
      hardware:
        protocol: "relay"  # Dry contact relay
        relay_device: "relay_board_1"
        relay_channel: 1
        
      behavior:
        unlock_duration: 3  # seconds
        
    - lock_id: "garage_door_opener"
      name: "Garage Door"
      type: "garage_door"
      
      hardware:
        protocol: "ip"
        brand: "myq"
        ip_address: "192.168.1.100"
        api_token: "myq_token"
  
  # Access logs
  logging:
    enabled: true
    retention_days: 90
    log_events:
      - "unlock"
      - "lock"
      - "access_denied"
      - "forced_entry"  # Door opened without unlock
```

---

## KVM Audio Integration

### Overview

**KVM Audio** uses the room's KVM microphone and speakers for ALL communication types:
- SIP phone calls
- Intercom calls
- Doorbell calls
- Paging announcements

This provides a **unified audio experience** - users don't need to know which type of call it is, they just talk naturally.

### Benefits

✅ **Single microphone** - No separate desk phone, intercom mic, doorbell speaker  
✅ **Room-quality audio** - Professional ceiling mics, high-quality speakers  
✅ **Consistent experience** - All calls sound the same, same controls  
✅ **Hands-free** - No need to pick up handset  
✅ **Cost savings** - Eliminate separate audio hardware  
✅ **Echo cancellation** - Built-in acoustic echo cancellation  
✅ **Noise suppression** - AI-powered noise suppression from KVM

### Audio Routing

```
┌─────────────────────────────────────────────────┐
│         KVM Audio Routing                       │
│                                                 │
│  ┌──────────────┐                              │
│  │  KVM Audio   │                              │
│  │              │                              │
│  │ ┌──────────┐ │                              │
│  │ │   Mic    │ │  (Input)                     │
│  │ │  Array   │─┼──────────┐                   │
│  │ └──────────┘ │          │                   │
│  │              │          ▼                   │
│  │ ┌──────────┐ │   ┌──────────────┐          │
│  │ │ Speakers │◀┼───│ Audio Mixer  │          │
│  │ │ (Room)   │ │   │              │          │
│  │ └──────────┘ │   └──────┬───────┘          │
│  └──────────────┘          │                   │
│                             │                   │
│                    ┌────────┼────────┐         │
│                    │        │        │         │
│              ┌─────▼──┐ ┌──▼────┐ ┌─▼──────┐  │
│              │  SIP   │ │Intercom│ │Doorbell│  │
│              │  Call  │ │ Call  │ │  Call  │  │
│              └────────┘ └───────┘ └────────┘  │
│                                                 │
│  All communication types use same KVM audio    │
└─────────────────────────────────────────────────┘
```

### Configuration

```yaml
kvm_audio:
  enabled: true
  
  # Microphone
  microphone:
    device_id: "usb_mic_array_1"
    type: "array"  # "array", "single", "headset"
    channels: 4  # For beamforming
    sample_rate: 48000
    
    # Processing
    processing:
      echo_cancellation: true
      noise_suppression: true  # Use AI noise suppression
      gain: 0  # dB
      
  # Speakers
  speakers:
    device_id: "hdmi_audio_out"
    type: "ceiling"  # "ceiling", "desktop", "soundbar"
    channels: 2  # Stereo
    sample_rate: 48000
    volume: 70  # 0-100
    
  # Audio mixer (combines all sources)
  mixer:
    # Priorities (higher = more important)
    priorities:
      emergency_paging: 100
      doorbell: 90
      sip_call: 80
      intercom: 70
      paging: 60
      background_music: 10
    
    # Ducking (lower volume of lower-priority sources)
    ducking:
      enabled: true
      amount: -20  # dB (reduce by 20 dB)
```

---

## Seamless Call Handoff

### Overview

**Seamless Call Handoff** allows users to move between rooms while keeping calls active. The call is automatically held, then picked up in the new room without dropping.

### Use Cases

1. **Executive moves from office to conference room** - Call follows
2. **Nurse moves from desk to patient room** - Intercom call continues
3. **Security guard patrols building** - Doorbell call transfers to new location
4. **Teacher moves between classrooms** - Parent call doesn't drop

### How It Works

```
┌─────────────────────────────────────────────────┐
│         Call Handoff Flow                       │
│                                                 │
│  Room 301 (Active Call)                        │
│  ┌──────────────────────────────┐              │
│  │ Call with John Doe           │              │
│  │ Duration: 00:05:30           │              │
│  │                              │              │
│  │ User starts walking to Room 302              │
│  └──────────────────────────────┘              │
│         │                                       │
│         ▼                                       │
│  ┌──────────────────────────────┐              │
│  │ Call automatically HELD      │              │
│  │ "Please wait..."             │              │
│  │ (Music on hold plays)        │              │
│  └──────────────────────────────┘              │
│         │                                       │
│         ▼                                       │
│  Room 302 (Call waiting)                       │
│  ┌──────────────────────────────┐              │
│  │ 📞 Call on hold from Room 301│              │
│  │ [Pick Up] [Reject]           │              │
│  └──────────────────────────────┘              │
│         │                                       │
│         ▼ (User taps "Pick Up")                │
│  ┌──────────────────────────────┐              │
│  │ Call RESUMED                 │              │
│  │ John Doe                     │              │
│  │ Duration: 00:05:45           │              │
│  │ (Seamless continuation)      │              │
│  └──────────────────────────────┘              │
└─────────────────────────────────────────────────┘
```

### Handoff Methods

#### 1. **Manual Handoff**
- User taps "Hold & Transfer to Room 302" on touch panel
- Call placed on hold in Room 301
- Notification appears in Room 302
- User picks up in Room 302

#### 2. **Automatic Handoff (with badge/phone)**
- User wears RFID badge or carries phone with Bluetooth
- System detects user leaving Room 301
- Call automatically held
- System detects user entering Room 302
- Notification auto-appears: "Pick up call from Room 301?"

#### 3. **Follow-me Handoff**
- User enables "Follow Me" mode
- Calls automatically transfer to user's current location
- No manual pickup required

### Configuration

```yaml
call_handoff:
  enabled: true
  
  # Handoff methods
  methods:
    manual: true  # User-initiated handoff
    automatic: true  # Badge/phone detection
    follow_me: true  # Calls follow user
  
  # User tracking (for automatic handoff)
  user_tracking:
    enabled: true
    methods:
      - method: "badge"  # RFID badge
        enabled: true
      - method: "bluetooth"  # Phone Bluetooth
        enabled: true
      - method: "wifi"  # Wi-Fi triangulation
        enabled: false
  
  # Handoff behavior
  behavior:
    # Hold settings
    hold:
      music_on_hold: "/sounds/hold_music.mp3"
      hold_announcement: "Please wait while your call is transferred..."
      
    # Pickup settings
    pickup:
      auto_pickup: false  # Auto-pickup in new room (if Follow Me)
      pickup_timeout: 30  # seconds (if no answer, return to hold)
      
    # Fallback
    fallback:
      return_to_original_room: true  # If no pickup, return to Room 301
      forward_to_voicemail: true  # If still no answer
```

---

## Configuration

### Complete Unified Communications Configuration

```yaml
unified_communications:
  enabled: true
  location_id: "headquarters"
  
  # SIP Phone System
  sip_phone:
    enabled: true
    pbx:
      server: "pbx.company.com"
      port: 5060
    extensions:
      - extension_id: "301"
        room_id: "conference_room_a"
        display_name: "Conference Room A"
    audio:
      use_kvm_audio: true
  
  # Intercom System
  intercom:
    enabled: true
    stations:
      - station_id: "ic_301"
        room_id: "conference_room_a"
        name: "Conference Room A"
        auto_answer: false
    audio:
      use_kvm_audio: true
      codec: "opus"
    zones:
      - zone_id: "all"
        name: "Entire Building"
        stations: ["ic_301", "ic_302", "ic_reception"]
  
  # Paging System
  paging:
    enabled: true
    zones:
      - zone_id: "all"
        name: "Entire Building"
        speakers: ["all"]
    audio_source:
      use_kvm_audio: true
    scheduled:
      - schedule_id: "lunch"
        time: "12:00"
        zones: ["all"]
        message: "Lunch break. Cafeteria is open."
        tts: true
  
  # Doorbell System
  doorbells:
    enabled: true
    devices:
      - doorbell_id: "front_door"
        name: "Front Door"
        type: "video"
        hardware_type: "ring"
        access_control:
          lock_id: "front_door_lock"
        routing:
          notify_rooms: ["reception", "conference_room_a"]
          default_room: "reception"
        behavior:
          auto_popup: true
          pip_mode: true
          record_on_press: true
          
      - doorbell_id: "back_door"
        name: "Back Door"
        type: "audio"
        hardware_type: "sip"
        sip:
          extension: "8001"
        access_control:
          lock_id: "back_door_strike"
        routing:
          notify_rooms: ["warehouse"]
  
  # Access Control
  access_control:
    enabled: true
    locks:
      - lock_id: "front_door_lock"
        name: "Front Door Lock"
        type: "smart_lock"
        hardware:
          protocol: "zwave"
          device_id: "zwave_node_5"
        behavior:
          auto_lock: true
          auto_lock_delay: 30
        doorbell_id: "front_door"
        
      - lock_id: "back_door_strike"
        name: "Back Door Strike"
        type: "door_strike"
        hardware:
          protocol: "relay"
          relay_device: "relay_board_1"
          relay_channel: 1
        behavior:
          unlock_duration: 3
  
  # KVM Audio Integration
  kvm_audio:
    enabled: true
    microphone:
      device_id: "usb_mic_array_1"
      type: "array"
      channels: 4
      processing:
        echo_cancellation: true
        noise_suppression: true
    speakers:
      device_id: "hdmi_audio_out"
      type: "ceiling"
      volume: 70
    mixer:
      priorities:
        emergency_paging: 100
        doorbell: 90
        sip_call: 80
        intercom: 70
        paging: 60
  
  # Seamless Call Handoff
  call_handoff:
    enabled: true
    methods:
      manual: true
      automatic: true
      follow_me: true
    user_tracking:
      enabled: true
      methods:
        - method: "badge"
          enabled: true
        - method: "bluetooth"
          enabled: true
    behavior:
      hold:
        music_on_hold: "/sounds/hold_music.mp3"
      pickup:
        auto_pickup: false
        pickup_timeout: 30
```

---

## API Reference

### SIP Phone API

```http
# Make external call
POST /api/unified-comms/sip/call
{
  "room_id": "conference_room_a",
  "destination": "+1-555-123-4567"
}

# Transfer call to another room
POST /api/unified-comms/sip/transfer
{
  "call_id": "call_abc123",
  "from_room": "conference_room_a",
  "to_room": "conference_room_b"
}
```

### Intercom API

```http
# Call another room
POST /api/unified-comms/intercom/call
{
  "from_room": "conference_room_a",
  "to_room": "reception"
}

# All-call (broadcast to all rooms)
POST /api/unified-comms/intercom/all-call
{
  "from_room": "reception",
  "message": "Meeting in 5 minutes"
}

# Zone-call (broadcast to zone)
POST /api/unified-comms/intercom/zone-call
{
  "from_room": "reception",
  "zone_id": "conference_rooms",
  "message": "All conference rooms reserved for training"
}
```

### Paging API

```http
# Live paging announcement
POST /api/unified-comms/paging/announce
{
  "zones": ["all"],
  "message": "Attention: Building evacuation drill in progress"
}

# Text-to-speech announcement
POST /api/unified-comms/paging/tts
{
  "zones": ["floor_1"],
  "text": "Lunch break. Cafeteria is now open.",
  "voice": "en-US-female"
}

# Play pre-recorded message
POST /api/unified-comms/paging/play
{
  "zones": ["all"],
  "audio_file": "/announcements/fire_drill.mp3"
}
```

### Doorbell API

```http
# Get all doorbells for location
GET /api/unified-comms/doorbells?location_id=headquarters

Response:
{
  "doorbells": [
    {
      "doorbell_id": "front_door",
      "name": "Front Door",
      "type": "video",
      "online": true,
      "last_activity": "2026-07-31T09:30:00Z"
    },
    {
      "doorbell_id": "back_door",
      "name": "Back Door",
      "type": "audio",
      "online": true,
      "last_activity": "2026-07-31T08:45:00Z"
    }
  ]
}

# Answer doorbell from specific room
POST /api/unified-comms/doorbells/answer
{
  "doorbell_id": "front_door",
  "room_id": "reception"
}

# Unlock door from doorbell call
POST /api/unified-comms/doorbells/unlock
{
  "doorbell_id": "front_door"
}
```

### Access Control API

```http
# Unlock door
POST /api/unified-comms/access-control/unlock
{
  "lock_id": "front_door_lock",
  "duration": 5  # seconds (optional, for door strikes)
}

# Get access logs
GET /api/unified-comms/access-control/logs?lock_id=front_door_lock&days=7

Response:
{
  "logs": [
    {
      "timestamp": "2026-07-31T09:30:00Z",
      "lock_id": "front_door_lock",
      "event": "unlock",
      "method": "remote",
      "user": "John Doe",
      "room": "reception"
    }
  ]
}
```

### Call Handoff API

```http
# Hold and transfer call
POST /api/unified-comms/handoff/hold-transfer
{
  "call_id": "call_abc123",
  "from_room": "conference_room_a",
  "to_room": "conference_room_b"
}

# Pick up held call in new room
POST /api/unified-comms/handoff/pickup
{
  "call_id": "call_abc123",
  "room_id": "conference_room_b"
}

# Enable Follow Me mode
POST /api/unified-comms/handoff/follow-me
{
  "user_id": "john.doe",
  "enabled": true,
  "badge_id": "badge_12345"
}
```

---

## Use Cases

### 1. Multi-Family Home

**Setup:**
- 3 video doorbells (front, back, garage)
- 1 audio doorbell (side entrance)
- 5 rooms with MediaControl gateways
- Smart locks on all doors

**Workflow:**
1. Front doorbell rings (delivery)
2. Video appears on all TVs in house
3. Homeowner in bedroom answers via bedroom touch panel
4. Two-way audio via bedroom KVM speakers/mic
5. Homeowner sees it's legitimate delivery
6. Unlocks front door from bedroom
7. Delivery person leaves package, door auto-locks after 30 seconds

---

### 2. Corporate Office

**Setup:**
- 2 video doorbells (main entrance, executive entrance)
- 20 rooms with SIP extensions (200-219)
- Intercom system (all rooms)
- Paging system (4 zones: Floor 1, Floor 2, Outdoor, All)
- Access control (10 smart locks)

**Workflow:**
1. **Morning:** Receptionist uses paging to announce: "Good morning. All-hands meeting in 10 minutes"
2. **Mid-day:** Main entrance doorbell rings (client arrival)
   - Video appears on reception display
   - Receptionist answers via intercom
   - Unlocks main door remotely
3. **Afternoon:** Executive on SIP call in office (ext 200)
   - Needs to move to conference room for presentation
   - Taps "Hold & Transfer to Room 210" on touch panel
   - Walks to conference room
   - Call notification appears on conference room display
   - Picks up call seamlessly, continues conversation
4. **End of day:** Scheduled paging announcement: "Building closes in 15 minutes"

---

### 3. Hospital

**Setup:**
- 4 video doorbells (ER entrance, main entrance, staff entrance, loading dock)
- 100+ rooms with intercom (patient rooms, nurse stations, labs)
- Emergency paging system
- SIP phone system (extensions 1000-1999)
- Badge-based call handoff (nurses wear RFID badges)

**Workflow:**
1. **Emergency:** "Code Blue" emergency paging to all zones
2. **Nurse rounds:** Nurse at nurse station (ext 1500)
   - Receives intercom call from patient room 405
   - Answers via KVM speakers in nurse station
   - Patient reports issue
   - Nurse starts walking to room 405
   - Call automatically held (badge detected leaving station)
   - Call automatically picked up when nurse enters room 405
   - Seamless conversation continuation
3. **Visitor:** Main entrance doorbell rings
   - Security answers from security office
   - Verifies visitor identity via video
   - Unlocks main entrance remotely

---

## Best Practices

### Doorbell Placement

✅ **Front door:** Always video doorbell (primary entrance)  
✅ **Back door:** Audio doorbell (service/delivery entrance) - saves cost  
✅ **Garage:** Video doorbell (security for vehicle access)  
✅ **Side entrance:** Audio doorbell (employee entrance) - badge access primary  

### Audio Quality

✅ **Use KVM audio** for consistent experience  
✅ **Enable echo cancellation** (critical for hands-free)  
✅ **Enable AI noise suppression** (remove background noise)  
✅ **Test audio** in all rooms before deployment  

### Call Handoff

✅ **Enable manual handoff** (always safe)  
✅ **Enable automatic handoff** only for mobile staff (nurses, security)  
✅ **Test badge/Bluetooth** tracking before enabling Follow Me  
✅ **Set reasonable pickup timeout** (30s recommended)  

### Access Control

✅ **Enable auto-lock** on all doors (security)  
✅ **Set appropriate unlock duration** (door strikes: 3-5s)  
✅ **Log all access events** (compliance, security)  
✅ **Regular audits** of access logs  

---

## Troubleshooting

### Doorbell Not Ringing

**Check:**
1. Doorbell online? (check network connection)
2. Routing configured? (notify_rooms set correctly)
3. Do Not Disturb enabled? (check schedule)
4. Audio/video stream accessible? (test stream URL)

### Intercom Echo/Feedback

**Solutions:**
1. Enable echo cancellation in KVM audio config
2. Reduce speaker volume
3. Ensure microphone not too close to speakers
4. Use directional microphone (beamforming array)

### Call Handoff Fails

**Check:**
1. User tracking enabled?
2. Badge/Bluetooth detected? (check signal strength)
3. Target room online?
4. Pickup timeout too short? (increase to 60s)

### Access Control Not Unlocking

**Check:**
1. Lock online? (power, network)
2. Lock protocol correct? (Z-Wave, Zigbee, relay)
3. Unlock duration sufficient? (door strikes need 3-5s)
4. Battery low? (smart locks)

---

**For unified communications deployments:**  
**Contact:** telecom@mediacontrol.com  
**Support:** https://mediacontrol.com/support/unified-comms
