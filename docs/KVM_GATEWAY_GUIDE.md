# KVM Gateway - Complete Guide

**Keyboard, Video, Mouse Switching with USB Accessory Routing & Collaboration Features**

---

## Table of Contents

1. [Overview](#overview)
2. [Hardware Specifications](#hardware-specifications)
3. [KVM Switching Features](#kvm-switching-features)
4. [USB Accessory Switching](#usb-accessory-switching)
5. [Wireless Keyboard & Mouse](#wireless-keyboard--mouse)
6. [Microsoft Teams Room Integration](#microsoft-teams-room-integration)
7. [Thin Client PC Support](#thin-client-pc-support)
8. [Configuration Examples](#configuration-examples)
9. [API Reference](#api-reference)
10. [Use Cases & Scenarios](#use-cases--scenarios)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The **MediaControl Gateway KVM Edition** (MCG-400K, MCG-600K, MCG-Pro) adds enterprise-grade KVM switching to the standard gateway, enabling:

- **Keyboard, Video, Mouse routing** between multiple sources (computers, thin clients, Teams Rooms)
- **USB-C/USB-A accessory switching** (webcams, drives, dongles)
- **Wireless keyboard/mouse support** (Bluetooth 5.0)
- **One-button source switching** with automatic peripheral routing
- **Microsoft Teams Room & Zoom Room integration**
- **Hot desk & flexible workspace support**
- **Multi-PC workflows** (development, trading, control rooms)

### What Makes This Different?

Traditional KVM switches only handle keyboard/video/mouse for computers.

**MediaControl Gateway KVM** handles:
- ✅ Computers (Windows, Mac, Linux)
- ✅ Thin clients (VDI/DaaS)
- ✅ Microsoft Teams Rooms (Android-based)
- ✅ Apple TV, Android TV, Roku
- ✅ Set-top boxes, Blu-ray players
- ✅ Any HDMI source + USB peripheral routing

**All in one device.**

---

## Hardware Specifications

### KVM Models

| Model | HDMI Inputs | KVM-Enabled Ports | USB-C Ports | USB-A Ports | Wireless KB/Mouse |
|-------|-------------|-------------------|-------------|-------------|-------------------|
| **MCG-400K** | 4 | 4 | 2 (switchable) | 2 (switchable) | ✅ Bluetooth 5.0 |
| **MCG-600K** | 6 | 6 | 2 (switchable) | 2 (switchable) | ✅ Bluetooth 5.0 |
| **MCG-Pro** | 6 | 6 | 4 (switchable) | 4 (switchable) | ✅ Bluetooth 5.0 |

### USB Specifications

**USB-C Ports:**
- USB 3.2 Gen 2 (10 Gbps)
- Power Delivery 3.0 (15W per port)
- DisplayPort Alt Mode (optional, not used for KVM)
- Switchable between sources

**USB-A Ports:**
- USB 3.0 (5 Gbps)
- 900mA power per port
- Switchable between sources

**Wireless Receiver:**
- Bluetooth 5.0 (Low Energy + Classic)
- 2.4GHz frequency
- 10m range (typical)
- Simultaneous connections: up to 4 devices

---

## KVM Switching Features

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    MediaControl Gateway                  │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ HDMI In 1  │  │ HDMI In 2  │  │ HDMI In 3  │       │
│  │ (Laptop)   │  │ (Desktop)  │  │ (Teams Rm) │       │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘       │
│        │                │                │               │
│  ┌─────▼────────────────▼────────────────▼──────┐      │
│  │         USB Switching Controller              │      │
│  │  • Routes keyboard/mouse to active source     │      │
│  │  • Routes USB-C/USB-A accessories            │      │
│  └────────────┬──────────────────────────────────┘      │
│               │                                          │
│  ┌────────────▼──────────────────────────────────┐      │
│  │  Bluetooth Receiver (Wireless KB/Mouse)       │      │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  Output:                                                 │
│  • HDMI to displays (1-2 ports)                        │
│  • USB peripherals routed to active source             │
└─────────────────────────────────────────────────────────┘
```

### Switching Modes

#### 1. Manual Switching
- **Web UI:** Click source button
- **Mobile App:** Tap source in app
- **Physical Button:** Front-panel button (optional)
- **API:** Send command via REST/WebSocket

#### 2. Hotkey Switching (Keyboard)
- **Scroll Lock 2× + [1-6]:** Switch to source 1-6
- **Ctrl + Alt + [1-6]:** Alternative hotkey
- **Configurable per installation**

#### 3. Automatic Switching
- **Activity Detection:** Auto-switch when source becomes active
- **Time-Based:** Switch to specific source at scheduled times
- **Preset Triggers:** Switch as part of automation preset

### Switching Speed

| Component | Switch Time |
|-----------|-------------|
| **Video (HDMI)** | 100-300ms |
| **USB (Keyboard/Mouse)** | 50-150ms |
| **USB-C/A Accessories** | 200-500ms |
| **Total Switch Time** | ~500ms |

**Instant to the user.** No perceptible delay.

---

## USB Accessory Switching

### What Can Be Switched?

**USB-C Devices:**
- Webcams (4K, 1080p)
- External SSDs/HDDs
- USB hubs
- Docking stations
- Phone charging
- USB-C displays (via DisplayPort Alt Mode)

**USB-A Devices:**
- USB flash drives
- Wireless dongles (mouse, keyboard, headset)
- Fingerprint readers
- Smart card readers
- Legacy peripherals
- Arduino/development boards

### Configuration

```yaml
# KVM configuration in displays.yaml

kvm:
  enabled: true
  
  # USB-C ports
  usb_c_ports:
    - port: 1
      name: "Webcam Port"
      devices:
        - "Logitech BRIO 4K"
      auto_detect: true
      power_delivery: true  # 15W
    
    - port: 2
      name: "Storage Port"
      devices:
        - "Samsung T7 SSD"
      auto_detect: true
  
  # USB-A ports
  usb_a_ports:
    - port: 1
      name: "Wireless Dongle"
      devices:
        - "Logitech Unifying Receiver"
      dedicated: true  # Don't switch, always available
    
    - port: 2
      name: "General Purpose"
      auto_detect: true
  
  # Hotkey configuration
  hotkeys:
    enabled: true
    trigger: "scroll_lock"  # or "ctrl_alt"
    double_tap_delay: 500  # ms
```

### Dedicated vs. Switchable Ports

**Dedicated Ports:**
- Not switched between sources
- Always available to gateway
- Use for: wireless dongles, permanent storage

**Switchable Ports:**
- Routed to active source
- Use for: webcams, temp storage, peripherals

---

## Wireless Keyboard & Mouse

### Pairing Process

#### Bluetooth Keyboard/Mouse

1. **Put Gateway in Pairing Mode:**
   ```python
   # Via API
   POST /api/kvm/pair
   {
       "device_type": "keyboard"  # or "mouse"
   }
   ```
   
   Or via web UI: **Settings → KVM → Pair Wireless Device**

2. **Put Keyboard/Mouse in Pairing Mode:**
   - Bluetooth keyboards: Usually `Fn + Bluetooth` or hold pairing button
   - Bluetooth mice: Hold pairing button for 3-5 seconds

3. **Gateway auto-discovers and pairs**

4. **Confirm pairing in UI**

#### 2.4GHz Wireless Dongle (Logitech Unifying, etc.)

1. **Plug dongle into dedicated USB-A port**
2. **Pair keyboard/mouse using manufacturer's software** (run once on any computer)
3. **Dongle stays plugged in, always available**

### Supported Devices

**Tested & Verified:**
- Logitech MX Keys, MX Master 3
- Apple Magic Keyboard, Magic Mouse/Trackpad
- Microsoft Surface Keyboard/Mouse
- Keychron K-series (Bluetooth)
- Any generic Bluetooth HID keyboard/mouse

**Multi-Device Keyboards:**
Keyboards with multi-device switching (e.g., Logitech MX Keys has 3 device buttons):
- **Option 1:** Pair all 3 buttons to gateway → Use gateway's KVM switching
- **Option 2:** Pair button 1 to gateway, buttons 2-3 to specific sources directly

### Wireless Reliability

**Latency:** <5ms (Bluetooth 5.0 LE)
**Range:** 10m typical, 5m minimum
**Battery Life:** No impact (gateway is receiver, not source)
**Interference:** Auto-channel selection to avoid 2.4GHz congestion

---

## Microsoft Teams Room Integration

### Overview

**Microsoft Teams Rooms** (MTR) are Android-based appliances for video conferencing.

**Problem:** MTR devices need webcams, mics, speakers, and touch screens—but these peripherals can't be easily shared with other sources (laptops, desktops).

**Solution:** MediaControl Gateway routes USB peripherals between MTR and other sources dynamically.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Meeting Room Setup                      │
│                                                           │
│  ┌─────────────────┐         ┌──────────────────┐       │
│  │  Teams Room     │  USB-C  │  MediaControl    │       │
│  │  Device (MTR)   ├─────────┤  Gateway (MCG)   │       │
│  │  (Android)      │         │                  │       │
│  └─────────────────┘         └────────┬─────────┘       │
│                                        │                  │
│                           ┌────────────┼────────────┐    │
│                           │            │            │     │
│                    ┌──────▼───┐  ┌────▼────┐  ┌───▼───┐│
│                    │ Webcam   │  │  Mic    │  │ Touch ││
│                    │ (USB-C)  │  │ Array   │  │ Panel ││
│                    └──────────┘  └─────────┘  └───────┘ │
│                                                           │
│  Sources:                                                │
│  • HDMI 1: Teams Room (Android)                         │
│  • HDMI 2: User's Laptop (HDMI + USB-C)                │
│  • HDMI 3: Desktop PC                                   │
│                                                           │
│  Use Cases:                                              │
│  1. Teams Meeting → Route USB to MTR                    │
│  2. Laptop Presentation → Route USB to laptop           │
│  3. Normal Work → Route USB to desktop                  │
└──────────────────────────────────────────────────────────┘
```

### Configuration

```yaml
# Teams Room integration

kvm:
  sources:
    - id: "teams_room"
      name: "Microsoft Teams Room"
      hdmi_port: 1
      usb_connection: "usb_c_1"
      device_type: "mtr"
      
      # Peripherals for Teams Room
      peripherals:
        webcam:
          port: "usb_c_2"
          device: "Logitech Rally Camera"
          auto_route: true  # Automatically route to MTR during meetings
        
        microphone:
          port: "usb_a_1"
          device: "Jabra Speak 750"
          auto_route: true
        
        touch_panel:
          port: "usb_a_2"
          device: "Crestron Touch Screen"
          dedicated_to: "teams_room"  # Always for Teams Room
      
      # Auto-switch triggers
      triggers:
        calendar_event:
          enabled: true
          switch_before: 300  # Switch 5 min before meeting
        
        activity_detection:
          enabled: true
          
    - id: "user_laptop"
      name: "User Laptop"
      hdmi_port: 2
      usb_connection: "usb_c_1"  # Same USB-C can switch between sources
      device_type: "laptop"
```

### Typical Workflow

**Scenario: Teams meeting at 10:00 AM**

1. **9:55 AM:** Gateway auto-switches to Teams Room source (calendar integration)
2. **9:55 AM:** USB webcam + mic routed to Teams Room device
3. **10:00 AM:** Meeting starts, Teams Room shows on displays
4. **10:15 AM:** User wants to show laptop screen
   - User taps "Laptop" source in app
   - Video switches to laptop HDMI
   - USB webcam + mic **stay with Teams Room** (meeting continues)
5. **10:45 AM:** Meeting ends
6. **10:45 AM:** Gateway switches back to default source

---

## Thin Client PC Support

### Overview

**Thin Clients** (VDI/DaaS endpoints) are lightweight computers that connect to virtual desktops.

Examples: Dell Wyse, HP ThinPro, IGEL OS, Windows 10 IoT, Chrome OS

**Use Case:** Hot desks in offices—users sit at any desk, log into their VDI/virtual desktop, use keyboard/mouse.

### Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Hot Desk Setup                       │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Thin Client │  │ Apple TV    │  │ Cable TV    │   │
│  │ (HP Wyse)   │  │             │  │ (STB)       │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│    HDMI │           HDMI  │           HDMI │           │
│  ┌──────▼─────────────────▼────────────────▼───────┐  │
│  │         MediaControl Gateway (KVM)              │  │
│  │  • Keyboard/mouse to thin client when active    │  │
│  │  • USB accessories (webcam) to thin client      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  User Workflow:                                        │
│  1. Arrive at desk                                     │
│  2. Tap "Work PC" in app (or auto-switch)            │
│  3. Thin client HDMI shown, keyboard/mouse active     │
│  4. Log into VDI (Citrix, VMware Horizon, Azure)     │
│  5. Work normally                                      │
│                                                         │
│  Break Time:                                           │
│  1. Tap "Apple TV" or "Cable TV"                      │
│  2. Watch content with same remote/keyboard           │
└────────────────────────────────────────────────────────┘
```

### Configuration

```yaml
# Thin client configuration

kvm:
  sources:
    - id: "thin_client"
      name: "Work PC (VDI)"
      hdmi_port: 1
      usb_connection: "wired"  # Thin client has USB cable to gateway
      device_type: "thin_client"
      os: "wyse_thinOS"  # or "windows_iot", "igel", "chrome_os"
      
      vdi_provider: "citrix"  # or "vmware_horizon", "azure_avd"
      
      peripherals:
        keyboard_mouse:
          wireless: true
          auto_route: true
        
        webcam:
          port: "usb_c_1"
          auto_route: true  # For video calls in VDI
      
      # Auto-switch when user activity detected
      triggers:
        usb_activity: true
        keyboard_input: true
        
    - id: "apple_tv"
      name: "Apple TV"
      hdmi_port: 2
      control_protocol: "pyatv"
```

### Hot Desk Deployment (Example Office)

**200 hot desks, each with:**
- 1× Display (monitor)
- 1× MediaControl Gateway MCG-400K ($599)
- 1× Thin client (Dell Wyse 5070, $300)
- 1× Wireless keyboard/mouse (Logitech MX, $150)

**Total cost per desk:** $1,049

**Compare to traditional:**
- 1× Display ($300)
- 1× Thin client ($300)
- 1× KVM switch ($200)
- 1× USB hub ($50)
- 1× Wireless dongle ($30)
- 1× HDMI switcher ($100)
- **Total:** $980 + complexity

**MediaControl Gateway:**
- All-in-one solution
- Cloud-managed (IT can configure remotely)
- Automatic switching (no user confusion)
- Add cable TV, Apple TV, etc., for break rooms

---

## Configuration Examples

### Example 1: Executive Office (Multi-PC Workflow)

```yaml
# Executive with Windows PC (work) + Mac (personal) + Apple TV

kvm:
  enabled: true
  
  sources:
    - id: "work_pc"
      name: "Work PC (Windows)"
      hdmi_port: 1
      device_type: "desktop"
      os: "windows"
      
      peripherals:
        keyboard_mouse:
          wireless: true
          default_source: true  # Default on boot
        
        webcam:
          port: "usb_c_1"
          device: "Logitech BRIO"
        
        usb_drive:
          port: "usb_a_1"
          auto_route: true
      
      triggers:
        keyboard_input: true  # Auto-switch on keyboard activity
        
    - id: "mac"
      name: "MacBook Pro"
      hdmi_port: 2
      device_type: "laptop"
      os: "macos"
      
      peripherals:
        keyboard_mouse:
          wireless: true
        
        webcam:
          port: "usb_c_1"  # Same webcam, switches between PCs
        
      hotkey:
        key: "scroll_lock_2x_2"  # Scroll Lock 2× then press 2
        
    - id: "apple_tv"
      name: "Apple TV 4K"
      hdmi_port: 3
      device_type: "appletv"
      control_protocol: "pyatv"
      
      peripherals:
        keyboard_mouse:
          wireless: true  # Use keyboard to type in Apple TV search
      
      hotkey:
        key: "scroll_lock_2x_3"
  
  hotkeys:
    enabled: true
    trigger: "scroll_lock"
    double_tap_delay: 500
```

**User Experience:**
- Keyboard/mouse wirelessly paired to gateway
- **Scroll Lock 2× + 1:** Switch to Windows PC (work)
- **Scroll Lock 2× + 2:** Switch to Mac (personal)
- **Scroll Lock 2× + 3:** Switch to Apple TV (entertainment)
- Webcam automatically routes to active PC for video calls

---

### Example 2: Collaboration Room (Teams + BYOD)

```yaml
# Microsoft Teams Room + user laptop (BYOD)

kvm:
  enabled: true
  
  sources:
    - id: "teams_room"
      name: "Microsoft Teams Room"
      hdmi_port: 1
      device_type: "mtr"
      usb_connection: "usb_c_1"
      
      peripherals:
        webcam:
          port: "usb_c_2"
          device: "Logitech Rally"
          dedicated_to: "teams_room"  # Always for Teams
        
        mic_array:
          port: "usb_a_1"
          device: "Jabra Speak 750"
          dedicated_to: "teams_room"
        
        touch_panel:
          port: "usb_a_2"
          device: "Logitech Tap"
          dedicated_to: "teams_room"
      
      triggers:
        calendar_event:
          enabled: true
          calendar_integration: "microsoft_graph"
          switch_before: 300  # 5 min before meeting
        
    - id: "user_laptop"
      name: "User Laptop (BYOD)"
      hdmi_port: 2
      device_type: "laptop"
      usb_connection: "usb_c_1"  # User plugs in USB-C
      
      peripherals:
        keyboard_mouse:
          wireless: false  # User uses laptop's own keyboard
      
      # When laptop plugged in, auto-switch
      triggers:
        usb_connect: true
        hdmi_active: true
      
      auto_switch_back:
        enabled: true
        delay: 300  # Switch back to Teams Room 5 min after laptop unplugged
```

**User Experience:**
1. Meeting room default: Teams Room on screen
2. Calendar shows meeting at 2:00 PM → Auto-switches to Teams Room at 1:55 PM
3. Meeting starts, webcam/mic active with Teams device
4. At 2:15 PM, user plugs laptop via USB-C to present slides
5. Gateway auto-switches to laptop HDMI (webcam/mic stay on Teams)
6. After presentation, user unplugs laptop
7. Gateway switches back to Teams Room

---

## API Reference

### KVM Control Endpoints

#### Switch Source

```http
POST /api/kvm/switch
Content-Type: application/json

{
  "source_id": "work_pc",
  "switch_video": true,
  "switch_usb": true,
  "switch_accessories": true
}

Response:
{
  "status": "success",
  "active_source": "work_pc",
  "switch_time_ms": 485
}
```

#### Get KVM Status

```http
GET /api/kvm/status

Response:
{
  "active_source": "work_pc",
  "sources": [
    {
      "id": "work_pc",
      "name": "Work PC (Windows)",
      "hdmi_port": 1,
      "hdmi_active": true,
      "usb_routed": true
    },
    {
      "id": "mac",
      "name": "MacBook Pro",
      "hdmi_port": 2,
      "hdmi_active": false,
      "usb_routed": false
    }
  ],
  "usb_devices": {
    "usb_c_1": {
      "device": "Logitech BRIO",
      "routed_to": "work_pc"
    },
    "usb_a_1": {
      "device": "Samsung T7 SSD",
      "routed_to": "work_pc"
    }
  },
  "wireless_devices": [
    {
      "type": "keyboard",
      "name": "Logitech MX Keys",
      "battery": 85,
      "connected": true
    },
    {
      "type": "mouse",
      "name": "Logitech MX Master 3",
      "battery": 62,
      "connected": true
    }
  ]
}
```

#### Pair Wireless Device

```http
POST /api/kvm/pair
Content-Type: application/json

{
  "device_type": "keyboard",  # or "mouse"
  "timeout": 60  # seconds
}

Response:
{
  "status": "pairing",
  "message": "Put keyboard in pairing mode",
  "timeout_in": 60
}
```

---

## Use Cases & Scenarios

### 1. Trading Floor / Control Room

**Scenario:** Multiple PCs per trader/operator, need instant switching

**Setup:**
- 4× PCs (trading systems, Bloomberg terminal, email, research)
- 2× Displays
- 1× MCG-Pro gateway (6 HDMI inputs)
- Wireless keyboard/mouse

**Workflow:**
- **Scroll Lock 2× + 1:** Trading system
- **Scroll Lock 2× + 2:** Bloomberg
- **Scroll Lock 2× + 3:** Email
- **Instant switching, no cables**

**Benefits:**
- Single keyboard/mouse for all PCs
- Instant switching (500ms)
- No cable clutter
- Cloud-managed configuration

---

### 2. Developer Workstation

**Scenario:** Developer uses Windows (coding), Mac (design), Linux (testing)

**Setup:**
- Windows desktop (main dev)
- MacBook Pro (UI/UX design)
- Linux box (server testing)
- 3× displays (1 per PC)
- MCG-600K gateway

**Workflow:**
- Default: Windows desktop (coding in VS Code)
- **Cmd+Shift+M:** Switch to Mac (Figma, design)
- **Cmd+Shift+L:** Switch to Linux (Docker, testing)
- Webcam routes to active PC for video calls

**Benefits:**
- One keyboard/mouse for all 3 systems
- Webcam automatically switches for Zoom/Teams
- USB-C SSD switches between systems
- No KVM switch needed

---

### 3. Hotel Room (Luxury)

**Scenario:** Hotel guest wants seamless control of TV, laptop, streaming

**Setup:**
- Hotel cable TV (HDMI)
- Guest's laptop (HDMI + USB-C)
- Apple TV 4K (streaming)
- MCG-400K gateway

**Workflow:**
1. Guest checks in, opens MediaControl app
2. Connects laptop via USB-C cable
3. Taps "My Laptop" in app
4. Laptop screen on TV, wireless keyboard/mouse from nightstand works
5. For streaming, tap "Apple TV"
6. For cable TV, tap "Cable TV"

**Benefits:**
- Guest uses one keyboard/mouse for everything
- Seamless laptop connectivity
- Hotel upsell: "Premium AV suite, $25/night"

---

### 4. Classroom (Education)

**Scenario:** Teacher PC + student presentation laptop

**Setup:**
- Teacher's PC (Windows, always connected)
- Student laptop dock (HDMI + USB-C)
- Projector/displays
- MCG-400K gateway

**Workflow:**
- Default: Teacher PC on screen
- Student presents: Plug laptop into USB-C dock
- Gateway auto-switches to student laptop
- Student unplugs → Auto-switch back to teacher PC

**Benefits:**
- No manual switching (teacher doesn't need tech knowledge)
- Webcam auto-routes to whoever is active (for hybrid class)
- USB-C one-cable solution for students

---

## Troubleshooting

### Keyboard/Mouse Not Working

**Symptom:** Keyboard/mouse inputs not reaching active source

**Solutions:**

1. **Check wireless pairing:**
   ```bash
   # Via API
   GET /api/kvm/wireless-devices
   
   # Should show:
   {
     "keyboard": {
       "connected": true,
       "battery": 85
     },
     "mouse": {
       "connected": true,
       "battery": 70
     }
   }
   ```

2. **Re-pair device:**
   - Remove device from Bluetooth settings (forget device)
   - Put gateway in pairing mode
   - Pair again

3. **Check USB routing:**
   ```bash
   GET /api/kvm/status
   
   # Confirm "usb_routed": true for active source
   ```

4. **Verify source USB connection:**
   - Wired sources: Check USB cable from gateway to source
   - Wireless: Ensure gateway's USB output is connected to source

---

### USB-C Device Not Switching

**Symptom:** Webcam/accessory stuck on one source

**Solutions:**

1. **Check if port is dedicated:**
   ```yaml
   # In config
   usb_c_ports:
     - port: 1
       dedicated_to: "teams_room"  # <-- This port won't switch
   ```
   
   If dedicated, change to `auto_route: true`

2. **Verify USB-C cable:**
   - Use USB-C cable rated for data (not charge-only)
   - Try different cable

3. **Power cycle device:**
   - Unplug USB-C device
   - Wait 5 seconds
   - Plug back in

---

### Hotkey Not Working

**Symptom:** Scroll Lock 2× + number doesn't switch sources

**Solutions:**

1. **Check if hotkeys enabled:**
   ```yaml
   kvm:
     hotkeys:
       enabled: true  # <-- Must be true
   ```

2. **Verify keyboard has Scroll Lock key:**
   - Some compact keyboards don't have Scroll Lock
   - Change to `Ctrl+Alt` trigger:
     ```yaml
     hotkeys:
       trigger: "ctrl_alt"  # Now Ctrl+Alt+1, Ctrl+Alt+2, etc.
     ```

3. **Check double-tap timing:**
   ```yaml
   hotkeys:
     double_tap_delay: 500  # Try increasing to 1000 (1 second)
   ```

---

### Teams Room Peripherals Not Routing

**Symptom:** Webcam/mic not working with Teams Room device

**Solutions:**

1. **Verify USB-C connection to Teams Room:**
   - Teams Room device connected to gateway via USB-C
   - Check cable (must be data + power, not charge-only)

2. **Check peripheral routing:**
   ```yaml
   sources:
     - id: "teams_room"
       peripherals:
         webcam:
           port: "usb_c_2"
           dedicated_to: "teams_room"  # <-- Should be set
   ```

3. **Teams Room device permissions:**
   - In Teams Room settings, verify camera/mic permissions granted
   - Restart Teams Room application

4. **Test peripheral directly:**
   - Unplug peripheral from gateway
   - Plug directly into Teams Room device
   - If works → Gateway config issue
   - If doesn't work → Peripheral or Teams Room issue

---

## Advanced Topics

### EDID Management

**EDID (Extended Display Identification Data)** tells sources what resolutions displays support.

**Problem:** When multiple sources share one display via KVM/HDMI switching, EDID must be consistent.

**Solution:** Gateway stores and emulates EDID:

```yaml
kvm:
  edid:
    mode: "emulate"  # or "pass-through"
    
    # Emulate specific resolution for all sources
    emulated_resolution: "1920x1080@60"
    
    # Or use display's native EDID
    source_display: 1  # Read EDID from HDMI output 1
```

**Why it matters:** Prevents resolution flickering when switching sources.

---

### USB Power Management

**USB Power Delivery (USB-C ports):**

```yaml
kvm:
  usb_c_ports:
    - port: 1
      power_delivery:
        enabled: true
        max_power: 15  # Watts (per USB-C port)
        
        # Smart charging: detect device type
        smart_charging: true
```

**Power Budget (MCG-400K):**
- Total USB power: 30W (2× USB-C @ 15W)
- If both ports used: 15W each
- If one port: Full 30W available (for laptop charging)

---

## Next Steps

- **[Hardware Gateway Spec](../HARDWARE_GATEWAY_SPEC.md):** Full hardware architecture
- **[Multi-Device Setup](MULTI_DEVICE_SETUP.md):** Configure sources and displays
- **[Token Authentication](../token_auth.py):** Secure API access
- **[Subscription Model](../PRODUCT_ROADMAP.md):** Pricing and licensing

---

**For commercial deployments, contact:** sales@mediacontrol.com
