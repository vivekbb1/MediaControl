# Wireless Presentation & Screen Mirroring

**AirPlay, Chromecast, Miracast - Universal Wireless Presentation Gateway**

---

## Table of Contents

1. [Overview](#overview)
2. [AirPlay Receiver](#airplay-receiver)
3. [Chromecast Built-in](#chromecast-built-in)
4. [Miracast Receiver](#miracast-receiver)
5. [Configuration](#configuration)
6. [Multi-User Presentation](#multi-user-presentation)
7. [Security & Access Control](#security--access-control)
8. [Whiteboard Integration](#whiteboard-integration)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **MediaControl Gateway** acts as a universal wireless presentation receiver, supporting:

- **AirPlay** - Apple devices (iPhone, iPad, Mac)
- **Chromecast** - Android devices, Chrome browser
- **Miracast** - Windows PCs, Android devices
- **Google Cast** - Chrome browser, Android apps
- **WebRTC** - Browser-based screen sharing (any platform)

### Key Features

✅ **Multi-Protocol Support** - All major wireless presentation standards  
✅ **No Dongles Required** - Gateway receives wireless streams directly  
✅ **Multi-User Presentation** - Up to 4 simultaneous presenters  
✅ **Moderation Mode** - Host controls which presenter is on screen  
✅ **PIN/QR Code Access** - Secure wireless connection  
✅ **Device Whitelist** - Restrict access to approved devices  
✅ **BYOD Friendly** - Works with any device (iOS, Android, Windows, Mac, Linux)

---

## AirPlay Receiver

### Overview

Gateway acts as an **AirPlay 2 receiver**, appearing as an Apple TV to iOS/macOS devices.

### Hardware Support

**Implemented via:**
- **Software AirPlay server** running on gateway (using `shairport-sync` or similar)
- **Network:** Multicast DNS (mDNS) for device discovery
- **Protocols:** RAOP (Remote Audio Output Protocol), AirPlay 2

### Features

✅ **Video mirroring** - Full screen mirroring from iPhone/iPad/Mac  
✅ **Audio streaming** - AirPlay audio to room speakers  
✅ **4K support** - Up to 4K@30fps (hardware dependent)  
✅ **Low latency** - <200ms delay  
✅ **PIN protection** - Require PIN to connect  
✅ **Multi-room audio** - Sync audio across multiple gateways

### Setup

#### 1. Enable AirPlay Receiver

```yaml
# Gateway configuration
wireless_presentation:
  airplay:
    enabled: true
    name: "Conference Room A Display"  # Name shown on iOS devices
    password: "1234"  # Optional PIN (leave empty for open access)
    
    features:
      video_mirroring: true
      audio_streaming: true
      multi_room_audio: false
      
    video:
      max_resolution: "1920x1080"  # or "3840x2160" for 4K
      max_fps: 30
      
    audio:
      output: "hdmi"  # or "analog", "optical"
      sample_rate: 48000
      
    security:
      require_password: true
      allowed_devices: []  # Empty = all devices, or list MAC addresses
```

#### 2. User Experience (iOS/macOS)

**iPhone/iPad:**
1. Swipe down from top-right (Control Center)
2. Tap "Screen Mirroring"
3. Select "Conference Room A Display"
4. Enter PIN if required
5. Screen appears on room display

**Mac:**
1. Click Control Center icon (menu bar)
2. Click "Screen Mirroring"
3. Select "Conference Room A Display"
4. Enter PIN if required
5. Screen appears on room display

#### 3. Gateway Behavior

When AirPlay connection received:
- Gateway creates new HDMI input source (virtual)
- Video stream decoded and routed to display
- Audio extracted and routed to speakers
- Source name: "AirPlay - [Device Name]"

---

## Chromecast Built-in

### Overview

Gateway implements **Chromecast protocol**, appearing as a Chromecast device to Android/Chrome.

### Hardware Support

**Implemented via:**
- **Cast Receiver SDK** running on gateway
- **Network:** mDNS for device discovery
- **Protocols:** Google Cast protocol (gRPC over HTTP/2)

### Features

✅ **Screen casting** - Full screen cast from Android devices  
✅ **Tab casting** - Cast Chrome browser tab  
✅ **App casting** - Cast from Cast-enabled apps (YouTube, Netflix, etc.)  
✅ **Guest mode** - Cast without joining Wi-Fi network (via ultrasonic pairing)  
✅ **Multi-user queue** - Queue multiple presenters  
✅ **4K support** - Up to 4K@60fps

### Setup

#### 1. Enable Chromecast

```yaml
wireless_presentation:
  chromecast:
    enabled: true
    name: "Conference Room A Display"
    
    features:
      screen_casting: true
      tab_casting: true
      app_casting: true
      guest_mode: false  # Requires ultrasonic hardware
      
    video:
      max_resolution: "1920x1080"
      max_fps: 60
      codecs: ["h264", "vp8", "vp9"]
      
    audio:
      output: "hdmi"
      codecs: ["aac", "opus"]
      
    security:
      require_pin: true
      pin_code: "1234"  # Shown on display
      allowed_devices: []
```

#### 2. User Experience (Android/Chrome)

**Android:**
1. Swipe down (Quick Settings)
2. Tap "Cast" or "Screen Cast"
3. Select "Conference Room A Display"
4. Enter PIN shown on display
5. Screen appears on room display

**Chrome Browser:**
1. Click three-dot menu → Cast
2. Select "Conference Room A Display"
3. Choose: "Cast tab" or "Cast desktop"
4. Enter PIN if required
5. Content appears on room display

#### 3. Gateway Behavior

When Chromecast connection received:
- Gateway receives Cast stream (H.264 or VP9)
- Video decoded and routed to display
- Audio extracted and routed to speakers
- Source name: "Chromecast - [Device Name]"

---

## Miracast Receiver

### Overview

Gateway acts as a **Miracast sink**, compatible with Windows PCs and Android devices.

### Hardware Support

**Implemented via:**
- **Wi-Fi Direct** (P2P connection)
- **WFD (Wi-Fi Display)** protocol
- **H.264 video encoding/decoding**

### Features

✅ **Windows 10/11 support** - "Connect" app  
✅ **Android support** - Native screen mirroring  
✅ **Direct connection** - P2P Wi-Fi (no network required)  
✅ **1080p60 support** - Full HD at 60fps  
✅ **Low latency** - <100ms delay

### Setup

#### 1. Enable Miracast

```yaml
wireless_presentation:
  miracast:
    enabled: true
    name: "Conference Room A Display"
    
    wifi_direct:
      ssid: "DIRECT-MCG-ConfRoomA"
      password: "12345678"  # WPA2 password
      channel: 149  # 5GHz channel
      
    video:
      max_resolution: "1920x1080"
      max_fps: 60
      
    audio:
      output: "hdmi"
      
    security:
      require_pin: true
      pin_code: "1234"
```

#### 2. User Experience (Windows)

**Windows 10/11:**
1. Press `Win + K` (Connect shortcut)
2. Select "Conference Room A Display"
3. Enter PIN if required
4. Choose: "Duplicate", "Extend", or "Second screen only"
5. Screen appears on room display

**Android:**
1. Settings → Connected devices → Connection preferences → Cast
2. Enable "Wireless display"
3. Select "Conference Room A Display"
4. Enter PIN if required
5. Screen appears on room display

#### 3. Gateway Behavior

When Miracast connection received:
- Gateway establishes Wi-Fi Direct connection
- Receives H.264 video stream
- Video decoded and routed to display
- Source name: "Miracast - [Device Name]"

---

## Configuration

### Complete Wireless Presentation Config

```yaml
room:
  id: "conf_room_a"
  name: "Conference Room A"

wireless_presentation:
  # Global settings
  enabled: true
  display_pin_on_screen: true  # Show PIN on display when idle
  qr_code: true  # Show QR code for mobile apps
  welcome_message: "Welcome! Wireless Present: AirPlay, Chromecast, or Miracast"
  
  # AirPlay receiver
  airplay:
    enabled: true
    name: "Conf Room A - AirPlay"
    password: "1234"
    video:
      max_resolution: "1920x1080"
      max_fps: 30
    audio:
      output: "hdmi"
  
  # Chromecast receiver
  chromecast:
    enabled: true
    name: "Conf Room A - Cast"
    require_pin: true
    pin_code: "1234"
    video:
      max_resolution: "3840x2160"  # 4K
      max_fps: 60
  
  # Miracast receiver
  miracast:
    enabled: true
    name: "Conf Room A - Miracast"
    wifi_direct:
      ssid: "DIRECT-MCG-ConfRoomA"
      password: "confroom1234"
  
  # Multi-user presentation
  multi_user:
    enabled: true
    max_presenters: 4
    layout: "grid"  # or "spotlight", "sidebar"
    moderation: true  # Host approves presenters
    moderator_pin: "9999"
  
  # Security
  security:
    allowed_devices: []  # Empty = all, or list MAC addresses
    device_whitelist_mode: false
    session_timeout: 3600  # Auto-disconnect after 1 hour
    max_sessions_per_device: 1
  
  # Recording (optional)
  recording:
    enabled: false
    auto_record_presentations: false
    storage_path: "/recordings"
```

---

## Multi-User Presentation

### Overview

Support **multiple presenters simultaneously** on one display.

### Layouts

#### 1. **Grid Layout** (2×2 or 3×3)
- Up to 4 presenters in equal-sized tiles
- Best for: Collaborative work sessions

```
┌──────────┬──────────┐
│ Presenter│ Presenter│
│    1     │    2     │
├──────────┼──────────┤
│ Presenter│ Presenter│
│    3     │    4     │
└──────────┴──────────┘
```

#### 2. **Spotlight Layout**
- Main presenter (80% of screen)
- Thumbnails (20%, bottom strip)
- Best for: Formal presentations with Q&A

```
┌────────────────────────────┐
│                            │
│    Main Presenter (1)      │
│                            │
├────────┬────────┬──────────┤
│ Pres 2 │ Pres 3 │  Pres 4  │
└────────┴────────┴──────────┘
```

#### 3. **Sidebar Layout**
- Main presenter (70% of screen)
- Side panel with thumbnails (30%, right side)
- Best for: Code reviews, document collaboration

```
┌──────────────────┬──────┐
│                  │Pres 2│
│  Main Presenter  ├──────┤
│       (1)        │Pres 3│
│                  ├──────┤
│                  │Pres 4│
└──────────────────┴──────┘
```

### Configuration

```yaml
multi_user:
  enabled: true
  max_presenters: 4
  layout: "grid"  # or "spotlight", "sidebar"
  
  # Moderation mode
  moderation: true
  moderator_pin: "9999"
  
  # Presenter queue
  queue:
    enabled: true
    auto_promote: true  # Auto-promote next in queue
    max_queue_size: 10
  
  # Layout switching
  allow_layout_switch: true
  default_layout: "spotlight"
```

### User Experience

**Without Moderation:**
1. User 1 connects → Appears full screen
2. User 2 connects → Screen splits (2×1)
3. User 3 connects → Screen splits (2×2)
4. User 4 connects → Screen maintains 2×2

**With Moderation:**
1. User 1 connects → Appears in "waiting room" thumbnail
2. Moderator sees notification → Approves User 1
3. User 1 promoted to main screen
4. User 2 connects → Waits for approval
5. Moderator approves → User 2 appears in grid

### Moderator Controls

```yaml
# Moderator API
POST /api/wireless-presentation/approve-presenter
{
  "device_id": "iphone_abc123"
}

POST /api/wireless-presentation/promote-to-spotlight
{
  "device_id": "android_xyz789"
}

POST /api/wireless-presentation/change-layout
{
  "layout": "spotlight"
}

POST /api/wireless-presentation/disconnect-presenter
{
  "device_id": "mac_def456"
}
```

---

## Security & Access Control

### PIN Protection

**Dynamic PIN:**
- PIN changes every 24 hours
- Displayed on screen when idle
- Also available via QR code

```yaml
security:
  pin_mode: "dynamic"  # or "static"
  pin_rotation_hours: 24
  pin_length: 4  # 4-8 digits
  display_pin_on_screen: true
```

### Device Whitelist

**MAC Address Filtering:**
```yaml
security:
  device_whitelist_mode: true
  allowed_devices:
    - "AA:BB:CC:DD:EE:FF"  # John's iPhone
    - "11:22:33:44:55:66"  # Jane's Mac
    - "FF:EE:DD:CC:BB:AA"  # Bob's Android
```

### Guest Access

**Temporary Access:**
```http
POST /api/wireless-presentation/create-guest-access
{
  "guest_name": "Visitor - John Doe",
  "expiry_hours": 2,
  "max_uses": 3
}

Response:
{
  "guest_pin": "5678",
  "qr_code_url": "https://gateway.local/present?token=abc123",
  "expires_at": "2026-07-31T11:09:00Z"
}
```

### Session Timeout

**Auto-disconnect:**
```yaml
security:
  session_timeout: 1800  # 30 minutes
  idle_timeout: 300  # 5 minutes (no activity)
  max_sessions_per_device: 1
```

---

## Whiteboard Integration

### Overview

Integrated **digital whiteboard** for annotation and collaboration.

### Features

✅ **Drawing tools** - Pen, marker, highlighter, eraser  
✅ **Shapes** - Rectangle, circle, line, arrow  
✅ **Text** - Add text boxes  
✅ **Sticky notes** - Virtual Post-its  
✅ **Laser pointer** - Temporary cursor highlight  
✅ **Multi-user** - Simultaneous annotation by multiple users  
✅ **Save/Export** - Save whiteboard as PNG/PDF  
✅ **Share** - Email or upload to cloud storage

### Usage

**Scenario 1: Annotate Presentation**
1. User presents slides via AirPlay
2. Host taps "Annotate" on touch panel
3. Whiteboard overlay appears
4. Use stylus/finger to draw on presentation
5. Annotations visible to all in room
6. Save annotated slides

**Scenario 2: Standalone Whiteboard**
1. Tap "Whiteboard" on touch panel
2. Blank canvas appears on display
3. Multiple users draw simultaneously (different colors)
4. Save whiteboard session
5. Share via email

### Configuration

```yaml
whiteboard:
  enabled: true
  
  # Tools
  tools:
    - pen
    - marker
    - highlighter
    - eraser
    - shapes
    - text
    - sticky_notes
    - laser_pointer
  
  # Multi-user
  multi_user:
    enabled: true
    max_users: 8
    color_per_user: true  # Each user gets unique color
  
  # Save/Export
  export:
    formats: ["png", "pdf", "svg"]
    auto_save: true
    save_interval: 60  # seconds
  
  # Touch input
  touch:
    palm_rejection: true
    pressure_sensitivity: true  # If stylus supports
  
  # Integration
  overlay_mode: true  # Overlay on presentations
  standalone_mode: true  # Full whiteboard
```

### API Reference

```http
# Start whiteboard session
POST /api/whiteboard/start
{
  "mode": "overlay",  # or "standalone"
  "background": "presentation_1"  # or "blank", "grid"
}

# Add annotation
POST /api/whiteboard/annotate
{
  "type": "pen",
  "color": "#FF0000",
  "width": 3,
  "points": [
    {"x": 100, "y": 200},
    {"x": 150, "y": 250},
    {"x": 200, "y": 200}
  ],
  "user": "john_doe"
}

# Save whiteboard
POST /api/whiteboard/save
{
  "format": "pdf",
  "filename": "meeting_notes_2026-07-31.pdf"
}

# Share whiteboard
POST /api/whiteboard/share
{
  "method": "email",
  "recipients": ["team@company.com"],
  "subject": "Meeting Whiteboard - July 31"
}
```

---

## API Reference

### List Active Presentations

```http
GET /api/wireless-presentation/sessions

Response:
{
  "sessions": [
    {
      "session_id": "airplay_001",
      "protocol": "airplay",
      "device_name": "John's iPhone",
      "device_mac": "AA:BB:CC:DD:EE:FF",
      "resolution": "1920x1080",
      "fps": 30,
      "started_at": "2026-07-31T09:00:00Z",
      "duration_seconds": 540,
      "status": "active"
    },
    {
      "session_id": "chromecast_002",
      "protocol": "chromecast",
      "device_name": "Jane's MacBook Pro",
      "device_mac": "11:22:33:44:55:66",
      "resolution": "1920x1080",
      "fps": 60,
      "started_at": "2026-07-31T09:05:00Z",
      "duration_seconds": 240,
      "status": "paused"
    }
  ],
  "total_sessions": 2,
  "max_sessions": 4
}
```

### Disconnect Presenter

```http
POST /api/wireless-presentation/disconnect
{
  "session_id": "airplay_001",
  "reason": "moderator_request"
}

Response:
{
  "status": "success",
  "session_id": "airplay_001",
  "disconnected_at": "2026-07-31T09:10:00Z"
}
```

### Change Layout

```http
POST /api/wireless-presentation/layout
{
  "layout": "spotlight",
  "spotlight_session": "chromecast_002"
}

Response:
{
  "status": "success",
  "layout": "spotlight",
  "active_sessions": ["chromecast_002"],
  "thumbnail_sessions": ["airplay_001"]
}
```

---

## Troubleshooting

### AirPlay Device Not Found

**Symptom:** iPhone doesn't see gateway in Screen Mirroring list

**Solutions:**

1. **Check mDNS:** Gateway must advertise via Bonjour
   ```bash
   # Verify mDNS service
   avahi-browse -a | grep airplay
   ```

2. **Check network:** iPhone and gateway on same subnet
   - Gateway: `192.168.1.100`
   - iPhone: Must be `192.168.1.x`

3. **Restart AirPlay service:**
   ```bash
   systemctl restart shairport-sync
   ```

4. **Check firewall:** Ports 5000-5005, 7000-7100 must be open

---

### Chromecast Not Appearing

**Symptom:** Android device doesn't see gateway in Cast list

**Solutions:**

1. **Check Cast SDK:** Verify Cast Receiver is running
   ```bash
   systemctl status cast-receiver
   ```

2. **Check mDNS:** Cast uses mDNS discovery
   ```bash
   avahi-browse -a | grep googlecast
   ```

3. **Verify ports:** UDP 5353 (mDNS), TCP 8008-8009 (Cast)

---

### Miracast Connection Fails

**Symptom:** Windows PC can't connect to Miracast

**Solutions:**

1. **Check Wi-Fi Direct:** Gateway must support P2P
   ```bash
   iw dev wlan0 interface add p2p0 type __p2pdev
   ```

2. **Verify WFD service:**
   ```bash
   systemctl status wpa_supplicant
   ```

3. **Check Wi-Fi adapter:** Must support P2P mode

---

### High Latency / Lag

**Symptom:** Video has >500ms delay

**Solutions:**

1. **Check network bandwidth:**
   - AirPlay: Minimum 20 Mbps
   - Chromecast: Minimum 15 Mbps
   - Miracast: Minimum 10 Mbps

2. **Reduce video quality:**
   ```yaml
   video:
     max_resolution: "1280x720"  # Lower from 1080p
     max_fps: 30  # Lower from 60
   ```

3. **Use 5GHz Wi-Fi:** 2.4GHz has more interference

4. **Check CPU load:** Gateway may be overloaded
   ```bash
   top -b -n 1 | grep cast-receiver
   ```

---

## Best Practices

### Network Setup

✅ **Use 5GHz Wi-Fi** for wireless presentation (less congestion)  
✅ **Dedicated SSID** for presentation devices (separate from guest Wi-Fi)  
✅ **QoS enabled** for video streaming traffic  
✅ **Multicast enabled** for mDNS discovery

### Security

✅ **Enable PIN protection** for corporate environments  
✅ **Use device whitelist** for high-security rooms  
✅ **Rotate PINs daily** (automatic)  
✅ **Session timeout** to prevent abandoned connections

### User Experience

✅ **Display instructions** on screen when idle (how to connect)  
✅ **Show QR code** for mobile app download  
✅ **Moderator present** for large meetings (control presenter queue)  
✅ **Test before meetings** to ensure connectivity

---

## Next Steps

- **[Universal RTC Touch Panels](UNIVERSAL_RTC_PANELS.md):** Single panel for all video conferencing platforms
- **[Native Apps on Gateway](NATIVE_APPS.md):** Run Teams/Zoom directly on gateway
- **[Video Wall Controller](VIDEO_WALL_SIGNAGE.md):** Digital signage and video wall support
- **[Multi-User Frontend](MULTIUSER_FRONTEND.md):** Collaborative workspace interface

---

**For wireless presentation deployments:**  
**Contact:** enterprise@mediacontrol.com  
**Support:** https://mediacontrol.com/support/wireless-presentation
