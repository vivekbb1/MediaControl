# SIP Telephony & Doorbell Integration

**VoIP Phone System, Doorbell Camera, Advanced Multi-Source Display Layouts**

---

## Table of Contents

1. [SIP IP Phone Integration](#sip-ip-phone-integration)
2. [Doorbell Camera Integration](#doorbell-camera-integration)
3. [Picture-in-Picture (PiP)](#picture-in-picture-pip)
4. [Multi-Source Grid Layouts](#multi-source-grid-layouts)
5. [Touch-Based Source Resizing](#touch-based-source-resizing)
6. [Configuration](#configuration)
7. [API Reference](#api-reference)

---

## SIP IP Phone Integration

### Overview

**SIP (Session Initiation Protocol)** integration enables the gateway to act as:
- **SIP endpoint** - Make/receive calls like a desk phone
- **Room phone extension** - Conference room phone system
- **Intercom system** - Building-wide communication
- **Call forwarding** - Route calls to displays

### Features

✅ **Make/receive calls** - Full VoIP phone functionality  
✅ **Room extension** - Dedicated extension number per room  
✅ **Call display on screen** - Caller ID on main display  
✅ **Touch controls** - Answer, hang up, mute, hold via touch panel  
✅ **Audio routing** - Route call audio to room speakers  
✅ **Video calls** - SIP video calls (H.264/VP8)  
✅ **Call history** - Missed calls, recent calls  
✅ **Speed dial** - Quick dial contacts  
✅ **Transfer/forward** - Transfer calls between extensions

---

### Architecture

```
┌──────────────────────────────────────────────────┐
│         Meeting Room with SIP Phone              │
│                                                  │
│  ┌────────────────────────────┐                 │
│  │  Touch Panel (Crestron)    │                 │
│  │  • Dial pad                │                 │
│  │  • Call controls           │ RJ45            │
│  │  • Contact list            ├────────┐        │
│  └────────────────────────────┘        │        │
│                                        ▼        │
│                         ┌──────────────────┐    │
│                         │  MediaControl    │    │
│                         │  Gateway         │    │
│                         │  • SIP client    │    │
│                         │  • Extension 301 │    │
│                         └────────┬─────────┘    │
│                                  │ SIP          │
│                                  ▼              │
│                         ┌──────────────────┐    │
│                         │  PBX Server      │    │
│                         │  (FreePBX,       │    │
│                         │   Asterisk, etc.)│    │
│                         └──────────────────┘    │
│                                                  │
│  Call Flow:                                     │
│  1. Incoming call to extension 301              │
│  2. Gateway displays caller ID on screen        │
│  3. User taps "Answer" on touch panel          │
│  4. Call audio routed to room speakers/mic      │
└──────────────────────────────────────────────────┘
```

---

### Supported PBX Systems

#### 1. **FreePBX / Asterisk**
- Open-source PBX
- Full SIP support
- Extensions, IVR, voicemail
- **Most popular for enterprise**

#### 2. **3CX**
- Commercial PBX (Windows/Linux)
- Web-based management
- Mobile/desktop apps
- Video conferencing

#### 3. **Cisco Unified CM (CallManager)**
- Enterprise PBX
- SCCP + SIP support
- Advanced call routing

#### 4. **Microsoft Teams Phone**
- Cloud-based PBX
- Direct Routing via SIP trunk
- Integration with Microsoft 365

#### 5. **RingCentral / 8x8 / Vonage**
- Cloud PBX services
- SIP trunking
- Virtual phone system

---

### Configuration

```yaml
sip_phone:
  enabled: true
  
  # SIP account
  account:
    username: "301"  # Extension number
    password: "secure_password"
    domain: "pbx.company.com"
    display_name: "Conference Room A"
    
  # SIP server
  server:
    address: "pbx.company.com"
    port: 5060
    transport: "udp"  # or "tcp", "tls"
    
  # Audio settings
  audio:
    codecs: ["opus", "g722", "pcmu", "pcma"]
    sample_rate: 48000
    echo_cancellation: true
    noise_suppression: true
    
    # Microphone (room mic or USB mic)
    microphone:
      device: "usb_mic_1"
      gain: 0  # dB
      
    # Speaker output
    speaker:
      device: "hdmi_audio_out"
      volume: 70  # 0-100
  
  # Video settings (for SIP video calls)
  video:
    enabled: true
    codecs: ["h264", "vp8"]
    resolution: "1280x720"
    fps: 30
    camera: "usb_camera_1"
  
  # Call behavior
  call_behavior:
    auto_answer: false  # Auto-answer incoming calls
    auto_answer_delay: 0  # seconds
    ring_duration: 30  # seconds before voicemail
    call_waiting: true
    call_forwarding: false
    forward_to: ""  # Extension or number
    
  # Display settings
  display:
    show_caller_id_on_screen: true
    pip_mode: true  # Show caller in PiP during call
    pip_position: "top_right"
    full_screen_on_answer: false
    
  # Touch panel integration
  touch_panel:
    show_dial_pad: true
    show_contacts: true
    show_call_history: true
    show_speed_dial: true
```

---

### Call Controls UI

```
┌─────────────────────────────────────────────────┐
│          SIP Phone (Touch Panel)                │
│                                                 │
│  Status: Ready (Extension 301)                 │
│                                                 │
│  ┌────────────────────────────────────────┐   │
│  │        Dial Pad                        │   │
│  │  ┌────┬────┬────┐                      │   │
│  │  │ 1  │ 2  │ 3  │                      │   │
│  │  ├────┼────┼────┤                      │   │
│  │  │ 4  │ 5  │ 6  │                      │   │
│  │  ├────┼────┼────┤                      │   │
│  │  │ 7  │ 8  │ 9  │                      │   │
│  │  ├────┼────┼────┤                      │   │
│  │  │ *  │ 0  │ #  │                      │   │
│  │  └────┴────┴────┘                      │   │
│  │                                         │   │
│  │  Number: [_________________]  [Call]   │   │
│  └────────────────────────────────────────┘   │
│                                                 │
│  ┌────────────────────────────────────────┐   │
│  │  Speed Dial                            │   │
│  │  • Reception (ext 100)                 │   │
│  │  • IT Support (ext 200)                │   │
│  │  • Security (ext 911)                  │   │
│  └────────────────────────────────────────┘   │
│                                                 │
│  [Contacts] [History] [Voicemail]              │
└─────────────────────────────────────────────────┘
```

### During Call UI

```
┌─────────────────────────────────────────────────┐
│          Active Call                            │
│                                                 │
│  ┌────────────────────────────────────────┐   │
│  │  📞 John Doe (ext 102)                 │   │
│  │  Duration: 00:02:35                    │   │
│  └────────────────────────────────────────┘   │
│                                                 │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
│  │ 🔇   │ │ ⏸️   │ │ 🔀   │ │ 🔢   │         │
│  │ Mute │ │ Hold │ │Transf│ │Keypad│         │
│  └──────┘ └──────┘ └──────┘ └──────┘         │
│                                                 │
│  ┌──────┐ ┌──────┐                            │
│  │ 🔊+  │ │ 📞   │                            │
│  │Volume│ │Hang  │                            │
│  │      │ │ Up   │                            │
│  └──────┘ └──────┘                            │
└─────────────────────────────────────────────────┘
```

---

## Doorbell Camera Integration

### Overview

**Doorbell camera** integration enables:
- **Live video feed** when doorbell pressed
- **Two-way audio** - Talk to visitor from meeting room
- **Auto-popup** - Doorbell video appears on screen automatically
- **Record visitors** - Save doorbell footage
- **Access control** - Unlock door from touch panel

### Features

✅ **Instant popup** - Doorbell video appears on screen when pressed  
✅ **Two-way audio** - Communicate with visitor  
✅ **Picture-in-Picture** - Doorbell in PiP during meetings  
✅ **Smart notifications** - Motion detection alerts  
✅ **Video recording** - Save doorbell footage  
✅ **Access control integration** - Unlock door remotely  
✅ **Multiple doorbells** - Front door, back door, side entrance  
✅ **Do Not Disturb** - Suppress doorbell during meetings

---

### Supported Doorbell Systems

#### 1. **Ring Video Doorbell**
- Cloud-based
- Motion detection
- Night vision
- Ring API integration

#### 2. **Nest Hello (Google)**
- 24/7 streaming
- Familiar face detection
- Google Home integration
- Nest API

#### 3. **Arlo Video Doorbell**
- HDR video
- Package detection
- Cloud storage
- Arlo API

#### 4. **UniFi Protect Doorbell**
- Local storage (NVR)
- No cloud required
- PoE powered
- UniFi Protect API

#### 5. **Generic RTSP/ONVIF Doorbells**
- Any doorbell with RTSP stream
- ONVIF protocol support
- Local network only

---

### Architecture

```
┌──────────────────────────────────────────────────┐
│         Office/Meeting Room Setup                │
│                                                  │
│  ┌────────────────────────────┐                 │
│  │  Main Display              │                 │
│  │                            │                 │
│  │  ┌──────────────────┐     │                 │
│  │  │ Doorbell Video   │     │                 │
│  │  │ (Picture-in-Pic) │     │                 │
│  │  └──────────────────┘     │                 │
│  │                            │                 │
│  │  [Answer] [Ignore] [Unlock]                 │
│  └────────────────────────────┘                 │
│                    ▲                             │
│                    │ HDMI                        │
│  ┌─────────────────┴────────────────┐           │
│  │  MediaControl Gateway            │           │
│  │  • Doorbell client               │           │
│  │  • Access control                │           │
│  └────────┬─────────────────────────┘           │
│           │ Network (RTSP/API)                   │
│           ▼                                      │
│  ┌──────────────────┐     ┌──────────────┐     │
│  │ Ring Doorbell    │     │ Door Lock    │     │
│  │ (Front Door)     │     │ (Smart Lock) │     │
│  └──────────────────┘     └──────────────┘     │
│                                                  │
│  Event Flow:                                    │
│  1. Visitor presses doorbell                    │
│  2. Ring sends webhook to gateway               │
│  3. Gateway shows doorbell video in PiP         │
│  4. User taps "Answer" to talk to visitor       │
│  5. User can unlock door from touch panel       │
└──────────────────────────────────────────────────┘
```

---

### Configuration

```yaml
doorbell:
  enabled: true
  
  # Doorbells (support multiple)
  doorbells:
    - doorbell_id: "front_door"
      name: "Front Door"
      type: "ring"  # or "nest", "arlo", "unifi", "generic_rtsp"
      
      # Ring-specific config
      ring:
        device_id: "abc123"
        auth_token: "ring_auth_token"
        
      # Video stream
      stream:
        url: "rtsp://doorbell.local/live"
        protocol: "rtsp"  # or "hls", "webrtc"
        resolution: "1280x720"
        
      # Behavior
      behavior:
        auto_popup: true
        popup_duration: 60  # seconds
        pip_mode: true
        pip_position: "bottom_right"
        play_chime: true
        chime_sound: "/sounds/doorbell_chime.mp3"
        
      # Do Not Disturb
      dnd:
        enabled: true
        schedule:
          days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
          start_time: "09:00"
          end_time: "17:00"
        suppress_notifications: false  # Still show, but no audio
        
    - doorbell_id: "back_door"
      name: "Back Door (Delivery)"
      type: "generic_rtsp"
      stream:
        url: "rtsp://192.168.1.50/stream"
      behavior:
        auto_popup: true
        pip_position: "bottom_left"
  
  # Two-way audio
  audio:
    enabled: true
    microphone: "room_mic"
    speaker: "doorbell_speaker"  # Doorbell's speaker
    echo_cancellation: true
    
  # Recording
  recording:
    enabled: true
    record_on_press: true
    record_on_motion: false
    retention_days: 30
    storage_path: "/recordings/doorbell"
    
  # Access control
  access_control:
    enabled: true
    locks:
      - lock_id: "front_door_lock"
        name: "Front Door Lock"
        type: "august"  # or "schlage", "yale", "generic_zigbee"
        api_token: "lock_api_token"
        
  # Notifications
  notifications:
    enabled: true
    channels: ["screen", "email", "push"]
    recipients:
      - "security@company.com"
      - "reception@company.com"
```

---

### Doorbell Popup UI

```
┌─────────────────────────────────────────────────┐
│          Main Display (During Meeting)          │
│                                                 │
│  ┌────────────────────────────────────────┐   │
│  │                                         │   │
│  │     Teams Meeting (Main Content)       │   │
│  │                                         │   │
│  │                    ┌──────────────┐    │   │
│  │                    │ 🔔 DOORBELL  │    │   │
│  │                    │ Front Door   │    │   │
│  │                    │              │    │   │
│  │                    │ [Visitor]    │    │   │
│  │                    │              │    │   │
│  │                    │ John Smith   │    │   │
│  │                    │ Delivery     │    │   │
│  │                    │              │    │   │
│  │                    │[Answer][Ignore]   │   │
│  │                    │[Unlock Door]│    │   │
│  │                    └──────────────┘    │   │
│  │                                         │   │
│  └────────────────────────────────────────┘   │
│                                                 │
│  • Doorbell appears in bottom-right corner     │
│  • Meeting continues in background              │
│  • User can answer or ignore                    │
└─────────────────────────────────────────────────┘
```

---

## Picture-in-Picture (PiP)

### Overview

**Picture-in-Picture** displays one source in a small window overlaid on another source.

### Use Cases

1. **Doorbell during meeting** - Doorbell video in PiP while meeting continues
2. **Call during presentation** - SIP call video in PiP during slides
3. **News ticker** - News feed in PiP during signage
4. **Sports scores** - Live scores in PiP during main game
5. **Security camera** - Monitor entrance during normal operation

---

### Configuration

```yaml
picture_in_picture:
  enabled: true
  
  # PiP settings
  settings:
    # Size
    pip_width_percent: 25  # 25% of screen width
    pip_height_percent: 25  # 25% of screen height
    
    # Position presets
    positions:
      top_left: {x: 20, y: 20}
      top_right: {x: "75%", y: 20}
      bottom_left: {x: 20, y: "75%"}
      bottom_right: {x: "75%", y: "75%"}
      
    # Behavior
    movable: true  # User can drag PiP window
    resizable: true  # User can resize PiP window
    closable: true  # User can close PiP window
    
    # Opacity
    opacity: 1.0  # 0.0-1.0 (for transparency)
    opacity_when_inactive: 0.8
    
    # Auto-hide
    auto_hide_after: 0  # seconds (0 = never)
    hide_on_touch_outside: false
  
  # PiP sources (what can be shown in PiP)
  sources:
    - source_id: "doorbell_front"
      name: "Front Door Camera"
      priority: 1  # Higher priority = auto-popup
      
    - source_id: "sip_call"
      name: "SIP Video Call"
      priority: 2
      
    - source_id: "security_camera_lobby"
      name: "Lobby Camera"
      priority: 3
      
    - source_id: "news_feed"
      name: "News Ticker"
      priority: 4
```

---

## Multi-Source Grid Layouts

### Overview

**Grid layouts** display multiple sources simultaneously in a grid (2×2, 3×3, etc.).

### Supported Layouts

#### 1. **2×2 Grid (Quad View)**
```
┌──────────┬──────────┐
│ Source 1 │ Source 2 │
│          │          │
├──────────┼──────────┤
│ Source 3 │ Source 4 │
│          │          │
└──────────┴──────────┘
```

#### 2. **3×3 Grid (9 Sources)**
```
┌──────┬──────┬──────┐
│Src 1 │Src 2 │Src 3 │
├──────┼──────┼──────┤
│Src 4 │Src 5 │Src 6 │
├──────┼──────┼──────┤
│Src 7 │Src 8 │Src 9 │
└──────┴──────┴──────┘
```

#### 3. **Custom A×B Grid**
- 1×2, 1×3, 1×4 (horizontal strip)
- 2×1, 3×1, 4×1 (vertical strip)
- 2×3, 3×2 (mixed)
- Any combination up to display resolution limit

#### 4. **Asymmetric Layouts**
```
┌─────────────┬──────┐
│             │Src 2 │
│  Source 1   ├──────┤
│  (Large)    │Src 3 │
│             ├──────┤
│             │Src 4 │
└─────────────┴──────┘
```

---

### Configuration

```yaml
multi_source_layouts:
  enabled: true
  
  # Grid presets
  presets:
    - preset_id: "quad_view"
      name: "Quad View (2×2)"
      grid:
        rows: 2
        columns: 2
        sources: ["hdmi_1", "hdmi_2", "hdmi_3", "hdmi_4"]
        gap: 10  # pixels between sources
        
    - preset_id: "nine_up"
      name: "Nine-Up (3×3)"
      grid:
        rows: 3
        columns: 3
        sources: ["hdmi_1", "hdmi_2", "hdmi_3", "hdmi_4", "hdmi_5", "hdmi_6", "hdmi_7", "hdmi_8", "hdmi_9"]
        
    - preset_id: "main_plus_three"
      name: "Main + 3 Thumbnails"
      layout: "asymmetric"
      zones:
        - zone_id: "main"
          source: "hdmi_1"
          position: {x: 0, y: 0, width: "75%", height: "100%"}
          
        - zone_id: "thumb_1"
          source: "hdmi_2"
          position: {x: "75%", y: 0, width: "25%", height: "33%"}
          
        - zone_id: "thumb_2"
          source: "hdmi_3"
          position: {x: "75%", y: "33%", width: "25%", height: "33%"}
          
        - zone_id: "thumb_3"
          source: "hdmi_4"
          position: {x: "75%", y: "66%", width: "25%", height: "34%"}
  
  # Layout behavior
  behavior:
    auto_scale: true  # Scale sources to fit zones
    maintain_aspect_ratio: true
    show_labels: true  # Show source name in each zone
    show_borders: true
    border_color: "#333333"
    border_width: 2  # pixels
    
    # Active source highlight
    highlight_active: true
    active_border_color: "#00FF00"
    active_border_width: 4
```

---

## Touch-Based Source Resizing

### Overview

**Touch-based resizing** allows users to resize sources by dragging borders/corners on a touch display.

### Features

✅ **Drag to resize** - Touch and drag source borders  
✅ **Snap to grid** - Automatic alignment to grid  
✅ **Pinch to zoom** - Pinch gesture to resize  
✅ **Double-tap to maximize** - Quick full-screen  
✅ **Visual feedback** - Resize preview in real-time  
✅ **Constraint enforcement** - Min/max size limits  
✅ **Save layouts** - Save custom layouts as presets

---

### Touch Gestures

#### 1. **Tap to Select**
- Tap source to select (shows resize handles)

#### 2. **Drag Border to Resize**
- Drag edge to resize horizontally or vertically
- Drag corner to resize both dimensions

#### 3. **Drag Source to Move**
- Drag from center to move source

#### 4. **Pinch to Zoom**
- Two-finger pinch to resize proportionally

#### 5. **Double-Tap**
- Double-tap to maximize source to full screen
- Double-tap again to restore

#### 6. **Three-Finger Swipe**
- Swipe up: Expand source vertically
- Swipe down: Shrink source vertically
- Swipe left/right: Expand/shrink horizontally

---

### Configuration

```yaml
touch_resize:
  enabled: true
  
  # Touch behavior
  gestures:
    tap_to_select: true
    drag_to_resize: true
    drag_to_move: true
    pinch_to_zoom: true
    double_tap_to_maximize: true
    three_finger_swipe: true
    
  # Resize constraints
  constraints:
    min_width_percent: 10  # Minimum 10% of screen width
    min_height_percent: 10
    max_width_percent: 100
    max_height_percent: 100
    
    # Snap to grid
    snap_to_grid: true
    grid_size: 20  # pixels
    
    # Aspect ratio
    maintain_aspect_ratio: false  # Allow free resizing
    aspect_ratio_lock: false  # Hold shift to lock aspect
    
  # Visual feedback
  feedback:
    show_resize_handles: true
    handle_size: 30  # pixels
    handle_color: "#FFFFFF"
    
    show_resize_preview: true
    preview_opacity: 0.5
    
    show_size_label: true  # Show "1920×1080" during resize
    label_position: "center"
    
  # Resize modes
  modes:
    - mode_id: "free"
      name: "Free Resize"
      description: "Resize freely with no constraints"
      
    - mode_id: "snap_quarters"
      name: "Snap to Quarters"
      description: "Snap to 25%, 50%, 75%, 100%"
      snap_points: [25, 50, 75, 100]  # percent
      
    - mode_id: "grid_align"
      name: "Grid Align"
      description: "Align to 3×3 grid"
      grid: {rows: 3, columns: 3}
```

---

### Touch Resize UI

```
┌─────────────────────────────────────────────────┐
│          Multi-Source Display (Touch)           │
│                                                 │
│  ┌──────────────────────┐  ┌────────────┐     │
│  │                      │  │            │     │
│  │  Source 1 (HDMI 1)   │  │  Source 2  │     │
│  │  [Selected]          │  │  (HDMI 2)  │     │
│  │  1920×1080           │  │            │     │
│  │                      ├──┤            │     │
│  │  ┌─┐  ┌─┐  ┌─┐     │  │            │     │
│  │  │◄├──┤█├──┤►│     │  └────────────┘     │
│  │  └─┘  └─┘  └─┘     │                       │
│  │       ▲             │  ┌────────────┐     │
│  │       │ Resize      │  │            │     │
│  │       │ Handles     │  │  Source 3  │     │
│  │       ▼             │  │  (HDMI 3)  │     │
│  └──────────────────────┘  └────────────┘     │
│                                                 │
│  Tap source to select, drag borders to resize  │
│  [Save Layout] [Reset] [Presets ▼]             │
└─────────────────────────────────────────────────┘
```

---

## Configuration

### Complete Configuration Example

```yaml
# Complete SIP, Doorbell, PiP, Grid, Touch Resize configuration

# SIP IP Phone
sip_phone:
  enabled: true
  account:
    username: "301"
    password: "secure_pass"
    domain: "pbx.company.com"
  display:
    show_caller_id_on_screen: true
    pip_mode: true
    pip_position: "top_right"

# Doorbell
doorbell:
  enabled: true
  doorbells:
    - doorbell_id: "front_door"
      name: "Front Door"
      type: "ring"
      behavior:
        auto_popup: true
        pip_mode: true
        pip_position: "bottom_right"
      recording:
        enabled: true
        record_on_press: true

# Picture-in-Picture
picture_in_picture:
  enabled: true
  settings:
    pip_width_percent: 25
    pip_height_percent: 25
    movable: true
    resizable: true

# Multi-Source Grid
multi_source_layouts:
  enabled: true
  presets:
    - preset_id: "quad_view"
      name: "Quad View (2×2)"
      grid:
        rows: 2
        columns: 2
        sources: ["hdmi_1", "hdmi_2", "hdmi_3", "hdmi_4"]

# Touch Resize
touch_resize:
  enabled: true
  gestures:
    drag_to_resize: true
    pinch_to_zoom: true
    double_tap_to_maximize: true
  constraints:
    snap_to_grid: true
    grid_size: 20
```

---

## API Reference

### SIP Phone API

```http
# Make call
POST /api/sip/call
{
  "destination": "102",  # Extension or phone number
  "video": false
}

# Answer incoming call
POST /api/sip/answer
{
  "call_id": "call_abc123"
}

# Hang up
POST /api/sip/hangup
{
  "call_id": "call_abc123"
}

# Mute/unmute
POST /api/sip/mute
{
  "call_id": "call_abc123",
  "muted": true
}
```

### Doorbell API

```http
# Get doorbell status
GET /api/doorbell/status

Response:
{
  "doorbells": [
    {
      "doorbell_id": "front_door",
      "name": "Front Door",
      "online": true,
      "last_activity": "2026-07-31T09:15:00Z",
      "recording": false
    }
  ]
}

# Answer doorbell
POST /api/doorbell/answer
{
  "doorbell_id": "front_door"
}

# Unlock door
POST /api/doorbell/unlock
{
  "doorbell_id": "front_door"
}
```

### Picture-in-Picture API

```http
# Show source in PiP
POST /api/pip/show
{
  "source_id": "doorbell_front",
  "position": "bottom_right",
  "width_percent": 25,
  "height_percent": 25
}

# Close PiP
POST /api/pip/close
```

### Multi-Source Grid API

```http
# Activate grid preset
POST /api/layout/activate
{
  "preset_id": "quad_view"
}

# Create custom grid
POST /api/layout/grid
{
  "rows": 2,
  "columns": 2,
  "sources": ["hdmi_1", "hdmi_2", "hdmi_3", "hdmi_4"],
  "save_as": "my_custom_quad"
}
```

### Touch Resize API

```http
# Resize source
POST /api/layout/resize
{
  "source_id": "hdmi_1",
  "position": {
    "x": 0,
    "y": 0,
    "width": "50%",
    "height": "100%"
  }
}

# Save layout
POST /api/layout/save
{
  "layout_name": "My Custom Layout",
  "sources": [
    {
      "source_id": "hdmi_1",
      "position": {...}
    }
  ]
}
```

---

## Use Cases

### 1. Executive Office

**Setup:**
- 2× Displays (left: work, right: security/communications)
- SIP extension 501
- 3× Doorbell cameras (front, back, garage)
- Touch panel for controls

**Workflow:**
1. Executive works on left display
2. Right display shows security camera grid (2×2)
3. Doorbell rings → Auto-popup in PiP on right display
4. Executive sees visitor, taps "Answer" to speak
5. Taps "Unlock" to grant access
6. Incoming SIP call → Appears in PiP on work display
7. Executive can resize/move PiP windows via touch

---

### 2. Security Control Room

**Setup:**
- Video wall (3×3 = 9 displays)
- 50× Security cameras
- SIP intercom system (extensions 900-909)
- Touch panel for grid control

**Workflow:**
1. Display grid of 9 cameras
2. Touch camera to maximize to full screen
3. Drag to resize cameras
4. Doorbell at entrance 1 → Auto-popup in PiP
5. Guard calls entrance via SIP extension 905
6. Two-way audio conversation
7. Guard unlocks door remotely

---

### 3. Conference Room

**Setup:**
- Main display (Teams meetings)
- SIP extension 301
- Doorbell camera (room entrance)
- Touch panel

**Workflow:**
1. Teams meeting in progress
2. Late attendee at door → Doorbell rings
3. Doorbell video appears in PiP (doesn't interrupt meeting)
4. Participant taps "Unlock" to let them in
5. Incoming SIP call → Appears in second PiP
6. After meeting, switch to quad view (4 sources)

---

## Best Practices

### SIP Phone
✅ **Use TLS** for encrypted SIP signaling  
✅ **Enable echo cancellation** for room audio  
✅ **Set ring duration** to avoid infinite ringing  
✅ **Configure voicemail** forwarding

### Doorbell
✅ **Test auto-popup** timing (not too intrusive)  
✅ **Enable Do Not Disturb** during critical meetings  
✅ **Record all doorbell events** for security  
✅ **Integrate with access control** for seamless entry

### Picture-in-Picture
✅ **Limit PiP size** to 25% or less  
✅ **Default position** to corner (top-right, bottom-right)  
✅ **Allow user** to move/resize PiP  
✅ **Auto-close PiP** after inactivity

### Multi-Source Grid
✅ **Use presets** for common layouts (quad, nine-up)  
✅ **Show labels** to identify sources  
✅ **Highlight active** source with border  
✅ **Save custom layouts** for quick recall

### Touch Resize
✅ **Enable snap-to-grid** for clean layouts  
✅ **Show resize handles** clearly  
✅ **Visual feedback** during resize (preview)  
✅ **Enforce min/max** sizes to prevent tiny/huge windows

---

## Next Steps

- **[Wireless Presentation](WIRELESS_PRESENTATION.md):** AirPlay, Chromecast, Miracast
- **[Universal RTC Panels](UNIVERSAL_RTC_PANELS.md):** Teams/Zoom/Webex/Meet single interface
- **[Touch Panel Integration](TOUCH_PANEL_INTEGRATION.md):** Crestron, Extron, AMX
- **[Hardware Gateway Spec](../HARDWARE_GATEWAY_SPEC.md):** Complete hardware architecture

---

**For SIP, doorbell, and advanced layout deployments:**  
**Contact:** enterprise@mediacontrol.com  
**Support:** https://mediacontrol.com/support/telephony-security
