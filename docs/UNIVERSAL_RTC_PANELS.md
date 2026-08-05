# Universal RTC Touch Control Panels

**Single Touch Interface for Teams, Zoom, Webex, Google Meet - Eliminate Multi-Vendor Complexity**

---

## Table of Contents

1. [Overview](#overview)
2. [The Multi-Vendor Problem](#the-multi-vendor-problem)
3. [Universal RTC Solution](#universal-rte-solution)
4. [Supported Platforms](#supported-platforms)
5. [Touch Panel Integration](#touch-panel-integration)
6. [Unified Call Controls](#unified-call-controls)
7. [Calendar Integration](#calendar-integration)
8. [One-Touch Join](#one-touch-join)
9. [Configuration](#configuration)
10. [API Reference](#api-reference)
11. [Deployment Scenarios](#deployment-scenarios)

---

## Overview

**Problem:** Modern meeting rooms support multiple video conferencing platforms (Teams, Zoom, Webex, Google Meet), requiring:
- Multiple touch panels or complex UI switching
- Different control interfaces for each platform
- User confusion and setup time
- Higher cost and maintenance complexity

**Solution:** **Universal RTC Touch Panel** - Single, unified touch interface controlling all video conferencing platforms with consistent UX.

### Key Features

✅ **Single Touch Interface** - One panel for Teams, Zoom, Webex, Google Meet  
✅ **Platform Auto-Detection** - Automatically identifies meeting platform from calendar  
✅ **Unified Call Controls** - Same buttons for all platforms (mute, camera, share, etc.)  
✅ **One-Touch Join** - Tap meeting in calendar, gateway joins automatically  
✅ **Consistent UX** - Same experience regardless of platform  
✅ **RJ45 Connection** - PoE-powered touch panels (Crestron, Extron, custom)  
✅ **No PC Required** - Gateway runs all platforms natively

---

## The Multi-Vendor Problem

### Traditional Setup (Complex)

```
┌─────────────────────────────────────────────────┐
│             Meeting Room                         │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ Teams Room   │  │ Zoom Room    │            │
│  │ Console      │  │ Controller   │            │
│  │ (Logitech    │  │ (Neat Pad)   │            │
│  │  Tap)        │  └──────────────┘            │
│  └──────────────┘                               │
│                    ┌──────────────┐             │
│  ┌──────────────┐  │ Webex Board │             │
│  │ Google Meet  │  │ (Touch)     │             │
│  │ HW (Custom)  │  └──────────────┘            │
│  └──────────────┘                               │
│                                                  │
│  Problem:                                       │
│  • 4 different touch interfaces                │
│  • User confusion (which one for this meeting?)│
│  • 4× the cost                                 │
│  • 4× the maintenance                          │
└─────────────────────────────────────────────────┘
```

### Universal RTC Setup (Simple)

```
┌─────────────────────────────────────────────────┐
│             Meeting Room                         │
│                                                  │
│         ┌──────────────────────┐                │
│         │  Universal RTC Panel │  RJ45          │
│         │  (Crestron TSW-770)  ├────────┐       │
│         │                      │        │       │
│         │  • Teams             │        │       │
│         │  • Zoom              │        ▼       │
│         │  • Webex      ┌──────────────────┐   │
│         │  • Google Meet│  MediaControl    │   │
│         └───────────────┤  Gateway         │   │
│                         │  • Native apps   │   │
│                         │  • Unified API   │   │
│                         └──────────────────┘   │
│                                                  │
│  Solution:                                      │
│  ✅ 1 touch interface for ALL platforms         │
│  ✅ Consistent UX                               │
│  ✅ 1× the cost                                 │
│  ✅ 1× the maintenance                          │
└─────────────────────────────────────────────────┘
```

---

## Universal RTC Solution

### Architecture

```
┌────────────────────────────────────────────────────┐
│          Universal RTC Touch Panel                  │
│          (Crestron/Extron/Custom via RJ45)         │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │  Unified UI (Same for All Platforms)         │ │
│  │                                               │ │
│  │  [📅 Calendar] [🎥 Join] [🔇 Mute] [📹 Cam]  │ │
│  │  [🖥️ Share] [👥 Participants] [⋮ More]       │ │
│  └──────────────────────────────────────────────┘ │
└──────────────────┬─────────────────────────────────┘
                   │ RJ45 (Ethernet + PoE)
                   ▼
┌────────────────────────────────────────────────────┐
│         MediaControl Gateway                        │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │  Universal RTC API Layer                     │ │
│  │  • Normalize call controls across platforms  │ │
│  │  • Abstract platform differences             │ │
│  └───────────┬──────────────────────────────────┘ │
│              │                                      │
│  ┌───────────▼─────┬─────────┬─────────┬────────┐ │
│  │ Teams Native    │ Zoom    │ Webex   │ Google │ │
│  │ App (Android)   │ Client  │ Client  │ Meet   │ │
│  └─────────────────┴─────────┴─────────┴────────┘ │
└────────────────────────────────────────────────────┘
```

### How It Works

1. **Calendar sync:** Gateway syncs with Microsoft 365/Google Calendar
2. **Meeting detection:** Identifies platform from meeting link (teams.microsoft.com, zoom.us, etc.)
3. **One-touch join:** User taps meeting on panel
4. **Gateway launches:** Appropriate native app (Teams, Zoom, Webex, or Meet)
5. **Unified controls:** Panel sends standard commands (mute, camera, share)
6. **Gateway translates:** Commands to platform-specific API calls
7. **Consistent UX:** Same panel layout regardless of platform

---

## Supported Platforms

### 1. Microsoft Teams

**Integration:**
- **Native app:** Microsoft Teams for Android (on gateway)
- **API:** Microsoft Graph API for calendar, Teams Bot API for call control
- **Authentication:** OAuth 2.0 with device code flow

**Features:**
- ✅ One-touch join from calendar
- ✅ Mute/unmute (self and participants)
- ✅ Camera on/off
- ✅ Screen sharing
- ✅ Participant list
- ✅ Raise hand
- ✅ Reactions (👍, ❤️, 😂)
- ✅ Recording start/stop
- ✅ Background blur/virtual backgrounds
- ✅ Breakout rooms

---

### 2. Zoom

**Integration:**
- **Native app:** Zoom Client for Linux/Android (on gateway)
- **API:** Zoom Client SDK or Zoom Rooms API
- **Authentication:** OAuth 2.0 or Zoom Rooms license

**Features:**
- ✅ One-touch join (via meeting ID or calendar)
- ✅ Mute/unmute (self and participants)
- ✅ Camera on/off
- ✅ Screen sharing
- ✅ Participant list
- ✅ Raise hand
- ✅ Reactions
- ✅ Recording (host only)
- ✅ Virtual backgrounds
- ✅ Breakout rooms
- ✅ Waiting room management

---

### 3. Cisco Webex

**Integration:**
- **Native app:** Webex Meetings for Linux/Android (on gateway)
- **API:** Webex Meetings API or Webex Devices API
- **Authentication:** OAuth 2.0

**Features:**
- ✅ One-touch join from calendar
- ✅ Mute/unmute
- ✅ Camera on/off
- ✅ Screen sharing
- ✅ Participant list
- ✅ Raise hand
- ✅ Recording (host only)
- ✅ Virtual backgrounds
- ✅ Breakout sessions

---

### 4. Google Meet

**Integration:**
- **Native app:** Chrome browser with Google Meet (on gateway)
- **API:** Google Calendar API + Meet API (limited)
- **Authentication:** OAuth 2.0

**Features:**
- ✅ One-touch join from calendar
- ✅ Mute/unmute
- ✅ Camera on/off
- ✅ Screen sharing
- ✅ Participant list
- ✅ Raise hand
- ✅ Reactions
- ✅ Recording (host only, G Suite Enterprise)
- ✅ Background blur/virtual backgrounds
- ✅ Breakout rooms

---

## Touch Panel Integration

### Supported Touch Panel Types

1. **Crestron Touch Panels**
   - TSW-770, TSW-1070, TSW-760
   - Connection: RJ45 (Ethernet + PoE)
   - Protocol: Crestron CH5 (port 41794)

2. **Extron Touch Panels**
   - TouchLink Pro TLP series
   - Connection: RJ45 (Ethernet + PoE)
   - Protocol: Extron SIS (port 23)

3. **AMX Touch Panels**
   - Modero X Series (NXD)
   - Connection: RJ45 (Ethernet + PoE)
   - Protocol: AMX NetLinx (port 1319)

4. **Custom Touch Panels**
   - Web-based (HTML5/React)
   - Connection: HTTPS/WebSocket
   - Any tablet (iPad, Android) with browser

---

## Unified Call Controls

### Standard Control Layout

```
┌─────────────────────────────────────────────────┐
│     Universal RTC Control Panel UI              │
│                                                 │
│  ┌────────────────────────────────────────┐   │
│  │         Meeting Calendar               │   │
│  │  ┌────────────────────────────────┐   │   │
│  │  │ 9:00 AM - Project Review       │   │   │
│  │  │ Platform: Microsoft Teams      │   │   │
│  │  │ [Join Meeting →]               │   │   │
│  │  └────────────────────────────────┘   │   │
│  │  ┌────────────────────────────────┐   │   │
│  │  │ 10:00 AM - Client Call         │   │   │
│  │  │ Platform: Zoom                 │   │   │
│  │  │ [Join Meeting →]               │   │   │
│  │  └────────────────────────────────┘   │   │
│  └────────────────────────────────────────┘   │
│                                                 │
│  ┌────────────────────────────────────────┐   │
│  │         In-Call Controls               │   │
│  │                                         │   │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │   │
│  │  │ 🔇   │ │ 📹   │ │ 🖥️   │ │ 👥   │ │   │
│  │  │ Mute │ │Camera│ │Share │ │People│ │   │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ │   │
│  │                                         │   │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │   │
│  │  │ 🙋   │ │ 📹   │ │ 🔴   │ │ 📞   │ │   │
│  │  │Raise │ │Bckgnd│ │Record│ │ End  │ │   │
│  │  │ Hand │ │      │ │      │ │      │ │   │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ │   │
│  └────────────────────────────────────────┘   │
│                                                 │
│  Current: Teams Meeting (14 participants)      │
│  Duration: 00:23:45                            │
└─────────────────────────────────────────────────┘
```

### Unified Command Set

All platforms respond to the same commands:

| Command | Teams | Zoom | Webex | Meet | Action |
|---------|-------|------|-------|------|--------|
| **mute_toggle** | ✅ | ✅ | ✅ | ✅ | Mute/unmute microphone |
| **camera_toggle** | ✅ | ✅ | ✅ | ✅ | Turn camera on/off |
| **share_screen** | ✅ | ✅ | ✅ | ✅ | Start screen sharing |
| **stop_share** | ✅ | ✅ | ✅ | ✅ | Stop screen sharing |
| **raise_hand** | ✅ | ✅ | ✅ | ✅ | Raise hand |
| **show_participants** | ✅ | ✅ | ✅ | ✅ | Show participant list |
| **start_recording** | ✅ | ✅ | ✅ | ✅ | Start recording (host) |
| **end_call** | ✅ | ✅ | ✅ | ✅ | Leave/end meeting |
| **admit_participant** | ✅ | ✅ | ✅ | ✅ | Admit from waiting room |
| **mute_participant** | ✅ | ✅ | ✅ | ❌ | Mute specific participant |
| **spotlight_video** | ✅ | ✅ | ✅ | ✅ | Spotlight speaker |

---

## Calendar Integration

### Supported Calendar Systems

1. **Microsoft 365 / Exchange**
   - Microsoft Graph API
   - OAuth 2.0 authentication
   - Real-time sync via webhooks

2. **Google Workspace**
   - Google Calendar API
   - OAuth 2.0 authentication
   - Real-time sync via push notifications

3. **iCloud Calendar**
   - CalDAV protocol
   - App-specific password authentication

### Meeting Detection

Gateway automatically detects platform from meeting invitation:

```python
# Auto-detection logic
def detect_platform(meeting_url):
    if "teams.microsoft.com" in meeting_url:
        return "teams"
    elif "zoom.us" in meeting_url or "zoom.com" in meeting_url:
        return "zoom"
    elif "webex.com" in meeting_url:
        return "webex"
    elif "meet.google.com" in meeting_url:
        return "google_meet"
    else:
        return "unknown"
```

### Configuration

```yaml
calendar_integration:
  enabled: true
  
  # Microsoft 365
  microsoft:
    enabled: true
    tenant_id: "your-tenant-id"
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    resource_account: "room-confA@company.com"
    sync_interval: 60  # seconds
    
  # Google Workspace
  google:
    enabled: true
    project_id: "your-project-id"
    client_id: "your-client-id.apps.googleusercontent.com"
    client_secret: "your-client-secret"
    resource_account: "conf-room-a@company.com"
    sync_interval: 60
  
  # Display settings
  display:
    show_upcoming_meetings: 5
    show_private_meeting_details: false
    timezone: "America/Los_Angeles"
```

---

## One-Touch Join

### User Experience

**Traditional (Complex):**
1. Look at meeting invite on laptop
2. Identify platform (Teams? Zoom? Webex?)
3. Find correct touch controller
4. Wake up controller
5. Navigate to "Join Meeting"
6. Manually enter meeting ID or link
7. Wait for meeting to start
8. **Total time: 2-3 minutes**

**Universal RTC (Simple):**
1. Walk into meeting room
2. See meeting on touch panel
3. Tap "Join Meeting"
4. **Meeting starts in 5 seconds**

### Implementation

```yaml
one_touch_join:
  enabled: true
  
  # Pre-join settings
  pre_join:
    auto_mute: true  # Start muted
    auto_camera_off: false  # Start with camera on
    auto_admit_participants: false  # Host only
    
  # Join behavior
  join:
    auto_launch_app: true  # Launch platform app automatically
    join_before_meeting_time: 300  # Join button appears 5 min before
    auto_join_at_meeting_time: false  # Require manual tap
    
  # Post-join
  post_join:
    auto_spotlight_host: true  # Spotlight host when they join
    auto_record: false  # Don't auto-record
```

---

## Configuration

### Complete Universal RTC Config

```yaml
universal_rtc:
  enabled: true
  
  # Supported platforms
  platforms:
    - teams
    - zoom
    - webex
    - google_meet
  
  # Touch panel configuration
  touch_panel:
    type: "crestron"  # or "extron", "amx", "web"
    ip_address: "192.168.1.60"
    protocol: "crestron_ch5"
    port: 41794
    
    # UI theme
    theme: "auto"  # or "light", "dark"
    language: "en"
    
    # Layout
    layout:
      calendar_section: true
      quick_join_buttons: true
      in_call_controls: true
      participant_panel: true
  
  # Platform-specific settings
  teams:
    enabled: true
    app_type: "android"  # or "linux"
    auto_signin: true
    resource_account: "room-confA@company.com"
    
  zoom:
    enabled: true
    app_type: "linux"  # or "android"
    room_license: true
    zoom_room_id: "your-room-id"
    
  webex:
    enabled: true
    app_type: "linux"
    device_activation_code: "your-code"
    
  google_meet:
    enabled: true
    app_type: "chrome"  # Chrome browser
    resource_account: "conf-room-a@company.com"
  
  # Calendar integration
  calendar:
    provider: "microsoft"  # or "google"
    sync_enabled: true
    sync_interval: 60
  
  # Call controls
  controls:
    unified_commands: true
    platform_specific_features: true  # Show Teams-only features when in Teams
    
  # Security
  security:
    require_pin: false  # For joining meetings
    admin_pin: "9999"  # For settings
    auto_lock_timeout: 300  # Lock panel after 5 min idle
```

---

## API Reference

### Join Meeting

```http
POST /api/rtc/join-meeting
Content-Type: application/json

{
  "meeting_id": "cal_event_123",
  "platform": "teams",  # auto-detected from calendar
  "options": {
    "muted": true,
    "camera_off": false
  }
}

Response:
{
  "status": "success",
  "session_id": "rtc_session_001",
  "platform": "teams",
  "meeting_url": "https://teams.microsoft.com/l/meetup-join/...",
  "joined_at": "2026-07-31T09:30:00Z"
}
```

### Call Control (Unified)

```http
POST /api/rtc/control
Content-Type: application/json

{
  "session_id": "rtc_session_001",
  "command": "mute_toggle"
}

Response:
{
  "status": "success",
  "command": "mute_toggle",
  "new_state": "muted",
  "platform": "teams"
}
```

### Get Meeting Status

```http
GET /api/rtc/status

Response:
{
  "active_session": {
    "session_id": "rtc_session_001",
    "platform": "teams",
    "meeting_title": "Project Review",
    "participants": 14,
    "duration_seconds": 1425,
    "muted": false,
    "camera_on": true,
    "screen_sharing": false,
    "recording": false,
    "host": "john.doe@company.com"
  },
  "upcoming_meetings": [
    {
      "meeting_id": "cal_event_124",
      "platform": "zoom",
      "title": "Client Call",
      "start_time": "2026-07-31T10:00:00Z",
      "duration_minutes": 60,
      "can_join": true
    }
  ]
}
```

---

## Deployment Scenarios

### Scenario 1: Enterprise Hybrid Office

**Environment:**
- 50 meeting rooms
- Mix of Teams (primary), Zoom (external clients), Webex (acquired company)
- Microsoft 365 calendar

**Solution:**
- MediaControl Gateway MCG-400K in each room
- Crestron TSW-770 touch panel per room
- Universal RTC interface
- Microsoft Graph API for calendar sync

**Benefits:**
- ✅ Same touch panel for all platforms
- ✅ Users don't need to know which platform
- ✅ IT manages 1 system instead of 3
- ✅ Cost: $599/room vs $2,000+/room (3× savings)

---

### Scenario 2: Law Firm (Multi-Client)

**Environment:**
- 20 meeting rooms
- Clients use different platforms (Teams, Zoom, Webex, Meet)
- Google Workspace calendar

**Solution:**
- MediaControl Gateway MCG-600K in each room
- Web-based touch interface on iPad Pro
- Universal RTC with all platforms enabled
- Google Calendar API integration

**Benefits:**
- ✅ Support any client's preferred platform
- ✅ No pre-meeting setup needed
- ✅ One-touch join regardless of platform
- ✅ Professional experience for all clients

---

### Scenario 3: University Classrooms

**Environment:**
- 100 classrooms
- Faculty use Teams, students use Zoom/Meet
- Mix of Microsoft 365 and Google Workspace

**Solution:**
- MediaControl Gateway MCG-400 in each room
- Custom web panel on touch-enabled monitors
- Universal RTC interface
- Dual calendar sync (Microsoft + Google)

**Benefits:**
- ✅ Faculty and students use same interface
- ✅ No training required
- ✅ Low cost per room ($449)
- ✅ Scalable to 100+ rooms

---

## Best Practices

### Network Requirements

✅ **Bandwidth:** Minimum 5 Mbps up/down per room  
✅ **QoS:** Prioritize RTC traffic (DSCP EF/46)  
✅ **Firewall:** Allow outbound HTTPS (443), SIP (5060-5061)  
✅ **NAT:** Use STUN/TURN servers for NAT traversal

### Calendar Setup

✅ **Resource accounts:** Create dedicated room accounts  
✅ **Auto-accept:** Enable automatic meeting acceptance  
✅ **Permissions:** Grant calendar read/write permissions  
✅ **Sync frequency:** 1-minute sync for real-time updates

### User Training

✅ **Signage:** Display instructions on screen when idle  
✅ **Onboarding:** 5-minute video for new users  
✅ **Support:** Helpdesk trained on Universal RTC  
✅ **Documentation:** QR code to user guide

---

## Next Steps

- **[Native Apps on Gateway](NATIVE_APPS.md):** Run Teams/Zoom directly on gateway (no external device)
- **[Video Wall & Signage](VIDEO_WALL_SIGNAGE.md):** Digital signage and video wall controller
- **[Multi-User Frontend](MULTIUSER_FRONTEND.md):** Collaborative workspace with simultaneous users
- **[Wireless Presentation](WIRELESS_PRESENTATION.md):** AirPlay, Chromecast, Miracast support

---

**For Universal RTC deployments:**  
**Contact:** rtc@mediacontrol.com  
**Demo:** Schedule a virtual demo at https://mediacontrol.com/demo/universal-rtc
