# Door Access Control - Multi-Factor Authentication

**Complete Access Control System with NFC, RFID, Face Recognition, Fingerprint, and PIN Pad**

---

## Table of Contents

1. [Overview](#overview)
2. [NFC Access Control](#nfc-access-control)
3. [RFID Access Control](#rfid-access-control)
4. [Face Recognition](#face-recognition)
5. [Fingerprint Access](#fingerprint-access)
6. [PIN Pad Access](#pin-pad-access)
7. [Multi-Factor Authentication (MFA)](#multi-factor-authentication-mfa)
8. [Hardware Integration](#hardware-integration)
9. [Configuration](#configuration)
10. [API Reference](#api-reference)

---

## Overview

**MediaControl Access Control System** supports **5 authentication methods** with flexible multi-factor authentication:

| Method | Technology | Speed | Security | Use Cases |
|--------|-----------|-------|----------|-----------|
| **NFC** | Near Field Communication | ⚡ Instant | 🔒 High | Cards, key fobs, smartphones |
| **RFID** | Radio Frequency ID | ⚡ Instant | 🔒 Medium-High | Traditional access cards |
| **Face Recognition** | AI Computer Vision | ⚡⚡ Fast (0.3s) | 🔒🔒 Very High | Touchless, hands-free access |
| **Fingerprint** | Capacitive/Optical | ⚡ Fast (0.5s) | 🔒🔒 Very High | High-security areas |
| **PIN Pad** | Keypad Entry | ⚡⚡⚡ Slow (5s) | 🔒 Medium | Backup, temporary access |

### Key Features

- ✅ **Multi-factor authentication** - Require 2+ methods for high-security areas
- ✅ **Fallback options** - If face recognition fails, use fingerprint or PIN
- ✅ **Touchless access** - Face recognition, NFC via smartphone
- ✅ **Time-based access** - Grant access during specific hours/days
- ✅ **Anti-passback** - Prevent tailgating, require exit scan
- ✅ **Real-time logging** - All access attempts logged with photos/videos
- ✅ **Emergency override** - PIN code for lockdown/evacuation
- ✅ **Visitor management** - Temporary PINs, time-limited access
- ✅ **Integration** - Works with Ubiquiti Access, Salto, ASSA ABLOY, and more

---

## NFC Access Control

### Overview

**Near Field Communication (NFC)** provides fast, secure, contactless access via:
- NFC cards (ISO 14443A/B, 13.56 MHz)
- NFC key fobs
- Smartphones (Apple Wallet, Google Wallet, Samsung Wallet)
- Smartwatches (Apple Watch, Wear OS, Galaxy Watch)

### Advantages

- ✅ **Instant access** - Tap and go (<0.3 seconds)
- ✅ **Secure** - AES-128 encryption, mutual authentication
- ✅ **Convenient** - No battery required (passive cards)
- ✅ **Multi-device** - Works with cards, phones, watches
- ✅ **No physical contact** - Touchless operation
- ✅ **Already in your pocket** - Most people carry NFC-enabled phones

### Supported NFC Standards

| Standard | Frequency | Range | Use Case |
|----------|-----------|-------|----------|
| **ISO 14443A** | 13.56 MHz | 0-10 cm | MIFARE cards, Apple Pay, Google Pay |
| **ISO 14443B** | 13.56 MHz | 0-10 cm | Government IDs, passports |
| **ISO 15693** | 13.56 MHz | 0-100 cm | Vicinity cards (longer range) |
| **NFC Type 2** | 13.56 MHz | 0-10 cm | NTAG215/216, low-cost tags |

### NFC Card Types

**MIFARE Classic:**
- ✅ 1KB/4KB memory
- ✅ ISO 14443A compatible
- ✅ Low cost ($0.50-$1 per card)
- ⚠️ Moderate security (48-bit keys)

**MIFARE DESFire:**
- ✅ 2KB/4KB/8KB memory
- ✅ AES-128 encryption
- ✅ High security
- ✅ Multi-application support
- 💰 Higher cost ($3-$5 per card)

**MIFARE Plus:**
- ✅ AES-128 encryption
- ✅ Backward compatible with MIFARE Classic
- ✅ Good balance of security and cost

**NFC Forum Type 2 (NTAG):**
- ✅ Ultra-low cost ($0.10-$0.30)
- ✅ Read-only or read-write
- ⚠️ Basic security (password protection)

### Hardware Requirements

**NFC Reader:**
- Compatible with ISO 14443A/B
- USB, Ethernet, or RS-485 interface
- Example: ACR122U, PN532, RC522

**Recommended Readers:**
- **ACR122U** - USB NFC reader ($20-$30)
- **HID OMNIKEY 5427** - Enterprise NFC reader ($100-$150)
- **ELATEC TWN4 MultiTech** - Multi-protocol reader ($150-$200)

### Configuration

```yaml
access_control:
  doors:
    - id: "door_main_entrance"
      name: "Main Entrance"
      
      authentication:
        nfc:
          enabled: true
          
          # Reader hardware
          reader:
            type: "acr122u"  # or "omnikey_5427", "twn4"
            interface: "usb"  # or "ethernet", "rs485"
            device: "/dev/ttyUSB0"  # or "192.168.1.100:8080"
          
          # Supported card types
          card_types:
            - "mifare_desfire"  # Highest security
            - "mifare_plus"
            - "mifare_classic"
            - "ntag"
          
          # Security settings
          encryption: "aes128"
          mutual_authentication: true
          
          # Access rules
          rules:
            require_registered_card: true
            max_attempts: 3
            lockout_duration: 300  # 5 minutes after 3 failed attempts
```

### Smartphone NFC (Apple/Google/Samsung Wallet)

**Already implemented!** See `docs/HOSPITALITY_LUXURY_MANAGEMENT.md` for:
- Apple Wallet integration (Express Mode, Power Reserve)
- Google Wallet integration (Gmail auto-import)
- Samsung Wallet integration (Knox security)

---

## RFID Access Control

### Overview

**Radio Frequency Identification (RFID)** is the traditional access control method using:
- Low Frequency (LF) cards - 125 kHz
- High Frequency (HF) cards - 13.56 MHz (same as NFC)
- Ultra High Frequency (UHF) cards - 860-960 MHz (long range)

### Advantages

- ✅ **Proven technology** - Decades of use in enterprise
- ✅ **Long range** - UHF can read 1-10 meters
- ✅ **Low cost** - LF cards as low as $0.20 each
- ✅ **Durable** - Passive cards, no battery, waterproof
- ✅ **Legacy support** - Works with existing systems

### RFID Frequencies

| Frequency | Range | Speed | Use Case |
|-----------|-------|-------|----------|
| **LF (125 kHz)** | 0-10 cm | Slow | Legacy systems, proximity cards |
| **HF (13.56 MHz)** | 0-10 cm | Fast | Modern systems, NFC-compatible |
| **UHF (860-960 MHz)** | 1-10 m | Fast | Parking, warehouse, vehicle access |

### RFID Card Types

**EM4100/EM4102 (LF):**
- ✅ Read-only
- ✅ Ultra-low cost ($0.20 per card)
- ⚠️ No encryption (card ID only)
- ⚠️ Easy to clone

**HID Proximity (LF):**
- ✅ 125 kHz
- ✅ Industry standard
- ⚠️ Moderate security (proprietary format)
- 💰 Medium cost ($1-$2 per card)

**HID iCLASS (HF):**
- ✅ 13.56 MHz (NFC-compatible!)
- ✅ AES encryption
- ✅ High security
- ✅ Multi-application support
- 💰 Higher cost ($3-$5 per card)

**UHF RFID (860-960 MHz):**
- ✅ Long range (1-10 meters)
- ✅ Fast read speed
- ✅ EPC Gen2 standard
- 💰 Medium cost ($0.50-$2 per tag)

### Hardware Requirements

**RFID Reader:**
- Compatible with desired frequency (LF/HF/UHF)
- Wiegand, RS-485, or Ethernet output
- Example: HID ProxPoint Plus, HID iCLASS SE

**Recommended Readers:**
- **HID ProxPoint Plus** - LF 125 kHz reader ($50-$80)
- **HID iCLASS SE** - HF 13.56 MHz reader ($100-$150)
- **Impinj Speedway** - UHF reader for long-range ($500-$1000)

### Configuration

```yaml
access_control:
  doors:
    - id: "door_parking_garage"
      name: "Parking Garage"
      
      authentication:
        rfid:
          enabled: true
          
          # Reader hardware
          reader:
            type: "hid_proxpoint"  # or "hid_iclass", "impinj_speedway"
            frequency: "125khz"  # or "13.56mhz", "uhf"
            interface: "wiegand"  # or "rs485", "ethernet"
            
            # Wiegand configuration
            wiegand:
              data0_pin: 17  # GPIO pin for D0
              data1_pin: 18  # GPIO pin for D1
              format: "26bit"  # Standard Wiegand 26-bit
          
          # Supported card types
          card_types:
            - "hid_prox"
            - "em4100"
          
          # Long-range settings (UHF only)
          long_range:
            enabled: false
            max_distance: 5  # meters
            min_rssi: -70  # Signal strength threshold
```

---

## Face Recognition

### Overview

**AI-powered face recognition** provides touchless, hands-free access:
- No physical contact required
- Fast recognition (0.3-1 second)
- Works with masks (optional)
- Liveness detection (anti-spoofing)
- 99.9%+ accuracy with modern algorithms

### Advantages

- ✅ **Touchless** - No contact, hygienic
- ✅ **Hands-free** - No need to reach for card/phone
- ✅ **Fast** - Recognition in <0.5 seconds
- ✅ **Difficult to forge** - Liveness detection prevents photos/videos
- ✅ **User-friendly** - Just walk up to the door
- ✅ **Audit trail** - Photo of every access attempt

### Technology

**AI Models:**
- **FaceNet** - Google's face recognition model (99.63% accuracy on LFW)
- **ArcFace** - State-of-the-art face recognition (99.83% accuracy)
- **DeepFace** - Facebook's face recognition library

**Liveness Detection:**
- ✅ **3D depth sensing** - Detect fake faces (photos, videos)
- ✅ **IR camera** - Work in low light, detect masks
- ✅ **Eye blink detection** - Ensure live person
- ✅ **Face movement** - Request slight head turn

**Privacy Features:**
- ✅ **Edge processing** - Face data never leaves the device
- ✅ **Encrypted storage** - Face templates encrypted with AES-256
- ✅ **No cloud** - All processing happens locally
- ✅ **GDPR compliant** - Right to delete, data portability

### Hardware Requirements

**Camera:**
- **RGB camera** - 720p minimum, 1080p recommended
- **IR camera** - For low-light and liveness detection
- **3D depth camera** - Intel RealSense, Azure Kinect (optional, for liveness)

**Processing:**
- **GPU recommended** - NVIDIA GPU for real-time processing
- **CPU fallback** - Works on CPU but slower (1-2 seconds)

**Recommended Hardware:**
- **Hikvision DS-K1T342** - Face recognition terminal ($200-$300)
- **Dahua DHI-ASI7213Y-V3** - Face + card reader ($250-$350)
- **ZKTeco SpeedFace-V5L** - Face recognition with mask detection ($300-$400)
- **DIY:** Raspberry Pi 4 + USB camera + Coral TPU ($150-$200)

### Configuration

```yaml
access_control:
  doors:
    - id: "door_executive_office"
      name: "Executive Office"
      
      authentication:
        face_recognition:
          enabled: true
          
          # Camera hardware
          camera:
            type: "hikvision_face"  # or "dahua_face", "zkteco", "custom"
            ip: "192.168.1.150"
            
            # For custom camera (e.g., USB webcam)
            device: "/dev/video0"
            resolution: "1920x1080"
            fps: 30
          
          # AI model
          model:
            algorithm: "arcface"  # or "facenet", "deepface"
            accuracy_threshold: 0.95  # 95% match required
            
            # GPU acceleration (optional)
            use_gpu: true
            gpu_device: 0
          
          # Liveness detection
          liveness:
            enabled: true
            methods:
              - "3d_depth"  # Requires depth camera
              - "ir_camera"  # Requires IR camera
              - "eye_blink"
              - "face_movement"
            
            # Anti-spoofing
            reject_photos: true
            reject_videos: true
            reject_masks: false  # Allow masks (COVID-19)
          
          # Performance
          max_faces_per_frame: 5
          recognition_speed: "fast"  # or "balanced", "accurate"
          
          # Privacy
          store_photos: false  # Only store face templates
          encrypt_templates: true
          encryption_key: "your_aes256_key"
```

### Face Enrollment

**Process:**
1. User stands in front of camera
2. System captures multiple angles (front, left, right, up, down)
3. AI extracts face template (128-512 dimensional vector)
4. Template encrypted and stored
5. Original photos deleted (optional)

**Best Practices:**
- Capture 5-10 photos per person
- Vary lighting conditions
- Capture with/without glasses
- Capture with/without mask (if mask support needed)

---

## Fingerprint Access

### Overview

**Biometric fingerprint scanning** provides high-security access:
- Unique to each person
- Cannot be lost or forgotten
- Fast recognition (0.5-1 second)
- High accuracy (99.9%+)

### Advantages

- ✅ **Unique** - Each person's fingerprint is unique
- ✅ **Cannot be lost** - Unlike cards or keys
- ✅ **Fast** - Recognition in <1 second
- ✅ **High accuracy** - False acceptance rate <0.001%
- ✅ **Durable** - Scanners last 5-10 years
- ✅ **Compact** - Small form factor

### Technology

**Sensor Types:**

| Type | Technology | Pros | Cons | Cost |
|------|-----------|------|------|------|
| **Capacitive** | Electrical current | High accuracy, difficult to spoof | Affected by dirty/wet fingers | Medium |
| **Optical** | Camera + LED | Low cost, durable | Can be spoofed with photos | Low |
| **Ultrasonic** | Sound waves | 3D capture, works with wet fingers | Higher cost | High |

**Capacitive (Recommended):**
- ✅ High accuracy (FRR <1%, FAR <0.001%)
- ✅ Anti-spoofing (detects live skin)
- ✅ Works with dry fingers
- ⚠️ Struggles with wet/dirty fingers

**Optical:**
- ✅ Low cost ($20-$50)
- ✅ Durable (no moving parts)
- ⚠️ Can be fooled by high-quality photos
- ⚠️ Lower accuracy than capacitive

**Ultrasonic:**
- ✅ 3D fingerprint capture
- ✅ Works with wet/dirty fingers
- ✅ Highest security (difficult to spoof)
- 💰 High cost ($100-$200)

### Hardware Requirements

**Fingerprint Scanner:**
- **USB:** For desktop/server integration
- **Ethernet:** For networked access control
- **Standalone:** Built-in processor and storage

**Recommended Scanners:**
- **ZKTeco SLK20R** - Capacitive fingerprint reader ($80-$120)
- **Suprema BioMini Plus 2** - Optical scanner ($150-$200)
- **HID DigitalPersona U.are.U 4500** - Capacitive USB scanner ($100-$150)
- **Integrated terminals:** Hikvision DS-K1T341 (fingerprint + card, $150-$200)

### Configuration

```yaml
access_control:
  doors:
    - id: "door_server_room"
      name: "Server Room"
      
      authentication:
        fingerprint:
          enabled: true
          
          # Scanner hardware
          scanner:
            type: "zkteco_slk20r"  # or "suprema", "hid_dp"
            interface: "ethernet"  # or "usb"
            ip: "192.168.1.160"  # For networked scanners
            
            # For USB scanners
            device: "/dev/usb/fingerprint0"
          
          # Sensor type
          sensor:
            type: "capacitive"  # or "optical", "ultrasonic"
            resolution: 500  # DPI (500 recommended)
          
          # Matching algorithm
          matching:
            algorithm: "minutiae"  # or "pattern", "ridge"
            threshold: 40  # Lower = stricter (0-100)
            
            # FAR (False Acceptance Rate)
            far: "0.001%"  # 1 in 100,000
            
            # FRR (False Rejection Rate)
            frr: "1%"  # 1 in 100
          
          # Security
          liveness_detection: true  # Detect fake fingers
          encryption: "aes256"
          
          # Enrollment
          fingerprints_per_user: 2  # Left + right index finger
          
          # Performance
          identification_speed: 1  # seconds
          max_users: 10000
```

### Fingerprint Enrollment

**Process:**
1. User places finger on scanner
2. Scanner captures fingerprint image
3. AI extracts minutiae points (ridges, bifurcations)
4. Template created (256-512 bytes)
5. Template encrypted and stored
6. Original image deleted

**Best Practices:**
- Enroll 2 fingers per person (left + right index)
- Clean finger before enrollment
- Multiple scans per finger (3-5 captures)
- Re-enroll if accuracy drops over time

---

## PIN Pad Access

### Overview

**Keypad entry** provides a reliable backup and temporary access method:
- No card/phone needed
- Easy to share (temporary codes)
- Time-limited codes
- Audit trail

### Advantages

- ✅ **Universal** - Everyone knows how to use a keypad
- ✅ **Backup** - If card/phone/biometric fails
- ✅ **Temporary access** - Visitor codes, contractor codes
- ✅ **No hardware** - User's "card" is in their head
- ✅ **Revocable** - Change codes instantly
- ✅ **Time-limited** - Codes expire automatically

### Security Considerations

- ⚠️ **Can be shoulder-surfed** - Someone watches you type
- ⚠️ **Can be shared** - Users may share codes
- ⚠️ **Brute-force attacks** - Attackers try many codes
- ✅ **Mitigations:** Rate limiting, lockout after failed attempts, scrambled keypads

### PIN Code Types

**Personal PIN:**
- Unique to each user
- 4-8 digits
- Never expires (unless changed)

**Temporary PIN:**
- One-time use or time-limited
- For visitors, contractors, deliveries
- Expires after use or time limit

**Master PIN:**
- Override code for emergencies
- Administrator only
- Logged and alerted

**Duress PIN:**
- Silent alarm code
- Unlocks door but triggers alert
- For robbery/hostage situations

### Hardware Requirements

**Keypad Types:**
- **Mechanical** - Physical buttons, tactile feedback
- **Capacitive** - Touch-sensitive, no moving parts
- **Backlit** - Illuminated for night use
- **Weatherproof** - IP65/IP67 rated for outdoor

**Recommended Keypads:**
- **HID pivCLASS RPKCL40** - PIN + card reader ($150-$200)
- **Suprema XPass D2** - PIN + fingerprint + card ($200-$250)
- **Paxton Net2 Keypad** - Ethernet keypad ($100-$150)
- **DIY:** 4x4 matrix keypad + Raspberry Pi ($20-$30)

### Configuration

```yaml
access_control:
  doors:
    - id: "door_loading_dock"
      name: "Loading Dock"
      
      authentication:
        pin_pad:
          enabled: true
          
          # Keypad hardware
          keypad:
            type: "hid_pivclass"  # or "suprema_xpass", "paxton_net2", "custom"
            interface: "wiegand"  # or "rs485", "ethernet"
            backlit: true
            weatherproof: true  # IP67 rated
          
          # PIN code settings
          pin:
            min_length: 4
            max_length: 8
            require_complex: false  # No repeated digits (1111, 1234)
            
            # Personal PINs
            personal_pins:
              enabled: true
              expiry: null  # Never expire
              
            # Temporary PINs
            temporary_pins:
              enabled: true
              max_uses: 1  # One-time use
              max_duration: 86400  # 24 hours
              
            # Master PIN
            master_pin:
              enabled: true
              code: "123456789"  # Change this!
              log_uses: true
              alert_on_use: true
          
          # Security
          anti_brute_force:
            enabled: true
            max_attempts: 3
            lockout_duration: 300  # 5 minutes
            
          scrambled_keypad:
            enabled: false  # Randomize key positions
          
          # Duress code
          duress:
            enabled: true
            silent_alarm: true
            alert_security: true
```

### Temporary PIN Generation

**API:**
```http
POST /api/access-control/pin/generate-temporary

Request:
{
  "door_id": "door_loading_dock",
  "visitor_name": "John Doe",
  "visitor_email": "john@example.com",
  "max_uses": 1,
  "expires_at": "2026-08-01T18:00:00Z"
}

Response:
{
  "pin": "847392",
  "expires_at": "2026-08-01T18:00:00Z",
  "max_uses": 1,
  "remaining_uses": 1
}
```

---

## Multi-Factor Authentication (MFA)

### Overview

**Combine multiple authentication methods** for high-security areas:
- **2FA:** Card + PIN
- **2FA:** Face + Fingerprint
- **3FA:** Card + PIN + Fingerprint

### MFA Combinations

| Combination | Security | Speed | Use Case |
|-------------|----------|-------|----------|
| **Card + PIN** | 🔒🔒 High | ⚡⚡ Fast | Standard high-security |
| **Face + Fingerprint** | 🔒🔒🔒 Very High | ⚡ Medium | Executive offices, data centers |
| **Card + Fingerprint** | 🔒🔒 High | ⚡ Fast | Labs, server rooms |
| **Face + PIN** | 🔒🔒 High | ⚡⚡ Fast | Touchless with backup |
| **Card + PIN + Fingerprint** | 🔒🔒🔒🔒 Extreme | ⚡ Slow | Vaults, critical infrastructure |

### Configuration

```yaml
access_control:
  doors:
    - id: "door_vault"
      name: "Vault"
      
      authentication:
        # Require ALL of these methods
        mfa:
          enabled: true
          required_methods: 2  # 2FA
          
          # Method 1: NFC card
          nfc:
            enabled: true
            weight: 1  # Each method counts as 1
          
          # Method 2: Fingerprint
          fingerprint:
            enabled: true
            weight: 1
          
          # Method 3: PIN (optional backup)
          pin_pad:
            enabled: true
            weight: 1
            backup_only: true  # Only if biometric fails
          
          # MFA rules
          rules:
            timeout: 30  # Complete all methods within 30 seconds
            order: "any"  # or "sequential" (must be in order)
            allow_backup: true  # Allow PIN if biometric fails
```

### Fallback Logic

**Example:** Face + Fingerprint required

```
User approaches door
    ↓
Face recognition attempted
    ↓
Face recognized? ───Yes──→ Request fingerprint
    │                           ↓
    No                     Fingerprint verified? ───Yes──→ GRANT ACCESS
    ↓                           │
Request fingerprint             No
    ↓                           ↓
Fingerprint verified?      Show PIN pad (fallback)
    │                           ↓
    Yes                    PIN entered correctly? ───Yes──→ GRANT ACCESS
    ↓                           │
Request face recognition        No
    ↓                           ↓
Face recognized? ───Yes──→ GRANT ACCESS
    │
    No
    ↓
Show PIN pad (fallback)
    ↓
PIN entered correctly? ───Yes──→ GRANT ACCESS
    │
    No
    ↓
DENY ACCESS (log attempt with photo)
```

---

## Hardware Integration

### Supported Access Control Systems

| System | NFC | RFID | Face | Fingerprint | PIN | Integration Method |
|--------|-----|------|------|-------------|-----|-------------------|
| **Ubiquiti Access** | ✅ | ✅ | ❌ | ❌ | ✅ | HTTP API + Webhooks |
| **Salto Space** | ✅ | ✅ | ✅ | ❌ | ✅ | REST API |
| **ASSA ABLOY** | ✅ | ✅ | ✅ | ✅ | ✅ | OSDP, Wiegand |
| **HID** | ✅ | ✅ | ❌ | ✅ | ✅ | Wiegand, OSDP |
| **ZKTeco** | ✅ | ✅ | ✅ | ✅ | ✅ | TCP/IP API |
| **Hikvision** | ✅ | ✅ | ✅ | ✅ | ✅ | ISAPI (HTTP API) |
| **Dahua** | ✅ | ✅ | ✅ | ✅ | ✅ | HTTP API |
| **Generic** | ✅ | ✅ | ✅ | ✅ | ✅ | Wiegand, RS-485 |

### Communication Protocols

**Wiegand:**
- ✅ Industry standard for card readers
- ✅ Simple 2-wire interface (D0, D1)
- ✅ Supports 26-bit, 37-bit, HID Corporate 1000 formats
- ⚠️ One-way communication (reader → controller)

**OSDP (Open Supervised Device Protocol):**
- ✅ Modern replacement for Wiegand
- ✅ Two-way communication
- ✅ AES-128 encryption
- ✅ Supports biometrics, displays, keypads
- ✅ Built-in tamper detection

**RS-485:**
- ✅ Long-distance communication (up to 1200m)
- ✅ Multi-drop (multiple devices on one bus)
- ✅ Two-way communication
- ⚠️ Requires addressing

**TCP/IP (Ethernet):**
- ✅ Standard network connection
- ✅ PoE support (Power over Ethernet)
- ✅ Easy integration with existing network
- ✅ Remote management

### Gateway Integration

**MediaControl Gateway acts as access control panel:**
- Connects to card readers (Wiegand, OSDP, RS-485)
- Processes authentication locally
- Controls door locks (relay output)
- Logs all access attempts
- Real-time notifications

**Hardware I/O:**
- **Wiegand input** - Connect card/RFID readers
- **RS-485 port** - Connect fingerprint scanners
- **USB ports** - Connect USB fingerprint/face recognition devices
- **Ethernet** - Connect IP-based readers (face recognition terminals)
- **Relay outputs** - Control electric strikes, magnetic locks
- **GPIO pins** - Door sensors, REX (Request to Exit) buttons

---

## Configuration

### Complete Example (All Methods)

```yaml
access_control:
  enabled: true
  
  # Global settings
  logging:
    enabled: true
    log_photos: true  # Store photos of face recognition attempts
    log_videos: false  # Store videos (high storage)
    retention_days: 90
  
  # Doors
  doors:
    # Executive Office - Face + Fingerprint (MFA)
    - id: "door_executive"
      name: "Executive Office"
      location: "Floor 10, East Wing"
      
      # Lock hardware
      lock:
        type: "electric_strike"
        relay_pin: 23  # GPIO pin
        unlock_duration: 5  # seconds
        fail_secure: true  # Lock when power off
      
      # Door sensor
      sensor:
        enabled: true
        gpio_pin: 24
        alert_if_held_open: 30  # seconds
      
      # Authentication methods (MFA)
      authentication:
        mfa:
          enabled: true
          required_methods: 2  # Face + Fingerprint
          timeout: 30  # seconds
        
        # Method 1: Face Recognition
        face_recognition:
          enabled: true
          camera:
            type: "hikvision_face"
            ip: "192.168.1.150"
            username: "admin"
            password: "password123"
          model:
            algorithm: "arcface"
            accuracy_threshold: 0.95
          liveness:
            enabled: true
            methods: ["ir_camera", "eye_blink"]
        
        # Method 2: Fingerprint
        fingerprint:
          enabled: true
          scanner:
            type: "zkteco_slk20r"
            ip: "192.168.1.160"
          matching:
            threshold: 40
            far: "0.001%"
          fingerprints_per_user: 2
        
        # Backup: PIN pad
        pin_pad:
          enabled: true
          backup_only: true  # Only if biometric fails
          pin:
            min_length: 6
            max_length: 8
      
      # Access rules
      access_rules:
        # Time-based
        time_zones:
          - name: "Business Hours"
            days: ["MON", "TUE", "WED", "THU", "FRI"]
            start_time: "08:00"
            end_time: "18:00"
            allow: true
          
          - name: "After Hours"
            days: ["MON", "TUE", "WED", "THU", "FRI"]
            start_time: "18:00"
            end_time: "08:00"
            allow: false
            exceptions:
              - user_role: "executive"
                allow: true
        
        # Anti-passback
        anti_passback:
          enabled: true
          require_exit_scan: true
          forgiveness_time: 300  # 5 minutes
    
    # Main Entrance - NFC/RFID + PIN
    - id: "door_main"
      name: "Main Entrance"
      location: "Ground Floor"
      
      lock:
        type: "magnetic_lock"
        relay_pin: 25
        unlock_duration: 3
      
      authentication:
        # NFC (smartphones, cards)
        nfc:
          enabled: true
          reader:
            type: "acr122u"
            interface: "usb"
            device: "/dev/ttyUSB0"
          card_types:
            - "mifare_desfire"
            - "mifare_plus"
        
        # RFID (legacy cards)
        rfid:
          enabled: true
          reader:
            type: "hid_proxpoint"
            frequency: "125khz"
            interface: "wiegand"
            wiegand:
              data0_pin: 17
              data1_pin: 18
              format: "26bit"
          card_types:
            - "hid_prox"
        
        # PIN pad (backup + temporary access)
        pin_pad:
          enabled: true
          keypad:
            type: "hid_pivclass"
            interface: "wiegand"
          pin:
            min_length: 4
            temporary_pins:
              enabled: true
              max_uses: 1
              max_duration: 86400  # 24 hours
          anti_brute_force:
            max_attempts: 3
            lockout_duration: 300
      
      # Visitor management
      visitor_access:
        enabled: true
        qr_code_access: true  # Visitors get QR code
        escort_required: false
    
    # Server Room - Card + Fingerprint + PIN (3FA)
    - id: "door_server_room"
      name: "Server Room"
      location: "Basement"
      
      lock:
        type: "electric_strike"
        relay_pin: 26
        fail_secure: true
      
      authentication:
        mfa:
          enabled: true
          required_methods: 3  # Highest security
          order: "sequential"  # Must be in order
        
        # Step 1: NFC card
        nfc:
          enabled: true
          weight: 1
        
        # Step 2: Fingerprint
        fingerprint:
          enabled: true
          weight: 1
        
        # Step 3: PIN
        pin_pad:
          enabled: true
          weight: 1
          pin:
            min_length: 6
      
      # Mantrap / Airlock
      mantrap:
        enabled: true
        exit_door: "door_server_room_exit"
        max_occupancy: 1
        require_exit_before_entry: true
  
  # Emergency overrides
  emergency:
    lockdown:
      enabled: true
      pin: "999999"
      lock_all_doors: true
    
    evacuation:
      enabled: true
      pin: "000000"
      unlock_all_doors: true

# User Management
users:
  - id: "user_john_ceo"
    name: "John Smith"
    email: "john@company.com"
    role: "executive"
    
    # Credentials
    credentials:
      # NFC cards
      nfc_cards:
        - card_id: "04:A1:B2:C3:D4:E5:F6"
          card_type: "mifare_desfire"
          issued_date: "2026-01-15"
      
      # RFID cards
      rfid_cards:
        - card_id: "0012345678"
          card_type: "hid_prox"
      
      # Face template (encrypted)
      face_template: "encrypted_base64_template_here"
      
      # Fingerprints
      fingerprints:
        - finger: "left_index"
          template: "encrypted_base64_template_here"
        - finger: "right_index"
          template: "encrypted_base64_template_here"
      
      # PIN codes
      personal_pin: "847392"
    
    # Access permissions
    access:
      doors:
        - "door_executive"
        - "door_main"
        - "door_server_room"
      
      time_zones:
        - "24/7"  # CEO has 24/7 access
  
  - id: "user_jane_it"
    name: "Jane Doe"
    email: "jane@company.com"
    role: "it_admin"
    
    credentials:
      nfc_cards:
        - card_id: "04:B1:C2:D3:E4:F5:A6"
      fingerprints:
        - finger: "right_index"
          template: "encrypted_base64_template_here"
      personal_pin: "652841"
    
    access:
      doors:
        - "door_main"
        - "door_server_room"
      time_zones:
        - "Business Hours"

# Visitor Management
visitors:
  - id: "visitor_123"
    name: "Bob Johnson"
    email: "bob@visitor.com"
    company: "Acme Corp"
    
    # Host (employee)
    host_user_id: "user_jane_it"
    
    # Temporary credentials
    credentials:
      temporary_pin: "394857"
      qr_code: "https://access.company.com/v/394857"
    
    # Access
    access:
      doors:
        - "door_main"
      valid_from: "2026-07-31T09:00:00Z"
      valid_until: "2026-07-31T17:00:00Z"
      max_uses: 2  # Entry + exit
```

---

## API Reference

### Authentication

```http
# Verify access (called by reader/gateway)
POST /api/access-control/authenticate

Request:
{
  "door_id": "door_executive",
  "method": "face_recognition",  // or "nfc", "rfid", "fingerprint", "pin"
  "credential": {
    // For face recognition
    "face_template": "base64_template",
    "photo": "base64_jpeg",
    
    // For NFC/RFID
    "card_id": "04:A1:B2:C3:D4:E5:F6",
    
    // For fingerprint
    "fingerprint_template": "base64_template",
    
    // For PIN
    "pin": "847392"
  },
  "timestamp": "2026-07-31T10:47:00Z"
}

Response (SUCCESS):
{
  "access_granted": true,
  "user": {
    "id": "user_john_ceo",
    "name": "John Smith",
    "role": "executive"
  },
  "mfa_required": true,
  "mfa_remaining_methods": ["fingerprint"],
  "unlock_duration": 5,  // seconds
  "message": "Welcome, John!"
}

Response (DENIED):
{
  "access_granted": false,
  "reason": "invalid_credential",
  "message": "Face not recognized",
  "retry_allowed": true,
  "attempts_remaining": 2
}
```

### User Management

```http
# Enroll user
POST /api/access-control/users

Request:
{
  "name": "John Smith",
  "email": "john@company.com",
  "role": "executive",
  "credentials": {
    "nfc_cards": [
      {"card_id": "04:A1:B2:C3:D4:E5:F6"}
    ],
    "personal_pin": "847392"
  },
  "access": {
    "doors": ["door_executive", "door_main"],
    "time_zones": ["24/7"]
  }
}

Response:
{
  "user_id": "user_john_ceo",
  "enrollment_complete": false,
  "pending_enrollments": [
    "face_recognition",
    "fingerprint"
  ]
}

# Enroll face
POST /api/access-control/users/{user_id}/enroll/face

Request (multipart/form-data):
- photo1: [JPEG file]
- photo2: [JPEG file]
- photo3: [JPEG file]
- photo4: [JPEG file]
- photo5: [JPEG file]

Response:
{
  "success": true,
  "face_template_id": "face_abc123",
  "quality_score": 0.98
}

# Enroll fingerprint
POST /api/access-control/users/{user_id}/enroll/fingerprint

Request:
{
  "finger": "left_index",
  "template": "base64_fingerprint_template",
  "quality_score": 95
}

Response:
{
  "success": true,
  "fingerprint_id": "fp_def456"
}
```

### Visitor Management

```http
# Create visitor pass
POST /api/access-control/visitors

Request:
{
  "visitor_name": "Bob Johnson",
  "visitor_email": "bob@visitor.com",
  "visitor_company": "Acme Corp",
  "host_user_id": "user_jane_it",
  "doors": ["door_main"],
  "valid_from": "2026-07-31T09:00:00Z",
  "valid_until": "2026-07-31T17:00:00Z",
  "access_method": "pin"  // or "qr_code", "temporary_card"
}

Response:
{
  "visitor_id": "visitor_123",
  "temporary_pin": "394857",
  "qr_code_url": "https://access.company.com/v/394857",
  "qr_code_image": "base64_png",
  "instructions": "Show QR code or enter PIN 394857 at main entrance"
}

# Check visitor status
GET /api/access-control/visitors/{visitor_id}

Response:
{
  "visitor_id": "visitor_123",
  "name": "Bob Johnson",
  "status": "active",
  "valid_until": "2026-07-31T17:00:00Z",
  "remaining_uses": 1,
  "last_access": {
    "door_id": "door_main",
    "timestamp": "2026-07-31T09:15:00Z",
    "direction": "entry"
  }
}
```

### Access Logs

```http
# Get access logs
GET /api/access-control/logs?door_id=door_executive&start_date=2026-07-31

Response:
{
  "logs": [
    {
      "log_id": "log_789012",
      "door_id": "door_executive",
      "timestamp": "2026-07-31T10:47:00Z",
      "user_id": "user_john_ceo",
      "user_name": "John Smith",
      "method": "face_recognition",
      "result": "granted",
      "photo": "base64_jpeg",  // If log_photos enabled
      "mfa_completed": true,
      "mfa_methods": ["face_recognition", "fingerprint"]
    },
    {
      "log_id": "log_789013",
      "door_id": "door_executive",
      "timestamp": "2026-07-31T10:48:00Z",
      "user_id": null,
      "method": "face_recognition",
      "result": "denied",
      "reason": "face_not_recognized",
      "photo": "base64_jpeg"
    }
  ],
  "total": 2
}
```

### Emergency Control

```http
# Trigger lockdown
POST /api/access-control/emergency/lockdown

Request:
{
  "pin": "999999",
  "reason": "Security incident",
  "initiated_by": "user_john_ceo"
}

Response:
{
  "success": true,
  "doors_locked": 47,
  "timestamp": "2026-07-31T10:50:00Z"
}

# Trigger evacuation
POST /api/access-control/emergency/evacuation

Request:
{
  "pin": "000000",
  "reason": "Fire alarm",
  "initiated_by": "user_jane_it"
}

Response:
{
  "success": true,
  "doors_unlocked": 47,
  "timestamp": "2026-07-31T10:55:00Z"
}
```

---

## Integration Examples

### Ubiquiti Access + Face Recognition

```yaml
access_control:
  doors:
    - id: "door_front"
      name: "Front Door"
      
      # Ubiquiti Access (card reader)
      ubiquiti_access:
        enabled: true
        host: "192.168.1.100"
        token: "your_unifi_access_token"
        door_id: "door_abc123"
      
      # Add face recognition
      authentication:
        face_recognition:
          enabled: true
          camera:
            type: "hikvision_face"
            ip: "192.168.1.150"
```

### Salto + Fingerprint

```yaml
access_control:
  doors:
    - id: "door_office"
      name: "Office"
      
      # Salto Space (lock system)
      salto:
        enabled: true
        api_url: "https://api.saltospace.com"
        api_key: "your_salto_api_key"
        lock_id: "lock_def456"
      
      # Add fingerprint scanner
      authentication:
        fingerprint:
          enabled: true
          scanner:
            type: "suprema"
            ip: "192.168.1.170"
```

---

## Best Practices

### Security

1. **Use MFA for high-security areas** - Server rooms, vaults, executive offices
2. **Enable liveness detection** - Prevent spoofing with photos/videos
3. **Encrypt all templates** - Face templates, fingerprints stored encrypted
4. **Log all attempts** - Keep audit trail with photos
5. **Rate limiting** - Prevent brute-force attacks on PIN pads
6. **Anti-passback** - Prevent tailgating
7. **Regular audits** - Review access logs monthly

### Privacy

1. **Store templates, not photos** - Delete original photos after enrollment
2. **Encrypt at rest** - AES-256 encryption for all biometric data
3. **Edge processing** - Face recognition on-device, not cloud
4. **GDPR compliance** - Right to delete, data portability
5. **Consent** - Get written consent for biometric enrollment
6. **Retention policy** - Delete logs after 90 days (or as required)

### User Experience

1. **Provide multiple methods** - Don't force single authentication method
2. **Clear feedback** - LED indicators, beeps, display messages
3. **Fast enrollment** - 5 minutes or less per user
4. **Backup methods** - PIN pad if biometric fails
5. **Visitor-friendly** - Easy temporary access via QR code or PIN

### Maintenance

1. **Clean readers regularly** - Fingerprint scanners get dirty
2. **Check cameras** - Ensure proper lighting, angle for face recognition
3. **Update firmware** - Security patches for readers
4. **Test backups** - Ensure PIN pads work if primary method fails
5. **Monitor logs** - Watch for repeated failed attempts

---

## Compliance

### Standards

- **ISO 27001** - Information security management
- **NIST SP 800-63B** - Digital identity guidelines
- **GDPR** - Data protection (EU)
- **CCPA** - Consumer Privacy Act (California)
- **HIPAA** - Healthcare privacy (if applicable)

### Certifications

- **FIPS 140-2** - Cryptographic module validation
- **Common Criteria EAL4+** - Security evaluation
- **UL 294** - Access control system units

---

**For access control integration support:**
- **Email:** access-control@mediacontrol.com
- **Website:** https://mediacontrol.com/access-control
- **Documentation:** https://docs.mediacontrol.com/access-control

**Hardware Vendors:**
- **HID Global:** https://hidglobal.com
- **ASSA ABLOY:** https://assaabloy.com
- **Salto Systems:** https://saltosystems.com
- **Suprema:** https://supremainc.com
- **ZKTeco:** https://zkteco.com
- **Hikvision:** https://hikvision.com