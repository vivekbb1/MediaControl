# MULTI-DEVICE SETUP GUIDE

Complete guide for controlling multiple source devices (STB, Apple TV, Android TV, etc.) across multiple displays with automatic input switching and contextual control.

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Quick Start](#quick-start)
4. [Device Setup](#device-setup)
   - [Apple TV](#apple-tv-setup)
   - [Android TV](#android-tv-setup)
   - [STB (already supported)](#stb-setup)
   - [HDMI Matrix](#hdmi-matrix-setup)
5. [Configuration](#configuration)
6. [User Guide](#user-guide)
7. [Troubleshooting](#troubleshooting)

---

## OVERVIEW

### What This Adds

**Previous capabilities:**
- Control Samsung Flip displays
- Control 1 STB via Broadlink IR
- EPG/TV Guide

**New capabilities:**
- ✅ **Multiple source devices** per room (STB, Apple TV, Android TV, etc.)
- ✅ **Multiple displays** per room (1-3 TVs)
- ✅ **App launching** (Netflix, Prime, Disney+, YouTube, etc.)
- ✅ **Automatic input switching** (select Netflix → TV switches to Apple TV input)
- ✅ **Contextual control** (D-pad controls whichever device is active)
- ✅ **HDMI matrix support** (route any source to any display)
- ✅ **Source presets** (one-tap access to apps/channels)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     INPUT ROUTER                         │
│  • Source-to-display mapping                             │
│  • Automatic input switching                             │
│  • Preset activation                                     │
└─────────────────────────────────────────────────────────┘
                            ↓
       ┌────────────────────┴────────────────────┐
       ↓                                         ↓
┌──────────────────┐                  ┌──────────────────┐
│  SOURCE MANAGER  │                  │ CONTEXT MANAGER  │
│  • STB devices   │                  │  • Active source │
│  • Apple TV      │                  │    per display   │
│  • Android TV    │                  │  • Command       │
│  • Control APIs  │                  │    routing       │
└──────────────────┘                  └──────────────────┘
```

---

## HARDWARE REQUIREMENTS

### Essential

1. **Samsung Flip / Smart TV** (1-3 per room)
   - Network-connected
   - MDC protocol support

2. **Broadlink RM4 Mini/Pro** (for STB control)
   - WiFi-connected
   - IR blaster

3. **Source Devices** (choose what you need):
   - Set-Top Box (Airtel, Jio, e&, du, OSN, etc.)
   - Apple TV (4th gen or later)
   - Android TV / Fire TV Stick
   - Any other HDMI source

### Optional

4. **HDMI Matrix Switcher** (for multi-display)
   - TCP/IP or RS-232 control
   - Brands: Monoprice, Kramer, Extron, Atlona
   - 4x4 or 8x8 recommended

5. **HDMI to IP Encoder** (for network streaming)
   - NDI, Dante, or proprietary

---

## QUICK START

### 1. Install Dependencies

```bash
# Install Python requirements
pip install -r requirements.txt

# Install Android SDK Platform Tools (for Android TV)
# macOS:
brew install android-platform-tools

# Linux:
sudo apt-get install android-tools-adb

# Windows:
# Download from https://developer.android.com/studio/releases/platform-tools
```

### 2. Set Up Devices

**Apple TV:**
```bash
# Pair with Apple TV (one-time setup)
python3 -c "
from appletv_device import pair_apple_tv
import asyncio
asyncio.run(pair_apple_tv('192.168.1.60', 'credentials/appletv.json'))
"
```

**Android TV:**
```bash
# Enable USB Debugging on Android TV
# Settings → About → Build Number (tap 7 times)
# Settings → Developer Options → USB Debugging (enable)
# Settings → Developer Options → Network Debugging (enable)

# Connect from computer
adb connect 192.168.1.61:5555

# Accept authorization on TV screen

# Test
adb -s 192.168.1.61:5555 shell echo test
```

**STB:**
```bash
# Already set up! Use existing Broadlink + IR codes
# See BROADLINK_SETUP.md for details
```

### 3. Configure Room

Copy and customize a config template:

```bash
# Simple setup (1 TV, Apple TV + STB)
cp SIMPLE_MULTI_DEVICE_CONFIG.yaml displays.yaml

# OR

# Complex setup (3 TVs, multiple sources, matrix)
cp MULTI_DEVICE_CONFIG_EXAMPLE.yaml displays.yaml

# Edit to match your hardware
nano displays.yaml
```

### 4. Test

```bash
# Start server
python3 server.py

# Open web interface
# http://YOUR_SERVER_IP:8080

# Try a preset (e.g., "Netflix")
# Should: switch TV to Apple TV input, wake Apple TV, launch Netflix
```

---

## DEVICE SETUP

### APPLE TV SETUP

#### Requirements

- Apple TV 4th generation or later
- Connected to same network as control server
- macOS/iOS device for initial pairing (one-time)

#### Setup Steps

1. **Find Apple TV IP Address**
   - On Apple TV: Settings → Network → Check "IP Address"
   - Or use network scanner

2. **Pair with Apple TV**

```bash
# Run pairing script
python3 -c "
from appletv_device import pair_apple_tv
import asyncio
asyncio.run(pair_apple_tv('APPLE_TV_IP', 'credentials/appletv.json'))
"
```

3. **Enter PIN**
   - PIN will appear on Apple TV screen
   - Enter it when prompted
   - Credentials saved to `credentials/appletv.json`

4. **Configure in displays.yaml**

```yaml
sources:
  - id: "apple-tv"
    type: "apple_tv"
    name: "Apple TV 4K"
    control:
      type: "pyatv"
      ip: "192.168.1.60"
      credentials_file: "credentials/appletv.json"
    hdmi_connection:
      display_id: "display-1"
      input_port: "hdmi2"
    apps:
      - id: "com.netflix.Netflix"
        name: "Netflix"
        icon: "netflix"
      - id: "com.amazon.aiv.AIVApp"
        name: "Prime Video"
        icon: "prime"
```

#### Finding App Bundle IDs

```bash
# List installed apps
pyatv --id <APPLE_TV_ID> apps

# Common apps:
# Netflix: com.netflix.Netflix
# Prime Video: com.amazon.aiv.AIVApp
# Disney+: com.disney.disneyplus
# YouTube: com.google.ios.youtube
# Apple TV+: com.apple.TVWatchList
# Hulu: com.hulu.plus
# Spotify: com.spotify.client
```

---

### ANDROID TV SETUP

#### Requirements

- Android TV or Fire TV device
- Connected to same network
- USB Debugging enabled

#### Setup Steps

1. **Enable Developer Mode**
   - Settings → About
   - Find "Build Number" (or "Android TV OS Build")
   - Tap 7 times
   - "You are now a developer" message appears

2. **Enable USB Debugging**
   - Settings → Device Preferences → Developer Options
   - Enable "USB Debugging"
   - Enable "Network Debugging" (if available)

3. **Find IP Address**
   - Settings → Network & Internet → WiFi → Advanced
   - Note IP address

4. **Connect via ADB**

```bash
# Connect
adb connect 192.168.1.61:5555

# Accept prompt on TV screen (first time only)

# Verify
adb -s 192.168.1.61:5555 shell echo test
# Should print: test
```

5. **Find App Package Names**

```bash
# List all packages
adb -s 192.168.1.61:5555 shell pm list packages

# Find Netflix
adb -s 192.168.1.61:5555 shell pm list packages | grep netflix

# Get main activity
adb -s 192.168.1.61:5555 shell dumpsys package com.netflix.ninja | grep -i activity
```

6. **Configure in displays.yaml**

```yaml
sources:
  - id: "android-stick"
    type: "android_tv"
    name: "Mi TV Stick"
    control:
      type: "adb"
      ip: "192.168.1.61"
      port: 5555
    hdmi_connection:
      display_id: "display-1"
      input_port: "hdmi3"
    apps:
      - id: "com.netflix.ninja/.MainActivity"
        name: "Netflix"
        icon: "netflix"
      - id: "com.hotstar.streaming/.MainActivity"
        name: "Hotstar"
        icon: "hotstar"
```

#### Common App Package/Activity Names

| App | Package/Activity |
|-----|------------------|
| Netflix | `com.netflix.ninja/.MainActivity` |
| Prime Video | `com.amazon.avod/.client.android.app.HomeActivity` |
| Disney+ | `com.disney.disneyplus/.StartActivity` |
| YouTube | `com.google.android.youtube.tv/.activity.ShellActivity` |
| Hotstar | `com.hotstar.streaming/.MainActivity` |
| Zee5 | `tv.zee5/.MainActivity` |
| SonyLIV | `com.sonyliv/.MainActivity` |
| Spotify | `com.spotify.tv.android/.SpotifyTVActivity` |

---

### STB SETUP

Already fully supported! See existing documentation:
- `BROADLINK_SETUP.md` - Complete Broadlink integration guide
- `BROADLINK_CONFIG_EXAMPLE.yaml` - STB configuration
- `INDIA_STB_CONFIG.yaml` - Indian provider configs
- `UAE_STB_CONFIG.yaml` - UAE provider configs

---

### HDMI MATRIX SETUP

#### Supported Matrices

1. **Monoprice Blackbird** (built-in support)
2. **Generic TCP** (Kramer, Extron, Atlona, OREI, etc.)

#### Configuration

```yaml
matrix:
  id: "matrix-1"
  type: "monoprice_blackbird"  # or "generic_tcp"
  name: "4x4 Matrix"
  control:
    ip: "192.168.1.100"
    port: 23
  num_inputs: 4
  num_outputs: 4
  inputs:
    1: "stb-airtel"
    2: "apple-tv"
    3: "android-stick"
    4: null
  outputs:
    1: "display-1"
    2: "display-2"
    3: "display-3"
    4: null
```

#### For Generic TCP Matrices

Find the command format in your matrix's manual:

```yaml
matrix:
  type: "generic_tcp"
  control:
    ip: "192.168.1.100"
    port: 5000
    route_command: "#{output}@{input}."  # Customize this!
    terminator: "\r\n"
```

Common formats:
- `#{output}@{input}.` (common)
- `SW {input} {output}` (Kramer)
- `{output}*{input}!` (Extron)

---

## CONFIGURATION

### Source Presets

Presets are one-tap shortcuts that combine multiple actions:

```yaml
presets:
  # Launch Netflix
  - name: "Netflix"
    icon: "netflix"
    category: "streaming"
    source_id: "apple-tv"
    displays: ["display-1"]
    action:
      type: "launch_app"
      app_id: "com.netflix.Netflix"
  
  # Tune to channel
  - name: "Star Plus"
    category: "tv"
    source_id: "stb-airtel"
    displays: ["display-1"]
    action:
      type: "tune_channel"
      channel: 109
  
  # Show on all displays
  - name: "Apple TV on All"
    source_id: "apple-tv"
    displays: ["display-1", "display-2", "display-3"]
    action:
      type: "send_command"
      command: "home"
```

### Multi-Display Scenarios

**Scenario 1: Same source on all displays**

```yaml
- name: "Presentation Mode"
  source_id: "apple-tv"
  displays: ["display-1", "display-2", "display-3"]
  action:
    type: "launch_app"
    app_id: "com.apple.TVWatchList"
```

**Scenario 2: Different sources per display**

Set up multiple presets, one per display:

```yaml
- name: "Netflix (Main)"
  source_id: "apple-tv"
  displays: ["display-1"]
  
- name: "News (Side)"
  source_id: "stb"
  displays: ["display-2"]
```

---

## USER GUIDE

### How It Works

#### Source Selection
1. User taps "Netflix" in source grid
2. System identifies: Netflix is on Apple TV (HDMI 2)
3. System executes:
   - Switch TV to HDMI 2
   - Wake Apple TV
   - Launch Netflix app
4. Context Manager sets: Display 1 active source = Apple TV

#### Contextual Navigation
- D-pad, OK, Back buttons now control Apple TV
- If user then selects "Star Plus":
  - TV switches to HDMI 1 (STB)
  - STB tunes to channel 109
  - D-pad now controls STB instead

### API Endpoints

```bash
# Activate preset
POST /api/presets/Netflix/activate

# Switch to source
POST /api/displays/display-1/switch-to-source
{
  "source_id": "apple-tv",
  "auto_power_on": true
}

# Send contextual command (routes to active source)
POST /api/displays/display-1/send-contextual
{
  "command": "up"
}

# Get routing status
GET /api/routing/status

# List sources
GET /api/sources

# List presets
GET /api/presets
```

---

## TROUBLESHOOTING

### Apple TV Issues

**Problem: Pairing fails**
- Ensure Apple TV and computer on same network
- Check firewall isn't blocking ports 49152-65535
- Try restarting Apple TV

**Problem: Apps won't launch**
- Check bundle ID is correct: `pyatv --id <ID> apps`
- Some apps require user to be signed in first

**Problem: Connection drops**
- Apple TV may enter deep sleep
- Enable "Stay Awake" in Settings → General → Sleep After → Never

### Android TV Issues

**Problem: `adb: device unauthorized`**
- Check TV screen for authorization prompt
- Delete `~/.android/adbkey` and reconnect

**Problem: `adb: device offline`**
- Restart Android TV
- Reconnect: `adb disconnect` then `adb connect`

**Problem: Apps won't launch**
- Package name may be wrong
- Try: `adb shell monkey -p com.netflix.ninja 1`

### HDMI Matrix Issues

**Problem: Commands not working**
- Check IP and port are correct
- Verify matrix is on network: `ping <IP>`
- Check command format matches your matrix model

**Problem: Wrong routing**
- Matrix may remember previous state
- Send all routing commands explicitly

### General

**Problem: Input doesn't switch**
- Check `hdmi_connection` in config matches physical setup
- Verify display supports MDC input switching
- Test manual input switch on display first

**Problem: Contextual commands go to wrong device**
- Check Context Manager state: GET `/api/routing/status`
- Active source may not be set correctly
- Try explicitly selecting source again

---

## NEXT STEPS

1. ✅ Basic multi-device control working
2. ⏩ Frontend UI updates (source grid with app icons)
3. ⏩ Visual feedback (show active source)
4. ⏩ Advanced features:
   - Voice control integration
   - Automation scenes
   - Activity-based switching
   - Remote access (VPN/cloud)

---

## EXAMPLES

See these files for complete working examples:
- `MULTI_DEVICE_CONFIG_EXAMPLE.yaml` - Full 3-display setup
- `SIMPLE_MULTI_DEVICE_CONFIG.yaml` - Basic home setup
- `INDIA_STB_CONFIG.yaml` - Indian providers
- `UAE_STB_CONFIG.yaml` - UAE providers
- `CROSS_TIMEZONE_CONFIG.yaml` - Expat setups

---

**Ready to control your multimedia empire! 🎬📺🎮**
