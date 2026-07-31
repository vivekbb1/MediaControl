# Consumer Smart Home Platform Integration

**Apple Home, Google Home, Xiaomi Mi Home, Amazon Alexa, Samsung SmartThings**

---

## Table of Contents

1. [Overview](#overview)
2. [Apple Home (HomeKit) Integration](#apple-home-homekit-integration)
3. [Google Home Integration](#google-home-integration)
4. [Xiaomi Mi Home Integration](#xiaomi-mi-home-integration)
5. [Amazon Alexa Integration](#amazon-alexa-integration)
6. [Samsung SmartThings Integration](#samsung-smartthings-integration)
7. [Configuration](#configuration)
8. [API Reference](#api-reference)

---

## Overview

**MediaControl Consumer Platform Integration** provides native integration with the world's most popular smart home ecosystems:

- **Apple Home (HomeKit)** - Native HomeKit accessory protocol (HAP)
- **Google Home** - Native Google Home Local Home SDK
- **Xiaomi Mi Home** - Direct Mi Home app integration
- **Amazon Alexa** - Alexa Smart Home Skill API
- **Samsung SmartThings** - SmartThings Device SDK

### Why Direct Integration?

While MediaControl supports **Matter** (universal standard), many users prefer direct native integration with their chosen ecosystem:

| Feature | Matter | Native Integration |
|---------|--------|-------------------|
| **Setup** | QR code (simple) | OAuth + pairing (varies) |
| **Features** | Limited to Matter spec | Full ecosystem features |
| **Voice Control** | Basic commands | Advanced routines |
| **Automation** | Basic scenes | Advanced automations |
| **UI** | Generic | Platform-specific |

**Both are supported!** Use Matter for simplicity, or native integration for advanced features.

---

## Apple Home (HomeKit) Integration

### Overview

**Apple HomeKit** is Apple's smart home platform, integrated into iOS, iPadOS, macOS, watchOS, and Apple TV.

**MediaControl Gateway** becomes a **HomeKit accessory**, allowing control from:
- Home app (iPhone, iPad, Mac, Apple Watch)
- Siri voice commands
- HomeKit automations
- Control Center quick access

### HomeKit Accessory Protocol (HAP)

MediaControl implements the **HomeKit Accessory Protocol (HAP)** to become a native HomeKit accessory.

#### Supported HomeKit Services

MediaControl exposes the following HomeKit services:

| MediaControl Device | HomeKit Service | Characteristics |
|-------------------|-----------------|-----------------|
| Display | Television | Power, Input Source, Remote Key |
| Source Device | Television | Power, Input Source |
| Smart Lock | Lock Mechanism | Lock Current State, Lock Target State |
| Video Doorbell | Doorbell + Camera | Programmable Switch, Snapshot, Video Stream |
| Audio Zone | Speaker | Mute, Volume, Name |
| SIP Phone | Speaker | Mute, Volume |
| Room | Service Label | Service Label Namespace |

### Setup Instructions

#### 1. Generate HomeKit Pairing Code

MediaControl Gateway generates a unique 8-digit HomeKit setup code:

```
Setup Code: 123-45-678
```

This code is displayed:
- On the MediaControl web interface
- On the gateway's OLED display (if equipped)
- In the gateway's QR code (scannable from Home app)

#### 2. Add to Home App

**iPhone/iPad:**
1. Open **Home** app
2. Tap **+** → **Add Accessory**
3. Scan QR code on MediaControl Gateway (or enter setup code manually)
4. Follow on-screen instructions
5. Assign rooms and configure

**Mac:**
1. Open **Home** app
2. **File** → **Add Accessory**
3. Enter setup code
4. Configure

#### 3. Configure Devices

After adding, MediaControl devices appear in Home app:

```
Living Room
  └─ MediaControl Gateway
       ├─ Conference TV (Television)
       ├─ Apple TV (Television)
       ├─ Front Door Lock (Lock)
       ├─ Front Doorbell (Doorbell)
       └─ Room Audio (Speaker)
```

### HomeKit Features

#### Voice Control via Siri

```
"Hey Siri, turn on the Conference TV"
"Hey Siri, switch Conference TV to HDMI 2"
"Hey Siri, unlock the Front Door"
"Hey Siri, show me the Front Door camera"
"Hey Siri, set Conference Room volume to 50%"
```

#### Automations

**Arrive Home:**
```
When: I arrive home
Do:
  - Unlock Front Door
  - Turn on Living Room TV
  - Set input to Apple TV
  - Turn on lights (other HomeKit devices)
```

**Leave Home:**
```
When: I leave home
Do:
  - Lock Front Door
  - Turn off all TVs (MediaControl)
  - Turn off lights
  - Set thermostat to Away
```

**Bedtime:**
```
When: 10:00 PM
Do:
  - Lock all doors
  - Turn off all TVs
  - Turn off lights
  - Lower shades
```

#### Scenes

Create HomeKit scenes that control MediaControl devices:

**"Movie Time" Scene:**
- Turn on Living Room TV
- Switch to Apple TV input
- Dim lights to 20%
- Close curtains
- Set audio to Surround mode

**"Good Morning" Scene:**
- Unlock Front Door
- Turn on Kitchen TV → News channel
- Turn on lights
- Start coffee maker (HomeKit plug)

#### Remote Control

Control MediaControl displays using HomeKit remote:
- Play/Pause
- Up/Down/Left/Right (D-pad)
- Back
- Select
- Volume Up/Down
- Mute

### Configuration

```yaml
apple_homekit:
  enabled: true
  
  # HomeKit Accessory Protocol (HAP)
  hap:
    port: 51827  # Default HAP port
    setup_code: "123-45-678"  # 8-digit setup code (format: XXX-XX-XXX)
    
    # Accessory information
    accessory:
      name: "MediaControl Gateway"
      manufacturer: "MediaControl"
      model: "MCG-Pro"
      serial_number: "MC-PRO-00001"
      firmware_version: "1.0.0"
      
    # mDNS/Bonjour discovery
    mdns:
      enabled: true
      service_name: "_hap._tcp"
  
  # Devices to expose to HomeKit
  expose_devices:
    displays:
      - display_id: "display_1"
        name: "Conference TV"
        room: "Conference Room"
        service_type: "television"
        
        # Television characteristics
        characteristics:
          active: true  # Power on/off
          active_identifier: true  # Current input
          remote_key: true  # Remote control
          
        # Input sources
        input_sources:
          - identifier: 1
            name: "HDMI 1 (Laptop)"
            input_source_type: "hdmi"
          - identifier: 2
            name: "HDMI 2 (Apple TV)"
            input_source_type: "application"
          - identifier: 3
            name: "HDMI 3 (Cable Box)"
            input_source_type: "tuner"
    
    locks:
      - lock_id: "front_door_lock"
        name: "Front Door Lock"
        room: "Entrance"
        service_type: "lock_mechanism"
    
    doorbells:
      - doorbell_id: "front_door"
        name: "Front Doorbell"
        room: "Entrance"
        service_type: "doorbell"
        
        # Camera stream
        camera:
          stream_url: "rtsp://192.168.1.100/doorbell/front"
          snapshot_url: "http://192.168.1.100/api/doorbell/front/snapshot"
          width: 1920
          height: 1080
          framerate: 30
    
    audio_zones:
      - zone_id: "conference_audio"
        name: "Conference Room Speakers"
        room: "Conference Room"
        service_type: "speaker"
  
  # HomeKit Secure Video (HKSV)
  secure_video:
    enabled: false  # Requires iCloud+ subscription
    # If enabled, doorbell recordings are stored in iCloud (end-to-end encrypted)
  
  # Thread support (for HomeKit over Thread)
  thread:
    enabled: false  # Enable if gateway has Thread radio
    border_router: false  # Enable if gateway acts as Thread Border Router
```

### HomeKit Secure Video (HKSV)

If you have an **iCloud+ subscription** (50 GB or higher), you can enable **HomeKit Secure Video** for doorbells:

**Benefits:**
- **End-to-end encrypted** video storage in iCloud
- **10 days of recording** (iCloud+ 50 GB)
- **Activity zones** (record only in specific areas)
- **Face recognition** (identify known people)
- **Package detection** (notify when package delivered)
- **No additional cost** (included with iCloud+)

**Setup:**
1. Enable `secure_video: true` in config
2. In Home app, tap doorbell → Settings → Record Video
3. Choose recording options (Streaming & Recording, Streaming Only, Off)

---

## Google Home Integration

### Overview

**Google Home** is Google's smart home platform, integrated into:
- Google Home app (Android, iOS)
- Google Assistant (Android, iOS, web)
- Google Nest Hub displays
- Chromecast with Google TV

**MediaControl Gateway** integrates with Google Home via:
1. **Google Home Local Home SDK** (local control, low latency)
2. **Google Smart Home Action** (cloud control, voice commands)

### Supported Device Types

MediaControl exposes the following Google Home device types:

| MediaControl Device | Google Home Type | Traits |
|-------------------|------------------|--------|
| Display | TV | OnOff, Volume, InputSelector, TransportControl |
| Source Device | MediaPlayer | OnOff, TransportControl, MediaState |
| Smart Lock | Lock | LockUnlock |
| Video Doorbell | Camera | CameraStream |
| Audio Zone | Speaker | OnOff, Volume, MediaState |
| SIP Phone | Phone | - |
| Room | Scene | Scene |

### Setup Instructions

#### 1. Link MediaControl to Google Home

**Option A: Local Home SDK (Recommended)**

1. Open **Google Home** app
2. Tap **+** → **Set up device** → **Works with Google**
3. Search for "MediaControl"
4. Tap **MediaControl** → **Link**
5. Sign in with your MediaControl account
6. Allow permissions
7. Assign rooms

**Option B: Cloud Integration**

1. In MediaControl web interface, go to **Settings** → **Integrations** → **Google Home**
2. Click **Link with Google**
3. Sign in with Google account
4. Authorize MediaControl

#### 2. Assign Devices to Rooms

In Google Home app:
1. Tap device → Settings icon
2. **Device information** → **Room**
3. Select room (or create new)

#### 3. Configure Device Settings

For each device:
- Set default volume levels
- Configure input source names
- Enable/disable features

### Google Assistant Voice Commands

```
"Hey Google, turn on the Conference TV"
"Hey Google, switch Conference TV to HDMI 2"
"Hey Google, turn up the volume on Conference TV"
"Hey Google, play Netflix on Living Room TV"
"Hey Google, unlock the Front Door"
"Hey Google, show me the Front Door camera"
"Hey Google, show Front Door camera on Nest Hub"
```

### Routines

Create Google Home routines that control MediaControl devices:

**"Good Morning" Routine:**
```
Trigger: "Hey Google, good morning"
Actions:
  - Turn on Kitchen TV
  - Switch to YouTube TV
  - Open curtains (smart blinds)
  - Turn on coffee maker
  - Read news and weather
```

**"Movie Night" Routine:**
```
Trigger: "Hey Google, movie night"
Actions:
  - Turn on Living Room TV
  - Switch to Chromecast
  - Dim lights to 10%
  - Close curtains
  - Set Do Not Disturb
```

**"Leaving Home" Routine:**
```
Trigger: I leave home (location-based)
Actions:
  - Lock all doors (MediaControl)
  - Turn off all TVs (MediaControl)
  - Turn off lights
  - Set thermostat to Away
```

### Configuration

```yaml
google_home:
  enabled: true
  
  # Local Home SDK (local control, low latency)
  local_home:
    enabled: true
    port: 3388  # Local fulfillment port
    
    # mDNS discovery
    mdns:
      enabled: true
      service_name: "_mediacontrol._tcp"
      
  # Smart Home Action (cloud control, voice commands)
  smart_home_action:
    enabled: true
    
    # OAuth 2.0 credentials
    oauth:
      client_id: "your_google_client_id"
      client_secret: "your_google_client_secret"
      
    # Project ID from Google Cloud Console
    project_id: "mediacontrol-home"
    
  # Devices to expose to Google Home
  expose_devices:
    displays:
      - display_id: "display_1"
        name: "Conference TV"
        room: "Conference Room"
        type: "action.devices.types.TV"
        
        traits:
          - "action.devices.traits.OnOff"
          - "action.devices.traits.Volume"
          - "action.devices.traits.InputSelector"
          - "action.devices.traits.TransportControl"
          
        # Input sources
        inputs:
          - key: "hdmi1"
            names: ["HDMI 1", "Laptop"]
          - key: "hdmi2"
            names: ["HDMI 2", "Apple TV"]
          - key: "hdmi3"
            names: ["HDMI 3", "Cable"]
    
    locks:
      - lock_id: "front_door_lock"
        name: "Front Door Lock"
        room: "Entrance"
        type: "action.devices.types.LOCK"
        traits:
          - "action.devices.traits.LockUnlock"
    
    doorbells:
      - doorbell_id: "front_door"
        name: "Front Doorbell Camera"
        room: "Entrance"
        type: "action.devices.types.CAMERA"
        traits:
          - "action.devices.traits.CameraStream"
        
        # Camera stream
        camera_stream_protocol: "hls"
        camera_stream_url: "https://192.168.1.100/doorbell/front/stream.m3u8"
    
    audio_zones:
      - zone_id: "conference_audio"
        name: "Conference Room Speakers"
        room: "Conference Room"
        type: "action.devices.types.SPEAKER"
        traits:
          - "action.devices.traits.OnOff"
          - "action.devices.traits.Volume"
  
  # Google Assistant integration
  assistant:
    enabled: true
    # Custom voice commands
    custom_commands:
      - trigger: "presentation mode"
        action: "activate_preset"
        parameters:
          preset_id: "presentation"
```

### Google Nest Hub Integration

Display MediaControl camera streams on **Google Nest Hub**:

```
"Hey Google, show Front Door camera"
"Hey Google, show Conference Room camera on Living Room display"
```

MediaControl streams appear in full-screen on Nest Hub with:
- Live video feed
- Two-way audio (if doorbell supports it)
- Quick actions (unlock door, etc.)

---

## Xiaomi Mi Home Integration

### Overview

**Xiaomi Mi Home** (米家 Mǐjiā) is Xiaomi's smart home ecosystem, popular in China and globally.

**MediaControl** integrates with Mi Home via:
1. **Xiaomi Cloud API** (for Xiaomi account devices)
2. **Local Xiaomi Gateway Protocol** (for direct control)
3. **Aqara Hub** (for Aqara-branded Xiaomi devices)

**Note:** Xiaomi ecosystem includes:
- Xiaomi-branded devices (米家)
- Aqara-branded devices (绿米)
- Yeelight lighting
- Roborock vacuums
- Xiaomi appliances

### Supported Devices (Xiaomi → MediaControl)

MediaControl can control Xiaomi devices:

| Xiaomi Device | Control From MediaControl |
|--------------|---------------------------|
| Yeelight bulbs | Turn on/off, brightness, color |
| Xiaomi smart plugs | Turn on/off |
| Xiaomi IR remote | Send IR commands to TVs, ACs |
| Xiaomi door sensors | Monitor state, trigger events |
| Xiaomi motion sensors | Trigger MediaControl actions |
| Xiaomi curtain motors | Open/close curtains |

### Supported Devices (MediaControl → Mi Home)

MediaControl devices can be controlled from Mi Home app:

| MediaControl Device | Mi Home Device Type |
|-------------------|-------------------|
| Display | TV (电视) |
| Smart Lock | Smart Lock (智能门锁) |
| Video Doorbell | Doorbell Camera (门铃摄像机) |
| Audio Zone | Speaker (音箱) |

### Setup Instructions

#### 1. Link Xiaomi Account

**In MediaControl Web Interface:**
1. Go to **Settings** → **Integrations** → **Xiaomi Mi Home**
2. Click **Login with Xiaomi Account**
3. Enter Xiaomi username/password
4. Enter verification code (SMS or email)
5. Click **Authorize**

**Supported Regions:**
- China Mainland (中国大陆): mi.com
- Global (国际版): xiaomi-mi.com
- Singapore: sg.mi.com
- India: in.mi.com
- Russia: ru.mi.com

#### 2. Discover Xiaomi Devices

MediaControl automatically discovers Xiaomi devices on your account:

```
Found Xiaomi Devices:
  - Yeelight Color Bulb (Living Room)
  - Xiaomi Smart Plug (TV Power)
  - Xiaomi Door Sensor (Front Door)
  - Xiaomi Motion Sensor (Hallway)
  - Xiaomi IR Remote (Living Room)
```

#### 3. Add MediaControl to Mi Home App

**In Mi Home App:**
1. Tap **+** → **Add Device**
2. Select **Video & Monitoring** → **Video Doorbell** (or other type)
3. Select **MediaControl Gateway**
4. Follow on-screen instructions
5. Enter pairing code (shown in MediaControl web interface)

### Mi Home Voice Control (Xiao AI)

Control MediaControl devices with **Xiao AI** (小爱同学):

```
"小爱同学，打开会议室电视"
(Xiǎo Ài Tóngxué, dǎkāi huìyìshì diànshì)
"Xiao AI, turn on Conference Room TV"

"小爱同学，切换到HDMI 2"
(Xiǎo Ài Tóngxué, qiēhuàn dào HDMI 2)
"Xiao AI, switch to HDMI 2"

"小爱同学，打开前门锁"
(Xiǎo Ài Tóngxué, dǎkāi qiánmén suǒ)
"Xiao AI, unlock front door"
```

### Mi Home Automation

Create Mi Home automations (智能场景) with MediaControl:

**回家模式 (Arrive Home):**
```
触发条件: 手机连接家庭Wi-Fi
When: Phone connects to home WiFi

执行动作:
Actions:
  - 打开客厅电视 (Turn on Living Room TV)
  - 打开灯光 (Turn on lights - Yeelight)
  - 解锁前门 (Unlock front door)
  - 打开空调 (Turn on AC - Xiaomi)
```

**离家模式 (Leave Home):**
```
触发条件: 手机断开家庭Wi-Fi
When: Phone disconnects from home WiFi

执行动作:
Actions:
  - 关闭所有电视 (Turn off all TVs)
  - 关闭灯光 (Turn off lights)
  - 锁门 (Lock door)
  - 启动扫地机器人 (Start Roborock vacuum)
```

### Configuration

```yaml
xiaomi_mihome:
  enabled: true
  
  # Xiaomi account
  account:
    username: "your_xiaomi_account@example.com"
    password: "your_password"
    region: "global"  # "cn", "global", "sg", "in", "ru"
    
  # Xiaomi Cloud API
  cloud_api:
    enabled: true
    server: "https://api.io.mi.com"  # or "https://api.sg.mi.com" for Singapore
    
  # Local Xiaomi Gateway Protocol
  local_gateway:
    enabled: true
    # Auto-discover gateways on local network
    discover: true
    
    # Manual gateway configuration
    gateways:
      - gateway_id: "34ce00123456"
        ip_address: "192.168.1.50"
        token: "your_gateway_token"
  
  # Control Xiaomi devices from MediaControl
  control_xiaomi_devices:
    enabled: true
    
    devices:
      # Yeelight bulb
      - device_id: "yeelight_living_room"
        name: "Living Room Light"
        type: "light"
        did: "123456789"  # Xiaomi device ID
        
      # Xiaomi IR Remote
      - device_id: "ir_remote_living_room"
        name: "Living Room IR Remote"
        type: "ir_remote"
        did: "987654321"
        
        # Use Xiaomi IR remote to control non-smart devices
        commands:
          tv_power: "01234567890abcdef"
          tv_input: "fedcba0987654321"
  
  # Expose MediaControl devices to Mi Home
  expose_to_mihome:
    displays:
      - display_id: "display_1"
        name: "会议室电视"  # Conference Room TV
        room: "会议室"  # Conference Room
        type: "tv"
        
    locks:
      - lock_id: "front_door_lock"
        name: "前门锁"  # Front Door Lock
        room: "入口"  # Entrance
        type: "smart_lock"
        
    doorbells:
      - doorbell_id: "front_door"
        name: "前门门铃"  # Front Door Doorbell
        room: "入口"  # Entrance
        type: "doorbell_camera"
```

### Yeelight Integration

**Yeelight** is Xiaomi's smart lighting brand. MediaControl integrates directly:

```python
# Control Yeelight from MediaControl
yeelight_bulb = xiaomi.get_device("yeelight_living_room")
yeelight_bulb.turn_on()
yeelight_bulb.set_brightness(80)  # 0-100
yeelight_bulb.set_color_temp(4000)  # 1700-6500K
yeelight_bulb.set_rgb(255, 0, 0)  # Red
```

**Use Cases:**
- Meeting started → Dim Yeelight bulbs to 30%
- Presentation mode → Set Yeelight to cool white (6500K)
- Video call → Set Yeelight behind camera for face lighting

---

## Amazon Alexa Integration

### Overview

**Amazon Alexa** is Amazon's voice assistant and smart home platform.

**MediaControl Gateway** integrates with Alexa via:
1. **Alexa Smart Home Skill API** (device control)
2. **Alexa Video Skill API** (for video devices like doorbells)

### Supported Alexa Device Types

| MediaControl Device | Alexa Device Type | Capabilities |
|-------------------|-------------------|--------------|
| Display | TV | PowerController, InputController, RemoteControl |
| Source Device | MediaPlayer | PlaybackController, SeekController |
| Smart Lock | SmartLock | LockController |
| Video Doorbell | Doorbell | DoorbellEventSource, CameraStreamController |
| Audio Zone | Speaker | Speaker, StepSpeaker |
| Room | Scene | SceneController |

### Setup Instructions

#### 1. Enable MediaControl Alexa Skill

**In Alexa App:**
1. Open **Alexa** app
2. Tap **More** → **Skills & Games**
3. Search for "MediaControl"
4. Tap **MediaControl Smart Home** skill
5. Tap **Enable to Use**
6. Sign in with MediaControl account
7. Tap **Authorize**

#### 2. Discover Devices

```
"Alexa, discover devices"
```

Alexa will find all MediaControl devices:
```
Found 8 devices:
  - Conference TV
  - Living Room TV
  - Front Door Lock
  - Front Door Doorbell
  - Conference Room Speakers
  - Apple TV
  - Cable Box
  - Presentation Mode (scene)
```

#### 3. Assign to Groups

In Alexa app:
1. Tap **Devices** → **+** → **Add Group**
2. Name the group (e.g., "Conference Room")
3. Select devices to include
4. Tap **Save**

### Alexa Voice Commands

```
"Alexa, turn on Conference TV"
"Alexa, turn off all TVs"
"Alexa, switch Conference TV to HDMI 2"
"Alexa, switch Conference TV to Apple TV"
"Alexa, turn up the volume on Conference TV"
"Alexa, mute Conference TV"
"Alexa, unlock Front Door"
"Alexa, show Front Door camera"
"Alexa, play on Conference Room speakers"
```

### Alexa Routines

Create Alexa routines that control MediaControl devices:

**"Start My Day" Routine:**
```
Trigger: "Alexa, start my day"
Time: 7:00 AM
Actions:
  - Turn on Kitchen TV
  - Switch to Good Morning America
  - Turn on coffee maker
  - Open curtains
  - Read weather forecast
```

**"Movie Time" Routine:**
```
Trigger: "Alexa, movie time"
Actions:
  - Turn on Living Room TV
  - Switch to Fire TV
  - Dim lights to 5%
  - Close curtains
  - Set temperature to 70°F
```

**"Security Mode" Routine:**
```
Trigger: "Alexa, security mode"
Actions:
  - Lock all doors (MediaControl)
  - Turn on Front Door camera (recording)
  - Turn off all TVs
  - Turn on outdoor lights
  - Enable Alexa Guard
```

### Configuration

```yaml
amazon_alexa:
  enabled: true
  
  # Alexa Smart Home Skill
  smart_home_skill:
    enabled: true
    
    # OAuth 2.0 credentials
    oauth:
      client_id: "your_alexa_client_id"
      client_secret: "your_alexa_client_secret"
      authorization_url: "https://www.amazon.com/ap/oa"
      token_url: "https://api.amazon.com/auth/o2/token"
      
    # Lambda endpoint
    lambda:
      function_arn: "arn:aws:lambda:us-east-1:123456789012:function:MediaControlSkill"
      region: "us-east-1"
  
  # Alexa Video Skill (for doorbells)
  video_skill:
    enabled: true
    
  # Devices to expose to Alexa
  expose_devices:
    displays:
      - display_id: "display_1"
        name: "Conference TV"
        type: "TV"
        
        capabilities:
          - "Alexa.PowerController"
          - "Alexa.InputController"
          - "Alexa.Speaker"
          - "Alexa.StepSpeaker"
          - "Alexa.PlaybackController"
          
        # Input sources
        inputs:
          - name: "HDMI 1"
            friendly_name: "Laptop"
          - name: "HDMI 2"
            friendly_name: "Apple TV"
          - name: "HDMI 3"
            friendly_name: "Cable Box"
    
    locks:
      - lock_id: "front_door_lock"
        name: "Front Door Lock"
        type: "SMARTLOCK"
        capabilities:
          - "Alexa.LockController"
    
    doorbells:
      - doorbell_id: "front_door"
        name: "Front Door Doorbell"
        type: "DOORBELL"
        capabilities:
          - "Alexa.DoorbellEventSource"
          - "Alexa.CameraStreamController"
        
        # Camera stream
        camera:
          protocol: "RTSP"
          uri: "rtsp://192.168.1.100/doorbell/front"
          resolution: "1920x1080"
          
    audio_zones:
      - zone_id: "conference_audio"
        name: "Conference Room Speakers"
        type: "SPEAKER"
        capabilities:
          - "Alexa.Speaker"
          - "Alexa.StepSpeaker"
  
  # Proactive state updates
  proactive_updates:
    enabled: true
    # Send state changes to Alexa in real-time
    # (e.g., door unlocked → Alexa notification)
```

### Alexa Echo Show Integration

View MediaControl camera streams on **Echo Show**:

```
"Alexa, show Front Door camera"
"Alexa, show Conference Room camera on Kitchen display"
```

---

## Samsung SmartThings Integration

### Overview

**Samsung SmartThings** is Samsung's smart home platform.

**MediaControl** integrates with SmartThings via:
1. **SmartThings Device SDK** (local execution)
2. **SmartThings Cloud API** (cloud control)

### Supported Device Types

| MediaControl Device | SmartThings Capability |
|-------------------|----------------------|
| Display | Switch, MediaPlayback |
| Smart Lock | Lock |
| Video Doorbell | VideoCamera, Button |
| Audio Zone | AudioVolume, AudioMute |

### Setup Instructions

#### 1. Add MediaControl to SmartThings

**In SmartThings App:**
1. Tap **+** → **Add Device**
2. Select **My Testing Devices** (for beta)
3. Search for "MediaControl"
4. Tap **MediaControl Gateway**
5. Sign in with MediaControl account
6. Authorize access
7. Assign rooms

#### 2. Configure Devices

Assign MediaControl devices to SmartThings rooms:
- Living Room
- Bedroom
- Conference Room
- etc.

### SmartThings Automations

Create SmartThings automations with MediaControl:

**"Good Night" Automation:**
```
If: 10:00 PM every day
Then:
  - Lock Front Door (MediaControl)
  - Turn off all TVs (MediaControl)
  - Turn off lights (SmartThings)
  - Lower shades (SmartThings)
```

### Configuration

```yaml
samsung_smartthings:
  enabled: true
  
  # SmartThings API
  api:
    personal_access_token: "your_smartthings_pat"
    endpoint_url: "https://api.smartthings.com/v1"
    
  # SmartThings Device SDK
  device_sdk:
    enabled: true
    port: 39500
    
  # Devices to expose to SmartThings
  expose_devices:
    displays:
      - display_id: "display_1"
        name: "Conference TV"
        room: "Conference Room"
        capabilities:
          - "switch"
          - "mediaPlayback"
          
    locks:
      - lock_id: "front_door_lock"
        name: "Front Door Lock"
        room: "Entrance"
        capabilities:
          - "lock"
```

---

## Multi-Platform Comparison

| Feature | Apple Home | Google Home | Xiaomi | Alexa | SmartThings |
|---------|-----------|-------------|--------|-------|-------------|
| **Voice Assistant** | Siri | Google Assistant | Xiao AI | Alexa | Bixby |
| **Local Control** | ✅ HAP | ✅ Local Home SDK | ✅ Local Gateway | ❌ Cloud only | ✅ Device SDK |
| **Setup Difficulty** | Easy (QR code) | Easy (OAuth) | Medium | Easy | Easy |
| **Privacy** | ✅ Excellent | ⚠️ Good | ⚠️ China data | ⚠️ Amazon data | ⚠️ Samsung data |
| **Automation** | ✅ Excellent | ✅ Excellent | ✅ Good | ✅ Excellent | ✅ Good |
| **Ecosystem Size** | Large | Largest | Large (Asia) | Largest | Large |
| **Best For** | Apple users | Android users | Xiaomi users | Amazon users | Samsung users |

---

## Configuration (All Platforms)

```yaml
consumer_platforms:
  # Apple HomeKit
  apple_homekit:
    enabled: true
    setup_code: "123-45-678"
    # See detailed config above
    
  # Google Home
  google_home:
    enabled: true
    local_home: true
    # See detailed config above
    
  # Xiaomi Mi Home
  xiaomi_mihome:
    enabled: true
    region: "global"
    # See detailed config above
    
  # Amazon Alexa
  amazon_alexa:
    enabled: true
    smart_home_skill: true
    # See detailed config above
    
  # Samsung SmartThings
  samsung_smartthings:
    enabled: true
    # See detailed config above
```

---

## API Reference

### Apple HomeKit API

```http
# Get HomeKit pairing code
GET /api/consumer-platforms/apple-home/pairing-code

Response:
{
  "setup_code": "123-45-678",
  "qr_code_url": "/api/consumer-platforms/apple-home/qr-code.png"
}
```

### Google Home API

```http
# OAuth callback
POST /api/consumer-platforms/google-home/oauth/callback

# Fulfill intent
POST /api/consumer-platforms/google-home/fulfill
{
  "intent": "action.devices.EXECUTE",
  "payload": {
    "commands": [{
      "devices": [{"id": "display_1"}],
      "execution": [{
        "command": "action.devices.commands.OnOff",
        "params": {"on": true}
      }]
    }]
  }
}
```

### Xiaomi Mi Home API

```http
# Get Xiaomi devices
GET /api/consumer-platforms/xiaomi/devices

# Control Yeelight
POST /api/consumer-platforms/xiaomi/control
{
  "device_id": "yeelight_living_room",
  "command": "set_brightness",
  "params": {"brightness": 80}
}
```

### Amazon Alexa API

```http
# Alexa Smart Home Skill handler
POST /api/consumer-platforms/alexa/skill
{
  "directive": {
    "header": {
      "namespace": "Alexa.PowerController",
      "name": "TurnOn"
    },
    "endpoint": {
      "endpointId": "display_1"
    }
  }
}
```

### Samsung SmartThings API

```http
# SmartThings command
POST /api/consumer-platforms/smartthings/command
{
  "device_id": "display_1",
  "capability": "switch",
  "command": "on"
}
```

---

## Best Practices

### Apple HomeKit
✅ Use meaningful device names (avoid "Device 1", "TV 2")  
✅ Organize by rooms in Home app  
✅ Create scenes for common tasks (Movie Time, Good Night)  
✅ Use HomeKit Secure Video for doorbells (requires iCloud+)  
✅ Enable Thread if gateway supports it (lower latency)

### Google Home
✅ Assign devices to rooms for "turn off bedroom lights" commands  
✅ Create routines for multi-device actions  
✅ Use Local Home SDK for faster response (no cloud latency)  
✅ Link to Google Calendar for time-based automations  
✅ Use Nest Hub for camera viewing

### Xiaomi Mi Home
✅ Use China region if in China (faster, more features)  
✅ Use Global region elsewhere  
✅ Enable local gateway protocol for offline control  
✅ Group Xiaomi + MediaControl devices in scenes  
✅ Use Xiaomi IR remote to control legacy devices

### Amazon Alexa
✅ Create groups for room-based voice control  
✅ Use descriptive names ("Conference Room TV" not "TV 1")  
✅ Set up routines for multi-step actions  
✅ Use Alexa Guard for security monitoring  
✅ Enable proactive state updates for notifications

### Samsung SmartThings
✅ Use local execution when possible  
✅ Create SmartThings scenes with MediaControl devices  
✅ Link to Samsung TVs for integrated control  
✅ Use SmartThings hub for Zigbee/Z-Wave devices

---

**For consumer platform integration support:**  
**Email:** consumer-platforms@mediacontrol.com  
**Website:** https://mediacontrol.com/consumer-platforms
