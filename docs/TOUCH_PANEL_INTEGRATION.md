# Touch Panel Integration Guide

**Enterprise Touch Panel Support for Microsoft Teams Rooms & Meeting Spaces**

---

## Table of Contents

1. [Overview](#overview)
2. [Supported Touch Panel Types](#supported-touch-panel-types)
3. [Hardware Requirements](#hardware-requirements)
4. [Connection Methods](#connection-methods)
5. [Microsoft Teams Room Touch Panels](#microsoft-teams-room-touch-panels)
6. [Enterprise Control Panels](#enterprise-control-panels)
7. [Custom Web-Based Panels](#custom-web-based-panels)
8. [Configuration Examples](#configuration-examples)
9. [Touch Input Routing](#touch-input-routing)
10. [API Reference](#api-reference)
11. [Common Deployments](#common-deployments)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The **MediaControl Gateway** supports comprehensive touch panel integration for:

- **Microsoft Teams Rooms** (Logitech Tap, Crestron Flex, Poly G100)
- **Enterprise control panels** (Crestron, Extron, AMX)
- **KNX touch visualizations** (Gira, Jung, ABB)
- **Custom web panels** (iPad, Android tablets, wall-mounted displays)
- **Interactive displays** (Smart boards, touch monitors)

### Key Features

✅ **USB Touch Input Routing** - Route touch panels between sources (Teams device, laptops, PCs)  
✅ **IP/Ethernet Control** - Web-based panels for room control  
✅ **Native Protocol Support** - Crestron CH5, Extron SIS, AMX RMS  
✅ **Multi-Panel Support** - Multiple touch panels per room  
✅ **Automatic Routing** - Context-aware touch input switching  
✅ **Bidirectional Feedback** - Panel displays current room state

---

## Supported Touch Panel Types

### 1. USB Touch Panels (HID)

**Description:** Touch panels that connect via USB and appear as HID touch input devices.

**Examples:**
- Logitech Tap (Teams Room controller)
- Crestron TSW-770 (with USB connection)
- Poly G100 (Teams Room console)
- Generic USB touch monitors

**Connection:** USB-A or USB-C to MediaControl Gateway

**Use Cases:**
- Teams Room control surfaces
- Touch monitors for source control
- Interactive displays

---

### 2. IP/Ethernet Touch Panels

**Description:** Web-based or native-protocol panels that communicate over Ethernet.

**Examples:**
- Crestron TSW-770 (Ethernet mode)
- Extron TouchLink Pro
- AMX Modero X
- KNX touch panels (Gira, Jung, ABB)
- iPad/Android tablets running control apps

**Connection:** Ethernet to local network

**Use Cases:**
- Wall-mounted control panels
- Mobile device control (BYOD)
- KNX visualization systems
- Enterprise AV control

---

### 3. Serial Touch Panels (RS232/RS485)

**Description:** Legacy touch panels using serial communication.

**Examples:**
- Crestron TPMC series (older models)
- AMX MVP series
- Extron IPL Pro series (serial mode)

**Connection:** RS232/RS485 port on gateway

**Use Cases:**
- Legacy system integration
- Retrofit installations

---

### 4. Custom Web Panels

**Description:** Browser-based control interfaces hosted by the gateway.

**Examples:**
- MediaControl web UI
- KNX widget (embedded)
- Custom React/Vue frontends

**Connection:** HTTPS to gateway's web server

**Use Cases:**
- Universal control (any device with browser)
- No dedicated hardware needed
- Cost-effective deployments

---

## Hardware Requirements

### MediaControl Gateway KVM Models

| Model | USB Touch Panels | IP Touch Panels | Serial Panels | Web Panels |
|-------|------------------|-----------------|---------------|------------|
| **MCG-400K** | 2× USB | Unlimited (network) | 2× RS232/485 | ✅ Built-in |
| **MCG-600K** | 2× USB | Unlimited (network) | 2× RS232/485 | ✅ Built-in |
| **MCG-Pro** | 4× USB | Unlimited (network) | 2× RS232/485 | ✅ Built-in |

### Gateway Hardware Additions (for Touch Support)

**No additional hardware needed!** The existing KVM gateway supports:
- ✅ USB-A/USB-C ports for USB touch panels
- ✅ Gigabit Ethernet for IP panels
- ✅ RS232/RS485 ports for serial panels
- ✅ Built-in web server for custom panels

### Optional: Touch Display Output

**For integrated touch displays:**
- Connect HDMI output to touch monitor
- Connect monitor's USB touch input back to gateway
- Gateway routes touch input to appropriate source

```
┌──────────────────────────────────────────────────┐
│              Touch Monitor                       │
│  (Display shows current source)                  │
│                                                  │
│  HDMI Input ◄───────── HDMI Output (Gateway)    │
│  USB Touch ─────────► USB Input (Gateway)       │
└──────────────────────────────────────────────────┘
```

---

## Connection Methods

### Method 1: USB Touch Panel (Direct Connection)

**Best for:** Teams Room controllers, touch monitors

```yaml
touch_panels:
  - id: "teams_tap"
    name: "Logitech Tap (Teams Controller)"
    type: "usb_hid"
    connection:
      port: "usb_a_1"
      dedicated_to: "teams_room"  # Always connected to Teams device
    
    features:
      touch_input: true
      display: true  # Has built-in display
      audio_controls: true
      call_controls: true
```

**Physical Setup:**
1. Plug Logitech Tap USB cable into gateway USB-A port 1
2. Gateway routes touch input to Teams Room device
3. Tap controls Teams application on Teams device

---

### Method 2: IP Touch Panel (Ethernet)

**Best for:** Wall-mounted panels, tablets, KNX systems

```yaml
touch_panels:
  - id: "crestron_wall_panel"
    name: "Crestron TSW-770 (Wall Mount)"
    type: "ip_ethernet"
    connection:
      ip_address: "192.168.1.50"
      protocol: "crestron_ch5"  # or "http", "websocket", "extron_sis"
      port: 41794
    
    features:
      room_control: true
      source_switching: true
      climate_control: true  # If integrated with HVAC
      lighting_control: true  # If integrated with lighting
```

**Physical Setup:**
1. Connect panel to network via Ethernet
2. Configure panel IP address (static recommended)
3. Gateway communicates with panel via Crestron CH5 protocol
4. Panel displays room controls, gateway responds to commands

---

### Method 3: Web Panel (Browser-Based)

**Best for:** BYOD, universal access, cost-effective

```yaml
touch_panels:
  - id: "web_tablet"
    name: "iPad Control (Web Browser)"
    type: "web_browser"
    connection:
      url: "https://gateway.local/room/boardroom"
      authentication: "token"
      token: "room_abc123_token"
    
    features:
      responsive_ui: true
      offline_mode: false
      theme: "auto"  # day/night/system
```

**Physical Setup:**
1. Mount iPad/Android tablet on wall (optional)
2. Open browser to gateway URL
3. Authenticate with room token
4. Control room from browser

---

## Microsoft Teams Room Touch Panels

### Overview

Microsoft Teams Rooms use dedicated touch controllers for call management.

**Common Controllers:**
- **Logitech Tap** - 10.1" touchscreen, USB, most popular
- **Crestron Flex** - 7" touchscreen, USB + network
- **Poly G100** - 7" console, USB
- **Lenovo ThinkSmart Core** - Integrated compute + touch
- **Yealink MeetingBoard** - All-in-one display + touch

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Teams Room Setup                          │
│                                                             │
│  ┌──────────────┐                                          │
│  │ Logitech Tap │  USB                                     │
│  │ (Controller) ├────────┐                                 │
│  └──────────────┘        │                                 │
│                          ▼                                  │
│                  ┌───────────────────┐                     │
│                  │  MediaControl     │  USB-C              │
│                  │  Gateway          ├──────────┐          │
│                  │  (MCG-400K)       │          │          │
│                  └────────┬──────────┘          │          │
│                           │ HDMI                │          │
│                           ▼                     ▼          │
│                    ┌──────────┐      ┌──────────────────┐ │
│                    │ Display  │      │ Teams Room Device│ │
│                    │ (Monitor)│      │ (Android/Win 10) │ │
│                    └──────────┘      └──────────────────┘ │
│                                                             │
│  Flow:                                                      │
│  1. User taps "Join Meeting" on Tap                        │
│  2. Tap sends USB HID command                              │
│  3. Gateway routes command to Teams device                 │
│  4. Teams device joins meeting                             │
│  5. Gateway routes HDMI video to display                   │
└────────────────────────────────────────────────────────────┘
```

### Configuration

```yaml
# Microsoft Teams Room with Logitech Tap

sources:
  - id: "teams_room"
    name: "Microsoft Teams Room"
    hdmi_port: 1
    device_type: "mtr"
    usb_connection: "usb_c_1"
    
    # Touch panel configuration
    touch_panels:
      - id: "logitech_tap"
        name: "Logitech Tap"
        type: "usb_hid"
        usb_port: "usb_a_1"
        dedicated: true  # Always for Teams device
        
        # Features supported
        capabilities:
          call_controls: true      # Join, mute, hang up
          volume_controls: true    # Audio level
          camera_controls: true    # Pan, tilt, zoom (if supported)
          content_sharing: true    # Start/stop screen share
          roster_display: true     # Show participants
          
        # Automatic behaviors
        auto_behaviors:
          wake_on_touch: true           # Wake display when touched
          switch_source_on_call: true   # Auto-switch to Teams on meeting start
          dim_when_idle: true           # Dim panel after 5 min idle
          idle_timeout: 300             # seconds
          
  - id: "user_laptop"
    name: "User Laptop (BYOD)"
    hdmi_port: 2
    device_type: "laptop"
    
    # Laptop can use wall-mounted IP panel for control
    touch_panels:
      - id: "wall_panel"
        name: "Crestron Wall Panel"
        type: "ip_ethernet"
        ip_address: "192.168.1.50"
        shared: true  # Shared between sources
```

### Logitech Tap Setup

**Step 1: Physical Connection**
```bash
# Connect Logitech Tap USB cable to gateway USB-A port 1
# Connect Teams Room device to gateway USB-C port 1
```

**Step 2: Gateway Configuration**
```yaml
touch_panels:
  - id: "logitech_tap"
    type: "usb_hid"
    usb_port: "usb_a_1"
    routed_to: "teams_room"
    
    device_info:
      vendor_id: "0x046d"  # Logitech
      product_id: "0x0893"  # Tap
      manufacturer: "Logitech"
      product: "Logi Tap"
```

**Step 3: Verify Detection**
```bash
# Via API
GET /api/touch-panels/status

Response:
{
  "touch_panels": [
    {
      "id": "logitech_tap",
      "name": "Logi Tap",
      "connected": true,
      "routed_to": "teams_room",
      "status": "active",
      "last_activity": "2026-07-31T08:55:23Z"
    }
  ]
}
```

**Step 4: Test Touch Input**
- Tap "Join Meeting" button on Tap
- Gateway routes USB HID command to Teams device
- Teams device joins meeting

### Crestron Flex Setup

**Crestron Flex** has both USB and Ethernet connections.

**Dual-Mode Configuration:**
```yaml
touch_panels:
  - id: "crestron_flex"
    name: "Crestron Flex UC"
    type: "hybrid"  # USB + Ethernet
    
    # USB connection for touch input (to Teams device)
    usb:
      port: "usb_a_2"
      routed_to: "teams_room"
    
    # Ethernet connection for advanced control (to gateway)
    ip:
      ip_address: "192.168.1.51"
      protocol: "crestron_ch5"
      port: 41794
      
    # Use Ethernet for custom controls beyond Teams
    custom_controls:
      lighting: true
      shades: true
      temperature: true
```

**Why Dual-Mode?**
- **USB to Teams device:** Standard Teams room controls (join, mute, etc.)
- **Ethernet to Gateway:** Advanced room controls (lights, shades, presets)

---

## Enterprise Control Panels

### Crestron Touch Panels

#### Crestron TSW-770 (7" Touch Panel)

**Connection:** Ethernet (Crestron CH5 protocol)

```yaml
touch_panels:
  - id: "crestron_tsw770"
    name: "Crestron TSW-770"
    type: "ip_ethernet"
    connection:
      ip_address: "192.168.1.60"
      protocol: "crestron_ch5"
      port: 41794
    
    # Gateway runs Crestron CH5 server
    gateway_server:
      enabled: true
      port: 41794
      ssl: true
      
    # UI pages on panel
    pages:
      - name: "Main"
        controls:
          - type: "source_selector"
            sources: ["teams_room", "laptop", "apple_tv", "cable_tv"]
          - type: "volume_slider"
            targets: ["main_display", "speakers"]
          - type: "preset_buttons"
            presets: ["presentation", "video_call", "entertainment"]
            
      - name: "Climate"
        controls:
          - type: "temperature_control"
            hvac_integration: "knx"
            
      - name: "Lighting"
        controls:
          - type: "scene_buttons"
            scenes: ["meeting", "presentation", "dim", "off"]
```

**Crestron SIMPL Windows Programming:**

```csharp
// Crestron SIMPL# code example
// Gateway provides TCP server at port 41794

public class MediaControlGateway
{
    // Source switching
    public void SwitchSource(string sourceId)
    {
        // Send to gateway
        SendCommand($"SOURCE:SELECT:{sourceId}");
    }
    
    // Volume control
    public void SetVolume(int level)
    {
        SendCommand($"VOLUME:SET:{level}");
    }
    
    // Preset activation
    public void ActivatePreset(string presetName)
    {
        SendCommand($"PRESET:ACTIVATE:{presetName}");
    }
    
    // Receive status updates from gateway
    public void OnStatusUpdate(string status)
    {
        // Update panel display
        if (status.StartsWith("SOURCE:ACTIVE:"))
        {
            string activeSource = status.Split(':')[2];
            UpdateSourceIndicator(activeSource);
        }
    }
}
```

---

### Extron Touch Panels

#### Extron TouchLink Pro TLP Pro 720T (7" Touch Panel)

**Connection:** Ethernet (Extron SIS protocol)

```yaml
touch_panels:
  - id: "extron_tlp720"
    name: "Extron TouchLink Pro 720T"
    type: "ip_ethernet"
    connection:
      ip_address: "192.168.1.61"
      protocol: "extron_sis"
      port: 23  # Telnet-based
    
    # Gateway runs Extron SIS server
    gateway_server:
      enabled: true
      port: 23
      protocol: "telnet"
      
    # SIS command mapping
    commands:
      source_switch: "1*{source_id}!"
      volume_set: "V{level}AU"
      mute_toggle: "ZAU"
```

**Extron Global Scripter Code:**

```javascript
// Extron Global Scripter example
// Connect to gateway via TCP

var gateway = new TCPClient("192.168.1.100", 23);

// Switch to source 1
function switchToSource1() {
    gateway.send("1*1!\r\n");
}

// Set volume to 50%
function setVolume50() {
    gateway.send("V50AU\r\n");
}

// Receive status from gateway
gateway.onReceive = function(data) {
    if (data.includes("SOURCE:ACTIVE:")) {
        var source = data.split(":")[2];
        updatePanelDisplay(source);
    }
};
```

---

### AMX Touch Panels

#### AMX Modero X Series (NXD-1000Vi)

**Connection:** Ethernet (AMX protocol)

```yaml
touch_panels:
  - id: "amx_modero_x"
    name: "AMX Modero X NXD-1000Vi"
    type: "ip_ethernet"
    connection:
      ip_address: "192.168.1.62"
      protocol: "amx_native"
      port: 1319
    
    # Gateway runs AMX NetLinx server emulation
    gateway_server:
      enabled: true
      port: 1319
      device_id: 10001
      
    # Button mappings
    buttons:
      1: "source_teams_room"
      2: "source_laptop"
      3: "source_apple_tv"
      4: "source_cable_tv"
      11: "preset_presentation"
      12: "preset_video_call"
```

**AMX NetLinx Code:**

```netlinx
// AMX NetLinx code example
DEFINE_DEVICE
dvGateway = 0:1:0  // MediaControl Gateway (IP connection)
dvPanel = 10001:1:0  // AMX Panel

DEFINE_EVENT

// Button press events
BUTTON_EVENT[dvPanel, 1]  // Teams Room button
{
    PUSH:
    {
        SEND_STRING dvGateway, "'SOURCE:SELECT:teams_room',13"
    }
}

BUTTON_EVENT[dvPanel, 2]  // Laptop button
{
    PUSH:
    {
        SEND_STRING dvGateway, "'SOURCE:SELECT:laptop',13"
    }
}

// Receive status from gateway
DATA_EVENT[dvGateway]
{
    STRING:
    {
        // Parse gateway status and update panel
        IF(FIND_STRING(DATA.TEXT,'SOURCE:ACTIVE:',1))
        {
            // Update button feedback
        }
    }
}
```

---

## Custom Web-Based Panels

### React Web Panel

**Gateway hosts a React-based control interface.**

```yaml
touch_panels:
  - id: "web_panel_ipad"
    name: "iPad Wall Mount (Web)"
    type: "web_browser"
    connection:
      url: "https://gateway.local/room/boardroom"
      authentication: "token"
      token: "room_boardroom_token_abc123"
    
    features:
      responsive: true
      pwa: true  # Progressive Web App (works offline)
      theme: "auto"
      language: "en"
      
    ui_components:
      - source_selector
      - volume_controls
      - preset_buttons
      - climate_controls
      - lighting_scenes
      - now_playing  # Show current media
```

**Frontend Implementation:**

```typescript
// React component for web panel
import React, { useState, useEffect } from 'react';

interface WebPanelProps {
  roomId: string;
  token: string;
}

const WebPanel: React.FC<WebPanelProps> = ({ roomId, token }) => {
  const [sources, setSources] = useState([]);
  const [activeSource, setActiveSource] = useState(null);
  
  // WebSocket connection to gateway
  useEffect(() => {
    const ws = new WebSocket(`wss://gateway.local/ws?token=${token}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'SOURCE_CHANGED') {
        setActiveSource(data.source_id);
      }
    };
    
    return () => ws.close();
  }, [token]);
  
  // Fetch available sources
  useEffect(() => {
    fetch(`/api/rooms/${roomId}/sources`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setSources(data.sources));
  }, [roomId, token]);
  
  // Switch source
  const handleSourceSwitch = (sourceId: string) => {
    fetch(`/api/rooms/${roomId}/switch-source`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ source_id: sourceId })
    });
  };
  
  return (
    <div className="web-panel">
      <h2>Room Control</h2>
      
      {/* Source selector */}
      <div className="source-selector">
        {sources.map(source => (
          <button
            key={source.id}
            className={activeSource === source.id ? 'active' : ''}
            onClick={() => handleSourceSwitch(source.id)}
          >
            {source.name}
          </button>
        ))}
      </div>
      
      {/* Volume control */}
      <VolumeSlider roomId={roomId} token={token} />
      
      {/* Presets */}
      <PresetButtons roomId={roomId} token={token} />
    </div>
  );
};
```

---

## Touch Input Routing

### USB Touch Panel Routing

**Problem:** USB touch panel connected to gateway needs to send touch input to the active source.

**Solution:** Gateway acts as USB hub and routes touch input dynamically.

```
┌─────────────────────────────────────────────────────┐
│               Touch Monitor                          │
│  (User touches screen to control application)       │
│                                                      │
│  USB Touch Output ──────────┐                       │
└─────────────────────────────┼───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────┐
│          MediaControl Gateway (USB Routing)          │
│                                                      │
│  USB Touch Input ───► USB Routing Logic             │
│                           │                          │
│                     ┌─────┴──────┬─────────────┐   │
│                     ▼            ▼             ▼    │
│              ┌──────────┐  ┌──────────┐  ┌──────┐  │
│              │ Source 1 │  │ Source 2 │  │ Src 3│  │
│              │ (Active) │  │          │  │      │  │
│              └──────────┘  └──────────┘  └──────┘  │
└─────────────────────────────────────────────────────┘
```

**Configuration:**

```yaml
touch_panels:
  - id: "touch_monitor"
    name: "32\" Touch Display"
    type: "usb_hid"
    usb_port: "usb_a_3"
    
    # Touch routing behavior
    routing:
      mode: "follow_active_source"  # or "manual", "dedicated"
      
      # Route touch to whichever source is active on main display
      follow_display: "main_display"
      
      # Delay before routing (to prevent accidental switches)
      switch_delay_ms: 100
      
    # Touch calibration (if needed)
    calibration:
      enabled: false
      points: []  # Calibration points
```

**Routing Modes:**

1. **Follow Active Source** (default)
   - Touch input routes to whichever source is active on specified display
   - Use case: Single touch monitor controlling multiple PCs

2. **Manual Routing**
   - Touch input routes based on explicit API commands
   - Use case: Complex multi-display setups

3. **Dedicated**
   - Touch input always routes to specific source
   - Use case: Touch panel for Teams Room controller (always Teams device)

---

## API Reference

### Touch Panel Endpoints

#### List Touch Panels

```http
GET /api/touch-panels

Response:
{
  "touch_panels": [
    {
      "id": "logitech_tap",
      "name": "Logitech Tap",
      "type": "usb_hid",
      "connected": true,
      "routed_to": "teams_room",
      "status": "active",
      "last_activity": "2026-07-31T08:55:23Z",
      "capabilities": {
        "touch_input": true,
        "display": true,
        "audio_controls": true
      }
    },
    {
      "id": "crestron_panel",
      "name": "Crestron TSW-770",
      "type": "ip_ethernet",
      "connected": true,
      "ip_address": "192.168.1.60",
      "protocol": "crestron_ch5",
      "status": "active",
      "last_activity": "2026-07-31T08:56:10Z"
    }
  ]
}
```

#### Route Touch Panel

```http
POST /api/touch-panels/{panel_id}/route
Content-Type: application/json

{
  "target_source": "laptop",
  "reason": "user_switched_source"
}

Response:
{
  "status": "success",
  "panel_id": "touch_monitor",
  "routed_to": "laptop",
  "timestamp": "2026-07-31T08:57:00Z"
}
```

#### Get Touch Panel Status

```http
GET /api/touch-panels/{panel_id}/status

Response:
{
  "id": "logitech_tap",
  "name": "Logitech Tap",
  "connected": true,
  "routed_to": "teams_room",
  "input_events_last_minute": 45,
  "battery_level": null,
  "firmware_version": "1.12.45",
  "capabilities": {
    "touch_input": true,
    "multi_touch": true,
    "max_touch_points": 10,
    "display_resolution": "1280x800",
    "audio_output": true,
    "microphone_input": false
  }
}
```

#### Send Command to IP Panel

```http
POST /api/touch-panels/{panel_id}/send-command
Content-Type: application/json

{
  "command": "UPDATE_SOURCE_INDICATOR",
  "parameters": {
    "active_source": "teams_room",
    "button_id": 1,
    "state": "active"
  }
}

Response:
{
  "status": "success",
  "panel_id": "crestron_panel",
  "command_sent": true
}
```

---

## Common Deployments

### Deployment 1: Microsoft Teams Room (Standard)

**Components:**
- 1× Teams Room device (Lenovo ThinkSmart Core)
- 1× Logitech Tap (USB controller)
- 1× MediaControl Gateway MCG-400K
- 1× Main display (65" TV)
- 1× Crestron TSW-770 (wall panel for room control)

**Configuration:**

```yaml
room:
  id: "conf_room_a"
  name: "Conference Room A"
  
sources:
  - id: "teams_room"
    name: "Microsoft Teams Room"
    hdmi_port: 1
    usb_connection: "usb_c_1"
    device_type: "mtr"
    
  - id: "user_laptop"
    name: "User Laptop (BYOD)"
    hdmi_port: 2
    usb_connection: "usb_c_1"  # Same port, switches
    device_type: "laptop"

displays:
  - id: "main_display"
    name: "Main Display (65\" TV)"
    hdmi_port: 1
    default_source: "teams_room"

touch_panels:
  # Logitech Tap - dedicated to Teams device
  - id: "logitech_tap"
    name: "Logitech Tap"
    type: "usb_hid"
    usb_port: "usb_a_1"
    routed_to: "teams_room"
    dedicated: true
    
  # Crestron wall panel - room control
  - id: "crestron_wall"
    name: "Crestron TSW-770 (Wall)"
    type: "ip_ethernet"
    ip_address: "192.168.1.60"
    protocol: "crestron_ch5"
    controls:
      - source_switching
      - volume_control
      - lighting_scenes
      - temperature_control
```

**User Experience:**

1. **Teams Meeting:**
   - User taps "Join" on Logitech Tap
   - Teams Room joins meeting
   - Main display shows meeting

2. **Laptop Presentation:**
   - User plugs laptop into USB-C
   - Gateway auto-switches to laptop HDMI
   - User uses Crestron wall panel to adjust volume
   - Teams meeting continues (audio stays on Teams device)

3. **Room Controls:**
   - User uses Crestron panel to dim lights
   - User adjusts temperature
   - User activates "Presentation" preset

---

### Deployment 2: Executive Office (Multi-PC + Touch)

**Components:**
- 3× PCs (Windows work, Mac personal, Linux dev)
- 1× Apple TV
- 2× Displays (27" monitors)
- 1× MediaControl Gateway MCG-Pro
- 1× iPad Pro (wall-mounted, web panel)
- 1× Wireless keyboard/mouse

**Configuration:**

```yaml
room:
  id: "exec_office"
  name: "Executive Office"
  
sources:
  - id: "work_pc"
    hdmi_port: 1
  - id: "mac"
    hdmi_port: 2
  - id: "linux_dev"
    hdmi_port: 3
  - id: "apple_tv"
    hdmi_port: 4

displays:
  - id: "left_monitor"
    hdmi_port: 1
  - id: "right_monitor"
    hdmi_port: 2

touch_panels:
  # iPad wall mount with web UI
  - id: "ipad_control"
    name: "iPad Pro (Wall Mount)"
    type: "web_browser"
    url: "https://gateway.local/room/exec-office"
    token: "exec_office_token_xyz"
    
    ui_components:
      - source_selector
      - display_routing
      - volume_controls
      - preset_buttons
      - now_playing
```

**User Experience:**

- Tap "Work PC" on iPad → Windows PC shows on left monitor
- Tap "Mac" on iPad → Mac shows on right monitor
- Wireless keyboard/mouse routes to active source
- Quick presets: "Coding" (Windows + Linux), "Email" (Mac + Apple TV)

---

### Deployment 3: Classroom (Interactive Display)

**Components:**
- 1× Teacher PC (Windows)
- 1× Student laptop dock (HDMI + USB-C)
- 1× 86" Interactive Smart Board (touch display)
- 1× MediaControl Gateway MCG-400K
- 1× Document camera

**Configuration:**

```yaml
room:
  id: "classroom_101"
  name: "Classroom 101"
  
sources:
  - id: "teacher_pc"
    hdmi_port: 1
    default: true
    
  - id: "student_laptop"
    hdmi_port: 2
    auto_switch_on_connect: true
    
  - id: "doc_camera"
    hdmi_port: 3

displays:
  - id: "smart_board"
    name: "86\" Interactive Display"
    hdmi_port: 1
    touch_input_usb: "usb_a_1"

touch_panels:
  # Smart board's built-in touch
  - id: "smart_board_touch"
    name: "Smart Board Touch Input"
    type: "usb_hid"
    usb_port: "usb_a_1"
    routing:
      mode: "follow_active_source"
      follow_display: "smart_board"
```

**User Experience:**

1. **Normal Teaching:**
   - Teacher PC active, touch works on teacher's applications
   - Teacher annotates on screen

2. **Student Presentation:**
   - Student plugs laptop into USB-C dock
   - Gateway auto-switches to student laptop
   - Touch input automatically routes to student laptop
   - Student controls their presentation via touch

3. **Document Camera:**
   - Teacher taps "Doc Camera" button
   - Live document camera feed shows
   - Touch disabled (doc camera doesn't accept touch input)

---

## Troubleshooting

### USB Touch Panel Not Detected

**Symptom:** USB touch panel plugged in but not showing in gateway

**Solutions:**

1. **Check USB connection:**
   ```bash
   # Via API
   GET /api/usb-devices
   
   # Should list all connected USB devices
   ```

2. **Verify USB port:**
   - Try different USB port on gateway
   - Ensure USB cable supports data (not charge-only)

3. **Check device compatibility:**
   ```bash
   # Get USB device info
   GET /api/usb-devices/{device_id}
   
   # Look for HID touch interface
   # Should have interface class 0x03 (HID)
   ```

4. **Restart gateway:**
   ```bash
   POST /api/system/restart
   ```

---

### Touch Input Not Reaching Source

**Symptom:** Touch panel detected but touch events not working on source

**Solutions:**

1. **Check routing:**
   ```bash
   GET /api/touch-panels/{panel_id}/status
   
   # Verify "routed_to" matches active source
   ```

2. **Manual route:**
   ```bash
   POST /api/touch-panels/{panel_id}/route
   {
     "target_source": "teams_room"
   }
   ```

3. **Verify USB connection to source:**
   - Check USB cable from gateway to source
   - Ensure source recognizes touch input device

---

### IP Panel Not Connecting

**Symptom:** Ethernet touch panel shows "disconnected"

**Solutions:**

1. **Ping panel:**
   ```bash
   ping 192.168.1.60
   ```

2. **Check gateway server:**
   ```bash
   GET /api/touch-panels/servers
   
   # Verify Crestron CH5 server running
   {
     "servers": [
       {
         "protocol": "crestron_ch5",
         "port": 41794,
         "status": "running"
       }
     ]
   }
   ```

3. **Check panel IP configuration:**
   - Ensure panel has correct gateway IP
   - Verify subnet mask
   - Check firewall rules

4. **Test connection from panel:**
   - In panel settings, test connection to gateway
   - Check connection logs

---

### Crestron Panel Shows Wrong Status

**Symptom:** Crestron panel buttons don't reflect current room state

**Solutions:**

1. **Enable feedback:**
   ```yaml
   touch_panels:
     - id: "crestron_panel"
       feedback:
         enabled: true
         update_interval: 1000  # ms
         push_on_change: true
   ```

2. **Verify CH5 connection:**
   ```bash
   GET /api/touch-panels/crestron_panel/connection
   
   # Should show "connected: true"
   ```

3. **Reprogram panel:**
   - Re-upload VT Pro-e project to panel
   - Verify IP address in SIMPL Windows program matches gateway

---

## Best Practices

### 1. USB Touch Panels

✅ **Use dedicated USB ports for critical panels** (e.g., Teams Tap always on USB-A 1)  
✅ **Keep USB cables under 5 meters** for reliable HID communication  
✅ **Use powered USB hubs** if more than 2 USB touch panels needed

### 2. IP Touch Panels

✅ **Use static IP addresses** for panels (avoid DHCP)  
✅ **Enable bidirectional feedback** so panels always show current state  
✅ **Test panel programming** before final installation  
✅ **Document button/command mappings** for maintenance

### 3. Web Panels

✅ **Use HTTPS** with valid SSL certificate  
✅ **Enable PWA** for offline functionality  
✅ **Implement token expiration** for security  
✅ **Test on target devices** (iPad, Android tablets) before deployment

### 4. Routing

✅ **Use "dedicated" mode** for Teams Room controllers (never switch)  
✅ **Use "follow_active_source"** for interactive displays  
✅ **Add switch delay** (100-200ms) to prevent accidental routing changes

---

## Next Steps

- **[KVM Gateway Guide](KVM_GATEWAY_GUIDE.md):** Complete KVM documentation
- **[Hardware Gateway Spec](../HARDWARE_GATEWAY_SPEC.md):** Full hardware architecture
- **[Multi-Device Setup](MULTI_DEVICE_SETUP.md):** Configure sources and displays
- **[Crestron Integration Examples](../examples/crestron/):** Sample SIMPL programs
- **[Extron Integration Examples](../examples/extron/):** Sample Global Scripter code

---

**For enterprise deployments with touch panel integration:**  
**Contact:** enterprise@mediacontrol.com  
**Phone:** +1 (555) 123-4567  
**Web:** https://mediacontrol.com/enterprise
