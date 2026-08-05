# Smart Home Ecosystem Integration

**Ubiquiti Access, Aqara, Nuki, Home Assistant, Matter, Zigbee**

---

## Table of Contents

1. [Overview](#overview)
2. [Ubiquiti Access Integration](#ubiquiti-access-integration)
3. [Aqara Doorbell Integration](#aqara-doorbell-integration)
4. [Nuki Smart Lock Integration](#nuki-smart-lock-integration)
5. [Home Assistant Integration](#home-assistant-integration)
6. [Matter Protocol Support](#matter-protocol-support)
7. [Zigbee Integration](#zigbee-integration)
8. [Configuration](#configuration)
9. [API Reference](#api-reference)

---

## Overview

**MediaControl Smart Home Ecosystem Integration** provides bidirectional communication with popular smart home platforms and protocols:

- **Ubiquiti Access** - Enterprise-grade access control, door locks, card readers
- **Aqara** - Affordable smart home devices (doorbells, locks, sensors)
- **Nuki** - Premium European smart locks with proven reliability
- **Home Assistant** - Open-source home automation hub (bidirectional)
- **Matter** - Universal smart home standard (Apple, Google, Amazon)
- **Zigbee** - Low-power mesh network protocol (bidirectional)

### Bidirectional Integration

**MediaControl → Smart Home:**
- Control locks from MediaControl interface
- Trigger doorbell notifications
- Manage access codes
- View live video feeds

**Smart Home → MediaControl:**
- Lock/unlock events trigger MediaControl actions
- Doorbell presses show on MediaControl displays
- Sensor data influences MediaControl automation
- Home Assistant automations control MediaControl

---

## Ubiquiti Access Integration

### Overview

**Ubiquiti Access** is an enterprise-grade access control system with:
- Door locks (smart locks, electric strikes, maglocks)
- Door readers (NFC, RFID, QR code, PIN)
- Door controllers (network-connected)
- Access management (UniFi Protect integration)

### Supported Devices

#### 1. **UA Hub** (Door Controller)
- Network-connected hub for access control
- Supports 4-8 doors per hub
- PoE powered
- Web-based management

#### 2. **UA Reader Pro** (Door Reader)
- NFC, RFID (13.56 MHz)
- PIN code entry
- QR code scanning
- Bluetooth unlock (via UniFi app)
- Built-in camera (takes photo on entry)

#### 3. **UA Lite** (Affordable Reader)
- NFC, RFID only
- No PIN, no camera
- More affordable option

#### 4. **UA-G2-Pro** (Smart Lock)
- Motorized deadbolt
- Battery-powered (6-12 months)
- Remote unlock
- Auto-lock

#### 5. **Electric Strikes / Maglocks**
- Wired to UA Hub
- Fail-safe or fail-secure
- Multiple brands supported

### Integration Architecture

```
┌─────────────────────────────────────────────────┐
│         Ubiquiti Access Integration             │
│                                                 │
│  ┌──────────────┐         ┌──────────────┐     │
│  │MediaControl  │◀───────▶│ UA Hub       │     │
│  │Gateway       │  API    │ (Controller) │     │
│  └──────────────┘         └──────┬───────┘     │
│         │                        │             │
│         │ (Bidirectional)        ▼             │
│         │                 ┌──────────────┐     │
│         │                 │ UA Reader Pro│     │
│         │                 │ (Front Door) │     │
│         │                 └──────┬───────┘     │
│         │                        │             │
│         │                        ▼             │
│         │                 ┌──────────────┐     │
│         │                 │ UA-G2-Pro    │     │
│         │                 │ (Smart Lock) │     │
│         │                 └──────────────┘     │
│         │                                       │
│  Events from Ubiquiti → MediaControl:          │
│  • Card scanned (trigger display update)       │
│  • Door unlocked (show notification)           │
│  • Door forced open (alarm on display)         │
│                                                 │
│  Commands from MediaControl → Ubiquiti:        │
│  • Unlock door (remote unlock)                 │
│  • Grant temporary access (time-limited)       │
│  • Disable reader (lockdown)                   │
└─────────────────────────────────────────────────┘
```

### Configuration

```yaml
ubiquiti_access:
  enabled: true
  
  # UA Hub connection
  hub:
    host: "192.168.1.100"  # UA Hub IP address
    port: 12445  # UniFi Access API port
    api_key: "your_api_key_here"
    site: "default"  # UniFi site name
    
  # Doors
  doors:
    - door_id: "front_door"
      name: "Front Door"
      ua_door_id: "5f8a1b2c3d4e5f6g"  # UA Hub door ID
      
      # Associated MediaControl doorbell
      doorbell_id: "front_door"
      
      # Access control
      access_control:
        auto_lock: true
        auto_lock_delay: 30  # seconds
        unlock_duration: 5  # seconds
        
      # Notifications
      notifications:
        show_on_display: true
        play_chime: true
        
    - door_id: "back_door"
      name: "Back Door (Employees)"
      ua_door_id: "5f8a1b2c3d4e5f6h"
  
  # Readers
  readers:
    - reader_id: "front_door_reader"
      name: "Front Door Reader Pro"
      ua_reader_id: "5f8a1b2c3d4e5f6i"
      type: "ua_reader_pro"  # or "ua_lite"
      
      # Features
      features:
        nfc: true
        rfid: true
        pin: true
        qr_code: true
        bluetooth: true
        camera: true  # Takes photo on entry
  
  # Events to monitor
  events:
    - event: "door_unlocked"
      action: "show_notification"
      
    - event: "card_scanned"
      action: "log_access"
      
    - event: "door_forced_open"
      action: "trigger_alarm"
      
    - event: "invalid_card"
      action: "show_warning"
  
  # Access management
  access:
    # Sync MediaControl users with UA Access
    sync_users: true
    
    # Grant temporary access via MediaControl
    temporary_access: true
```

### API Integration

```python
# MediaControl → Ubiquiti Access
POST https://ua-hub-ip:12445/api/access/v1/door/{door_id}/unlock
Headers:
  X-API-Key: your_api_key

# Ubiquiti Access → MediaControl (Webhook)
POST http://mediacontrol-gateway-ip:8080/api/ubiquiti/webhook
{
  "event": "door_unlocked",
  "door_id": "5f8a1b2c3d4e5f6g",
  "user": "John Doe",
  "method": "nfc_card",
  "timestamp": "2026-07-31T09:50:00Z"
}
```

---

## Aqara Doorbell Integration

### Overview

**Aqara** is part of the Xiaomi smart home ecosystem, offering affordable devices:
- Video doorbells (battery or wired)
- Smart locks (Bluetooth, Zigbee)
- Door/window sensors
- Motion sensors
- Hub integration (Aqara Hub M2, M3)

### Supported Devices

#### 1. **Aqara Video Doorbell G4** (Battery-Powered)
- 1080p HD video
- 162° wide-angle
- Night vision
- Two-way audio
- PIR motion detection
- Battery: 3-6 months
- WiFi or Zigbee (requires Aqara Hub)

#### 2. **Aqara Video Doorbell G220** (Wired)
- 2K video (2304×1296)
- 180° ultra-wide angle
- HDR night vision
- Local storage (microSD)
- PoE support
- WiFi

#### 3. **Aqara Smart Lock U100** (Zigbee)
- Fingerprint (50 users)
- NFC cards (100 cards)
- PIN codes (unlimited)
- Bluetooth unlock (via Aqara app)
- Zigbee 3.0 (requires Aqara Hub)
- Battery: 8-12 months

#### 4. **Aqara Hub M2 / M3**
- Zigbee 3.0 hub
- WiFi bridge
- Ethernet (M3 only)
- Local automation
- Works with Apple HomeKit, Google Home, Amazon Alexa

### Integration Architecture

```
┌─────────────────────────────────────────────────┐
│         Aqara Integration                       │
│                                                 │
│  ┌──────────────┐         ┌──────────────┐     │
│  │MediaControl  │◀───────▶│ Aqara Hub M3 │     │
│  │Gateway       │  MQTT   │ (Zigbee Hub) │     │
│  └──────────────┘         └──────┬───────┘     │
│         │                        │             │
│         │                   Zigbee 3.0         │
│         │                        │             │
│         │              ┌─────────┼─────────┐   │
│         │              │         │         │   │
│         │         ┌────▼───┐ ┌──▼────┐ ┌──▼──┐│
│         │         │Doorbell│ │ Lock  │ │Sensor││
│         │         │ G4     │ │ U100  │ │      ││
│         │         └────────┘ └───────┘ └──────┘│
│         │                                       │
│  Integration Methods:                          │
│  1. MQTT (Aqara Hub → MediaControl)            │
│  2. HomeKit (via Aqara Hub)                    │
│  3. Local API (Aqara Hub M3)                   │
└─────────────────────────────────────────────────┘
```

### Configuration

```yaml
aqara:
  enabled: true
  
  # Aqara Hub
  hub:
    type: "m3"  # "m2", "m3", "camera_hub_g3"
    host: "192.168.1.110"
    port: 9898  # Aqara local API port
    token: "your_hub_token"
    
    # MQTT (if Aqara Hub has MQTT enabled)
    mqtt:
      enabled: true
      broker: "192.168.1.110"
      port: 1883
      username: "aqara"
      password: "mqtt_password"
  
  # Doorbells
  doorbells:
    - doorbell_id: "aqara_front_door"
      name: "Front Door (Aqara G4)"
      device_type: "g4"  # or "g220"
      zigbee_id: "lumi.1234567890"
      
      # Video stream (via Aqara Hub)
      stream:
        protocol: "rtsp"
        url: "rtsp://192.168.1.110/lumi.1234567890"
        
      # Behavior
      behavior:
        auto_popup: true
        pip_mode: true
        record_on_press: true
        
      # Associated lock
      lock_id: "aqara_front_lock"
  
  # Smart Locks
  locks:
    - lock_id: "aqara_front_lock"
      name: "Front Door Lock (Aqara U100)"
      device_type: "u100"  # or "n100", "n200"
      zigbee_id: "lumi.0987654321"
      
      # Access methods
      access_methods:
        fingerprint: true
        nfc_card: true
        pin_code: true
        bluetooth: true
        
      # Behavior
      behavior:
        auto_lock: true
        auto_lock_delay: 30
  
  # Door/Window Sensors
  sensors:
    - sensor_id: "aqara_front_door_sensor"
      name: "Front Door Sensor"
      device_type: "door_window_sensor"
      zigbee_id: "lumi.1111111111"
      
      # Trigger MediaControl events
      events:
        - event: "opened"
          action: "show_notification"
        - event: "closed"
          action: "dismiss_notification"
        - event: "left_open"  # Open for 5+ minutes
          duration: 300  # seconds
          action: "trigger_alarm"
  
  # Integration with MediaControl
  integration:
    # Show Aqara events on MediaControl displays
    show_events: true
    
    # Control Aqara devices from MediaControl
    control_devices: true
    
    # Sync with Home Assistant (if both enabled)
    sync_with_home_assistant: true
```

### MQTT Topics (Aqara Hub → MediaControl)

```
# Doorbell pressed
zigbee2mqtt/lumi.1234567890/action
Payload: {"action": "button_pressed"}

# Lock status
zigbee2mqtt/lumi.0987654321/state
Payload: {"state": "locked", "user": "John Doe", "method": "fingerprint"}

# Door sensor
zigbee2mqtt/lumi.1111111111/state
Payload: {"contact": false}  # false = open, true = closed
```

---

## Nuki Smart Lock Integration

### Overview

**Nuki** is a premium European smart lock system with:
- Retrofit smart locks (attach to existing deadbolt)
- Smart Lock Pro (4th generation)
- Smart Lock 3.0
- Opener (for intercoms and gates)
- Keypad (PIN entry, NFC)
- Bridge (WiFi connectivity)

### Supported Devices

#### 1. **Nuki Smart Lock Pro (4th Gen)**
- Matter support
- WiFi built-in (no Bridge required)
- Bluetooth
- Ultra-low power (1 year battery)
- Auto-unlock (geofencing)
- Quiet motor

#### 2. **Nuki Smart Lock 3.0**
- Bluetooth + Bridge (for WiFi)
- Battery: 6-12 months
- Auto-unlock
- Retrofit installation

#### 3. **Nuki Keypad 2.0**
- PIN codes (up to 200)
- NFC cards
- Battery-powered
- Weatherproof (IP65)

#### 4. **Nuki Bridge**
- WiFi connectivity
- Internet access (remote control)
- MQTT support
- Webhooks

#### 5. **Nuki Opener**
- Smart intercom controller
- Works with existing intercoms
- Ring-to-open
- Auto-unlock

### Integration Architecture

```
┌─────────────────────────────────────────────────┐
│         Nuki Integration                        │
│                                                 │
│  ┌──────────────┐         ┌──────────────┐     │
│  │MediaControl  │◀───────▶│ Nuki Bridge  │     │
│  │Gateway       │  HTTP   │ or           │     │
│  │              │  MQTT   │ Matter       │     │
│  └──────────────┘         └──────┬───────┘     │
│         │                        │             │
│         │                   Bluetooth          │
│         │                        │             │
│         │              ┌─────────┼─────────┐   │
│         │              │         │         │   │
│         │         ┌────▼───┐ ┌──▼────┐ ┌──▼──┐│
│         │         │Nuki Pro│ │Keypad │ │Opener││
│         │         │(Lock)  │ │ 2.0   │ │      ││
│         │         └────────┘ └───────┘ └──────┘│
│         │                                       │
│  Integration Methods:                          │
│  1. HTTP API (Nuki Bridge)                     │
│  2. MQTT (Nuki Bridge)                         │
│  3. Matter (Nuki Smart Lock Pro)               │
│  4. Webhooks (Nuki Cloud)                      │
└─────────────────────────────────────────────────┘
```

### Configuration

```yaml
nuki:
  enabled: true
  
  # Nuki Bridge (for Smart Lock 3.0)
  bridge:
    host: "192.168.1.120"
    port: 8080
    api_token: "nuki_bridge_token"
    
    # MQTT (optional)
    mqtt:
      enabled: true
      broker: "192.168.1.120"
      port: 1883
  
  # Nuki Smart Locks
  locks:
    - lock_id: "nuki_front_door"
      name: "Front Door (Nuki Pro)"
      device_type: "smart_lock_pro"  # or "smart_lock_3"
      nuki_id: 12345678  # Nuki device ID
      
      # Connection method
      connection:
        method: "matter"  # or "bridge", "bluetooth"
        
      # Lock actions
      actions:
        lock: true
        unlock: true
        unlatch: true  # Open door latch (for European doors)
        lock_n_go: true  # Unlock, wait, then lock
        
      # Auto-unlock
      auto_unlock:
        enabled: true
        method: "geofencing"  # or "bluetooth_proximity"
        
      # Behavior
      behavior:
        auto_lock: true
        auto_lock_delay: 30
        
      # Associated doorbell
      doorbell_id: "front_door"
    
    - lock_id: "nuki_back_door"
      name: "Back Door (Nuki 3.0)"
      device_type: "smart_lock_3"
      nuki_id: 87654321
      connection:
        method: "bridge"
  
  # Nuki Keypad
  keypads:
    - keypad_id: "nuki_front_keypad"
      name: "Front Door Keypad"
      nuki_id: 11111111
      
      # PIN codes
      pin_codes:
        - code: "123456"
          name: "Family Code"
          enabled: true
        - code: "987654"
          name: "Guest Code"
          enabled: false
          
      # NFC cards
      nfc_cards:
        - card_id: "0123456789"
          name: "John's Card"
          enabled: true
  
  # Nuki Opener (for intercoms)
  openers:
    - opener_id: "nuki_main_entrance"
      name: "Building Intercom Opener"
      nuki_id: 22222222
      
      # Ring-to-open
      ring_to_open:
        enabled: true
        schedule:
          days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
          start_time: "08:00"
          end_time: "18:00"
  
  # Webhooks (Nuki Cloud)
  webhooks:
    enabled: true
    # Nuki sends webhooks to this endpoint
    endpoint: "http://mediacontrol-gateway-ip:8080/api/nuki/webhook"
    
  # Events
  events:
    - event: "locked"
      action: "show_notification"
    - event: "unlocked"
      action: "show_notification"
    - event: "battery_low"
      action: "send_alert"
```

### API Integration

```python
# MediaControl → Nuki (via Bridge)
POST http://nuki-bridge-ip:8080/lockAction
Params:
  nukiId=12345678
  action=1  # 1=unlock, 2=lock, 3=unlatch, 4=lock_n_go
  token=nuki_bridge_token

# Nuki → MediaControl (Webhook from Nuki Cloud)
POST http://mediacontrol-gateway-ip:8080/api/nuki/webhook
{
  "nukiId": 12345678,
  "state": 1,  # 1=locked, 3=unlocked
  "stateName": "locked",
  "batteryCritical": false,
  "timestamp": "2026-07-31T09:50:00Z"
}
```

---

## Home Assistant Integration

### Overview

**Home Assistant** is the leading open-source home automation platform with:
- 2000+ integrations
- Local control (no cloud required)
- Advanced automation
- Beautiful dashboards
- Voice assistant (Year of the Voice)

**MediaControl ↔ Home Assistant** is **fully bidirectional**.

### Integration Architecture

```
┌─────────────────────────────────────────────────┐
│    MediaControl ↔ Home Assistant                │
│    (Bidirectional Integration)                  │
│                                                 │
│  ┌──────────────┐         ┌──────────────┐     │
│  │MediaControl  │◀───────▶│Home Assistant│     │
│  │Gateway       │  MQTT   │              │     │
│  │              │  REST   │              │     │
│  │              │WebSocket│              │     │
│  └──────┬───────┘         └──────┬───────┘     │
│         │                        │             │
│         │                        │             │
│  MediaControl exposes:     Home Assistant      │
│  • Displays (on/off)       exposes:            │
│  • Sources (active)        • Lights            │
│  • Audio zones             • Switches          │
│  • Doorbells               • Sensors           │
│  • Locks                   • Cameras           │
│  • Rooms                   • Climate           │
│                            • Media Players     │
│                                                 │
│  Automation Examples:                          │
│  1. HA: Lights off → MC: Turn off displays     │
│  2. MC: Doorbell → HA: Turn on porch light     │
│  3. HA: Bedtime scene → MC: Turn off all rooms │
│  4. MC: Meeting active → HA: Do Not Disturb    │
└─────────────────────────────────────────────────┘
```

### Configuration

```yaml
home_assistant:
  enabled: true
  
  # Home Assistant connection
  host: "192.168.1.8"
  port: 8123
  access_token: "your_long_lived_access_token"
  
  # Connection methods
  connection:
    # REST API (for device control)
    rest_api: true
    
    # MQTT (for real-time updates)
    mqtt:
      enabled: true
      discovery: true  # Auto-discovery via MQTT
      broker: "192.168.1.8"
      port: 1883
      username: "mediacontrol"
      password: "mqtt_password"
      topic_prefix: "mediacontrol"
    
    # WebSocket (for real-time state updates)
    websocket: true
  
  # MediaControl devices exposed to Home Assistant
  expose_to_ha:
    displays:
      - display_id: "display_1"
        name: "Conference Room TV"
        device_class: "tv"  # HA device class
        
      - display_id: "display_2"
        name: "Executive Office Monitor"
        device_class: "tv"
    
    audio_zones:
      - zone_id: "conference_room_audio"
        name: "Conference Room Speakers"
        device_class: "speaker"
    
    doorbells:
      - doorbell_id: "front_door"
        name: "Front Door Doorbell"
        device_class: "doorbell"
    
    locks:
      - lock_id: "front_door_lock"
        name: "Front Door Lock"
        device_class: "lock"
    
    rooms:
      - room_id: "conference_room_a"
        name: "Conference Room A"
        # Expose room as a "scene" in HA
        # Scenes: presentation_mode, video_call_mode, idle
  
  # Home Assistant devices/entities used by MediaControl
  import_from_ha:
    lights:
      - entity_id: "light.conference_room_ceiling"
        control_from_mc: true  # Allow MediaControl to control
        
      - entity_id: "light.porch_light"
        control_from_mc: true
    
    switches:
      - entity_id: "switch.coffee_maker"
        control_from_mc: false  # View only
    
    climate:
      - entity_id: "climate.conference_room_thermostat"
        control_from_mc: true
    
    sensors:
      - entity_id: "sensor.conference_room_occupancy"
        # Use for automation (auto-turn on display when occupied)
        trigger_mc_automation: true
    
    cameras:
      - entity_id: "camera.driveway"
        show_on_mc_display: true  # Show in PiP
  
  # Automation (MediaControl → Home Assistant)
  automations_mc_to_ha:
    - trigger:
        mc_event: "doorbell_pressed"
        doorbell_id: "front_door"
      action:
        ha_service: "light.turn_on"
        entity_id: "light.porch_light"
        
    - trigger:
        mc_event: "meeting_started"
        room_id: "conference_room_a"
      action:
        ha_service: "scene.turn_on"
        entity_id: "scene.conference_room_meeting"
        
    - trigger:
        mc_event: "room_idle"
        room_id: "conference_room_a"
        duration: 300  # 5 minutes
      action:
        ha_service: "climate.set_temperature"
        entity_id: "climate.conference_room_thermostat"
        data:
          temperature: 72  # Energy saving
  
  # Automation (Home Assistant → MediaControl)
  automations_ha_to_mc:
    - trigger:
        ha_entity: "input_boolean.bedtime"
        state: "on"
      action:
        mc_command: "turn_off_all_displays"
        
    - trigger:
        ha_entity: "binary_sensor.front_door"
        state: "on"  # Door opened
      action:
        mc_command: "show_notification"
        message: "Front door opened"
        
    - trigger:
        ha_entity: "alarm_control_panel.home_alarm"
        state: "triggered"
      action:
        mc_command: "emergency_page"
        message: "Security alarm triggered!"
```

### MQTT Auto-Discovery (Home Assistant)

MediaControl publishes discovery messages so Home Assistant automatically finds devices:

```json
// MediaControl Display
Topic: homeassistant/switch/mediacontrol_display_1/config
Payload:
{
  "name": "Conference Room TV",
  "unique_id": "mc_display_1",
  "state_topic": "mediacontrol/display_1/state",
  "command_topic": "mediacontrol/display_1/set",
  "device_class": "switch",
  "device": {
    "identifiers": ["mediacontrol_gateway_1"],
    "name": "MediaControl Gateway",
    "model": "MCG-Pro",
    "manufacturer": "MediaControl"
  }
}

// MediaControl Lock
Topic: homeassistant/lock/mediacontrol_front_door_lock/config
Payload:
{
  "name": "Front Door Lock",
  "unique_id": "mc_lock_front_door",
  "state_topic": "mediacontrol/lock/front_door/state",
  "command_topic": "mediacontrol/lock/front_door/set",
  "payload_lock": "LOCK",
  "payload_unlock": "UNLOCK",
  "device_class": "lock"
}
```

---

## Matter Protocol Support

### Overview

**Matter** is the universal smart home standard backed by:
- Apple (HomeKit)
- Google (Google Home)
- Amazon (Alexa)
- Samsung (SmartThings)
- 280+ companies in Connectivity Standards Alliance (CSA)

**Benefits:**
- Interoperability (one device, multiple ecosystems)
- Local control (no cloud required)
- Security (end-to-end encryption)
- Easy setup (QR code pairing)

### Supported Devices

MediaControl supports Matter-certified devices:
- Smart locks (Nuki Smart Lock Pro, Yale Assure Lock 2, Schlage Encode Plus)
- Doorbells (Ring Battery Doorbell Plus, Google Nest Doorbell)
- Sensors (Eve Door & Window, Aqara Door Sensor P2)
- Lights, switches, thermostats, etc.

### Integration Architecture

```
┌─────────────────────────────────────────────────┐
│         Matter Integration                      │
│                                                 │
│  ┌──────────────┐         ┌──────────────┐     │
│  │MediaControl  │◀───────▶│   Matter     │     │
│  │Gateway       │ Thread  │   Border     │     │
│  │(Matter       │   or    │   Router     │     │
│  │ Controller)  │  WiFi   │  (optional)  │     │
│  └──────────────┘         └──────┬───────┘     │
│         │                        │             │
│         │                   Matter/Thread      │
│         │                        │             │
│         │              ┌─────────┼─────────┐   │
│         │              │         │         │   │
│         │         ┌────▼───┐ ┌──▼────┐ ┌──▼──┐│
│         │         │Nuki Pro│ │ Ring  │ │ Eve ││
│         │         │(Matter)│ │Doorbell│ │Sensor││
│         │         └────────┘ └───────┘ └──────┘│
│         │                                       │
│  MediaControl acts as Matter Controller        │
│  • Commission Matter devices                   │
│  • Control via local network                   │
│  • Works with Apple Home, Google Home, Alexa   │
└─────────────────────────────────────────────────┘
```

### Configuration

```yaml
matter:
  enabled: true
  
  # Matter Controller settings
  controller:
    vendor_id: 0xFFF1  # MediaControl vendor ID (TBD)
    product_id: 0x8000  # MediaControl Gateway product ID
    
    # Storage for Matter credentials
    storage_path: "/var/lib/mediacontrol/matter"
    
    # Network
    port: 5540  # Matter default port
    
  # Matter Border Router (optional, for Thread devices)
  border_router:
    enabled: false  # Use if you have Thread devices
    # If disabled, Thread devices connect via Matter-over-WiFi
  
  # Matter devices
  devices:
    - device_id: "matter_nuki_front"
      name: "Front Door Lock (Nuki Pro - Matter)"
      device_type: "lock"
      
      # Matter node ID (assigned during commissioning)
      node_id: 12345
      
      # Commissioning (one-time setup)
      # Use QR code or manual pairing code
      # pairing_code: "34970112332"
      
      # MediaControl lock ID (map to unified system)
      mc_lock_id: "front_door_lock"
      
    - device_id: "matter_ring_doorbell"
      name: "Front Door Doorbell (Ring - Matter)"
      device_type: "doorbell"
      node_id: 67890
      
      # MediaControl doorbell ID
      mc_doorbell_id: "front_door"
      
    - device_id: "matter_eve_door_sensor"
      name: "Back Door Sensor (Eve - Matter)"
      device_type: "contact_sensor"
      node_id: 11111
  
  # Ecosystem integration
  ecosystems:
    # Allow other Matter controllers to control MediaControl devices
    expose_mc_devices: true
    
    # Apple HomeKit
    homekit:
      enabled: true
      # MediaControl Gateway appears in Home app
      
    # Google Home
    google_home:
      enabled: true
      
    # Amazon Alexa
    alexa:
      enabled: false
```

### Matter Device Commissioning

**Setup Flow:**
1. User scans QR code on Matter device (e.g., Nuki Smart Lock Pro)
2. MediaControl Gateway commissions device over WiFi or Thread
3. Device appears in MediaControl interface
4. Device is automatically mapped to unified system (lock, doorbell, etc.)
5. Device can also be controlled via Apple Home, Google Home, Alexa

**Benefits:**
- One device, multiple control methods
- Works even if MediaControl is offline (local control via Apple/Google/Amazon)
- Easy migration (Matter devices work with any compatible system)

---

## Zigbee Integration

### Overview

**Zigbee** is a low-power mesh network protocol used by:
- Philips Hue (lights)
- Aqara (sensors, locks, doorbells)
- IKEA TRÅDFRI (lights, blinds)
- Sonoff (switches, sensors)
- Tuya (various devices)

**MediaControl Zigbee Integration** is **bidirectional**:
- Control Zigbee devices from MediaControl
- Zigbee events trigger MediaControl actions

### Zigbee Coordinator Options

MediaControl supports multiple Zigbee coordinators:

#### 1. **ConBee II / ConBee III** (Dresden Elektronik)
- USB Zigbee coordinator
- Supports Zigbee 3.0
- Works with Zigbee2MQTT, deCONZ

#### 2. **Sonoff Zigbee 3.0 USB Dongle Plus**
- Affordable ($10-15)
- TI CC2652P chip
- Works with Zigbee2MQTT, ZHA

#### 3. **Home Assistant SkyConnect**
- Multi-protocol (Zigbee + Thread + Matter)
- Official HA hardware
- Works with ZHA

#### 4. **Aqara Hub M2 / M3**
- Zigbee 3.0 hub
- Built-in automations
- Works with Aqara devices

### Integration Architecture

```
┌─────────────────────────────────────────────────┐
│         Zigbee Integration                      │
│                                                 │
│  ┌──────────────┐         ┌──────────────┐     │
│  │MediaControl  │◀───────▶│Zigbee2MQTT   │     │
│  │Gateway       │  MQTT   │(Zigbee       │     │
│  │              │         │ Coordinator) │     │
│  └──────────────┘         └──────┬───────┘     │
│         │                        │             │
│         │                   Zigbee Mesh        │
│         │                        │             │
│         │              ┌─────────┼─────────┐   │
│         │              │         │         │   │
│         │         ┌────▼───┐ ┌──▼────┐ ┌──▼──┐│
│         │         │Aqara   │ │ Philips│ │Sonoff││
│         │         │Door    │ │  Hue  │ │Switch││
│         │         │Sensor  │ │ Bulb  │ │      ││
│         │         └────────┘ └───────┘ └──────┘│
│         │                                       │
│  Bidirectional:                                │
│  • MC controls Zigbee devices (lights, locks)  │
│  • Zigbee events trigger MC (door open → notify)│
└─────────────────────────────────────────────────┘
```

### Configuration

```yaml
zigbee:
  enabled: true
  
  # Zigbee coordinator
  coordinator:
    type: "zigbee2mqtt"  # or "zha", "deconz", "aqara_hub"
    
    # Zigbee2MQTT configuration
    zigbee2mqtt:
      mqtt_broker: "192.168.1.8"
      mqtt_port: 1883
      mqtt_username: "zigbee"
      mqtt_password: "mqtt_password"
      topic_prefix: "zigbee2mqtt"
      
      # USB device (for Zigbee2MQTT)
      usb_device: "/dev/ttyUSB0"  # or "/dev/ttyACM0"
  
  # Zigbee devices
  devices:
    # Door/Window Sensors
    - device_id: "zigbee_front_door_sensor"
      name: "Front Door Sensor"
      zigbee_friendly_name: "door_sensor_front"  # Zigbee2MQTT friendly name
      device_type: "contact_sensor"
      manufacturer: "aqara"
      model: "MCCGQ11LM"
      
      # Trigger MediaControl events
      events:
        - zigbee_event: "contact"
          zigbee_state: false  # false = open
          mc_action: "show_notification"
          message: "Front door opened"
          
        - zigbee_event: "contact"
          zigbee_state: true  # true = closed
          mc_action: "dismiss_notification"
    
    # Smart Lock
    - device_id: "zigbee_back_door_lock"
      name: "Back Door Lock"
      zigbee_friendly_name: "lock_back_door"
      device_type: "lock"
      manufacturer: "aqara"
      model: "ZNMS12LM"
      
      # Map to MediaControl lock
      mc_lock_id: "back_door_lock"
    
    # Motion Sensor
    - device_id: "zigbee_hallway_motion"
      name: "Hallway Motion Sensor"
      zigbee_friendly_name: "motion_hallway"
      device_type: "motion_sensor"
      manufacturer: "aqara"
      model: "RTCGQ11LM"
      
      # Trigger MediaControl automation
      events:
        - zigbee_event: "occupancy"
          zigbee_state: true  # motion detected
          mc_action: "turn_on_display"
          display_id: "display_hallway"
          
        - zigbee_event: "occupancy"
          zigbee_state: false  # no motion for 5 min
          mc_action: "turn_off_display"
          display_id: "display_hallway"
          delay: 300  # seconds
    
    # Smart Light (Philips Hue)
    - device_id: "zigbee_conference_light"
      name: "Conference Room Light"
      zigbee_friendly_name: "hue_conference"
      device_type: "light"
      manufacturer: "philips"
      model: "LCT015"
      
      # Control from MediaControl
      mc_control: true
    
    # Smart Switch (Sonoff)
    - device_id: "zigbee_projector_switch"
      name: "Projector Power Switch"
      zigbee_friendly_name: "switch_projector"
      device_type: "switch"
      manufacturer: "sonoff"
      model: "ZBMINI"
      
      # Control from MediaControl
      mc_control: true
      
      # Link to MediaControl display
      mc_display_id: "display_projector"
      # When MC turns on display → turn on switch
      # When MC turns off display → turn off switch
  
  # MediaControl devices exposed to Zigbee
  expose_to_zigbee:
    # Expose MediaControl displays as Zigbee devices
    # (so Zigbee automation can control MediaControl)
    displays:
      - display_id: "display_1"
        expose_as: "switch"
        zigbee_friendly_name: "mc_display_conference"
```

### MQTT Topics (Zigbee2MQTT)

```bash
# Subscribe to all Zigbee devices
mosquitto_sub -h 192.168.1.8 -t "zigbee2mqtt/#"

# Door sensor state
Topic: zigbee2mqtt/door_sensor_front
Payload: {"contact": false, "battery": 95, "linkquality": 120}

# Control light from MediaControl
Topic: zigbee2mqtt/hue_conference/set
Payload: {"state": "ON", "brightness": 200, "color_temp": 300}

# MediaControl display exposed to Zigbee
Topic: zigbee2mqtt/mc_display_conference
Payload: {"state": "ON"}
```

---

## API Reference

### Ubiquiti Access API

```http
# Unlock door
POST /api/smart-home/ubiquiti/unlock
{
  "door_id": "front_door"
}

# Get door status
GET /api/smart-home/ubiquiti/door/{door_id}/status

Response:
{
  "door_id": "front_door",
  "name": "Front Door",
  "locked": true,
  "last_event": {
    "type": "unlocked",
    "user": "John Doe",
    "method": "nfc_card",
    "timestamp": "2026-07-31T09:50:00Z"
  }
}
```

### Aqara API

```http
# Control Aqara lock
POST /api/smart-home/aqara/lock
{
  "lock_id": "aqara_front_lock",
  "action": "unlock"
}

# Get doorbell events
GET /api/smart-home/aqara/doorbell/{doorbell_id}/events?hours=24

Response:
{
  "events": [
    {
      "type": "button_pressed",
      "timestamp": "2026-07-31T09:45:00Z",
      "snapshot_url": "/recordings/aqara_front_20260731_094500.jpg"
    }
  ]
}
```

### Nuki API

```http
# Unlock Nuki lock
POST /api/smart-home/nuki/unlock
{
  "lock_id": "nuki_front_door",
  "action": "unlatch"  # or "unlock", "lock", "lock_n_go"
}

# Get Nuki lock state
GET /api/smart-home/nuki/lock/{lock_id}/state

Response:
{
  "lock_id": "nuki_front_door",
  "state": "locked",
  "battery_critical": false,
  "battery_charge": 85
}
```

### Home Assistant API

```http
# Call Home Assistant service
POST /api/smart-home/home-assistant/service
{
  "domain": "light",
  "service": "turn_on",
  "entity_id": "light.conference_room_ceiling",
  "data": {
    "brightness": 200
  }
}

# Get Home Assistant entity state
GET /api/smart-home/home-assistant/state/{entity_id}

Response:
{
  "entity_id": "light.conference_room_ceiling",
  "state": "on",
  "attributes": {
    "brightness": 200,
    "color_temp": 300
  }
}
```

### Matter API

```http
# Commission Matter device
POST /api/smart-home/matter/commission
{
  "pairing_code": "34970112332",
  "device_name": "Front Door Lock"
}

# Control Matter device
POST /api/smart-home/matter/control
{
  "node_id": 12345,
  "cluster": "door_lock",
  "command": "unlock_door"
}
```

### Zigbee API

```http
# Control Zigbee device
POST /api/smart-home/zigbee/control
{
  "friendly_name": "hue_conference",
  "state": "ON",
  "brightness": 200
}

# Get Zigbee device state
GET /api/smart-home/zigbee/device/{friendly_name}

Response:
{
  "friendly_name": "hue_conference",
  "state": "ON",
  "brightness": 200,
  "linkquality": 120
}
```

---

## Use Cases

### 1. Smart Home Integration (Home)

**Setup:**
- MediaControl MCG-Standard gateway
- Home Assistant running on Raspberry Pi
- 3× Aqara door sensors (Zigbee)
- 2× Nuki Smart Lock Pro (Matter)
- 1× Aqara G4 video doorbell
- 5× Philips Hue lights (Zigbee)

**Automation:**
1. Front doorbell pressed → MediaControl shows video + Home Assistant turns on porch light
2. Door opened (Aqara sensor) → MediaControl notification + log entry
3. Bedtime (Home Assistant scene) → MediaControl turns off all displays
4. Motion detected (hallway) → MediaControl turns on hallway display + Hue lights

---

### 2. Enterprise Access Control (Office)

**Setup:**
- MediaControl MCG-Pro gateways (10 rooms)
- Ubiquiti Access (5 doors, 10 readers)
- Home Assistant for automation
- Zigbee sensors for occupancy

**Automation:**
1. Card scanned at front door → MediaControl logs access + shows on security display
2. Door forced open → MediaControl triggers alarm + emergency paging
3. Meeting room occupied (Zigbee sensor) → MediaControl auto-turns on display + adjusts thermostat
4. After hours access → MediaControl sends alert to security

---

### 3. Multi-Protocol Home (Prosumer)

**Setup:**
- MediaControl MCG-Pro gateway
- Ubiquiti Access (2 doors)
- Nuki Smart Lock Pro (1 door, Matter)
- Aqara Hub M3 + 10 Aqara devices (Zigbee)
- Home Assistant
- Apple HomeKit, Google Home

**Benefit:**
- All devices work together seamlessly
- Control from MediaControl, Home Assistant, Apple Home, or Google Home
- Matter devices work with all ecosystems
- Zigbee mesh network for sensors
- Ubiquiti for secure main entrance

---

## Best Practices

### Ubiquiti Access
✅ Use UA Reader Pro for main entrances (camera captures entry photo)  
✅ Use UA Lite for employee entrances (affordable)  
✅ Set auto-lock to 30 seconds for security  
✅ Regular firmware updates

### Aqara
✅ Use Aqara Hub M3 (Ethernet more reliable than M2)  
✅ Battery devices: check battery monthly  
✅ Zigbee mesh: place devices max 10m apart  
✅ Enable local automation (works without internet)

### Nuki
✅ Use Nuki Smart Lock Pro for Matter support (future-proof)  
✅ Enable auto-lock (security)  
✅ Keypad codes: disable guest codes after use  
✅ Regular battery checks (low battery = failure to unlock)

### Home Assistant
✅ Use MQTT for real-time updates (faster than REST API)  
✅ Enable auto-discovery (devices appear automatically)  
✅ Backup Home Assistant config regularly  
✅ Use local control (avoid cloud when possible)

### Matter
✅ Commission devices via MediaControl (centralized management)  
✅ Also add to Apple Home/Google Home for redundancy  
✅ Update firmware regularly (Matter still evolving)

### Zigbee
✅ Use Zigbee2MQTT for flexibility (supports most devices)  
✅ Place coordinator centrally (USB extension cable if needed)  
✅ Add Zigbee routers (powered devices) for mesh strength  
✅ Avoid WiFi channel overlap (Zigbee uses 2.4 GHz)

---

**For smart home ecosystem integration:**  
**Contact:** integrations@mediacontrol.com  
**Support:** https://mediacontrol.com/support/smart-home
