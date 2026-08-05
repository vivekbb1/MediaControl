# KNX Integration & Cloud Bridge Architecture

**Complete KNX/IP Integration, ETS Configuration Import, 2-Way Communication, Cloud Bridge**

---

## Table of Contents

1. [Overview](#overview)
2. [KNX/IP Protocol Integration](#knxip-protocol-integration)
3. [ETS Configuration Import](#ets-configuration-import)
4. [2-Way Communication](#2-way-communication)
5. [Cloud Bridge Architecture](#cloud-bridge-architecture)
6. [Gateway as KNX Bridge](#gateway-as-knx-bridge)
7. [Unified Control Interface](#unified-control-interface)
8. [Configuration](#configuration)
9. [API Reference](#api-reference)

---

## Overview

**MediaControl KNX Integration** transforms the MediaControl Gateway into a **complete KNX bridge** with:

- ✅ **KNX/IP Protocol** - Native KNX/IP (Tunneling, Routing) support
- ✅ **ETS Configuration Import** - Import ETS5/ETS6 project files (.knxproj, .xml)
- ✅ **2-Way Communication** - Read, write, subscribe to KNX group addresses
- ✅ **Cloud Bridge** - Remote access via HTTPS public URL
- ✅ **Local Storage** - Store KNX configuration on gateway
- ✅ **Unified Interface** - Single app/webpage/server for all control

### Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                    MediaControl Cloud                         │
│                  (Public HTTPS URL)                           │
│  https://abc123.mediacontrol.cloud                            │
│                                                               │
│  • Web interface (responsive, mobile-friendly)               │
│  • RESTful API (JSON)                                        │
│  • WebSocket (real-time updates)                             │
│  • User authentication (OAuth 2.0)                           │
└───────────┬───────────────────────────────────────────────────┘
            │ HTTPS (encrypted)
            │ WebSocket (real-time)
            ▼
┌───────────────────────────────────────────────────────────────┐
│              MediaControl Gateway (Local)                      │
│                                                               │
│  ┌─────────────────┐          ┌─────────────────┐           │
│  │ KNX Configuration│          │  Cloud Bridge   │           │
│  │   - ETS Import  │◀────────▶│  - HTTPS Client │           │
│  │   - Group Addr  │          │  - WebSocket    │           │
│  │   - Datapoints  │          │  - Local Cache  │           │
│  └─────────────────┘          └─────────────────┘           │
│           │                             │                     │
│           ▼                             ▼                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           KNX/IP Interface (xknx library)               │ │
│  │  • KNX/IP Tunneling (secure connection to KNX/IP GW)   │ │
│  │  • KNX/IP Routing (multicast, for multiple gateways)   │ │
│  │  • Group Address Read/Write/Subscribe                  │ │
│  │  • Datapoint Type conversion (DPT 1-255)               │ │
│  └─────────────┬───────────────────────────────────────────┘ │
└────────────────┼───────────────────────────────────────────────┘
                 │ KNX/IP (UDP 3671)
                 │ KNX Secure (optional)
                 ▼
┌───────────────────────────────────────────────────────────────┐
│                    KNX Bus Infrastructure                      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ KNX/IP       │  │ KNX Devices  │  │ KNX Devices  │       │
│  │ Gateway      │◀─│ (Lights,     │◀─│ (Blinds,     │       │
│  │ (Line/Area   │  │  Switches)   │  │  HVAC, etc.) │       │
│  │  Coupler)    │  └──────────────┘  └──────────────┘       │
│  └──────────────┘                                            │
│        ▲                                                      │
│        │ KNX TP (Twisted Pair Bus)                           │
│        │ 9600 baud                                           │
└────────┴───────────────────────────────────────────────────────┘
```

---

## KNX/IP Protocol Integration

### Overview

**KNX/IP** is the IP-based protocol for KNX home/building automation, standardized as ISO/IEC 14543-3.

**MediaControl** uses the **xknx** Python library for native KNX/IP support.

### KNX/IP Modes

#### 1. **KNX/IP Tunneling** (Recommended)

Point-to-point connection between MediaControl Gateway and KNX/IP interface.

**Advantages:**
- Secure, dedicated connection
- Low latency
- Connection status monitoring
- Supports KNX Secure (encrypted)

**Use Case:** Single MediaControl Gateway controlling one KNX installation

**Configuration:**
```yaml
knx:
  connection:
    mode: "tunneling"
    gateway_ip: "192.168.1.50"  # KNX/IP Gateway IP
    gateway_port: 3671  # Default KNX/IP port
    local_ip: "192.168.1.100"  # MediaControl Gateway IP
    
    # Optional: KNX Secure (encrypted)
    secure:
      enabled: false
      user_id: 2
      password: "knx_secure_password"
      device_auth: "knx_device_auth_code"
```

#### 2. **KNX/IP Routing** (Advanced)

Multicast-based communication, multiple devices can send/receive simultaneously.

**Advantages:**
- Multiple gateways can coexist
- No connection setup required
- Broadcasts to all devices

**Disadvantages:**
- Requires multicast-capable network
- More network traffic
- No connection status

**Use Case:** Large installations with multiple control systems

**Configuration:**
```yaml
knx:
  connection:
    mode: "routing"
    multicast_address: "224.0.23.12"  # KNX multicast address
    multicast_port: 3671
    local_ip: "192.168.1.100"
```

### Supported Features

| Feature | Tunneling | Routing |
|---------|-----------|---------|
| **Group Address Read** | ✅ | ✅ |
| **Group Address Write** | ✅ | ✅ |
| **Group Address Subscribe** | ✅ | ✅ |
| **Connection Status** | ✅ | ❌ |
| **KNX Secure** | ✅ | ❌ |
| **Multiple Gateways** | ❌ | ✅ |

---

## ETS Configuration Import

### Overview

**ETS (Engineering Tool Software)** is the official KNX configuration software. MediaControl can import ETS projects to automatically discover:

- Group addresses (e.g., `1/2/3` for "Living Room Light")
- Datapoint types (DPT 1.001 for switch, DPT 5.001 for brightness, etc.)
- Device names and locations
- Floor plans and room assignments

### Supported ETS Versions

- ✅ **ETS5** - .knxproj files (XML-based)
- ✅ **ETS6** - .knxproj files (XML-based, enhanced)
- ✅ **ETS4** - .xml export files (legacy)

### Import Process

#### 1. **Export from ETS**

**ETS5/ETS6:**
1. Open your project in ETS
2. **File** → **Export** → **Export project information**
3. Select "Group addresses" and "Datapoint types"
4. Save as `.knxproj` or `.xml`

**ETS4:**
1. **Extras** → **Export** → **Group addresses**
2. Export to `.xml`

#### 2. **Import to MediaControl**

**Via Web Interface:**
1. Open MediaControl web interface: `http://gateway-ip`
2. Navigate to **Settings** → **KNX** → **Import ETS Configuration**
3. Upload `.knxproj` or `.xml` file
4. Click **Import**
5. Review detected group addresses
6. Click **Save**

**Via API:**
```http
POST /api/knx/import-ets
Content-Type: multipart/form-data

file: project.knxproj
```

#### 3. **Parsed Information**

MediaControl extracts:

```json
{
  "project_name": "Smart Home Project",
  "ets_version": "5.7.6",
  "imported_at": "2026-07-31T10:15:00Z",
  "group_addresses": [
    {
      "address": "1/2/3",
      "name": "Living Room Light",
      "dpt": "1.001",  // Switch (on/off)
      "room": "Living Room",
      "floor": "Ground Floor",
      "comment": "Main ceiling light",
      "read": true,
      "write": true,
      "subscribe": true
    },
    {
      "address": "1/2/4",
      "name": "Living Room Dimmer",
      "dpt": "5.001",  // Scaling (0-100%)
      "room": "Living Room",
      "read": true,
      "write": true,
      "subscribe": true
    },
    {
      "address": "1/3/1",
      "name": "Living Room Blinds Position",
      "dpt": "5.001",  // Scaling (0-100%)
      "room": "Living Room",
      "read": true,
      "write": true,
      "subscribe": true
    },
    {
      "address": "2/1/1",
      "name": "Living Room Temperature",
      "dpt": "9.001",  // Temperature (°C)
      "room": "Living Room",
      "read": true,
      "write": false,
      "subscribe": true
    }
  ],
  "total_addresses": 4,
  "total_rooms": 1,
  "total_floors": 1
}
```

### Datapoint Types (DPT)

MediaControl supports **all standard KNX DPTs** (1-255):

| DPT | Name | Example | Use Case |
|-----|------|---------|----------|
| **1.001** | Switch | on/off | Lights, switches |
| **5.001** | Scaling | 0-100% | Dimmers, blinds position |
| **5.010** | Value (0-255) | 0-255 | RGB color channels |
| **7.001** | Value (2-byte) | 0-65535 | Counters |
| **9.001** | Temperature | 20.5°C | Room temperature |
| **9.004** | Lux | 500 lux | Light sensor |
| **12.001** | Counter (4-byte) | 123456 | Energy meter |
| **14.056** | Power | 1500 W | Power consumption |
| **16.001** | String (14 char) | "Hello World" | Text display |
| **232.600** | RGB | (255, 0, 0) | RGB lighting |

**Full list:** 255+ DPTs supported via xknx library

---

## 2-Way Communication

### Overview

MediaControl provides **full bidirectional communication** with KNX:

1. **Write** - Send commands to KNX (turn on light, set temperature, etc.)
2. **Read** - Request current status from KNX devices
3. **Subscribe** - Receive real-time updates when KNX devices change state

### 1. Write to KNX

**Send commands from MediaControl to KNX devices:**

```python
# Turn on Living Room Light
await knx.write("1/2/3", True)  # DPT 1.001 (Switch)

# Set dimmer to 80%
await knx.write("1/2/4", 80)  # DPT 5.001 (Scaling)

# Close blinds (100% = fully closed)
await knx.write("1/3/1", 100)  # DPT 5.001

# Set target temperature to 21°C
await knx.write("2/1/2", 21.0)  # DPT 9.001 (Temperature)

# Set RGB color to red
await knx.write("3/1/1", (255, 0, 0))  # DPT 232.600 (RGB)
```

**Via HTTP API:**
```http
POST /api/knx/write
{
  "address": "1/2/3",
  "value": true,
  "dpt": "1.001"
}
```

### 2. Read from KNX

**Request current status from KNX devices:**

```python
# Read light status
status = await knx.read("1/2/3")  # Returns: True or False

# Read dimmer value
brightness = await knx.read("1/2/4")  # Returns: 0-100

# Read temperature
temp = await knx.read("2/1/1")  # Returns: 20.5 (°C)

# Read power consumption
power = await knx.read("4/1/1")  # Returns: 1500 (W)
```

**Via HTTP API:**
```http
GET /api/knx/read?address=1/2/3

Response:
{
  "address": "1/2/3",
  "name": "Living Room Light",
  "value": true,
  "dpt": "1.001",
  "timestamp": "2026-07-31T10:15:00Z"
}
```

### 3. Subscribe to KNX Updates

**Receive real-time updates when KNX devices change state:**

```python
# Subscribe to light status changes
@knx.on_value_update("1/2/3")
async def on_light_change(address, value):
    print(f"Light {address} changed to {value}")
    # Trigger MediaControl action
    if value:
        await display_manager.turn_on("display_living_room")

# Subscribe to temperature changes
@knx.on_value_update("2/1/1")
async def on_temp_change(address, value):
    print(f"Temperature changed to {value}°C")
    # Update MediaControl display
    await display_manager.show_notification(f"Living Room: {value}°C")

# Subscribe to all group addresses in a room
for address in knx.get_room_addresses("Living Room"):
    @knx.on_value_update(address)
    async def on_update(addr, val):
        print(f"{addr} = {val}")
```

**Via WebSocket:**
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://gateway-ip:8081/knx/subscribe');

// Subscribe to group address
ws.send(JSON.stringify({
  "action": "subscribe",
  "address": "1/2/3"
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`${data.address} = ${data.value}`);
  // Update UI
  document.getElementById('light-status').innerText = data.value ? 'ON' : 'OFF';
};
```

---

## Cloud Bridge Architecture

### Overview

**MediaControl Cloud Bridge** provides secure remote access to KNX installations via **HTTPS public URL**.

**Benefits:**
- ✅ **Remote Access** - Control KNX from anywhere (mobile app, web browser)
- ✅ **Secure** - End-to-end encryption (TLS 1.3)
- ✅ **No Port Forwarding** - No need to open firewall ports
- ✅ **Dynamic DNS** - Each gateway gets a unique public URL
- ✅ **Real-Time** - WebSocket for instant updates
- ✅ **Multi-User** - Family members, staff can all access

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  User (Mobile/Web)                          │
│  https://abc123.mediacontrol.cloud                          │
└───────────┬─────────────────────────────────────────────────┘
            │ HTTPS (TLS 1.3)
            │ WebSocket (WSS)
            ▼
┌───────────────────────────────────────────────────────────────┐
│              MediaControl Cloud Server                        │
│        (cloud.mediacontrol.com - Load Balanced)               │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Web Interface  │  │  RESTful API    │  │  WebSocket   │ │
│  │  (React SPA)    │  │  (JSON)         │  │  (Real-Time) │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│           │                     │                   │         │
│           ▼                     ▼                   ▼         │
│  ┌───────────────────────────────────────────────────────┐   │
│  │          Authentication & Authorization               │   │
│  │  • OAuth 2.0 / OpenID Connect                        │   │
│  │  • JWT tokens (refresh + access)                     │   │
│  │  • Role-based access control (Admin, User, Guest)    │   │
│  └───────────────────────────────────────────────────────┘   │
│           │                                                   │
│           ▼                                                   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │           Gateway Connection Manager                  │   │
│  │  • Maintains persistent connections to gateways      │   │
│  │  • Handles reconnection (exponential backoff)        │   │
│  │  • Load balancing (multiple gateways)                │   │
│  └───────────────────────────────────────────────────────┘   │
└───────────┬───────────────────────────────────────────────────┘
            │ Outbound HTTPS (gateway → cloud)
            │ WebSocket (persistent connection)
            ▼
┌───────────────────────────────────────────────────────────────┐
│          MediaControl Gateway (Customer Premises)             │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              Cloud Bridge Client                      │   │
│  │  • Initiates outbound connection to cloud            │   │
│  │  • Maintains persistent WebSocket                    │   │
│  │  • Handles commands from cloud                       │   │
│  │  • Sends status updates to cloud                     │   │
│  │  • Local cache (works offline)                       │   │
│  └───────────────────────────────────────────────────────┘   │
│           │                                                   │
│           ▼                                                   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │           KNX/IP Interface (Local)                    │   │
│  │  • Communicates with local KNX bus                   │   │
│  │  • Stores configuration locally                      │   │
│  │  • Works even if cloud is offline                    │   │
│  └───────────────────────────────────────────────────────┘   │
└───────────┬───────────────────────────────────────────────────┘
            │ KNX/IP (UDP 3671, local network)
            ▼
┌───────────────────────────────────────────────────────────────┐
│                  KNX Bus Infrastructure                        │
└───────────────────────────────────────────────────────────────┘
```

### Gateway Registration

**1. Gateway Initialization:**
```python
# On first boot, gateway registers with cloud
gateway_id = generate_unique_id()  # e.g., "abc123def456"
public_url = f"https://{gateway_id}.mediacontrol.cloud"

# Register with cloud server
response = await cloud_client.register(
    gateway_id=gateway_id,
    name="Home Gateway",
    location="123 Main St",
    timezone="America/Los_Angeles"
)

# Store cloud credentials
save_config({
    "gateway_id": gateway_id,
    "public_url": public_url,
    "api_key": response["api_key"],
    "api_secret": response["api_secret"]
})
```

**2. Persistent Connection:**
```python
# Establish WebSocket connection to cloud
ws = await websockets.connect(
    f"wss://cloud.mediacontrol.com/gateway/{gateway_id}",
    extra_headers={
        "Authorization": f"Bearer {api_key}"
    }
)

# Keep connection alive (heartbeat every 30s)
while True:
    await ws.send(json.dumps({"type": "ping"}))
    await asyncio.sleep(30)
```

**3. Handle Cloud Commands:**
```python
async def handle_cloud_command(command):
    """Handle command from cloud"""
    if command["type"] == "knx_write":
        # Execute KNX write command
        await knx.write(
            address=command["address"],
            value=command["value"]
        )
        # Send confirmation to cloud
        await cloud_client.send_response({
            "command_id": command["id"],
            "status": "success"
        })
    
    elif command["type"] == "knx_read":
        # Execute KNX read command
        value = await knx.read(address=command["address"])
        # Send result to cloud
        await cloud_client.send_response({
            "command_id": command["id"],
            "value": value
        })
```

**4. Push Updates to Cloud:**
```python
# When KNX device changes state, push update to cloud
@knx.on_value_update("*")  # Subscribe to all addresses
async def on_knx_update(address, value):
    await cloud_client.push_update({
        "type": "knx_update",
        "address": address,
        "value": value,
        "timestamp": datetime.now().isoformat()
    })
```

### Security

**End-to-End Encryption:**
- ✅ TLS 1.3 (HTTPS/WSS)
- ✅ Certificate pinning
- ✅ JWT tokens (RS256)
- ✅ API key + API secret (HMAC-SHA256)

**Authentication:**
- ✅ OAuth 2.0 / OpenID Connect
- ✅ Multi-factor authentication (TOTP)
- ✅ Biometric (Face ID, Touch ID, fingerprint)

**Authorization:**
- ✅ Role-based access control (RBAC)
  - **Admin** - Full access (config, users, KNX)
  - **User** - Control devices, view status
  - **Guest** - View-only access

**Offline Mode:**
- ✅ Local cache (last known state)
- ✅ Local control still works (gateway → KNX)
- ✅ Sync when connection restored

---

## Gateway as KNX Bridge

### Overview

**MediaControl Gateway** acts as a **unified bridge** between:
- KNX bus (home/building automation)
- AV devices (TVs, displays, sources)
- Smart home platforms (Apple Home, Google Home, Alexa, etc.)
- Unified communications (SIP, intercom, paging)
- Cloud services (remote access, analytics)

### Integration Examples

#### 1. **KNX → MediaControl**

KNX devices trigger MediaControl actions:

```yaml
knx_to_mediacontrol:
  # KNX light switch → Turn on MediaControl display
  - knx_address: "1/1/1"  # KNX switch in living room
    knx_value: true  # Switch turned on
    mc_action: "turn_on_display"
    mc_display_id: "display_living_room"
  
  # KNX motion sensor → Turn on display
  - knx_address: "1/1/5"  # KNX motion sensor in hallway
    knx_value: true  # Motion detected
    mc_action: "turn_on_display"
    mc_display_id: "display_hallway"
    delay: 0  # Immediate
  
  - knx_address: "1/1/5"  # Same motion sensor
    knx_value: false  # No motion for 10 minutes
    mc_action: "turn_off_display"
    mc_display_id: "display_hallway"
    delay: 600  # 10 minutes
  
  # KNX scene button → Activate MediaControl preset
  - knx_address: "1/1/10"  # KNX scene button "Movie"
    knx_value: 1  # Scene activated
    mc_action: "activate_preset"
    mc_preset_id: "movie_mode"
  
  # KNX temperature → Update MediaControl display
  - knx_address: "2/1/1"  # Living room temperature
    mc_action: "update_display_text"
    mc_display_id: "display_living_room"
    mc_text_template: "Living Room: {value}°C"
```

#### 2. **MediaControl → KNX**

MediaControl actions control KNX devices:

```yaml
mediacontrol_to_knx:
  # Meeting started → Dim lights, close blinds
  - mc_event: "meeting_started"
    mc_room: "conference_room"
    knx_actions:
      - address: "1/2/1"  # Conference room lights
        value: 30  # Dim to 30%
        dpt: "5.001"
      
      - address: "1/3/1"  # Conference room blinds
        value: 100  # Close (100%)
        dpt: "5.001"
  
  # Presentation mode → Set lights to cool white, dim to 10%
  - mc_event: "preset_activated"
    mc_preset_id: "presentation_mode"
    knx_actions:
      - address: "1/2/1"  # Lights brightness
        value: 10
        dpt: "5.001"
      
      - address: "1/2/2"  # Lights color temperature
        value: 6500  # Cool white (K)
        dpt: "7.600"
  
  # Doorbell pressed → Turn on porch light
  - mc_event: "doorbell_pressed"
    mc_doorbell_id: "front_door"
    knx_actions:
      - address: "1/5/1"  # Porch light
        value: true
        dpt: "1.001"
  
  # Display turned on → Turn on KNX outlet (TV power)
  - mc_event: "display_turned_on"
    mc_display_id: "display_living_room"
    knx_actions:
      - address: "1/4/1"  # TV outlet
        value: true
        dpt: "1.001"
```

#### 3. **KNX ↔ Smart Home Platforms**

KNX devices control (and are controlled by) Apple Home, Google Home, etc.:

```yaml
knx_smart_home_bridge:
  # Expose KNX devices to Apple HomeKit
  expose_to_homekit:
    - knx_address: "1/2/1"
      name: "Living Room Lights"
      type: "light"
      dpt: "1.001"  # Switch
      room: "Living Room"
    
    - knx_address: "1/2/2"
      name: "Living Room Dimmer"
      type: "light_brightness"
      dpt: "5.001"  # Brightness 0-100%
      room: "Living Room"
    
    - knx_address: "1/3/1"
      name: "Living Room Blinds"
      type: "blind"
      dpt: "5.001"  # Position 0-100%
      room: "Living Room"
  
  # Control KNX from Apple Home
  # (Automatic - HomeKit commands → KNX write)
  
  # Example Siri command:
  # "Hey Siri, turn on Living Room Lights"
  # → MediaControl writes to KNX address 1/2/1 (value: true)
```

---

## Unified Control Interface

### Web Interface

**Single-page application (React) accessible via:**
- **Local:** `http://gateway-ip` (LAN only)
- **Cloud:** `https://abc123.mediacontrol.cloud` (anywhere)

**Features:**
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Real-time updates (WebSocket)
- ✅ KNX device control (switches, dimmers, blinds, HVAC)
- ✅ MediaControl devices (displays, sources, audio)
- ✅ Floor plans (upload custom floor plan image)
- ✅ Room view (grouped by room/floor)
- ✅ Favorites (quick access to frequently used devices)
- ✅ Scenes (one-tap shortcuts)
- ✅ Automation rules (visual editor)
- ✅ Settings (KNX config, user management, cloud settings)

### Mobile App

**Native apps for iOS and Android:**
- ✅ Native performance
- ✅ Push notifications (doorbell, alarms, alerts)
- ✅ Widgets (iOS/Android home screen)
- ✅ Voice control (Siri, Google Assistant)
- ✅ Biometric authentication
- ✅ Offline mode (local control when on same network)

### API

**RESTful API (JSON):**
```http
# Get KNX device status
GET /api/knx/device/{address}

# Control KNX device
POST /api/knx/device/{address}
{
  "value": true
}

# Get MediaControl display status
GET /api/display/{display_id}

# Control MediaControl display
POST /api/display/{display_id}/power
{
  "power": true
}

# Activate scene
POST /api/scene/{scene_id}/activate
```

**WebSocket (Real-Time):**
```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://abc123.mediacontrol.cloud/ws');

// Subscribe to updates
ws.send(JSON.stringify({
  "action": "subscribe",
  "topics": ["knx/*", "display/*", "doorbell/*"]
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
  // Update UI
};
```

---

(Continued in next file due to length...)

---

## Configuration

### Complete Configuration Example

```yaml
knx:
  # Enable KNX integration
  enabled: true
  
  # KNX/IP Connection
  connection:
    mode: "tunneling"  # or "routing"
    gateway_ip: "192.168.1.50"
    gateway_port: 3671
    local_ip: "192.168.1.100"
    
    # Optional: KNX Secure
    secure:
      enabled: false
      user_id: 2
      password: "your_secure_password"
      device_auth: "your_device_auth"
  
  # ETS Configuration
  ets_import:
    # Path to imported ETS project
    config_file: "/var/lib/mediacontrol/knx_config.json"
    
    # Auto-import on startup
    auto_import: true
    
    # Sync with ETS on change detection
    auto_sync: false
  
  # Group Addresses (manual configuration if not using ETS import)
  group_addresses:
    - address: "1/2/3"
      name: "Living Room Light"
      dpt: "1.001"
      room: "Living Room"
      read: true
      write: true
      subscribe: true
      
    - address: "1/2/4"
      name: "Living Room Dimmer"
      dpt: "5.001"
      room: "Living Room"
      read: true
      write: true
      subscribe: true
  
  # Integration with MediaControl
  integration:
    # KNX → MediaControl
    knx_to_mc:
      - knx_address: "1/1/1"
        knx_value: true
        mc_action: "turn_on_display"
        mc_display_id: "display_living_room"
    
    # MediaControl → KNX
    mc_to_knx:
      - mc_event: "meeting_started"
        mc_room: "conference_room"
        knx_actions:
          - address: "1/2/1"
            value: 30
            dpt: "5.001"
  
  # Cloud Bridge
  cloud:
    enabled: true
    
    # Cloud server URL
    server_url: "https://cloud.mediacontrol.com"
    
    # Gateway credentials (auto-generated on first boot)
    gateway_id: "abc123def456"
    api_key: "your_api_key"
    api_secret: "your_api_secret"
    
    # Public URL (auto-assigned)
    public_url: "https://abc123.mediacontrol.cloud"
    
    # Connection settings
    reconnect:
      enabled: true
      max_retries: -1  # Infinite
      backoff: "exponential"  # exponential, linear, constant
      initial_delay: 1  # seconds
      max_delay: 300  # seconds (5 minutes)
    
    # Local cache (for offline mode)
    cache:
      enabled: true
      ttl: 3600  # 1 hour
```

---

## API Reference

### KNX Read/Write API

#### Write to KNX Group Address

```http
POST /api/knx/write

Request:
{
  "address": "1/2/3",
  "value": true,
  "dpt": "1.001"
}

Response:
{
  "status": "success",
  "address": "1/2/3",
  "value": true,
  "timestamp": "2026-07-31T10:15:00Z"
}
```

#### Read from KNX Group Address

```http
GET /api/knx/read?address=1/2/3

Response:
{
  "address": "1/2/3",
  "name": "Living Room Light",
  "value": true,
  "dpt": "1.001",
  "timestamp": "2026-07-31T10:15:00Z"
}
```

#### Get All Group Addresses

```http
GET /api/knx/addresses

Response:
{
  "total": 50,
  "addresses": [
    {
      "address": "1/2/3",
      "name": "Living Room Light",
      "dpt": "1.001",
      "room": "Living Room",
      "value": true,
      "last_update": "2026-07-31T10:15:00Z"
    },
    ...
  ]
}
```

### ETS Import API

#### Import ETS Configuration

```http
POST /api/knx/import-ets
Content-Type: multipart/form-data

file: project.knxproj

Response:
{
  "status": "success",
  "project_name": "Smart Home Project",
  "imported_addresses": 50,
  "imported_rooms": 10,
  "imported_floors": 2
}
```

#### Get Import Status

```http
GET /api/knx/import-status

Response:
{
  "last_import": "2026-07-31T10:00:00Z",
  "project_name": "Smart Home Project",
  "ets_version": "5.7.6",
  "total_addresses": 50
}
```

### Cloud Bridge API

#### Register Gateway

```http
POST https://cloud.mediacontrol.com/api/gateway/register

Request:
{
  "name": "Home Gateway",
  "location": "123 Main St",
  "timezone": "America/Los_Angeles"
}

Response:
{
  "gateway_id": "abc123def456",
  "public_url": "https://abc123.mediacontrol.cloud",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret"
}
```

#### Get Gateway Status

```http
GET https://abc123.mediacontrol.cloud/api/gateway/status

Response:
{
  "gateway_id": "abc123def456",
  "online": true,
  "last_seen": "2026-07-31T10:15:00Z",
  "knx_connected": true,
  "knx_addresses": 50,
  "uptime": 86400  // seconds
}
```

---

## Best Practices

### KNX/IP Connection

✅ **Use Tunneling for single gateway** - More reliable than routing  
✅ **Reserve IP address** - Assign static IP to KNX/IP gateway  
✅ **Monitor connection status** - Set up alerts for disconnections  
✅ **Use KNX Secure** - For enhanced security (if supported by hardware)  
✅ **Test read/write** - Verify communication before deploying  

### ETS Configuration

✅ **Keep ETS project up-to-date** - Re-import after changes  
✅ **Use descriptive names** - "Living Room Light" not "Light 1"  
✅ **Organize by room/floor** - Makes navigation easier  
✅ **Document group addresses** - Add comments in ETS  
✅ **Backup ETS project** - Store .knxproj files safely  

### Cloud Bridge

✅ **Enable HTTPS** - Always use secure connection  
✅ **Use strong passwords** - Enable MFA for cloud access  
✅ **Monitor connection** - Set up alerts for offline gateways  
✅ **Local cache** - Ensure offline mode works  
✅ **Rate limiting** - Prevent API abuse  

### Security

✅ **Use KNX Secure** - If hardware supports it  
✅ **Firewall rules** - Block KNX/IP port (3671) from internet  
✅ **VPN** - For remote access (alternative to cloud)  
✅ **User authentication** - Enable for web interface  
✅ **Audit logs** - Track who controls what  

---

**For KNX integration support:**  
**Email:** knx@mediacontrol.com  
**Website:** https://mediacontrol.com/knx
