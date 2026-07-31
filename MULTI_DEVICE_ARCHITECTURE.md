# MULTI-DEVICE ARCHITECTURE DESIGN

## Current vs Required Architecture

### **CURRENT (Single Device per Type)**
```
Room → Display (Samsung Flip) → STB (via Broadlink IR)
```

### **REQUIRED (Multi-Device Matrix)**
```
Room
├── Display 1 (Samsung Flip)
│   ├── HDMI 1 → STB (Airtel)
│   ├── HDMI 2 → Apple TV
│   ├── HDMI 3 → Android TV Stick
│   └── HDMI 4 → HDMI Matrix Output
├── Display 2 (Samsung Flip)
│   ├── HDMI 1 → HDMI Matrix Output
│   └── USB-C → Laptop
├── Display 3 (Samsung Flip)
│   └── HDMI 1 → HDMI Matrix Output
├── Source Devices
│   ├── STB 1 (Airtel)
│   ├── STB 2 (Jio)
│   ├── Apple TV
│   ├── Android TV Stick
│   └── Fire TV Stick
├── HDMI Matrix Switcher (4x4 or 8x8)
│   └── Routes any source to any display
└── HDMI to IP Encoders
    └── Stream to network devices
```

---

## NEW ARCHITECTURE COMPONENTS

### 1. **Device Abstraction Layer**

Each source device has:
- **Device ID** (unique identifier)
- **Device Type** (stb, apple_tv, android_tv, fire_tv, game_console, etc.)
- **Control Protocol** (ir, network_api, cec, adb, rest_api)
- **Physical Connection** (which HDMI port, which display)
- **Capabilities** (apps it can run, commands it supports)
- **State** (power, current app, current input)

### 2. **Source Manager**

Manages all source devices:
```python
class SourceDevice:
    id: str
    type: str  # stb, apple_tv, android_tv, etc.
    name: str
    control_protocol: str
    connection: DeviceConnection
    capabilities: dict
    apps: dict  # app_id → app details
```

### 3. **Input Router**

Maps sources to display inputs:
```python
class InputRouter:
    # When user selects "Netflix", router:
    # 1. Identifies device (Apple TV)
    # 2. Gets HDMI port (Display 1, HDMI 2)
    # 3. Switches display to HDMI 2
    # 4. Wakes Apple TV
    # 5. Opens Netflix app
```

### 4. **Context Manager**

Tracks active source per display:
```python
class ContextManager:
    # Tracks which source is active on each display
    # Routes D-pad/navigation to active device
    active_sources: dict  # display_id → source_device_id
```

### 5. **HDMI Matrix Controller**

Controls HDMI switchers:
```python
class HDMIMatrix:
    # Route source N to output M
    # Common brands: Monoprice, Kramer, Extron
    # Protocols: RS-232, TCP/IP, HTTP
```

---

## CONTROL PROTOCOLS PER DEVICE TYPE

### **STB (Already Implemented ✅)**
- **Protocol:** Broadlink IR/RF
- **Commands:** Channel, navigation, transport
- **Status:** Fully implemented

### **Apple TV (NEW ❌)**
- **Protocol Options:**
  1. **pyatv** (network API) - BEST
     - Full control over network
     - Can launch apps by app ID
     - Can send remote commands
     - Requires pairing
  2. **HDMI-CEC** (via display)
     - Basic control
     - May work through Samsung Flip
  3. **IR** (via Broadlink)
     - Less reliable
     - Can't launch specific apps

- **Required:**
  - Install `pyatv` Python library
  - Discover Apple TV on network
  - Pair with device
  - Store credentials

- **App Launching:**
  ```python
  # Launch Netflix
  atv.apps.launch_app("com.netflix.Netflix")
  
  # Launch Prime Video
  atv.apps.launch_app("com.amazon.aiv.AIVApp")
  ```

### **Android TV / Fire TV Stick (NEW ❌)**
- **Protocol Options:**
  1. **ADB over Network** - BEST
     - Full control via Android Debug Bridge
     - Launch apps by package name
     - Send keyevent codes
     - Requires USB debugging enabled
  2. **IR** (via Broadlink)
     - Basic control
     - Can't launch specific apps

- **Required:**
  - Enable Developer Options on Android TV
  - Enable USB Debugging
  - Enable Network ADB
  - Install `pure-python-adb` or use `adb` command

- **App Launching:**
  ```bash
  # Launch Netflix
  adb connect 192.168.1.100:5555
  adb shell am start -n com.netflix.ninja/.MainActivity
  
  # Launch Prime Video
  adb shell am start -n com.amazon.avod/.client.android.app.HomeActivity
  
  # Send D-pad commands
  adb shell input keyevent KEYCODE_DPAD_UP
  ```

### **HDMI Matrix Switcher (NEW ❌)**
- **Common Brands:**
  - Monoprice Blackbird
  - Kramer
  - Extron
  - Atlona
  - OREI

- **Control Protocols:**
  1. **TCP/IP** (most common)
  2. **RS-232** (serial)
  3. **HTTP REST API** (newer models)
  4. **IR** (basic models)

- **Example Commands:**
  ```python
  # Route input 2 (Apple TV) to output 1 (Display 1)
  matrix.route(input=2, output=1)
  
  # Get current routing
  matrix.get_status()
  ```

### **HDMI to IP Encoders (NEW ❌)**
- **Examples:** NDI, Dante, proprietary encoders
- **Purpose:** Stream HDMI sources over network
- **Control:** Usually HTTP API or SNMP
- **Not priority** - can be added later

---

## USER INTERACTION FLOW

### **Example 1: User Wants to Watch Netflix**

**Current System:** N/A (not supported)

**New System:**
1. **User:** Taps "Netflix" on source grid
2. **System identifies:**
   - Netflix is on Apple TV
   - Apple TV is connected to Display 1, HDMI 2
3. **System executes:**
   - Switch Display 1 to HDMI 2 (via MDC)
   - Wake Apple TV (via pyatv)
   - Launch Netflix app (via pyatv)
4. **Context Manager:** Sets Display 1 active source = Apple TV
5. **D-pad now controls:** Apple TV (all nav commands go to Apple TV)

### **Example 2: User Wants to Watch Star Plus**

**Current System:** Works ✅

**New System (enhanced):**
1. **User:** Taps "Star Plus" on EPG or channel grid
2. **System identifies:**
   - Star Plus is channel 109 on Airtel STB
   - Airtel STB is connected to Display 1, HDMI 1
3. **System executes:**
   - Switch Display 1 to HDMI 1 (via MDC)
   - Wake STB (via Broadlink IR: Power)
   - Tune to channel 109 (via Broadlink IR: 1-0-9)
4. **Context Manager:** Sets Display 1 active source = Airtel STB
5. **D-pad now controls:** Airtel STB

### **Example 3: Multi-Display Setup**

**Scenario:** Conference room with 3 displays, want to show same content on all

1. **User:** Selects "Show Apple TV on all displays"
2. **System:**
   - If using HDMI matrix:
     - Route Apple TV input to outputs 1, 2, 3
   - If using direct connections:
     - Switch Display 1 to HDMI 2 (Apple TV)
     - Switch Display 2 to HDMI 1 (Apple TV via splitter)
     - Switch Display 3 to HDMI 1 (Apple TV via splitter)
3. **Context Manager:** All displays = Apple TV
4. **D-pad controls:** Apple TV (affects all displays)

---

## CONFIGURATION STRUCTURE

### **New YAML Structure:**

```yaml
room:
  id: "multimedia-room-1"
  name: "Conference Room A"
  
  # Multiple displays
  displays:
    - id: "display-1"
      type: "samsung_flip"
      name: "Main Display"
      ip: "192.168.1.10"
      inputs:
        hdmi1: "stb-airtel"
        hdmi2: "apple-tv"
        hdmi3: "android-stick"
        hdmi4: "matrix-output-1"
    
    - id: "display-2"
      type: "samsung_flip"
      name: "Side Display"
      ip: "192.168.1.11"
      inputs:
        hdmi1: "matrix-output-2"
    
    - id: "display-3"
      type: "samsung_flip"
      name: "Back Display"
      ip: "192.168.1.12"
      inputs:
        hdmi1: "matrix-output-3"
  
  # Source devices
  sources:
    - id: "stb-airtel"
      type: "stb"
      name: "Airtel STB"
      control:
        type: "broadlink"
        device_ip: "192.168.1.50"
        ir_codes_file: "ir_codes/airtel_stb.yaml"
      epg:
        timezone: "Asia/Dubai"
        channels: [...] # existing channel config
    
    - id: "stb-jio"
      type: "stb"
      name: "Jio STB"
      control:
        type: "broadlink"
        device_ip: "192.168.1.50"
        ir_codes_file: "ir_codes/jio_stb.yaml"
    
    - id: "apple-tv"
      type: "apple_tv"
      name: "Apple TV 4K"
      control:
        type: "pyatv"
        ip: "192.168.1.60"
        credentials_file: "credentials/appletv.json"
      apps:
        - id: "com.netflix.Netflix"
          name: "Netflix"
          icon: "netflix"
        - id: "com.amazon.aiv.AIVApp"
          name: "Prime Video"
          icon: "prime"
        - id: "com.disney.disneyplus"
          name: "Disney+"
          icon: "disney"
        - id: "com.apple.TVWatchList"
          name: "Apple TV+"
          icon: "appletv"
    
    - id: "android-stick"
      type: "android_tv"
      name: "Mi TV Stick"
      control:
        type: "adb"
        ip: "192.168.1.61"
        port: 5555
      apps:
        - package: "com.netflix.ninja"
          name: "Netflix"
          icon: "netflix"
        - package: "com.hotstar.streaming"
          name: "Hotstar"
          icon: "hotstar"
  
  # HDMI Matrix (optional)
  matrix:
    type: "monoprice_blackbird"
    name: "4x4 Matrix"
    control:
      type: "tcp"
      ip: "192.168.1.100"
      port: 23
    inputs:
      1: "stb-airtel"
      2: "stb-jio"
      3: "apple-tv"
      4: "android-stick"
    outputs:
      1: "display-1"
      2: "display-2"
      3: "display-3"
  
  # Source presets
  presets:
    - name: "Netflix"
      source: "apple-tv"
      action:
        type: "launch_app"
        app_id: "com.netflix.Netflix"
      displays: ["display-1"]
    
    - name: "Star Plus"
      source: "stb-airtel"
      action:
        type: "tune_channel"
        channel: 109
      displays: ["display-1"]
    
    - name: "All Displays - Apple TV"
      source: "apple-tv"
      displays: ["display-1", "display-2", "display-3"]
```

---

## IMPLEMENTATION PRIORITIES

### **Phase 1: Foundation (Core Multi-Device)**
1. ✅ Device abstraction layer
2. ✅ Source manager
3. ✅ Input router (basic)
4. ✅ Context manager
5. ✅ Multi-display support in config

### **Phase 2: Apple TV Control**
1. ✅ Install `pyatv`
2. ✅ Discovery and pairing module
3. ✅ App launcher
4. ✅ Remote control commands
5. ✅ Integration with input router

### **Phase 3: Android TV Control**
1. ✅ ADB network control module
2. ✅ App launcher (via intent)
3. ✅ Remote control (keyevents)
4. ✅ Integration with input router

### **Phase 4: HDMI Matrix Control**
1. ✅ TCP/IP matrix controller
2. ✅ Common protocol support (Monoprice, Kramer)
3. ✅ Routing logic
4. ✅ Status monitoring

### **Phase 5: UI Updates**
1. ✅ Source grid (by device type)
2. ✅ App shortcuts (Netflix, Prime, etc.)
3. ✅ Display selector (for multi-display)
4. ✅ Active source indicator
5. ✅ Contextual D-pad (shows which device is being controlled)

### **Phase 6: Advanced Features**
1. ⚠️ HDMI to IP encoder support
2. ⚠️ Preset scenes ("Movie Night" = all displays, Apple TV, dim lights)
3. ⚠️ Picture-in-picture routing
4. ⚠️ Audio routing (separate from video)

---

## TECHNICAL CHALLENGES

### **Challenge 1: Device Discovery**
- **Problem:** Finding devices on network automatically
- **Solutions:**
  - mDNS/Bonjour for Apple TV
  - ADB scanning for Android TV
  - Manual IP configuration as fallback

### **Challenge 2: Device State Sync**
- **Problem:** Knowing if Apple TV is on Netflix or Home screen
- **Solutions:**
  - Poll device status regularly
  - Listen to state change callbacks (if supported)
  - Track last command sent as fallback

### **Challenge 3: Command Latency**
- **Problem:** Multiple commands in sequence (switch input, wake device, launch app)
- **Solutions:**
  - Add delays between commands
  - Wait for device ready state
  - Async command queue

### **Challenge 4: Device Authentication**
- **Problem:** Apple TV requires pairing, Android TV requires ADB auth
- **Solutions:**
  - Pairing wizard in web UI
  - Store credentials securely
  - Auto-reconnect on failure

### **Challenge 5: Contextual Control**
- **Problem:** User presses D-pad, which device should respond?
- **Solutions:**
  - Track active source per display
  - Show active source in UI clearly
  - Allow manual source selection

---

## COMPARISON: BEFORE vs AFTER

| Feature | Current System | New Multi-Device System |
|---------|----------------|-------------------------|
| Displays per room | 1 | 1-3 (configurable) |
| Source devices | 1 STB | Multiple (STB, Apple TV, Android TV, etc.) |
| Control methods | IR only | IR + Network API + ADB + CEC |
| App launching | ❌ No | ✅ Yes (Netflix, Prime, etc.) |
| Auto input switch | ⚠️ Manual | ✅ Automatic |
| Contextual D-pad | ❌ No | ✅ Yes |
| HDMI matrix | ❌ No | ✅ Yes |
| Source presets | ⚠️ Limited | ✅ Full (quick actions) |
| Multi-display sync | ❌ No | ✅ Yes |

---

## ESTIMATED COMPLEXITY

**Current System Complexity:** ⭐⭐ (Simple)
- Display control + IR commands
- About 2,000 lines of code

**New System Complexity:** ⭐⭐⭐⭐⭐ (Professional AV System)
- Device abstraction, multiple protocols, routing logic
- Estimated 8,000-10,000 lines of code
- Similar to Crestron/Control4 systems

**Development Effort:**
- Phase 1 (Foundation): ~40-50 tool calls
- Phase 2 (Apple TV): ~30-40 tool calls
- Phase 3 (Android TV): ~30-40 tool calls
- Phase 4 (HDMI Matrix): ~20-30 tool calls
- Phase 5 (UI): ~30-40 tool calls
- **Total: ~150-200 tool calls**

---

## NEXT STEPS

1. ✅ Design architecture (THIS DOCUMENT)
2. ⏩ Create device abstraction layer
3. ⏩ Implement source manager
4. ⏩ Add Apple TV control module
5. ⏩ Add Android TV control module
6. ⏩ Implement input routing logic
7. ⏩ Add contextual control
8. ⏩ Update UI for source grid
9. ⏩ Testing with real devices

**Ready to proceed?** This is a major architectural upgrade but will result in a truly professional multi-device control system.
