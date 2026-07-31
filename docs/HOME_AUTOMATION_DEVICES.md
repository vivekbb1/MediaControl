# Home Automation & Security Devices Integration

**Complete Integration Guide for Garage, Irrigation, Pool, Elevator, Access Control, and CCTV**

---

## Table of Contents

1. [Overview](#overview)
2. [Tailwind Garage Controller](#tailwind-garage-controller)
3. [Irrigation Systems (Rachio)](#irrigation-systems-rachio)
4. [Swimming Pool Automation](#swimming-pool-automation)
5. [Elevator/Lift Control](#elevatorlift-control)
6. [Door Access Control (Electric Strike)](#door-access-control-electric-strike)
7. [CCTV Camera Integration](#cctv-camera-integration)
8. [Configuration Examples](#configuration-examples)
9. [API Reference](#api-reference)

---

## Overview

**MediaControl now integrates with ALL major home automation and security systems**, providing unified control from a single interface:

| Device Type | Brands Supported | Protocol | Integration Method |
|-------------|------------------|----------|-------------------|
| **Garage Door** | Tailwind iQ3 | HTTP + Local API | Direct local control (no cloud!) |
| **Irrigation** | Rachio, Rain Bird, Hunter | REST API + Webhooks | Cloud API with local fallback |
| **Swimming Pool** | Pentair, Hayward | RS-485, MQTT, WebSocket | Local control + cloud monitoring |
| **Elevator/Lift** | TK Elevator, Schindler, Generic | MQTT, REST API | Building automation integration |
| **Door Access** | Ubiquiti Access, Generic Strike | HTTP API + Webhooks | Real-time lock/unlock control |
| **CCTV Cameras** | Dahua, Hikvision, Ubiquiti | ONVIF + RTSP | Universal camera standard |

### Why This Matters

🏆 **Unified Control** - Control garage, pool, irrigation, elevator, doors, and cameras from ONE interface  
🏆 **Local-First** - Most integrations work locally (no internet required)  
🏆 **Real-Time** - WebSocket/webhook support for instant status updates  
🏆 **Universal** - Works with multiple brands via standard protocols  
🏆 **Secure** - TLS encryption, local control keys, role-based access  

---

## Tailwind Garage Controller

### Overview

**Tailwind iQ3** is a professional-grade smart garage door controller with **local API** (no cloud required!).

**Supported Models:**
- ✅ Tailwind iQ3 (Original) - Firmware v10.80+
- ✅ Tailwind iQ3 2.0 / 2.1 - Firmware v10.30+
- ✅ Up to 3 garage doors per controller

### Architecture

```
MediaControl Gateway
    ↓ HTTP POST (port 80, local network)
Tailwind iQ3 Controller (192.168.1.X)
    ↓ Wired connection
Garage Door Opener(s) (1-3 doors)
```

### Features

| Feature | Support |
|---------|---------|
| **Open Door** | ✅ HTTP POST `/json` |
| **Close Door** | ✅ HTTP POST `/json` |
| **Status Polling** | ✅ Real-time (open/closed/opening/closing) |
| **Multi-Door** | ✅ Up to 3 doors per controller |
| **Local Control** | ✅ No cloud required |
| **Authentication** | ✅ Local Control Key (6-digit token) |

### Setup Instructions

#### 1. **Get Local Control Key**

1. Visit [Tailwind Web Portal](https://web.gotailwind.com)
2. Sign in with your Tailwind account
3. Click **"Local Control Key"** tab
4. Copy the **6-digit code** (e.g., `123456`)

#### 2. **Find Device IP Address**

1. Open Tailwind mobile app
2. Select your iQ3 device
3. Tap the **cog icon** (settings)
4. Note the **IP address** in "Device Info" section (e.g., `192.168.1.50`)

#### 3. **Configure MediaControl**

```yaml
garage:
  - id: "garage_main"
    name: "Main Garage"
    type: "tailwind"
    ip: "192.168.1.50"
    port: 80
    local_control_key: "123456"  # Your 6-digit key
    doors:
      - door_index: 0
        name: "Left Door"
      - door_index: 1
        name: "Right Door"
```

### API Details

**Authentication:**
- HTTP Header: `TOKEN: {local_control_key}` (6-digit code)

**Status Poll:**
```http
POST http://192.168.1.50/json
Headers:
  TOKEN: 123456
  Content-Type: application/json

Body:
{
  "version": "0.1",
  "data": {
    "type": "get",
    "name": "dev_st"
  }
}

Response:
{
  "data": {
    "door0": {
      "status": "closed",  // "closed", "open", "opening", "closing"
      "last_change": "2026-07-31T10:00:00Z"
    },
    "door1": {
      "status": "open"
    }
  }
}
```

**Open/Close Door:**
```http
POST http://192.168.1.50/json
Headers:
  TOKEN: 123456
  Content-Type: application/json

Body:
{
  "product": "iQ3",
  "version": "0.1",
  "data": {
    "type": "set",
    "name": "door_op",
    "value": {
      "door_idx": 0,      // 0, 1, or 2
      "cmd": "open"       // "open" or "close"
    }
  }
}
```

### Voice Commands

**Via Apple HomeKit, Google Home, Alexa:**
- "Hey Siri, open the garage door"
- "Hey Google, close the main garage"
- "Alexa, is the garage door open?"

(Requires Tailwind cloud integration for voice control)

---

## Irrigation Systems (Rachio)

### Overview

**Rachio** is the leading smart irrigation controller with cloud API and webhook support.

**Supported Models:**
- ✅ Rachio 3 (8-zone, 16-zone)
- ✅ Rachio 3e (8-zone, 16-zone)
- ✅ Rachio Smart Hose Timer

### Architecture

```
MediaControl Gateway
    ↓ HTTPS (Rachio Cloud API)
Rachio Cloud (app.rach.io)
    ↓ WiFi
Rachio Controller (Local)
    ↓ 24VAC wiring
Sprinkler Valves/Zones
```

### Features

| Feature | Support |
|---------|---------|
| **Start/Stop Zone** | ✅ Individual zone control |
| **Start Schedule** | ✅ Run predefined schedules |
| **Rain Delay** | ✅ 24-hour rain delay |
| **Standby Mode** | ✅ Enable/disable controller |
| **Zone Moisture** | ✅ Adjust soil moisture % |
| **Webhooks** | ✅ Real-time status updates |

### Setup Instructions

#### 1. **Get API Key**

1. Visit [Rachio App](https://app.rach.io/)
2. Sign in to your account
3. Go to **Settings**
4. Click **"Get API Key"**
5. Copy the API key (e.g., `a1b2c3d4-e5f6-7890-abcd-1234567890ab`)

#### 2. **Configure MediaControl**

```yaml
irrigation:
  - id: "irrigation_main"
    name: "Front Yard Irrigation"
    type: "rachio"
    api_key: "a1b2c3d4-e5f6-7890-abcd-1234567890ab"
    
    # Optional: Webhook URL for real-time updates
    webhook:
      enabled: true
      url: "https://gateway-id.mediacontrol.cloud/api/rachio/webhook"
```

### API Details

**Base URL:** `https://api.rach.io/1/public/`

**Authentication:**
- HTTP Header: `Authorization: Bearer {api_key}`

**Get Person Info (includes devices):**
```http
GET https://api.rach.io/1/public/person/info
Headers:
  Authorization: Bearer a1b2c3d4-e5f6-7890-abcd-1234567890ab

Response:
{
  "id": "person_id_123",
  "devices": [
    {
      "id": "device_id_456",
      "name": "Front Yard Controller",
      "zones": [
        {
          "id": "zone_id_789",
          "name": "Front Lawn",
          "zoneNumber": 1,
          "enabled": true
        }
      ]
    }
  ]
}
```

**Start Watering Zone:**
```http
PUT https://api.rach.io/1/public/zone/start
Headers:
  Authorization: Bearer {api_key}
  Content-Type: application/json

Body:
{
  "id": "zone_id_789",
  "duration": 600  // seconds (10 minutes)
}
```

**Stop Watering:**
```http
PUT https://api.rach.io/1/public/device/stop_water
Headers:
  Authorization: Bearer {api_key}
  Content-Type: application/json

Body:
{
  "id": "device_id_456"
}
```

### Webhook Events

**Event Types:**
- `ZONE_STARTED` - Zone watering started
- `ZONE_STOPPED` - Zone watering stopped
- `ZONE_COMPLETED` - Zone cycle completed
- `DEVICE_OFFLINE` - Controller went offline
- `DEVICE_ONLINE` - Controller came online

**Webhook Payload:**
```json
{
  "eventType": "ZONE_STARTED",
  "deviceId": "device_id_456",
  "zoneId": "zone_id_789",
  "zoneName": "Front Lawn",
  "duration": 600,
  "timestamp": "2026-07-31T10:15:00Z"
}
```

### Rate Limits

- **1,700-3,500 API calls per day** (per API key)
- Use webhooks to avoid excessive polling

---

## Swimming Pool Automation

### Overview

**Pentair** and **Hayward** are the two major pool automation brands. MediaControl supports both via community-developed integrations.

**Supported Systems:**

**Pentair:**
- ✅ IntelliCenter (Local WebSocket on port 6680)
- ✅ IntelliTouch / EasyTouch (RS-485)
- ✅ IntelliConnect (Cloud API)

**Hayward:**
- ✅ OmniLogic (Cloud API)
- ✅ AquaRite (Cloud API)
- ✅ ProLogic / AquaLogic (RS-485)

### Architecture

**Option 1: Local Control (Pentair IntelliCenter)**
```
MediaControl Gateway
    ↓ WebSocket (port 6680, local network)
Pentair IntelliCenter OCP (192.168.1.X)
    ↓ Wired connections
Pool Equipment (pumps, heaters, lights, valves)
```

**Option 2: Cloud API (Pentair IntelliConnect, Hayward)**
```
MediaControl Gateway
    ↓ HTTPS
Pentair/Hayward Cloud
    ↓ WiFi
Pool Controller
    ↓ Wired connections
Pool Equipment
```

**Option 3: RS-485 (Advanced)**
```
MediaControl Gateway
    ↓ USB-to-RS485 Adapter
Pool Controller (IntelliTouch, ProLogic, etc.)
    ↓ Wired connections
Pool Equipment
```

### Features

| Feature | Pentair IntelliCenter | Hayward OmniLogic | Support |
|---------|----------------------|-------------------|---------|
| **Pool/Spa On/Off** | ✅ | ✅ | Switch |
| **Temperature Control** | ✅ | ✅ | Climate entity |
| **Heater Control** | ✅ | ✅ | On/off, setpoint |
| **Pump Control** | ✅ | ✅ | Speed, GPM, power (W) |
| **Light Control** | ✅ | ✅ | On/off, color effects |
| **Chlorinator** | ✅ | ✅ | Output %, salt level (ppm) |
| **Chemistry** | ✅ (IntelliChem) | ✅ | pH, ORP, tank levels |
| **Schedules** | ✅ | ✅ | Start/stop schedules |

### Setup Instructions (Pentair IntelliCenter - Local)

#### 1. **Enable IntelliCenter WebSocket API**

1. Open IntelliCenter dashPanel (web interface)
2. Navigate to **Settings** → **Communications**
3. Enable **"JSON WebSocket API"** on port **6680**
4. Note the **OCP IP address** (e.g., `192.168.1.60`)

#### 2. **Configure MediaControl**

```yaml
pool:
  - id: "pool_main"
    name: "Main Pool"
    type: "pentair_intellicenter"
    connection_type: "websocket"  # Local, no authentication required!
    ip: "192.168.1.60"
    port: 6680
    
    features:
      - type: "pool"
        name: "Pool"
      - type: "spa"
        name: "Spa"
      - type: "pump"
        name: "Pool Pump"
        pump_id: 1
      - type: "heater"
        name: "Pool Heater"
      - type: "light"
        name: "Pool Lights"
        light_type: "intellibrite"  # IntelliBrite, MagicStream
      - type: "chlorinator"
        name: "Salt Chlorinator"
```

### Setup Instructions (Hayward OmniLogic - Cloud)

#### 1. **Get API Credentials**

1. Create a Hayward account at [Hayward OmniLogic](https://www.hayward-pool.com/)
2. Link your OmniLogic controller to your account
3. Contact Hayward support for API access (or use community library)

#### 2. **Configure MediaControl**

```yaml
pool:
  - id: "pool_main"
    name: "Main Pool"
    type: "hayward_omnilogic"
    connection_type: "cloud"
    username: "your_hayward_username"
    password: "your_hayward_password"
    
    # MspSystemID (obtained from API)
    system_id: "your_msp_system_id"
```

### API Details (Pentair IntelliCenter - Local WebSocket)

**Connection:**
```
ws://192.168.1.60:6680
```

**No authentication required for local connection!**

**Get Status:**
```json
// Send (WebSocket message)
{
  "command": "GetState"
}

// Receive
{
  "pool": {
    "isOn": true,
    "temp": 82,  // °F
    "heater": "on",
    "setPoint": 84
  },
  "spa": {
    "isOn": false
  },
  "pumps": [
    {
      "id": 1,
      "status": "running",
      "rpm": 2400,
      "gpm": 60,
      "power": 1200  // Watts
    }
  ]
}
```

**Control Pool/Spa:**
```json
// Turn on pool
{
  "command": "SetCircuitState",
  "circuitId": 500,  // 500 = Pool, 501 = Spa
  "state": 1  // 1 = on, 0 = off
}
```

**Control Lights:**
```json
// Turn on lights
{
  "command": "SetCircuitState",
  "circuitId": 505,  // Light circuit ID
  "state": 1
}

// Set light color/effect
{
  "command": "SetLightShow",
  "showId": 3  // 1-14 (different color effects)
}
```

---

## Elevator/Lift Control

### Overview

**Elevator integration** allows MediaControl to call elevators, monitor status, and integrate with building automation systems.

**Supported Systems:**

| System | Type | Integration Method |
|--------|------|-------------------|
| **TK Elevator MAX** | Commercial | REST API (Developer Portal) |
| **Schindler BuilT-In** | Commercial | REST API |
| **Generic MQTT** | Residential/Custom | MQTT protocol |
| **Home Automation Hubs** | Residential | Via KNX, Modbus, BACnet |

### Architecture

**Option 1: Commercial API (TK Elevator, Schindler)**
```
MediaControl Gateway
    ↓ HTTPS REST API
Elevator Cloud API
    ↓ Internet
Building Elevator Controller
    ↓ Elevator CAN bus / network
Elevator Cars
```

**Option 2: MQTT (Custom/Residential)**
```
MediaControl Gateway
    ↓ MQTT
MQTT Broker (e.g., Mosquitto)
    ↓ MQTT
Elevator Controller (Custom)
    ↓ Relay/CAN bus
Elevator Car
```

**Option 3: Building Automation (KNX, Modbus)**
```
MediaControl Gateway (KNX/IP)
    ↓ KNX/IP protocol
KNX Gateway
    ↓ KNX bus
Elevator Controller Module
    ↓ Elevator control system
Elevator Car
```

### Features

| Feature | TK Elevator MAX | Generic MQTT | KNX Integration |
|---------|----------------|--------------|-----------------|
| **Call Elevator** | ✅ | ✅ | ✅ |
| **Select Floor** | ✅ | ✅ | ✅ |
| **Status Monitoring** | ✅ | ✅ | ✅ |
| **Real-Time Updates** | ✅ (WebSocket) | ✅ (MQTT) | ✅ (KNX Subscribe) |
| **Multi-Car Coordination** | ✅ | ⚠️ | ⚠️ |
| **Robot Integration** | ✅ | ⚠️ | ❌ |

### Setup Instructions (Generic MQTT - Residential)

#### 1. **MQTT Broker Setup**

```yaml
elevator:
  - id: "elevator_main"
    name: "Home Elevator"
    type: "mqtt"
    
    mqtt:
      broker: "192.168.1.100"
      port: 1883
      username: "mediacontrol"
      password: "your_mqtt_password"
      
      # MQTT Topics
      topics:
        call: "elevator/call"  # Publish call commands
        status: "elevator/status"  # Subscribe to status updates
        floor: "elevator/floor"  # Current floor
    
    floors:
      - floor_id: 0
        name: "Ground Floor"
      - floor_id: 1
        name: "First Floor"
      - floor_id: 2
        name: "Second Floor"
```

#### 2. **MQTT Messages**

**Call Elevator to Floor:**
```
Topic: elevator/call
Payload: {"floor": 1, "direction": "up"}
```

**Status Updates:**
```
Topic: elevator/status
Payload: {"floor": 1, "moving": false, "door_open": false}
```

### Safety Considerations

⚠️ **IMPORTANT:**
- Elevator integration must comply with local safety regulations
- Emergency functions (stop, alarm) should NOT be exposed to third-party APIs
- Always have manual override/emergency stop available
- Test thoroughly before deploying
- Consider insurance and liability requirements

---

## Door Access Control (Electric Strike)

### Overview

**Ubiquiti Access** is MediaControl's primary door access control integration, supporting smart locks, electric strikes, and card readers.

### 🔍 Ubiquiti Access API Review

Based on comprehensive analysis of the [Ubiquiti Access Developer API](https://core-config-gfoz.uid.alpha.ui.com/configs/unifi-access/api_reference.pdf):

#### API Architecture

**Base URL:** `https://{host}/api/v1/developer/`

**Authentication:**
- Method: **Bearer Token**
- Header: `Authorization: Bearer {token}`
- Token obtained via OAuth 2.0 flow

#### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/doors` | GET | List all doors |
| `/doors/{id}` | GET | Get door details |
| `/doors/{id}/unlock` | PUT | Momentary unlock (pulse) |
| `/doors/{id}/lock_rule` | PUT | Set temporary lock rule |
| `/doors/{id}/lock_rule` | GET | Get current lock rule |
| `/doors/settings/emergency` | PUT | Emergency lockdown/evacuation |

#### Door Lock Rules

**Lock Rule Types:**

1. **`lock_early`** - End scheduled unlock early, lock immediately
   ```json
   {"type": "lock_early"}
   ```

2. **`keep_unlock`** - Hold door unlocked indefinitely
   ```json
   {"type": "keep_unlock"}
   ```

3. **`reset`** - Restore door to original schedule
   ```json
   {"type": "reset"}
   ```

4. **`lock_now`** - Force lock regardless of schedule
   ```json
   {"type": "lock_now"}
   ```

5. **`unlock_for`** - Temporary unlock for N minutes
   ```json
   {
     "type": "unlock_for",
     "duration": 60  // minutes
   }
   ```

#### Webhook Events

**Supported Events:**
- `access.door.unlock` - Door unlocked (manual, card, app)
- `access.door.lock` - Door locked
- `access.doorbell.incoming` - Doorbell pressed
- `access.doorbell.completed` - Doorbell call ended
- `access.device.dps_status` - Device power status
- `access.device.emergency_status` - Emergency mode change
- `access.remote_view` - Live video stream started
- `access.unlock_schedule.*` - Schedule events
- `access.visitor.status.changed` - Visitor access changed

**Webhook Payload Example:**
```json
{
  "event_type": "access.door.unlock",
  "timestamp": "2026-07-31T10:15:00Z",
  "door_id": "e4978b83-203d-4015-97df-b86efc91cb0c",
  "door_name": "Front Door",
  "actor": {
    "user_id": "user_123",
    "name": "John Smith",
    "method": "card"  // card, app, manual, schedule
  },
  "duration": 5  // seconds
}
```

#### Emergency Functions

**Emergency Lockdown:**
```http
PUT /api/v1/developer/doors/settings/emergency
{
  "mode": "lockdown"  // or "evacuation" or "normal"
}
```

**Modes:**
- **`lockdown`** - Lock all doors, deny all access (security threat)
- **`evacuation`** - Unlock all doors, allow free egress (fire/emergency)
- **`normal`** - Restore normal operation

#### Supported Devices

| Device | Model | Features |
|--------|-------|----------|
| **Access Ultra** | UA Ultra | Reader + Hub + Camera + Doorbell |
| **Access Hub** | UA Hub | Central controller for readers |
| **Reader Pro G2** | UA G2 Pro | Card reader + keypad |
| **Reader Lite** | UA Lite | Basic card reader |
| **Door Hub Mini** | UA Hub Mini | Standalone door controller |

#### Rate Limits

- **General API:** 100 requests/minute per token
- **Webhook Delivery:** Best-effort, 30-second timeout
- **WebSocket:** Real-time, no rate limit

### Setup Instructions (Ubiquiti Access)

#### 1. **Get API Token**

1. Open UniFi Access web interface
2. Navigate to **Settings** → **Integrations**
3. Click **"Create API Token"**
4. Copy the **Bearer token**

#### 2. **Configure MediaControl**

```yaml
access_control:
  - id: "access_main"
    name: "Building Access Control"
    type: "ubiquiti_access"
    
    connection:
      host: "192.168.1.70"  # UniFi Access controller IP
      port: 443
      token: "wHFmHRuX4I7sB2oDkD6wHg"  # Your Bearer token
      verify_ssl: true
    
    webhook:
      enabled: true
      url: "https://gateway-id.mediacontrol.cloud/api/access/webhook"
      secret: "your_webhook_secret"
    
    doors:
      - door_id: "e4978b83-203d-4015-97df-b86efc91cb0c"
        name: "Front Door"
        auto_lock_delay: 5  # seconds
      
      - door_id: "f5a89c94-314e-5126-a8eg-c97fgd02dc1d"
        name: "Back Door"
        auto_lock_delay: 3
```

### Example Use Cases

**1. Doorbell → Turn on Porch Light (via KNX)**
```yaml
automation:
  - trigger:
      event: "doorbell_pressed"
      door: "Front Door"
    action:
      knx_write:
        address: "1/5/1"  # Porch light
        value: true
        dpt: "1.001"
```

**2. Meeting Started → Lock Conference Room**
```yaml
automation:
  - trigger:
      event: "meeting_started"
      room: "Conference Room A"
    action:
      access_control:
        door: "Conference Room Door"
        command: "lock_now"
```

**3. Unlock Door from MediaControl Display**
```yaml
# Display shows "Unlock Front Door" button
# User taps button → Door unlocks for 5 seconds
```

---

## CCTV Camera Integration

### Overview

**ONVIF** (Open Network Video Interface Forum) is the universal standard for IP cameras, supported by **Dahua**, **Hikvision**, **Ubiquiti**, and most other brands.

### Architecture

```
MediaControl Gateway
    ↓ ONVIF (HTTP/SOAP, port 80)
IP Camera (ONVIF-compliant)
    ↓ RTSP (port 554)
Video Stream (H.264/H.265)
```

### Supported Brands

| Brand | ONVIF Support | Notes |
|-------|---------------|-------|
| **Dahua** | ✅ Profile S, T | Must enable ONVIF + create ONVIF user |
| **Hikvision** | ✅ Profile S, T | Must enable ONVIF + create ONVIF user |
| **Ubiquiti** | ✅ Profile S, T | ONVIF enabled by default |
| **Axis** | ✅ Profile S, T, G, M | Full ONVIF support |
| **Reolink** | ✅ Profile S, T | Wide compatibility |
| **Amcrest** | ✅ Profile S, T | Full profile support |

### Features

| Feature | ONVIF Profile S | ONVIF Profile T | Support |
|---------|----------------|----------------|---------|
| **Live Stream (RTSP)** | ✅ | ✅ | H.264, H.265 |
| **PTZ Control** | ✅ | ✅ | Pan, tilt, zoom |
| **Motion Detection** | ✅ | ✅ | Events via webhook |
| **Snapshot** | ✅ | ✅ | JPEG image |
| **Two-Way Audio** | ⚠️ | ✅ | Profile T required |
| **Recording** | ❌ | ⚠️ | Via RTSP + FFmpeg |

### Setup Instructions

#### 1. **Enable ONVIF on Camera**

**Dahua:**
1. Log into camera web UI (`http://camera-ip`)
2. Go to **Setting** → **Network** → **Access Platform**
3. Select **ONVIF**
4. Check **"Enable"**
5. Click **"Add User"** → Create ONVIF user (e.g., `onvif` / `password123`)
6. Save settings

**Hikvision:**
1. Log into camera web UI
2. Go to **Configuration** → **Network** → **Advanced Settings**
3. Select **Integration Protocol**
4. Check **"Enable HIKVISION-CGI"** and **"Enable ONVIF"**
5. Create ONVIF user in **User Management**
6. Save settings

**Ubiquiti:**
- ONVIF enabled by default
- Use UniFi Protect credentials

#### 2. **Configure MediaControl**

```yaml
cctv:
  - id: "camera_front"
    name: "Front Door Camera"
    type: "onvif"
    
    connection:
      ip: "192.168.1.80"
      port: 80  # ONVIF port (HTTP)
      username: "onvif"
      password: "password123"
      onvif_profile: "profile_s"  # profile_s or profile_t
    
    stream:
      rtsp_port: 554
      main_stream_uri: "rtsp://onvif:password123@192.168.1.80:554/cam/realmonitor?channel=1&subtype=0"
      sub_stream_uri: "rtsp://onvif:password123@192.168.1.80:554/cam/realmonitor?channel=1&subtype=1"
    
    features:
      motion_detection: true
      ptz: false
      two_way_audio: false
```

#### 3. **RTSP Stream URLs**

**Common patterns:**

**Dahua:**
```
Main: rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0
Sub: rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=1
```

**Hikvision:**
```
Main: rtsp://username:password@ip:554/Streaming/channels/101
Sub: rtsp://username:password@ip:554/Streaming/channels/102
```

**Ubiquiti:**
```
Main: rtsp://username:password@ip:7447/{camera_id}
```

### ONVIF Discovery

MediaControl can auto-discover ONVIF cameras on the local network:

```python
from onvif import ONVIFCamera

# Discover cameras via WS-Discovery (multicast)
cameras = discover_onvif_cameras()

for camera in cameras:
    print(f"Found camera: {camera['name']} at {camera['ip']}")
```

### Video Streaming

**Option 1: Direct RTSP (Low Latency)**
- Display RTSP stream directly on MediaControl display
- Requires RTSP-compatible player (VLC, FFmpeg, etc.)

**Option 2: WebRTC (Browser-Compatible)**
- Convert RTSP → WebRTC for browser playback
- Uses `go2rtc` or similar transcoding server

**Option 3: HLS (Universal Compatibility)**
- Convert RTSP → HLS for maximum compatibility
- Uses FFmpeg for transcoding

### Integration with Doorbell

**Doorbell Camera Auto-Popup:**
```yaml
automation:
  - trigger:
      event: "doorbell_pressed"
      device: "Front Door Camera"
    action:
      display:
        show_video:
          camera: "Front Door Camera"
          duration: 30  # seconds
          layout: "picture_in_picture"
```

### Recording

**Record to NVR/NAS:**
```yaml
cctv:
  - id: "camera_front"
    recording:
      enabled: true
      destination: "nvr"  # or "nas"
      retention_days: 30
      motion_only: true  # Only record when motion detected
```

---

## Configuration Examples

### Example 1: Complete Smart Home

```yaml
# MediaControl Configuration
# Complete home automation integration

garage:
  - id: "garage_main"
    type: "tailwind"
    ip: "192.168.1.50"
    local_control_key: "123456"
    doors:
      - door_index: 0
        name: "Left Garage Door"
      - door_index: 1
        name: "Right Garage Door"

irrigation:
  - id: "irrigation_front"
    type: "rachio"
    api_key: "a1b2c3d4-e5f6-7890-abcd-1234567890ab"

pool:
  - id: "pool_main"
    type: "pentair_intellicenter"
    ip: "192.168.1.60"
    port: 6680

elevator:
  - id: "elevator_main"
    type: "mqtt"
    mqtt:
      broker: "192.168.1.100"
      topics:
        call: "elevator/call"
        status: "elevator/status"

access_control:
  - id: "access_main"
    type: "ubiquiti_access"
    host: "192.168.1.70"
    token: "your_bearer_token"

cctv:
  - id: "camera_front"
    type: "onvif"
    ip: "192.168.1.80"
    username: "onvif"
    password: "password123"
```

### Example 2: Automation Rules

```yaml
automations:
  # Garage opened → Turn on driveway lights (via KNX)
  - trigger:
      type: "garage_opened"
      device: "garage_main"
      door_index: 0
    action:
      knx_write:
        address: "1/6/1"  # Driveway lights
        value: true
  
  # Pool heater on → Notify via display
  - trigger:
      type: "pool_heater_on"
      device: "pool_main"
    action:
      display_notification:
        display: "kitchen_display"
        message: "Pool heater is ON"
  
  # Doorbell pressed → Show camera on TV
  - trigger:
      type: "doorbell_pressed"
      device: "camera_front"
    action:
      display_show_camera:
        display: "living_room_tv"
        camera: "camera_front"
        duration: 30
  
  # Elevator called → Announce on speakers
  - trigger:
      type: "elevator_called"
      device: "elevator_main"
      floor: 2
    action:
      audio_announcement:
        speaker_group: "hallway_speakers"
        message: "Elevator arriving at floor 2"
```

---

## API Reference

### Garage Control API

```http
# Open garage door
POST /api/garage/{garage_id}/doors/{door_index}/open

# Close garage door
POST /api/garage/{garage_id}/doors/{door_index}/close

# Get status
GET /api/garage/{garage_id}/doors/{door_index}/status

Response:
{
  "door_index": 0,
  "name": "Left Garage Door",
  "status": "closed",  // "closed", "open", "opening", "closing"
  "last_change": "2026-07-31T10:15:00Z"
}
```

### Irrigation API

```http
# Start watering zone
POST /api/irrigation/{system_id}/zones/{zone_id}/start
{
  "duration": 600  // seconds
}

# Stop watering
POST /api/irrigation/{system_id}/stop

# Get status
GET /api/irrigation/{system_id}/status

Response:
{
  "system_id": "irrigation_front",
  "status": "watering",
  "current_zone": {
    "zone_id": "zone_789",
    "name": "Front Lawn",
    "remaining": 480  // seconds
  }
}
```

### Pool Control API

```http
# Turn on pool/spa
POST /api/pool/{pool_id}/on

# Set temperature
POST /api/pool/{pool_id}/temperature
{
  "setpoint": 84  // °F
}

# Control pump speed
POST /api/pool/{pool_id}/pumps/{pump_id}/speed
{
  "rpm": 2400
}

# Get status
GET /api/pool/{pool_id}/status

Response:
{
  "pool_id": "pool_main",
  "pool": {
    "is_on": true,
    "temp": 82,
    "heater": "on",
    "setpoint": 84
  },
  "pumps": [
    {
      "id": 1,
      "status": "running",
      "rpm": 2400,
      "gpm": 60,
      "power": 1200
    }
  ]
}
```

### Access Control API

```http
# Unlock door (momentary)
POST /api/access/{system_id}/doors/{door_id}/unlock

# Lock door
POST /api/access/{system_id}/doors/{door_id}/lock

# Set temporary unlock
POST /api/access/{system_id}/doors/{door_id}/lock_rule
{
  "type": "unlock_for",
  "duration": 60  // minutes
}

# Get door status
GET /api/access/{system_id}/doors/{door_id}/status

Response:
{
  "door_id": "e4978b83...",
  "name": "Front Door",
  "status": "locked",  // "locked", "unlocked", "unknown"
  "last_event": {
    "type": "access.door.unlock",
    "actor": "John Smith",
    "method": "card",
    "timestamp": "2026-07-31T10:15:00Z"
  }
}
```

### CCTV API

```http
# Get snapshot
GET /api/cctv/{camera_id}/snapshot

Response: JPEG image

# Get RTSP stream URL
GET /api/cctv/{camera_id}/stream

Response:
{
  "camera_id": "camera_front",
  "name": "Front Door Camera",
  "main_stream": "rtsp://...",
  "sub_stream": "rtsp://...",
  "webrtc": "webrtc://..."
}

# PTZ control
POST /api/cctv/{camera_id}/ptz
{
  "command": "pan",  // pan, tilt, zoom
  "value": 10  // degrees or zoom level
}
```

---

**For support:**
- **Email:** homeautomation@mediacontrol.com
- **Website:** https://mediacontrol.com/home-automation
- **Documentation:** https://docs.mediacontrol.com

**Vendor-Specific Support:**
- **Tailwind:** https://gotailwind.com/support
- **Rachio:** https://support.rachio.com
- **Pentair:** https://www.pentair.com/pool-support
- **Hayward:** https://www.hayward-pool.com/support
- **Ubiquiti:** https://help.ui.com

