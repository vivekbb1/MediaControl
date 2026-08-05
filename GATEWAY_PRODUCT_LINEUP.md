# MediaControl Gateway Product Lineup

**Complete Hardware Specifications & Pricing Strategy**

---

## Product Philosophy

Every MediaControl Gateway includes:
- ✅ **Gigabit Ethernet** - Primary connection (PoE+ support on Pro/Enterprise)
- ✅ **WiFi 6** - Redundant connection (auto-failover if Ethernet drops)
- ✅ **Static IP Assignment** - Each gateway gets dedicated IP for control
- ✅ **Network Management** - Web interface for configuration
- ✅ **Core AV Control** - All models control displays, sources, audio

**Differentiation:** HDMI ports, control protocols, AI acceleration, KVM features, unified communications

---

## Product Lineup Overview

| Model | Target Market | Price (MSRP) | BOM Cost | Margin |
|-------|---------------|--------------|----------|--------|
| **MCG-Lite** | Home, Small Office (1-2 rooms) | $399 | $149 | 63% |
| **MCG-Standard** | Small Business, Prosumer (2-4 rooms) | $899 | $349 | 61% |
| **MCG-Pro** | Enterprise, Conference Rooms | $1,999 | $698 | 65% |
| **MCG-Enterprise** | Large Enterprise, Control Rooms | $3,999 | $1,298 | 68% |

---

## Smart Home Ecosystem Integration

**ALL MediaControl Gateways** support seamless integration with major smart home ecosystems:

### Supported Platforms

| Platform | Purpose | Integration Method |
|----------|---------|-------------------|
| **Ubiquiti Access** | Enterprise access control, door locks, card readers | HTTP API, Webhooks |
| **Aqara** | Affordable doorbells, locks, sensors | MQTT (via Aqara Hub M2/M3), Zigbee |
| **Nuki** | Premium European smart locks | HTTP API (Bridge), Matter |
| **Home Assistant** | Open-source home automation hub | MQTT, REST API, WebSocket (bidirectional) |
| **Matter** | Universal smart home standard | Local network (works with Apple, Google, Amazon) |
| **Zigbee** | Low-power mesh network | MQTT (via Zigbee2MQTT, ZHA, deCONZ) |

### Bidirectional Control

**MediaControl → Smart Home:**
- Control locks, lights, switches, climate from MediaControl interface
- Trigger smart home scenes based on MediaControl events (e.g., meeting started → Do Not Disturb)
- Manage access codes and permissions

**Smart Home → MediaControl:**
- Doorbell pressed → MediaControl shows video + notification
- Door sensor triggered → MediaControl logs event
- Home Assistant bedtime scene → MediaControl turns off all displays
- Zigbee motion sensor → MediaControl auto-turns on display

### Supported Devices

✅ **Smart Locks:** Ubiquiti UA-G2-Pro, Aqara U100, Nuki Smart Lock Pro, Yale Assure Lock 2, Schlage Encode Plus (Matter)  
✅ **Video Doorbells:** Aqara G4/G220, Ring Battery Doorbell Plus (Matter), Google Nest Doorbell (Matter), UniFi Protect doorbells  
✅ **Door Sensors:** Aqara, Eve Door & Window (Matter), any Zigbee contact sensor  
✅ **Motion Sensors:** Aqara, Philips Hue Motion (Zigbee), any Zigbee motion sensor  
✅ **Lights & Switches:** Philips Hue (Zigbee), IKEA TRÅDFRI (Zigbee), Sonoff (Zigbee), any Matter/Zigbee device  
✅ **Access Control:** Ubiquiti door readers, electric strikes, maglocks, garage door openers  

### Use Cases

**Residential:**
- "Front doorbell pressed → Turn on porch light (Home Assistant) + Show video on MediaControl TVs + Unlock door (Nuki)"
- "Bedtime scene → Turn off all lights (Zigbee) + Turn off all MediaControl displays + Lock doors (Aqara)"
- "Motion detected in hallway → Turn on hallway display + Lights (Philips Hue)"

**Commercial:**
- "Employee badge scanned (Ubiquiti Access) → MediaControl logs entry + Show security notification"
- "Meeting room occupied (Zigbee sensor) → MediaControl auto-turns on display + Adjust thermostat (Home Assistant)"
- "Door forced open → MediaControl emergency paging + Home Assistant alarm"

### Why This Matters

🏆 **Best-in-class integration** - MediaControl works with ALL major smart home ecosystems, not just one  
🏆 **Future-proof** - Matter support ensures compatibility with Apple HomeKit, Google Home, Amazon Alexa  
🏆 **Flexibility** - Use Aqara for affordability, Ubiquiti for enterprise security, Nuki for premium locks  
🏆 **Unified control** - Manage everything from one MediaControl interface, or use Home Assistant as hub  

---

## 1. MCG-Lite (Entry Level)

**Target:** Homes, home offices, small businesses, single meeting room

### Key Features
- ✅ 2 HDMI inputs, 1 HDMI output (4K@60Hz)
- ✅ IR blaster (2 ports) + RF control (Broadlink-compatible)
- ✅ Gigabit Ethernet + WiFi 6
- ✅ USB 2.0 ports (2x) for basic peripherals
- ✅ AI video effects (CPU-based, 720p@30fps)
- ✅ Basic audio (analog + HDMI ARC)
- ✅ SIP phone system (1 extension)
- ✅ Doorbell support (1 video doorbell)
- ✅ Web-based control interface

### Technical Specifications

**Processor:**
- SoC: Rockchip RK3568 or equivalent
  - Quad-core ARM Cortex-A55 @ 2.0 GHz
  - Mali-G52 GPU (basic AI inference)
- RAM: 4 GB LPDDR4
- Storage: 32 GB eMMC

**Video I/O:**
- HDMI Inputs: 2 × HDMI 2.0 (4K@60Hz)
- HDMI Outputs: 1 × HDMI 2.0 (4K@60Hz)
- Max resolution: 3840×2160@60Hz

**Audio:**
- HDMI ARC/eARC
- 3.5mm line out (stereo)
- USB audio (microphone/speaker support)

**Control Interfaces:**
- IR: 2 × IR blaster ports (38 kHz)
- RF: 433 MHz / 315 MHz (via USB dongle)
- RS232: 1 × DB9 (optional via USB adapter)

**Network:**
- Ethernet: 1 × Gigabit Ethernet (10/100/1000 Mbps)
- WiFi: WiFi 6 (802.11ax), dual-band 2.4/5 GHz
- Bluetooth: 5.0 (for badge tracking, remote control)

**USB:**
- USB 2.0: 2 × USB-A ports (peripherals, storage)
- USB-C: 1 × USB-C (power + data)

**Power:**
- Input: 12V DC, 3A (36W)
- Consumption: 15-25W typical

**Physical:**
- Dimensions: 150 × 100 × 30 mm (6" × 4" × 1.2")
- Weight: 300g
- Mounting: Wall mount, under-desk mount

**Operating System:**
- Linux-based (Debian/Ubuntu)
- MediaControl software pre-installed

### What You Get

✅ **Basic AV Control** - 2 sources → 1 display  
✅ **AI Video Effects** - Background blur (720p)  
✅ **Voice Focus** - Basic noise suppression  
✅ **SIP Phone** - 1 room extension  
✅ **Doorbell** - 1 video doorbell support  
✅ **Intercom** - Room-to-room (within network)  
✅ **Web Control** - Browser-based interface  
❌ KVM (no keyboard/mouse switching)  
❌ Native apps (no Android runtime)  
❌ Touch panel servers  
❌ Video wall  

### Use Cases
- Home theater (2 sources: Apple TV + game console → TV)
- Home office (laptop + desktop → monitor)
- Small meeting room (1 room, 1 display, basic calls)
- Residential doorbell + intercom

### Price
- **MSRP:** $399
- **BOM Cost:** $149
- **Margin:** 63%

---

## 2. MCG-Standard (Small Business)

**Target:** Small businesses, prosumer homes, huddle rooms, telehealth

### Key Features
- ✅ 4 HDMI inputs, 2 HDMI outputs (4K@60Hz)
- ✅ IR (4 ports) + RF + RS232 (2 ports)
- ✅ Gigabit Ethernet + WiFi 6
- ✅ USB 3.0 ports (4x) + USB-C
- ✅ Basic KVM (USB switching, no video)
- ✅ AI video effects (GPU-accelerated, 1080p@30fps)
- ✅ Advanced audio (I2S, SPDIF, USB)
- ✅ SIP + Intercom + Paging
- ✅ Doorbell support (2 doorbells)
- ✅ Access control (2 smart locks)
- ✅ Touch panel support (web-based)

### Technical Specifications

**Processor:**
- SoC: Rockchip RK3588 or NVIDIA Jetson Nano equivalent
  - Octa-core (4×A76 + 4×A55) @ 2.4 GHz
  - Mali-G610 GPU or Maxwell GPU (CUDA cores)
  - 1 TOPS NPU (AI acceleration)
- RAM: 8 GB LPDDR4X
- Storage: 64 GB eMMC

**Video I/O:**
- HDMI Inputs: 4 × HDMI 2.0 (4K@60Hz)
- HDMI Outputs: 2 × HDMI 2.0 (4K@60Hz, independent)
- Max resolution: 3840×2160@60Hz per output

**Audio:**
- HDMI ARC/eARC (both outputs)
- I2S (digital audio out)
- SPDIF optical
- 3.5mm line in/out (stereo)
- USB audio (multiple devices)

**Control Interfaces:**
- IR: 4 × IR blaster ports (38 kHz)
- RF: 433 MHz / 315 MHz (built-in)
- RS232: 2 × DB9 or terminal block
- TCP/IP: Network-based control

**Network:**
- Ethernet: 1 × Gigabit Ethernet (10/100/1000 Mbps)
- WiFi: WiFi 6 (802.11ax), dual-band 2.4/5 GHz, 2×2 MIMO
- Bluetooth: 5.2 (badge tracking, peripherals)

**USB:**
- USB 3.0: 4 × USB-A ports (high-speed peripherals)
- USB-C: 1 × USB-C (power + data, DisplayPort Alt Mode)

**KVM:**
- USB switching: Switch 4 USB devices between sources
- No video switching (use HDMI matrix externally if needed)

**Power:**
- Input: 12V DC, 5A (60W) or PoE+ (802.3at)
- Consumption: 30-50W typical

**Physical:**
- Dimensions: 200 × 150 × 35 mm (8" × 6" × 1.4")
- Weight: 600g
- Mounting: Wall mount, rack mount (1U half-width), under-desk

**Operating System:**
- Linux-based (Debian/Ubuntu)
- Android container (for native apps - basic)

### What You Get

✅ **Multi-source AV Control** - 4 sources → 2 displays  
✅ **AI Video Effects** - Background blur/replace (1080p@30fps)  
✅ **Voice Focus** - AI noise suppression (Krisp-level)  
✅ **SIP + Intercom + Paging** - Full unified communications  
✅ **Doorbell** - 2 video/audio doorbells  
✅ **Access Control** - 2 smart locks  
✅ **Basic KVM** - USB switching (no video)  
✅ **Native Apps** - Basic Android apps (YouTube, Chrome)  
✅ **Touch Panel** - Web-based interface  
✅ **Wireless Presentation** - AirPlay, Chromecast (receive)  
❌ Eye contact correction (NPU required)  
❌ Full KVM with video  
❌ Touch panel servers (Crestron/Extron)  
❌ Video wall controller  

### Use Cases
- Small business (2-4 meeting rooms)
- Medical office (telehealth room with doorbell)
- Home prosumer (multiple rooms, whole-home control)
- Huddle room (4 sources: laptop, desktop, Apple TV, Teams → 2 displays)

### Price
- **MSRP:** $899
- **BOM Cost:** $349
- **Margin:** 61%

---

## 3. MCG-Pro (Enterprise Conference Room)

**Target:** Enterprise conference rooms, training rooms, executive offices, hybrid work

### Key Features
- ✅ 6 HDMI inputs, 2 HDMI outputs (4K@60Hz, HDCP 2.3)
- ✅ IR (6 ports) + RF + RS232 (4 ports) + RS485
- ✅ Dual Gigabit Ethernet + WiFi 6
- ✅ USB 3.1 ports (6x) + USB-C (2x)
- ✅ **Full KVM** - Video/keyboard/mouse/USB switching
- ✅ AI video effects (NPU+GPU, 1080p@60fps)
  - Background blur/replace/remove
  - Eye contact correction
  - Auto framing
  - Portrait lighting
- ✅ Professional audio (XLR, I2S, SPDIF, AES/EBU)
- ✅ **Unified Communications (Full Suite)**
  - SIP phone system
  - Intercom
  - Paging
  - Doorbell (unlimited)
  - Access control (unlimited)
  - Seamless call handoff
- ✅ **Touch Panel Servers** - Crestron CH5, Extron SIS, WebSocket
- ✅ **Native Apps Runtime** - Full Android/Linux apps
- ✅ **Wireless Presentation** - AirPlay 2, Chromecast, Miracast

### Technical Specifications

**Processor:**
- SoC: Intel Core Ultra 5 125H or AMD Ryzen AI 7 7840U
  - 14-core (6P + 8E) or 8-core @ 4.5 GHz boost
  - Intel Iris Xe or AMD Radeon 780M (integrated GPU)
  - **NPU:** Intel AI Boost (10 TOPS) or AMD XDNA (16 TOPS)
- RAM: 16 GB DDR5
- Storage: 256 GB NVMe SSD

**Video I/O:**
- HDMI Inputs: 6 × HDMI 2.1 (4K@60Hz, 8K@30Hz)
- HDMI Outputs: 2 × HDMI 2.1 (4K@120Hz, 8K@30Hz)
- DisplayPort: 2 × DisplayPort 1.4 (via USB-C Alt Mode)
- Max resolution: 7680×4320@30Hz or 3840×2160@120Hz

**Audio:**
- HDMI ARC/eARC (both outputs)
- XLR inputs: 2 × XLR (mic inputs, 48V phantom power)
- I2S (8-channel)
- SPDIF optical + coaxial
- AES/EBU (professional digital audio)
- 3.5mm line in/out (stereo)
- USB audio (class-compliant, multiple devices)
- Dante audio (optional, via network)

**Control Interfaces:**
- IR: 6 × IR blaster ports (38 kHz, high-power)
- RF: 433 MHz / 315 MHz (built-in + external antenna)
- RS232: 4 × DB9 or terminal block (up to 115200 baud)
- RS485: 1 × RS485 (Modbus, DMX512)
- TCP/IP: Network-based control (unlimited devices)
- Relay: 4 × dry contact relay outputs (for door strikes, etc.)

**Network:**
- Ethernet: 2 × Gigabit Ethernet (10/100/1000 Mbps, failover/bonding)
- WiFi: WiFi 6E (802.11ax), tri-band 2.4/5/6 GHz, 2×2 MIMO
- Bluetooth: 5.3 (badge tracking, peripherals)
- Optional: 2.5 GbE or 10 GbE upgrade

**USB:**
- USB 3.2 Gen 2: 6 × USB-A ports (10 Gbps)
- USB-C: 2 × USB-C (Thunderbolt 4, 40 Gbps, DisplayPort Alt Mode, 100W PD)

**KVM:**
- Video switching: 6 HDMI inputs → 2 outputs (full matrix switching)
- Keyboard/mouse: Route KB/mouse to any connected source
- USB accessory switching: 6 USB devices switchable between sources
- Wireless KB/mouse support (Bluetooth)

**Touch Panel Integration:**
- Protocol servers: Crestron CH5, Extron SIS, AMX NetLinx, WebSocket
- Touch input routing: USB HID touch follows active source
- Multi-panel support: Up to 10 simultaneous panels

**Power:**
- Input: 19V DC, 6.5A (120W) or PoE++ (802.3bt, 90W)
- Consumption: 60-100W typical, 120W max
- Battery backup: Optional UPS module (30 min runtime)

**Physical:**
- Dimensions: 300 × 200 × 45 mm (12" × 8" × 1.8")
- Weight: 1.5 kg
- Mounting: Wall mount, rack mount (1U full-width), under-table

**Operating System:**
- Linux-based (Ubuntu 22.04 LTS)
- Android container (for native apps - full)
- Docker support (for custom applications)

### What You Get

✅ **Enterprise AV Control** - 6 sources → 2 displays (full matrix)  
✅ **AI Studio Effects (Full)** - Background, eye contact, framing, lighting  
✅ **Voice Focus (Professional)** - Krisp-level, echo cancellation  
✅ **Teams Premium Features** - Intelligent recap, speaker coaching  
✅ **Unified Communications (Full)** - SIP, intercom, paging, unlimited doorbells  
✅ **Full KVM** - Video + KB/mouse + USB switching  
✅ **Native Apps (Full)** - Teams, Zoom, Webex, Netflix, YouTube  
✅ **Touch Panel Servers** - Crestron, Extron, AMX, WebSocket  
✅ **Wireless Presentation** - AirPlay 2, Chromecast, Miracast (4 simultaneous)  
✅ **Universal RTC** - Single interface for Teams/Zoom/Webex/Meet  
✅ **Seamless Call Handoff** - Follow Me mode, badge tracking  
✅ **Access Control** - Unlimited smart locks  
❌ Video wall controller (use MCG-Enterprise)  

### Use Cases
- Enterprise conference room (6 sources: laptops, Teams Room PC, Apple TV, whiteboard camera → 2 displays + projector)
- Executive office (desktop, laptop, Teams → 2 monitors)
- Training room (instructor PC + 5 student laptops → 2 displays)
- Hybrid workspace (hot desk with KVM for multiple users)

### Price
- **MSRP:** $1,999
- **BOM Cost:** $698
- **Margin:** 65%

---

## 4. MCG-Enterprise (Control Room / Video Wall)

**Target:** Control rooms, NOCs, security centers, video walls, digital signage, large enterprises

### Key Features
- ✅ 12 HDMI inputs, 4 HDMI outputs (4K@60Hz, HDCP 2.3)
- ✅ All control protocols (IR, RF, RS232, RS485, TCP/IP, MQTT, KNX)
- ✅ Dual Gigabit Ethernet (bonded) + WiFi 6E + optional 10 GbE
- ✅ USB 3.2 ports (8x) + USB-C Thunderbolt (4x)
- ✅ **Advanced KVM** - Full matrix video/KB/mouse/USB switching
- ✅ **AI video effects (Dedicated GPU)** - 4K@60fps processing
  - All Windows Studio Effects
  - Real-time 4K background replacement
  - Multi-stream processing (4 simultaneous)
- ✅ **Professional audio** - XLR, Dante, MADI, AES67
- ✅ **Unified Communications (Enterprise)**
  - SIP phone system (unlimited extensions)
  - Intercom (unlimited stations)
  - Paging (unlimited zones)
  - Doorbell (unlimited)
  - Access control (unlimited)
- ✅ **Video Wall Controller** - Up to 4×4 (16 displays)
- ✅ **Digital Signage** - Content management, scheduling
- ✅ **Multi-User Frontend** - 10+ simultaneous users
- ✅ **Redundancy** - Dual power supplies, failover

### Technical Specifications

**Processor:**
- CPU: Intel Core i7-13700H or AMD Ryzen 9 7940HS
  - 14-core (6P + 8E) or 8-core @ 5.0 GHz boost
- GPU: **Dedicated GPU** - NVIDIA RTX 4060 Mobile (8 GB VRAM) or AMD Radeon RX 7600M
  - CUDA cores / Stream processors
  - Tensor cores for AI
  - Ray tracing cores
- NPU: Intel AI Boost (16 TOPS) or AMD XDNA (16 TOPS)
- RAM: 32 GB DDR5
- Storage: 512 GB NVMe SSD (M.2, expandable to 2 TB)

**Video I/O:**
- HDMI Inputs: 12 × HDMI 2.1 (4K@120Hz, 8K@60Hz)
- HDMI Outputs: 4 × HDMI 2.1 (4K@120Hz, 8K@60Hz, independent)
- DisplayPort: 4 × DisplayPort 2.0 (via Thunderbolt)
- SDI: 4 × 12G-SDI (optional, for broadcast)
- Max resolution: 7680×4320@60Hz or 3840×2160@120Hz per output

**Audio:**
- HDMI ARC/eARC (all 4 outputs)
- XLR inputs: 4 × XLR (mic inputs, 48V phantom power, +48 dB gain)
- XLR outputs: 4 × XLR (line outputs, balanced)
- Dante: 64×64 channels (audio-over-IP, AES67 compatible)
- MADI: Optical or coaxial (64 channels)
- I2S (16-channel)
- SPDIF optical + coaxial (multiple)
- AES/EBU (professional digital audio, multiple)
- USB audio (class-compliant, multiple devices)

**Control Interfaces:**
- IR: 8 × IR blaster ports (38 kHz, high-power, learning)
- RF: 433 MHz / 315 MHz (built-in + 2 external antennas)
- RS232: 8 × DB9 or terminal block (up to 921600 baud)
- RS485: 2 × RS485 (Modbus, DMX512, multiple devices)
- TCP/IP: Network-based control (unlimited devices)
- MQTT: IoT device control
- KNX: Smart home integration (KNX IP interface)
- Relay: 8 × dry contact relay outputs (10A, door strikes, etc.)
- GPIO: 16 × general-purpose I/O

**Network:**
- Ethernet: 2 × Gigabit Ethernet (bonded, 2 Gbps aggregate, failover)
- Optional: 1 × 10 Gigabit Ethernet (SFP+)
- WiFi: WiFi 6E (802.11ax), tri-band 2.4/5/6 GHz, 4×4 MIMO
- Bluetooth: 5.3 (badge tracking, peripherals)
- LTE/5G: Optional cellular modem (for failover)

**USB:**
- USB 3.2 Gen 2: 8 × USB-A ports (10 Gbps)
- USB-C Thunderbolt 4: 4 × USB-C (40 Gbps, DisplayPort 2.0, 100W PD)
- USB Hub: Internal 16-port hub for peripherals

**KVM:**
- Video matrix: 12 inputs × 4 outputs (full matrix switching)
- Keyboard/mouse: Route to any of 12 sources
- USB accessory switching: 16 USB devices switchable between sources
- Multi-user KVM: 4 operators can control different sources simultaneously
- Wireless KB/mouse support (Bluetooth, 2.4 GHz RF)

**Video Wall:**
- Configuration: Up to 4×4 (16 displays)
- Bezel correction: Automatic bezel compensation
- Content spanning: Single content across multiple displays
- Multi-content: Different content per display or zone
- Rotation: Portrait, landscape, any angle

**Touch Panel Integration:**
- Protocol servers: Crestron CH5, Extron SIS, AMX NetLinx, WebSocket, Custom
- Touch input routing: USB HID touch follows active source or manual routing
- Multi-panel support: Up to 50 simultaneous panels
- Panel types: USB, IP, Serial, Web

**Power:**
- Input: Dual 19V DC, 10A (190W each) or Dual PoE++ (802.3bt, 90W each)
- Total: 380W max, 200W typical
- Redundancy: Automatic failover between power supplies
- Battery backup: Optional UPS module (60 min runtime)

**Physical:**
- Dimensions: 430 × 300 × 65 mm (17" × 12" × 2.6")
- Weight: 3.5 kg
- Mounting: Rack mount (2U full-width), wall mount (heavy-duty)
- Cooling: Active cooling (fans), temperature monitoring

**Operating System:**
- Linux-based (Ubuntu 22.04 LTS)
- Android container (for native apps - full)
- Docker support (for custom applications)
- Kubernetes (optional, for enterprise orchestration)

### What You Get

✅ **Enterprise AV Control** - 12 sources → 4 displays (full matrix)  
✅ **AI Studio Effects (4K)** - All effects at 4K@60fps, 4 simultaneous streams  
✅ **Voice Focus (Studio-grade)** - Dante audio, professional DSP  
✅ **Teams Premium (Multi-user)** - 10+ simultaneous users  
✅ **Unified Communications (Enterprise)** - Unlimited everything  
✅ **Advanced KVM** - 12×4 video matrix + multi-user KVM  
✅ **Native Apps (Full)** - All platforms, 4K streaming  
✅ **Touch Panel Servers** - All protocols + custom  
✅ **Wireless Presentation** - 4 simultaneous presenters  
✅ **Universal RTC (Multi-room)** - Manage 50+ rooms  
✅ **Video Wall Controller** - Up to 4×4 (16 displays)  
✅ **Digital Signage** - Full CMS, scheduling, multi-zone  
✅ **Multi-User Frontend** - 10+ simultaneous operators  
✅ **Redundancy** - Dual power, dual network, failover  

### Use Cases
- Security/NOC control room (12 camera feeds → 4 operator displays + video wall)
- Trading floor (12 Bloomberg terminals → 4 trader displays)
- Digital signage (video wall in lobby, airport, retail)
- Enterprise command center (unified monitoring and control)
- Broadcast studio (12 sources → 4 outputs with SDI)

### Price
- **MSRP:** $3,999
- **BOM Cost:** $1,298
- **Margin:** 68%

---

## Network Configuration

### All Models Include

**IP Assignment:**
- Static IP configuration (default: 192.168.1.100)
- DHCP client (auto-assign from router)
- Manual IP via web interface or config file

**Network Management:**
- Web interface: http://gateway-ip (HTTPS available)
- SSH access: ssh admin@gateway-ip
- API: RESTful API on port 8080
- WebSocket: Real-time updates on port 8081

**Redundancy (Ethernet + WiFi):**
- Primary: Gigabit Ethernet (wired, lowest latency)
- Backup: WiFi 6/6E (automatic failover if Ethernet drops)
- Failover time: < 3 seconds
- Notification: Email/SMS when failover occurs

**Network Protocols:**
- HTTP/HTTPS (web interface, API)
- SSH (secure shell, management)
- MQTT (IoT devices, smart home)
- mDNS/Bonjour (service discovery)
- SNMP (network monitoring)
- Syslog (centralized logging)

### Network Diagram

```
┌─────────────────────────────────────────────────┐
│         MediaControl Gateway Network            │
│                                                 │
│  ┌──────────────┐         ┌──────────────┐     │
│  │   Primary    │         │   Backup     │     │
│  │   Gigabit    │         │   WiFi 6/6E  │     │
│  │   Ethernet   │         │              │     │
│  └──────┬───────┘         └──────┬───────┘     │
│         │                        │             │
│         │ (Wired)                │ (Wireless)  │
│         ▼                        ▼             │
│  ┌────────────────────────────────────┐        │
│  │  Network Switch / Router           │        │
│  │  (assigns IP: 192.168.1.100)       │        │
│  └────────────────┬───────────────────┘        │
│                   │                            │
│                   ▼                            │
│         ┌──────────────────┐                   │
│         │  Internet /      │                   │
│         │  Corporate LAN   │                   │
│         └──────────────────┘                   │
│                                                 │
│  Failover Logic:                               │
│  1. Ethernet link down? → Switch to WiFi       │
│  2. WiFi connected? → Resume operation          │
│  3. Ethernet restored? → Switch back           │
└─────────────────────────────────────────────────┘
```

---

## Comparison Table

| Feature | MCG-Lite | MCG-Standard | MCG-Pro | MCG-Enterprise |
|---------|----------|--------------|---------|----------------|
| **Price (MSRP)** | $399 | $899 | $1,999 | $3,999 |
| **Target** | Home | Small Biz | Enterprise | Control Room |
| | | | | |
| **HDMI In** | 2 | 4 | 6 | 12 |
| **HDMI Out** | 1 | 2 | 2 | 4 |
| **Max Resolution** | 4K@60Hz | 4K@60Hz | 4K@120Hz | 8K@60Hz |
| | | | | |
| **Network** | | | | |
| Gigabit Ethernet | 1 | 1 | 2 (bonded) | 2 (bonded) |
| WiFi | 6 | 6 | 6E | 6E (4×4) |
| Optional 10 GbE | ❌ | ❌ | ❌ | ✅ |
| | | | | |
| **Control** | | | | |
| IR Blasters | 2 | 4 | 6 | 8 |
| RF Control | ✅ | ✅ | ✅ | ✅ |
| RS232 | 1 (USB) | 2 | 4 | 8 |
| RS485 | ❌ | ❌ | 1 | 2 |
| Relay | ❌ | ❌ | 4 | 8 |
| | | | | |
| **USB** | | | | |
| USB-A Ports | 2 (USB 2.0) | 4 (USB 3.0) | 6 (USB 3.2) | 8 (USB 3.2) |
| USB-C Ports | 1 | 1 | 2 (TB4) | 4 (TB4) |
| | | | | |
| **KVM** | | | | |
| USB Switching | ❌ | Basic | Full | Advanced |
| Video Switching | ❌ | ❌ | ✅ (6×2) | ✅ (12×4) |
| Multi-user KVM | ❌ | ❌ | ❌ | ✅ (4 users) |
| | | | | |
| **AI Processing** | | | | |
| Processor | RK3568 | RK3588 | Core Ultra 5 | Core i7 |
| GPU | Mali-G52 | Mali-G610 | Iris Xe | RTX 4060 |
| NPU | ❌ | 1 TOPS | 10 TOPS | 16 TOPS |
| AI Resolution | 720p@30fps | 1080p@30fps | 1080p@60fps | 4K@60fps |
| Simultaneous Streams | 1 | 1 | 2 | 4 |
| | | | | |
| **AI Features** | | | | |
| Background Blur | ✅ | ✅ | ✅ | ✅ |
| Background Replace | ❌ | ✅ | ✅ | ✅ |
| Eye Contact Correction | ❌ | ❌ | ✅ | ✅ |
| Auto Framing | ❌ | ❌ | ✅ | ✅ |
| Portrait Lighting | ❌ | ❌ | ✅ | ✅ |
| | | | | |
| **Communications** | | | | |
| SIP Extensions | 1 | 2 | Unlimited | Unlimited |
| Intercom Stations | 1 | 2 | Unlimited | Unlimited |
| Paging Zones | ❌ | 1 | Unlimited | Unlimited |
| Doorbells | 1 | 2 | Unlimited | Unlimited |
| Access Control Locks | ❌ | 2 | Unlimited | Unlimited |
| Call Handoff | ❌ | Manual | Automatic | Follow Me |
| | | | | |
| **Touch Panels** | | | | |
| Web Interface | ✅ | ✅ | ✅ | ✅ |
| Crestron CH5 | ❌ | ❌ | ✅ | ✅ |
| Extron SIS | ❌ | ❌ | ✅ | ✅ |
| AMX NetLinx | ❌ | ❌ | ❌ | ✅ |
| Max Panels | 1 | 2 | 10 | 50 |
| | | | | |
| **Advanced Features** | | | | |
| Native Apps | ❌ | Basic | Full | Full |
| Universal RTC | ❌ | ❌ | ✅ | ✅ |
| Wireless Presentation | ❌ | ✅ (1) | ✅ (4) | ✅ (4) |
| Video Wall | ❌ | ❌ | ❌ | ✅ (4×4) |
| Digital Signage | ❌ | ❌ | ❌ | ✅ |
| Multi-User Frontend | ❌ | ❌ | ❌ | ✅ (10+) |
| | | | | |
| **Power** | | | | |
| Input | 12V 3A | 12V 5A | 19V 6.5A | 19V 10A × 2 |
| PoE+ | ❌ | ✅ | ✅ | ✅ |
| Consumption | 15-25W | 30-50W | 60-100W | 150-250W |
| Redundant PSU | ❌ | ❌ | ❌ | ✅ |
| | | | | |
| **Physical** | | | | |
| Dimensions (mm) | 150×100×30 | 200×150×35 | 300×200×45 | 430×300×65 |
| Weight | 300g | 600g | 1.5 kg | 3.5 kg |
| Rack Mount | ❌ | Half-width | Full-width | 2U |

---

## Bill of Materials (BOM) Breakdown

### MCG-Lite ($149 BOM)

| Component | Part | Cost |
|-----------|------|------|
| SoC | Rockchip RK3568 | $25 |
| RAM | 4 GB LPDDR4 | $10 |
| Storage | 32 GB eMMC | $8 |
| HDMI | 2 in + 1 out (IC + ports) | $15 |
| Ethernet | Gigabit PHY + RJ45 | $5 |
| WiFi/BT | WiFi 6 + BT 5.0 module | $12 |
| USB | 3 ports (IC + connectors) | $5 |
| IR/RF | IR blasters + RF module | $8 |
| Power | 12V 3A adapter | $6 |
| PCB | 4-layer PCB | $10 |
| Enclosure | Aluminum case | $15 |
| Cooling | Passive heatsink | $5 |
| Assembly | Labor + testing | $20 |
| Misc | Cables, connectors, etc. | $5 |
| **Total** | | **$149** |

### MCG-Standard ($349 BOM)

| Component | Part | Cost |
|-----------|------|------|
| SoC | Rockchip RK3588 | $65 |
| RAM | 8 GB LPDDR4X | $20 |
| Storage | 64 GB eMMC | $12 |
| HDMI | 4 in + 2 out (IC + ports) | $35 |
| Ethernet | Gigabit PHY + RJ45 | $5 |
| WiFi/BT | WiFi 6 + BT 5.2 module | $18 |
| USB | 5 ports (IC + connectors) | $10 |
| IR/RF/RS232 | Full control suite | $20 |
| Power | 12V 5A adapter or PoE+ | $10 |
| PCB | 6-layer PCB | $25 |
| Enclosure | Aluminum case | $30 |
| Cooling | Active cooling (fan) | $10 |
| Assembly | Labor + testing | $60 |
| Misc | Cables, connectors, etc. | $29 |
| **Total** | | **$349** |

### MCG-Pro ($698 BOM)

| Component | Part | Cost |
|-----------|------|------|
| CPU | Intel Core Ultra 5 125H | $280 |
| RAM | 16 GB DDR5 | $50 |
| Storage | 256 GB NVMe SSD | $30 |
| HDMI | 6 in + 2 out (IC + ports) | $60 |
| Ethernet | Dual Gigabit PHY | $10 |
| WiFi/BT | WiFi 6E + BT 5.3 module | $30 |
| USB | 8 ports + Thunderbolt 4 | $40 |
| IR/RF/RS232/RS485 | Full control suite | $35 |
| Audio | XLR + I2S + SPDIF | $25 |
| Power | 19V 6.5A adapter or PoE++ | $15 |
| PCB | 8-layer PCB | $40 |
| Enclosure | Aluminum case | $50 |
| Cooling | Active cooling (dual fans) | $20 |
| Assembly | Labor + testing | $100 |
| Misc | Cables, connectors, etc. | $13 |
| **Total** | | **$698** |

### MCG-Enterprise ($1,298 BOM)

| Component | Part | Cost |
|-----------|------|------|
| CPU | Intel Core i7-13700H | $400 |
| GPU | NVIDIA RTX 4060 Mobile (8 GB) | $280 |
| RAM | 32 GB DDR5 | $100 |
| Storage | 512 GB NVMe SSD | $50 |
| HDMI | 12 in + 4 out (IC + ports) | $120 |
| Ethernet | Dual Gigabit + optional 10 GbE | $30 |
| WiFi/BT | WiFi 6E (4×4) + BT 5.3 | $45 |
| USB | 12 ports + Thunderbolt 4 × 4 | $80 |
| IR/RF/RS232/RS485 | Full control suite (×2) | $60 |
| Audio | XLR + Dante + MADI | $50 |
| Power | Dual 19V 10A adapters | $30 |
| PCB | 10-layer PCB | $80 |
| Enclosure | Aluminum rack-mount case | $100 |
| Cooling | Active cooling (quad fans) | $40 |
| Assembly | Labor + testing | $200 |
| Misc | Cables, connectors, etc. | $133 |
| **Total** | | **$1,298** |

---

## Pricing Strategy

### Retail Pricing (MSRP)

| Model | MSRP | BOM | Margin | Dealer Cost (60%) | Dealer Margin |
|-------|------|-----|--------|-------------------|---------------|
| MCG-Lite | $399 | $149 | 63% | $240 | 40% |
| MCG-Standard | $899 | $349 | 61% | $540 | 40% |
| MCG-Pro | $1,999 | $698 | 65% | $1,200 | 42% |
| MCG-Enterprise | $3,999 | $1,298 | 68% | $2,400 | 46% |

### Channel Strategy

**Direct Sales (mediacontrol.com):**
- Full MSRP pricing
- Free shipping over $500
- 30-day money-back guarantee
- 3-year warranty

**AV Integrator Dealers:**
- 40% dealer discount (60% of MSRP)
- Minimum order: 10 units (mix and match)
- Co-op marketing funds (3%)
- Technical training included

**Enterprise Direct:**
- Volume pricing (50+ units: 10% additional discount)
- White-glove setup and training
- Dedicated account manager
- Custom configuration available

---

## Subscription Mapping

| Model | Recommended Tier | Cost/Mo | Total 3-Year Cost |
|-------|------------------|---------|-------------------|
| MCG-Lite | FREE or HOME | $0-$9 | $399-$723 |
| MCG-Standard | HOME PRO | $29 | $1,943 |
| MCG-Pro | BUSINESS | $99 | $5,563 |
| MCG-Enterprise | ENTERPRISE | $499 | $21,963 |

**Bundled Pricing (Hardware + 3-Year Subscription):**
- MCG-Lite + HOME: $399 + $324 = **$723** (save $72)
- MCG-Standard + HOME PRO: $899 + $1,044 = **$1,943** (save $200)
- MCG-Pro + BUSINESS: $1,999 + $3,564 = **$5,563** (save $500)
- MCG-Enterprise + ENTERPRISE: $3,999 + $17,964 = **$21,963** (save $1,000)

---

## Manufacturing & Supply Chain

### Manufacturing Partners

**Option 1: Foxconn (Taiwan/China)**
- High volume (100K+ units/year)
- Lowest cost ($10-$20 per unit assembly)
- 8-12 week lead time
- Minimum order: 5,000 units

**Option 2: Flex (Mexico/USA)**
- Medium volume (10K-100K units/year)
- Moderate cost ($20-$40 per unit assembly)
- 6-8 week lead time
- Minimum order: 1,000 units
- **Recommended for initial production**

**Option 3: Benchmark Electronics (USA)**
- Low-medium volume (1K-10K units/year)
- Higher cost ($40-$80 per unit assembly)
- 4-6 week lead time
- Minimum order: 100 units
- **Recommended for prototype/pilot**

### Component Sourcing

**Critical Components:**
- **CPUs:** Intel (direct), AMD (direct), Rockchip (distributors)
- **GPUs:** NVIDIA (authorized partners only)
- **HDMI ICs:** Silicon Image, Toshiba (distributors)
- **Network:** Intel (Ethernet), Qualcomm/Broadcom (WiFi)

**Lead Times:**
- CPUs/GPUs: 12-16 weeks (need forecasting)
- HDMI ICs: 8-12 weeks
- Commodity components: 4-8 weeks

### Inventory Strategy

**Initial Production (Year 1):**
- MCG-Lite: 5,000 units
- MCG-Standard: 3,000 units
- MCG-Pro: 1,000 units
- MCG-Enterprise: 500 units
- **Total: 9,500 units**

**Inventory Turns:** 4-6x per year (2-3 months inventory)

---

## Go-to-Market Timeline

### Phase 1: Pilot (Months 1-3)
- Build 100 units (MCG-Pro) with Benchmark Electronics
- Deploy to 10 beta customers
- Gather feedback, iterate firmware

### Phase 2: Limited Launch (Months 4-6)
- Build 1,000 units (mix) with Flex
- Launch direct sales (website)
- Onboard 10 AV integrator dealers

### Phase 3: Full Launch (Months 7-12)
- Build 10,000 units (mix) with Flex
- Expand to 50 dealers
- Launch enterprise sales team
- International expansion (UK, EU, APAC)

### Phase 4: Scale (Year 2+)
- Move high-volume (MCG-Lite, Standard) to Foxconn
- Keep MCG-Pro/Enterprise with Flex (better support)
- Target: 50,000 units/year

---

## Competitive Positioning

| Competitor | Product | Price | Our Equivalent | Our Price | Savings |
|------------|---------|-------|----------------|-----------|---------|
| Crestron | 3-Series Processor | $3,500 | MCG-Lite | $399 | 89% |
| Extron | IN1608 Scaler | $8,000 | MCG-Standard | $899 | 89% |
| Crestron | NVX 360 | $2,500 | MCG-Pro | $1,999 | 20% |
| Barco | ClickShare Conference | $3,000 | MCG-Pro | $1,999 | 33% |
| Crestron | DM-MD8×8 | $15,000 | MCG-Enterprise | $3,999 | 73% |

**Key Differentiators:**
- ✅ We're 20-89% cheaper
- ✅ We have AI features (they don't)
- ✅ We have unified communications (they don't)
- ✅ We're open-source (they're proprietary)
- ✅ We have Gigabit Ethernet + WiFi redundancy (standard)

---

## Summary

**MediaControl Gateway Lineup:**
1. **MCG-Lite** ($399) - Home, small office, 2-room setup
2. **MCG-Standard** ($899) - Small business, 4-room setup
3. **MCG-Pro** ($1,999) - Enterprise conference room, full features
4. **MCG-Enterprise** ($3,999) - Control room, video wall, unlimited

**Every Model Includes:**
- ✅ Gigabit Ethernet + WiFi (redundancy)
- ✅ Static IP assignment
- ✅ Core AV control
- ✅ Web management interface
- ✅ 3-year warranty

**Total Investment:**
- R&D: $2M (year 1)
- Manufacturing NRE: $500K (tooling, first build)
- Initial inventory: $3.5M (9,500 units)
- **Total: $6M**

**Projected Revenue:**
- Year 1: $85M (revenue projection already calculated)
- Break-even: Month 9
- ROI: 1,300% by end of Year 3

---

**For manufacturing inquiries:**
- **Email:** manufacturing@mediacontrol.com
- **Phone:** +1-555-GATEWAY (428-3929)
