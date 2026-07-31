# MediaControl Gateway Device - Hardware Specification

**All-in-One Room Control Gateway for Professional AV Integration**

---

## Executive Summary

The **MediaControl Gateway** is a professional-grade, single-device solution that consolidates:
- HDMI switching & encoding
- Legacy device control (IR/RF/RS232/RS485)
- Local web server for KNX integration
- Cloud synchronization & remote access
- Audio/video distribution

**One device per room** replaces: Raspberry Pi + Broadlink + HDMI encoder + serial controller + network bridge.

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
- **Use cases:** Audio streaming, proximity detection
- **Cost:** Integrated with Wi-Fi module

#### 6. Power Supply

**Input:** 12V DC, 5A (60W max)
- **Distribution:** Multiple voltage rails (5V, 3.3V, 12V)
- **Features:**
  - Over-current protection
  - Soft-start circuitry
  - Optional PoE (802.3at, 25W)
- **Cost:** ~$8-12

#### 7. Enclosure & Physical

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

| Model | HDMI In | HDMI Out | Audio Out | IR | RF | RS232/485 | Price (Est.) |
|-------|---------|----------|-----------|----|----|-----------|--------------|
| **MCG-200** | 2 | 1 | Stereo | 2 | Yes | 1 | $299 |
| **MCG-400** | 4 | 2 | Stereo | 4 | Yes | 2 | $449 |
| **MCG-600** | 6 | 2 | 5.1 | 4 | Yes | 2 | $599 |
| **MCG-Pro** | 6 | 2 | 5.1 | 4 | Yes | 2 + PoE | $799 |

---

## Software Architecture

### On-Device Software Stack

```
┌─────────────────────────────────────────────┐
│         Web Frontend (React/Vue)            │
│  • KNX Integration UI                       │
│  • Room Control Interface                   │
│  • Configuration Dashboard                  │
├─────────────────────────────────────────────┤
│         Local API Server (Python/Go)        │
│  • REST API endpoints                       │
│  • WebSocket for real-time control          │
│  • Token authentication                     │
├─────────────────────────────────────────────┤
│         Control Layer (Python)              │
│  • HDMI switching logic                     │
│  • IR/RF command dispatcher                 │
│  • RS232/485 communication                  │
│  • Audio routing                            │
├─────────────────────────────────────────────┤
│         Hardware Abstraction Layer          │
│  • HDMI encoder drivers                     │
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

#### 4. Local + Remote Access
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

### MCG-400 Model (4 HDMI In, 2 Out)

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

## Business Model

### Revenue Streams

#### 1. Hardware Sales

| Model | Wholesale | Retail | Margin |
|-------|-----------|--------|--------|
| MCG-200 | $180 | $299 | 40% |
| MCG-400 | $300 | $449 | 33% |
| MCG-600 | $380 | $599 | 37% |
| MCG-Pro | $510 | $799 | 36% |

**Projected Hardware Revenue:**
- Year 1: 1,000 units × $350 avg = $350,000
- Year 2: 5,000 units × $350 avg = $1,750,000
- Year 3: 15,000 units × $350 avg = $5,250,000

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

**Projected Subscription Revenue:**
- Year 1: 500 active devices × $8 avg × 12 months = $48,000
- Year 2: 3,000 active devices × $8 avg × 12 months = $288,000
- Year 3: 10,000 active devices × $8 avg × 12 months = $960,000

#### 3. Total Projected Revenue

| Year | Hardware | Subscription | Total |
|------|----------|--------------|-------|
| Year 1 | $350K | $48K | **$398K** |
| Year 2 | $1,750K | $288K | **$2,038K** |
| Year 3 | $5,250K | $960K | **$6,210K** |

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

**Physical:**
- Dimensions: 220 × 150 × 45mm
- Weight: 800g
- Mounting: Desktop, rack, VESA, DIN rail
- Power: 12V DC, 5A (60W max)
- Operating temp: 0-40°C

**Software:**
- Built-in web server for KNX
- Cloud synchronization
- Local + remote access
- OTA firmware updates
- REST API + WebSocket

---

## Competitive Analysis

| Feature | MediaControl Gateway | Control4 | Crestron | Savant | Raspberry Pi + DIY |
|---------|---------------------|----------|----------|--------|--------------------|
| **Price** | $449 | $4,000+ | $5,000+ | $3,500+ | $200-300 (no HDMI encoding) |
| **HDMI Encoding** | ✅ Built-in | ❌ Separate | ❌ Separate | ❌ Separate | ❌ Extra hardware needed |
| **IR/RF/RS232** | ✅ All included | ✅ Extra modules | ✅ Extra modules | ✅ Extra modules | ✅ Broadlink needed |
| **Cloud Management** | ✅ Included | ❌ Dealer only | ❌ Dealer only | ❌ Dealer only | ❌ Self-hosted |
| **KNX Integration** | ✅ Direct | ✅ Via driver | ✅ Via driver | ✅ Via driver | ❌ Manual |
| **Audio-Only Mode** | ✅ Native | ❌ | ❌ | ❌ | ❌ |
| **Dealer Required** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Warranty** | 2 years | 1-3 years | 1-3 years | 1-3 years | None |
| **Support** | Email/Chat | Dealer | Dealer | Dealer | Community |

**Market Position:** Professional features at prosumer pricing

---

## Go-to-Market Strategy

### Target Markets

1. **Hospitality (Primary)**
   - Hotels (100-500 rooms)
   - Resorts
   - Vacation rentals
   - Airbnb hosts (luxury)

2. **Residential (Secondary)**
   - Luxury homes
   - Smart home enthusiasts
   - Home theater integrators

3. **Commercial (Tertiary)**
   - Conference rooms
   - Corporate offices
   - Retail spaces
   - Restaurants/bars

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
✅ Legacy device control (IR, RF, RS232, RS485)
✅ Audio distribution with audio-only mode
✅ Local web server for KNX
✅ Cloud bridge for remote access
✅ Configuration storage & sync

**Business Model:**
- Hardware: $299-799 per device
- Subscription: $5-15/device/month
- Target: Hotels, luxury homes, commercial

**Competitive Advantage:**
- 10x cheaper than Control4/Crestron
- All-in-one (no Raspberry Pi + Broadlink)
- Professional grade
- Cloud-managed
- Open ecosystem

**Time to Market:** 12-18 months
**Initial Investment:** $700K
**Revenue Potential:** $6M+ by year 3

**This is a WINNING product!** 🎯
