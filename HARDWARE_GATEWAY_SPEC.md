# MediaControl Gateway Device - Hardware Specification

**All-in-One Room Control Gateway for Professional AV Integration**

---

## Executive Summary

The **MediaControl Gateway** is a professional-grade, single-device solution that consolidates:
- HDMI switching & encoding
- **KVM switching (Keyboard/Video/Mouse)**
- **USB-C/USB-A accessory switching**
- Legacy device control (IR/RF/RS232/RS485)
- **Wireless keyboard/mouse support**
- Local web server for KNX integration
- Cloud synchronization & remote access
- Audio/video distribution
- **Microsoft Teams Room & thin client PC integration**

**One device per room** replaces: Raspberry Pi + Broadlink + HDMI encoder + serial controller + network bridge + KVM switch + USB hub.

---

## Hardware Architecture

### Core Components

#### 1. Main Processor
**Recommendation:** **Rockchip RK3588** or **NXP i.MX8**
- **CPU:** Quad-core ARM Cortex-A76 + Quad-core Cortex-A55 (8 cores)
- **GPU:** Mali-G610 MP4 (for video encoding/decoding)
- **RAM:** 4GB LPDDR4
- **Storage:** 32GB eMMC + microSD slot
- **Cost:** ~$40-60 per unit (volume)

**Why this processor?**
- Hardware video encoding (H.264/H.265)
- Multiple HDMI inputs support
- Enough power for web server + streaming
- Linux-based (easy development)
- Cost-effective at scale

#### 2. HDMI Input/Output Module

**HDMI Inputs:** 2-6 ports (configurable models)
- **Chipset:** Toshiba TC358870 or Silicon Image SiI9678
- **Features:**
  - 4K@60Hz support
  - HDCP 2.2 compliance
  - Hardware H.264/H.265 encoding
  - Simultaneous encoding of all inputs
  - Auto-switching support
- **Cost:** ~$15-20 per input port

**HDMI Outputs:** 1-2 ports
- **Chipset:** Analog Devices ADV7513 or similar
- **Features:**
  - 4K@60Hz output
  - HDCP pass-through
  - CEC control
  - Audio extraction
- **Cost:** ~$8-12 per output port

#### 3. Audio Processing

**Audio Codec:** Cirrus Logic CS42448 or TI PCM5242
- **Inputs:** HDMI audio extraction (all inputs)
- **Outputs:**
  - Analog stereo (RCA/3.5mm)
  - Digital optical (TOSLINK)
  - Analog 5.1 (optional, higher-end model)
- **Features:**
  - Audio mixing
  - Volume control
  - Source selection
  - Audio-only mode (video off)
- **Cost:** ~$5-8 per unit

#### 4. Legacy Device Control

**IR Emitters:** 2-4 ports
- **Chipset:** Custom IR LED driver circuit
- **Features:**
  - 38kHz carrier frequency
  - 360° omnidirectional option
  - Dual-zone IR (configurable)
  - Learning capability
- **Cost:** ~$2-3 per port

**RF Transceiver:** 433MHz/315MHz
- **Chipset:** CC1101 or RFM69HCW
- **Features:**
  - 433MHz/315MHz switchable
  - Bidirectional (send/receive)
  - Compatible with Broadlink protocols
- **Cost:** ~$3-5 per unit

**RS232/RS485 Ports:** 1-2 ports
- **Chipset:** MAX3232 (RS232) + MAX485 (RS485)
- **Features:**
  - Auto-switching RS232/RS485
  - Isolated serial communication
  - DB9 connector (professional)
- **Cost:** ~$4-6 per port

#### 5. Network Connectivity

**Ethernet:** Gigabit (1000Mbps)
- **Chipset:** Realtek RTL8111 or integrated
- **Features:** PoE support (optional, higher-end)
- **Cost:** ~$3-5

**Wi-Fi:** Dual-band (2.4GHz + 5GHz)
- **Chipset:** Realtek RTL8822CE or similar
- **Features:** 
  - Wi-Fi 6 (802.11ax)
  - External antenna ports
  - AP mode for isolated control
- **Cost:** ~$5-8

**Bluetooth:** BLE 5.0
- **Use cases:** Audio streaming, proximity detection, **wireless keyboard/mouse**
- **Cost:** Integrated with Wi-Fi module

#### 7. KVM Switching Module

**USB Host Controller with Switching**
- **Chipset:** Cypress CY7C65632 or Microchip USB5537
- **Features:**
  - 4-port USB 3.0 hub per source
  - USB switching between sources (keyboard/mouse routing)
  - Wireless keyboard/mouse receiver (Bluetooth 5.0)
  - USB device emulation for seamless switching
  - Hotkey switching support (Scroll Lock 2x, etc.)
- **Cost:** ~$8-12 per unit

**USB-C/USB-A Accessory Ports (Switchable)**
- **2× USB-C ports** (USB 3.2, 10Gbps, 15W power)
  - Switchable between connected sources
  - Use cases: webcams, USB drives, charging
- **2× USB-A 3.0 ports** (5Gbps)
  - Switchable between sources
  - Use cases: peripherals, storage, dongles
- **Switching IC:** Analogix ANX7418 or similar
- **Cost:** ~$15-20 for all USB switching

**Wireless Keyboard/Mouse Support**
- **Bluetooth 5.0 receiver** (integrated with Wi-Fi module)
- **2.4GHz wireless dongle support** (USB)
- **Auto-pairing with gateway**
- **Multi-device support** (switch keyboard/mouse between sources)
- **Cost:** Included in BT module

#### 8. Collaboration Features

**Microsoft Teams Room Integration**
- **Use case:** Gateway acts as peripheral hub for Android Teams Room devices
- **Connection:** HDMI input + USB-C for control
- **Features:**
  - Route Teams Room video to displays
  - Share USB peripherals (camera, mic, speaker) with Teams device
  - Touch screen support (via USB HID)

**Thin Client PC Support**
- **Use case:** Gateway provides KVM access to thin client PCs (Windows 10 IoT, ThinOS, etc.)
- **Connection:** HDMI + USB
- **Features:**
  - Switch between thin client and other sources
  - Share keyboard/mouse with thin client
  - USB peripheral access

**Embedded Compute Module (Optional)**
- **Option:** Built-in Android or Linux compute module
- **Chipset:** Same RK3588 can run Android/Linux guest OS
- **Use cases:**
  - Native Teams/Zoom client (no external device)
  - Wireless presentation (Miracast, AirPlay)
  - Digital signage
- **Cost:** +$50 for Android license + software

#### 9. Power Supply

**Input:** 12V DC, 6A (72W max) - *Increased for USB-C power delivery*
- **Distribution:** Multiple voltage rails (5V, 3.3V, 12V)
- **Features:**
  - Over-current protection
  - Soft-start circuitry
  - Optional PoE++ (802.3bt, 60W)
  - USB-C PD 3.0 support (15W per port)
- **Cost:** ~$12-18

#### 10. Enclosure & Physical

**Dimensions:** Rack-mountable 1U or compact desktop unit
- **Size:** 220mm × 150mm × 45mm (approximately)
- **Material:** Aluminum enclosure (heat dissipation)
- **Mounting:** 
  - Rack ears (optional)
  - VESA mount (75mm/100mm)
  - DIN rail mount (optional)
- **Cooling:** Passive (heatsink) or active (low-noise fan)
- **Cost:** ~$15-25

---

## Device Models

### Model Lineup

| Model | HDMI In | HDMI Out | KVM | USB-C/A | Audio Out | IR | RF | RS232/485 | Price (Est.) |
|-------|---------|----------|-----|---------|-----------|----|----|-----------|--------------|
| **MCG-200** | 2 | 1 | ❌ | - | Stereo | 2 | Yes | 1 | $299 |
| **MCG-400** | 4 | 2 | ❌ | - | Stereo | 4 | Yes | 2 | $449 |
| **MCG-400K** | 4 | 2 | ✅ | 2C + 2A | Stereo | 4 | Yes | 2 | **$599** |
| **MCG-600** | 6 | 2 | ❌ | - | 5.1 | 4 | Yes | 2 | $649 |
| **MCG-600K** | 6 | 2 | ✅ | 2C + 2A | 5.1 | 4 | Yes | 2 | **$799** |
| **MCG-Pro** | 6 | 2 | ✅ | 4C + 4A | 5.1 | 4 | Yes | 2 + PoE++ | **$999** |

**K = KVM Edition** (adds USB switching, wireless keyboard/mouse, collaboration features)

---

## Software Architecture

### On-Device Software Stack

```
┌─────────────────────────────────────────────┐
│         Web Frontend (React/Vue)            │
│  • KNX Integration UI                       │
│  • Room Control Interface                   │
│  • Configuration Dashboard                  │
│  • KVM Switching UI (source selection)     │
├─────────────────────────────────────────────┤
│         Local API Server (Python/Go)        │
│  • REST API endpoints                       │
│  • WebSocket for real-time control          │
│  • Token authentication                     │
├─────────────────────────────────────────────┤
│         Control Layer (Python)              │
│  • HDMI switching logic                     │
│  • KVM switching (keyboard/mouse routing)   │
│  • USB accessory switching                  │
│  • IR/RF command dispatcher                 │
│  • RS232/485 communication                  │
│  • Audio routing                            │
├─────────────────────────────────────────────┤
│         Hardware Abstraction Layer          │
│  • HDMI encoder drivers                     │
│  • USB host controller drivers              │
│  • HID device emulation (keyboard/mouse)    │
│  • GPIO control (IR/RF)                     │
│  • Serial port management                   │
│  • Audio codec control                      │
├─────────────────────────────────────────────┤
│    Cloud Sync Service (Python/Go)           │
│  • Configuration download from cloud        │
│  • Status reporting                         │
│  • Remote access proxy                      │
│  • Firmware updates (OTA)                   │
├─────────────────────────────────────────────┤
│         Operating System (Linux)            │
│  • Buildroot or Yocto Project              │
│  • Minimal footprint                        │
│  • Read-only root filesystem                │
│  • Secure boot                              │
│  • USB Gadget mode for HID emulation        │
└─────────────────────────────────────────────┘
```

### Key Software Features

#### 1. Configuration Management
```python
# Device downloads config from cloud on boot
config = {
    "device_id": "mcg_room_101",
    "organization_id": "org_hotel_xyz",
    "room_id": "room_101",
    
    # HDMI routing
    "hdmi_sources": [
        {"port": 1, "name": "Apple TV", "type": "appletv"},
        {"port": 2, "name": "Cable STB", "type": "stb"},
        {"port": 3, "name": "Blu-ray", "type": "bluray"}
    ],
    
    # IR devices controlled through this gateway
    "ir_devices": [
        {
            "id": "ac_001",
            "name": "Daikin AC",
            "type": "air_conditioner",
            "ir_port": 1,
            "commands": {...}  # IR codes
        },
        {
            "id": "tv_001",
            "name": "Samsung TV",
            "type": "tv",
            "ir_port": 2,
            "commands": {...}
        }
    ],
    
    # Streaming settings
    "streaming": {
        "enabled": true,
        "quality": "1080p",
        "bitrate": 4000,
        "audio_only_mode": false
    },
    
    # Access control
    "access_token": "encrypted_token_here",
    "cloud_server": "https://api.mediacontrol.com"
}
```

#### 2. Audio-Only Mode
```python
# When only audio is active, disable video encoding
# Saves power and bandwidth

class AudioOnlyMode:
    def activate(self):
        # Stop video encoding
        self.hdmi_encoder.disable_video()
        
        # Keep audio extraction active
        self.audio_codec.enable()
        
        # Stream audio only (much lower bandwidth)
        self.stream_audio_only()
        
        # Power down video components
        self.power_management.disable_video_subsystem()
```

#### 3. Cloud Synchronization
```python
# Device as cloud bridge
class CloudBridge:
    def sync_configuration(self):
        # Download latest config from cloud
        config = self.cloud_api.get_device_config(self.device_id)
        
        # Store locally
        self.local_storage.save(config)
        
        # Apply configuration
        self.apply_config(config)
    
    def report_status(self):
        # Report device status to cloud
        status = {
            "device_id": self.device_id,
            "online": true,
            "uptime": self.get_uptime(),
            "current_source": self.hdmi_switcher.active_input,
            "streaming": self.stream_status(),
            "cpu_temp": self.get_temperature()
        }
        
        self.cloud_api.post_status(status)
```

#### 4. KVM Switching Control
```python
# KVM switching for keyboard/mouse/video/USB routing

class KVMController:
    def __init__(self):
        self.active_source = 1  # Currently active source (1-4)
        self.usb_hub_controller = USBHubController()
        self.hdmi_switcher = HDMISwitcher()
        
    def switch_to_source(self, source_id: int):
        """Switch keyboard, mouse, video, and USB to specified source"""
        # Switch HDMI video
        self.hdmi_switcher.set_active_input(source_id)
        
        # Route keyboard/mouse to source
        self.usb_hub_controller.route_hid_to_port(source_id)
        
        # Switch USB-C/USB-A accessories to source
        self.usb_hub_controller.route_accessories_to_port(source_id)
        
        # Update active source
        self.active_source = source_id
        
        logger.info(f"KVM switched to source {source_id}")
    
    def get_wireless_devices(self):
        """Get list of paired wireless keyboards/mice"""
        return self.usb_hub_controller.get_bluetooth_devices()
    
    def pair_wireless_device(self, device_type: str):
        """Put gateway into pairing mode for keyboard/mouse"""
        if device_type == "keyboard":
            self.usb_hub_controller.pair_keyboard()
        elif device_type == "mouse":
            self.usb_hub_controller.pair_mouse()

class USBHubController:
    """Control USB switching and routing"""
    
    def route_hid_to_port(self, port: int):
        """Route keyboard/mouse (HID devices) to specified port"""
        # USB switching IC command (via I2C or GPIO)
        self.switch_ic.set_hid_route(port)
    
    def route_accessories_to_port(self, port: int):
        """Route USB-C/USB-A accessories to specified port"""
        # Switch USB-C ports
        self.switch_ic.set_usbc_route(port)
        # Switch USB-A ports
        self.switch_ic.set_usba_route(port)
    
    def get_connected_devices(self):
        """List all USB devices connected to accessory ports"""
        return {
            "usb_c_1": self.get_device_info("/dev/usbc1"),
            "usb_c_2": self.get_device_info("/dev/usbc2"),
            "usb_a_1": self.get_device_info("/dev/usba1"),
            "usb_a_2": self.get_device_info("/dev/usba2")
        }
```

#### 5. Teams Room & Thin Client Integration
```python
# Integration with Microsoft Teams Room and thin client PCs

class CollaborationIntegration:
    def configure_teams_room(self, hdmi_port: int):
        """Configure gateway to work with Teams Room device"""
        config = {
            "device_type": "microsoft_teams_room",
            "hdmi_input": hdmi_port,
            "usb_connection": "usb_c_1",  # Teams Room connects via USB-C
            "features": {
                "camera_sharing": True,    # Share USB webcam with Teams device
                "audio_routing": True,     # Route audio from Teams to room speakers
                "touch_screen": True       # Pass touch input to Teams device
            }
        }
        
        # Configure USB routing for Teams Room
        self.kvm.usb_hub_controller.dedicate_port_to_device(
            port="usb_c_1",
            device=config["device_type"]
        )
        
        return config
    
    def configure_thin_client(self, hdmi_port: int, os_type: str):
        """Configure gateway to provide KVM access to thin client PC"""
        config = {
            "device_type": "thin_client",
            "os": os_type,  # "windows_iot", "thinos", "igel", "wyse", etc.
            "hdmi_input": hdmi_port,
            "kvm_enabled": True,
            "wireless_keyboard_mouse": True
        }
        
        # Enable KVM switching for thin client
        self.kvm.add_source(hdmi_port, config)
        
        return config
    
    def switch_to_teams_room(self):
        """Quick switch to Teams Room for video calls"""
        teams_port = self.get_teams_room_port()
        self.kvm.switch_to_source(teams_port)
        
        # Optionally mute other sources
        self.audio_router.mute_all_except(teams_port)

class EmbeddedComputeModule:
    """Optional: Run Android/Linux directly on gateway"""
    
    def __init__(self):
        self.android_vm = None  # Android container
        self.apps = []
    
    def start_teams_client(self):
        """Launch Microsoft Teams on embedded Android"""
        if not self.android_vm:
            self.android_vm = self.launch_android_container()
        
        # Launch Teams app
        self.android_vm.launch_app("com.microsoft.teams")
        
        # Route video to HDMI output
        self.hdmi_out.set_source("android_vm")
    
    def wireless_presentation_mode(self):
        """Enable Miracast/AirPlay for wireless screen sharing"""
        self.android_vm.enable_miracast()
        self.android_vm.enable_airplay()
```

#### 6. Local + Remote Access
```python
# Device runs local web server for KNX
# Also proxies to cloud for remote access

class AccessManager:
    def handle_request(self, request):
        # Check if local network or remote
        if self.is_local_network(request.ip):
            # Direct local access (low latency)
            return self.handle_local(request)
        else:
            # Remote access through cloud (with auth)
            return self.proxy_through_cloud(request)
```

---

## Bill of Materials (BOM)

### MCG-400 Model (4 HDMI In, 2 Out) - Standard

| Component | Description | Qty | Unit Cost | Total |
|-----------|-------------|-----|-----------|-------|
| **Main Board** | RK3588 SoM + carrier | 1 | $75 | $75 |
| **HDMI Input** | TC358870 encoder | 4 | $18 | $72 |
| **HDMI Output** | ADV7513 driver | 2 | $10 | $20 |
| **Audio Codec** | CS42448 | 1 | $6 | $6 |
| **IR Emitters** | LED + driver circuit | 4 | $2.50 | $10 |
| **RF Module** | CC1101 433MHz | 1 | $4 | $4 |
| **RS232/485** | MAX3232 + MAX485 | 2 | $5 | $10 |
| **Ethernet** | Gigabit PHY | 1 | $4 | $4 |
| **Wi-Fi/BT** | RTL8822CE module | 1 | $7 | $7 |
| **Power Supply** | 12V 5A adapter | 1 | $10 | $10 |
| **Enclosure** | Aluminum case | 1 | $20 | $20 |
| **PCB** | 4-layer custom | 1 | $15 | $15 |
| **Connectors** | HDMI, RCA, DB9, etc. | - | $12 | $12 |
| **Misc** | Capacitors, resistors | - | $8 | $8 |
| **Assembly** | PCB assembly (SMT) | 1 | $25 | $25 |
| | | | **TOTAL:** | **$298** |

**Wholesale Cost:** ~$300 per unit (volume 1000+)  
**Retail Price:** $449  
**Margin:** ~33%

---

### MCG-400K Model (4 HDMI In, 2 Out + KVM) - **NEW**

| Component | Description | Qty | Unit Cost | Total |
|-----------|-------------|-----|-----------|-------|
| **Main Board** | RK3588 SoM + carrier | 1 | $75 | $75 |
| **HDMI Input** | TC358870 encoder | 4 | $18 | $72 |
| **HDMI Output** | ADV7513 driver | 2 | $10 | $20 |
| **Audio Codec** | CS42448 | 1 | $6 | $6 |
| **USB Hub/Switch** | CY7C65632 (4-port USB 3.0 hub with switching) | 1 | $10 | $10 |
| **USB-C Ports** | 2× USB-C 3.2 w/ PD (15W) | 2 | $8 | $16 |
| **USB-A Ports** | 2× USB-A 3.0 | 2 | $2 | $4 |
| **USB Switching IC** | Analogix ANX7418 (USB-C/A switching) | 1 | $12 | $12 |
| **Wireless Receiver** | Bluetooth 5.0 (integrated) | - | - | $0 |
| **IR Emitters** | LED + driver circuit | 4 | $2.50 | $10 |
| **RF Module** | CC1101 433MHz | 1 | $4 | $4 |
| **RS232/485** | MAX3232 + MAX485 | 2 | $5 | $10 |
| **Ethernet** | Gigabit PHY | 1 | $4 | $4 |
| **Wi-Fi/BT** | RTL8822CE module | 1 | $7 | $7 |
| **Power Supply** | 12V 6A adapter (72W for USB-C PD) | 1 | $15 | $15 |
| **Enclosure** | Aluminum case (larger) | 1 | $25 | $25 |
| **PCB** | 6-layer custom (more complex routing) | 1 | $22 | $22 |
| **Connectors** | HDMI, USB-C, USB-A, RCA, DB9, etc. | - | $18 | $18 |
| **Misc** | Capacitors, resistors | - | $10 | $10 |
| **Assembly** | PCB assembly (SMT) | 1 | $35 | $35 |
| | | | **TOTAL:** | **$375** |

**Wholesale Cost:** ~$375 per unit (volume 1000+)  
**Retail Price:** $599  
**Margin:** ~37%

---

## Business Model

### Revenue Streams

#### 1. Hardware Sales

| Model | Wholesale | Retail | Margin | Target Market |
|-------|-----------|--------|--------|---------------|
| MCG-200 | $180 | $299 | 40% | Home users, small rooms |
| MCG-400 | $300 | $449 | 33% | Hotels, conference rooms |
| **MCG-400K** | **$375** | **$599** | **37%** | **Collaboration spaces, hot desks** |
| MCG-600 | $380 | $599 | 37% | Multi-display rooms |
| **MCG-600K** | **$490** | **$799** | **39%** | **Executive offices, Teams Rooms** |
| **MCG-Pro** | **$580** | **$999** | **42%** | **Enterprise meeting rooms, boardrooms** |

**Projected Hardware Revenue** (including KVM models):
- Year 1: 1,000 units × $400 avg = $400,000
- Year 2: 5,000 units × $450 avg = $2,250,000
- Year 3: 20,000 units × $450 avg = $9,000,000

*KVM models expected to represent 40-50% of sales due to collaboration/workspace demand*

#### 2. Subscription Model

**Per-Device Subscription:**
- **FREE:** Limited features, 1 room, basic support
- **HOME:** $5/device/month - Full features
- **PRO:** $10/device/month - Advanced automation, priority support
- **ENTERPRISE:** $15/device/month - White-label, dedicated support, SLA

**Example Hotel Deployment:**
- 100 rooms × 1 device each = 100 devices
- 100 devices × $10/month = $1,000/month
- Annual recurring revenue: $12,000 per hotel

**Example Corporate Office (KVM Focus):**
- 50 meeting rooms + 200 hot desks = 250 devices (MCG-400K/600K)
- 250 devices × $12/month = $3,000/month
- Annual recurring revenue: $36,000 per office

**Projected Subscription Revenue:**
- Year 1: 600 active devices × $9 avg × 12 months = $64,800
- Year 2: 4,000 active devices × $9 avg × 12 months = $432,000
- Year 3: 15,000 active devices × $10 avg × 12 months = $1,800,000

*Higher ARPU expected due to KVM/collaboration use cases (enterprise pricing)*

#### 3. Total Projected Revenue

| Year | Hardware | Subscription | Total |
|------|----------|--------------|-------|
| Year 1 | $400K | $65K | **$465K** |
| Year 2 | $2,250K | $432K | **$2,682K** |
| Year 3 | $9,000K | $1,800K | **$10,800K** |

**Revenue Growth Drivers:**
- KVM models command 33% higher ASP ($599 vs $449)
- Collaboration/workspace market (Teams Rooms, hot desks) is rapidly growing
- Enterprise customers pay premium subscriptions ($12-15/device vs $8-10)
- Hot desk market: 40M+ desks globally, growing 15% annually

### Competitive Advantages

✅ **vs. DIY Raspberry Pi + Broadlink:**
- Integrated solution (no assembly required)
- Professional appearance
- Better support
- Higher reliability
- Warranty included

✅ **vs. Control4/Crestron:**
- 10x cheaper ($449 vs $4,000+)
- No dealer lock-in
- Open API
- Cloud-based (remote access included)
- Modern web interface

✅ **vs. Generic HDMI Matrix:**
- Adds IR/RF/RS232 control
- Built-in streaming
- Cloud management
- KNX integration
- All-in-one solution

✅ **vs. Generic KVM Switch (Belkin, IOGEAR):**
- KVM + HDMI encoding + control in one device
- Wireless keyboard/mouse support (not just wired)
- Teams Room integration
- Cloud management
- 5x cheaper than enterprise KVM ($599 vs $2,000+)

---

## Development Roadmap

### Phase 1: Prototype (Months 1-3)
- [x] Hardware design (PCB schematic)
- [x] Component selection
- [ ] First prototype PCB fabrication
- [ ] Basic firmware (Linux boot, HDMI test)
- [ ] Initial software stack

**Milestone:** Working prototype with basic HDMI switching

### Phase 2: Alpha (Months 4-6)
- [ ] Full hardware integration
- [ ] IR/RF/RS232 drivers
- [ ] Web server implementation
- [ ] Cloud sync service
- [ ] Alpha testing (5-10 units)

**Milestone:** Fully functional alpha units

### Phase 3: Beta (Months 7-9)
- [ ] Enclosure design finalization
- [ ] Beta units (50-100 devices)
- [ ] Field testing (real deployments)
- [ ] Software refinement
- [ ] Documentation

**Milestone:** Beta program with early customers

### Phase 4: Production (Months 10-12)
- [ ] Manufacturing setup (China/Taiwan)
- [ ] Certifications (FCC, CE, RoHS)
- [ ] Initial production run (1,000 units)
- [ ] Sales & marketing launch
- [ ] Support infrastructure

**Milestone:** Product launch, first customer shipments

---

## Manufacturing

### Contract Manufacturer Options

**Recommended:** Taiwan or China CM
- **Taiwan:** Foxconn, Pegatron, Compal
  - Higher quality, higher cost
  - Good for initial runs
  
- **Shenzhen, China:** Many CMs available
  - Lower cost at scale
  - Fast iteration
  - Good for volume production

**MOQ (Minimum Order Quantity):** 500-1,000 units
**Lead Time:** 8-12 weeks
**Cost Reduction at Scale:**
- 1,000 units: $300/unit
- 5,000 units: $250/unit
- 10,000 units: $220/unit

### Certifications Required

1. **FCC (USA):** Electromagnetic compliance
2. **CE (Europe):** Safety and emissions
3. **RoHS:** Lead-free compliance
4. **HDCP:** License for HDMI encryption
5. **UL (Optional):** Safety certification

**Total Certification Cost:** ~$50,000-75,000
**Timeline:** 3-6 months

---

## Technical Specifications (Final)

### MediaControl Gateway MCG-400

**Video:**
- 4× HDMI 2.0 inputs (4K@60Hz)
- 2× HDMI 2.0 outputs (4K@60Hz)
- Simultaneous encoding of all inputs
- H.264/H.265 compression
- HLS/RTSP streaming output

**Audio:**
- HDMI audio extraction (all inputs)
- Stereo RCA output
- Optical TOSLINK output
- Audio-only streaming mode
- Independent volume control

**Control:**
- 4× IR emitter ports (360° coverage)
- 1× RF 433MHz/315MHz transceiver
- 2× RS232/RS485 ports (auto-switching)
- IR learning capability

**Network:**
- Gigabit Ethernet (1000Mbps)
- Wi-Fi 6 dual-band (2.4GHz + 5GHz)
- Bluetooth 5.0

**Processing:**
- Rockchip RK3588 (8-core ARM)
- 4GB RAM
- 32GB storage
- Linux-based OS

**KVM (MCG-400K only):**
- USB 3.0 switching (keyboard/mouse routing)
- Wireless keyboard/mouse support (Bluetooth 5.0)
- 2× USB-C ports (switchable, 15W PD)
- 2× USB-A 3.0 ports (switchable)
- Hotkey switching (Scroll Lock 2x)
- Microsoft Teams Room integration
- Thin client PC support

**Physical:**
- Dimensions: 220 × 150 × 45mm (standard), 240 × 180 × 50mm (KVM models)
- Weight: 800g (standard), 1000g (KVM)
- Mounting: Desktop, rack, VESA, DIN rail, under-desk
- Power: 12V DC, 5A (60W, standard), 12V DC, 6A (72W, KVM)
- Operating temp: 0-40°C

**Software:**
- Built-in web server for KNX
- Cloud synchronization
- Local + remote access
- OTA firmware updates
- REST API + WebSocket
- KVM control API (source switching, USB routing)
- Teams Room API integration

---

## Competitive Analysis

| Feature | MediaControl Gateway | MediaControl Gateway KVM | Control4 | Crestron | KVM Switch (IOGEAR) |
|---------|---------------------|--------------------------|----------|----------|---------------------|
| **Price** | $449 | **$599** | $4,000+ | $5,000+ | $2,000+ |
| **HDMI Encoding** | ✅ Built-in | ✅ Built-in | ❌ Separate | ❌ Separate | ❌ Video only |
| **KVM Switching** | ❌ | ✅ USB 3.0 + wireless | ❌ | ❌ | ✅ Wired only |
| **USB-C/A Switching** | ❌ | ✅ 2C + 2A | ❌ | ❌ | ❌ Limited |
| **Wireless KB/Mouse** | ❌ | ✅ Bluetooth 5.0 | ❌ | ❌ | ❌ No |
| **Teams Room Support** | ❌ | ✅ Native | ❌ | ❌ | ❌ No |
| **IR/RF/RS232** | ✅ All included | ✅ All included | ✅ Extra modules | ✅ Extra modules | ❌ No |
| **Cloud Management** | ✅ Included | ✅ Included | ❌ Dealer only | ❌ Dealer only | ❌ No |
| **KNX Integration** | ✅ Direct | ✅ Direct | ✅ Via driver | ✅ Via driver | ❌ No |
| **Audio-Only Mode** | ✅ Native | ✅ Native | ❌ | ❌ | ❌ No |
| **Dealer Required** | ❌ No | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Warranty** | 2 years | 2 years | 1-3 years | 1-3 years | 1 year |
| **Support** | Email/Chat | Email/Chat | Dealer | Dealer | Email only |

**Market Position:** Professional features at prosumer pricing

**Key Differentiator:** Only device combining HDMI matrix + KVM + IR/RF/RS232 + streaming + Teams integration in single unit

---

## Go-to-Market Strategy

### Target Markets

1. **Corporate Workspace (Primary)** - *KVM models*
   - Meeting rooms & conference centers
   - Hot desks & flexible workspaces
   - Executive offices
   - Microsoft Teams Rooms deployments
   - Coworking spaces (WeWork, Regus, etc.)
   - Hybrid work setups

2. **Hospitality (Primary)**
   - Hotels (100-500 rooms)
   - Resorts
   - Vacation rentals
   - Airbnb hosts (luxury)
   - Business centers

3. **Education (Secondary)** - *KVM models*
   - Classrooms with Teams/Zoom
   - Lecture halls
   - Computer labs (thin client deployments)
   - Library study rooms

4. **Residential (Tertiary)**
   - Luxury homes
   - Smart home enthusiasts
   - Home theater integrators
   - Home offices (remote work)

### Sales Channels

1. **Direct Sales** (mediacontrol.com)
   - Online store
   - 30-day return policy
   - Free shipping over $1,000

2. **Integrator Program**
   - 25-35% dealer discount
   - Training & certification
   - Lead generation support
   - Co-marketing funds

3. **Distributors**
   - ADI, SnapAV, etc.
   - Volume discounts
   - Demo units
   - Technical support

---

## Investment Required

### Initial Capital

| Item | Amount |
|------|--------|
| **Product Development** | |
| Engineering team (6 months) | $150,000 |
| Prototyping (10 units) | $15,000 |
| Tooling & molds | $30,000 |
| **Manufacturing** | |
| Initial production (1,000 units) | $300,000 |
| Certifications (FCC, CE, etc.) | $60,000 |
| **Operations** | |
| Inventory & logistics | $50,000 |
| Cloud infrastructure | $20,000 |
| Marketing & sales | $75,000 |
| **Total** | **$700,000** |

### Funding Options

1. **Bootstrap:** Start small, reinvest profits
2. **Angel/Seed:** $500K-1M for faster growth
3. **Kickstarter:** Pre-sales to fund production
4. **Strategic Partner:** AV distributor or manufacturer

---

## Summary

**YES, it's absolutely feasible!**

The MediaControl Gateway consolidates:
✅ HDMI switching & encoding (2-6 inputs)
✅ **KVM switching (keyboard/video/mouse routing)**
✅ **USB-C/USB-A accessory switching**
✅ **Wireless keyboard/mouse support (Bluetooth)**
✅ Legacy device control (IR, RF, RS232, RS485)
✅ Audio distribution with audio-only mode
✅ **Microsoft Teams Room integration**
✅ **Thin client PC support**
✅ Local web server for KNX
✅ Cloud bridge for remote access
✅ Configuration storage & sync

**Business Model:**
- Hardware: $299-999 per device (KVM models $599-999)
- Subscription: $5-15/device/month
- Target: **Corporate workspaces, meeting rooms, hot desks**, hotels, luxury homes

**Competitive Advantage:**
- 10x cheaper than Control4/Crestron
- 3x cheaper than enterprise KVM switches
- **Only device with HDMI matrix + KVM + control in one unit**
- **Wireless keyboard/mouse (no competitor has this)**
- **Native Teams Room integration**
- All-in-one (replaces: HDMI matrix + KVM switch + Broadlink + encoder + USB hub)
- Professional grade
- Cloud-managed
- Open ecosystem

**Time to Market:** 12-18 months
**Initial Investment:** $700K
**Revenue Potential:** $10.8M by year 3 (higher due to KVM/workspace market)

**Target Markets Expanded:**
1. **Corporate workspace & collaboration** (primary - high growth, high margin)
2. Hospitality (primary - established market)
3. Education (secondary - Teams/Zoom adoption)
4. Residential (tertiary - remote work trend)

**KVM Features Enable NEW Markets:**
- Hot desks & flexible workspaces (40M+ desks globally)
- Microsoft Teams Rooms (fastest growing UC endpoint)
- Hybrid work setups (100M+ remote workers)
- Thin client deployments (VDI/DaaS)

**This is a GAME-CHANGING product!** 🚀

**KVM models will likely outsell standard models 2:1 in commercial deployments.**
