# Guest Room Key - Passive Entry System

**Hands-Free Automatic Door Unlock with Apple Wallet & Google Wallet**

---

## Table of Contents

1. [Overview](#overview)
2. [Passive Entry Technologies](#passive-entry-technologies)
3. [Apple Wallet Passive Entry](#apple-wallet-passive-entry)
4. [Google Wallet Passive Entry](#google-wallet-passive-entry)
5. [BLE (Bluetooth Low Energy) Ranging](#ble-bluetooth-low-energy-ranging)
6. [UWB (Ultra-Wideband) Positioning](#uwb-ultra-wideband-positioning)
7. [Hardware Requirements](#hardware-requirements)
8. [Configuration](#configuration)
9. [Security](#security)
10. [API Reference](#api-reference)

---

## Overview

**Passive Entry** (also called **Hands-Free Entry**) allows guests to unlock doors **automatically** as they approach, without taking their phone out of their pocket or bag.

### Entry Methods Comparison

| Method | User Action | Technology | Range | Accuracy | Use Case |
|--------|-------------|-----------|-------|----------|----------|
| **Tap-to-Unlock (NFC)** | Tap phone on reader | NFC 13.56 MHz | 0-10 cm | N/A | Standard entry |
| **Passive Entry (BLE)** | Walk up to door | Bluetooth 5.0+ | 1-5 meters | ±1-2 m | Hands-free entry |
| **Passive Entry (UWB)** | Walk up to door | Ultra-Wideband | 0-10 meters | ±10 cm | Precise hands-free |
| **PIN Pad** | Enter code | Keypad | N/A | N/A | Backup |

### Passive Entry Features

✅ **Truly hands-free** - Phone stays in pocket/bag  
✅ **Automatic unlock** - Door unlocks as you approach (within 1-2 meters)  
✅ **Ultra-precise** - UWB positioning (10cm accuracy)  
✅ **Secure** - Encrypted BLE/UWB, mutual authentication  
✅ **Fast** - Door unlocks before you reach it  
✅ **Battery-efficient** - BLE uses minimal power  
✅ **Works in background** - No app launch required

### Typical User Experience

**Traditional NFC (Tap-to-Unlock):**
1. Guest approaches door
2. Takes phone out of pocket
3. Taps phone on reader
4. Door unlocks
5. Guest opens door

**Passive Entry (Hands-Free):**
1. Guest approaches door (phone in pocket/bag)
2. **Door unlocks automatically** at 1.5 meters
3. Guest opens door

**Time saved:** 3-5 seconds per entry × 2 entries/day × 365 days = **30-60 minutes/year**

---

## Passive Entry Technologies

### 1. BLE (Bluetooth Low Energy)

**How it works:**
- Phone continuously advertises BLE signal (even when locked)
- Door reader detects phone within range (1-5 meters)
- Reader measures signal strength (RSSI) to estimate distance
- When phone is within unlock radius (e.g., 1.5m), door unlocks

**Advantages:**
- ✅ Works on all modern smartphones (iPhone 5s+, Android 5.0+)
- ✅ Low power consumption
- ✅ No line-of-sight required (works through walls, bags)
- ✅ Standard Bluetooth 5.0+ support

**Limitations:**
- ⚠️ Lower accuracy (±1-2 meters)
- ⚠️ RSSI affected by obstacles, interference
- ⚠️ Cannot distinguish between inside/outside door

### 2. UWB (Ultra-Wideband)

**How it works:**
- Phone sends UWB pulses (3-10 GHz)
- Door reader measures Time-of-Flight (ToF)
- Calculates precise distance (±10cm accuracy)
- Determines direction and angle (AoA - Angle of Arrival)
- Unlocks door only when guest is approaching from outside

**Advantages:**
- ✅ **Ultra-precise** - 10cm accuracy vs. BLE's 1-2m
- ✅ **Directional** - Knows if you're inside or outside
- ✅ **Secure** - Immune to relay attacks
- ✅ **Fast** - Microsecond response time

**Limitations:**
- ⚠️ Requires UWB-capable phone (iPhone 11+, select Android)
- ⚠️ More expensive hardware ($100-200 vs. $20-50 for BLE)

### 3. Hybrid (BLE + UWB)

**Best of both worlds:**
- Use BLE for wake-up (detect phone in range)
- Switch to UWB for precise positioning
- Fallback to BLE if UWB not available

**Advantages:**
- ✅ Universal compatibility (BLE for older phones, UWB for newer)
- ✅ Energy efficient (UWB only active when needed)
- ✅ Precise and secure

---

## Apple Wallet Passive Entry

### Supported Devices

| Device | NFC | BLE | UWB | Express Mode | Power Reserve |
|--------|-----|-----|-----|--------------|---------------|
| **iPhone 15 Pro** | ✅ | ✅ | ✅ U2 chip | ✅ | ✅ 5 hours |
| **iPhone 14 Pro** | ✅ | ✅ | ✅ U1 chip | ✅ | ✅ 5 hours |
| **iPhone 13 Pro** | ✅ | ✅ | ✅ U1 chip | ✅ | ✅ 5 hours |
| **iPhone 12 Pro** | ✅ | ✅ | ✅ U1 chip | ✅ | ✅ 5 hours |
| **iPhone 11 Pro** | ✅ | ✅ | ✅ U1 chip | ✅ | ✅ 5 hours |
| **iPhone X/XS/XR** | ✅ | ✅ | ❌ | ✅ | ✅ 5 hours |
| **Apple Watch Ultra 2** | ✅ | ✅ | ✅ S9 + U2 | ✅ | N/A |
| **Apple Watch Series 9** | ✅ | ✅ | ✅ S9 + U2 | ✅ | N/A |
| **Apple Watch Series 6-8** | ✅ | ✅ | ✅ U1 chip | ✅ | N/A |

### Apple Wallet Features

**Home Keys (for Residential):**
- ✅ **Express Mode** - No Face ID/Touch ID required
- ✅ **Power Reserve** - Works 5 hours after battery dies
- ✅ **UWB Passive Entry** - Hands-free unlock (iPhone 11+)
- ✅ **BLE Passive Entry** - Fallback for older iPhones
- ✅ **Shared Keys** - Share via iMessage, Home app
- ✅ **Offline** - Keys stored locally on device

**Hotel Keys (for Hospitality):**
- ✅ **Express Mode** - Tap-to-unlock without unlocking phone
- ⚠️ **Limited Passive Entry** - Only some hotel lock systems support UWB
- ✅ **Auto-Archive** - Keys archived after check-out
- ✅ **Multi-Room** - Single pass for multiple rooms

### Implementation

**For Home Keys (Residential):**
```swift
// iOS/Swift code for Apple Home Key integration

import HomeKit

// Add lock accessory
let lockAccessory = HMAccessory()
lockAccessory.category = .lock

// Configure UWB passive entry
let service = lockAccessory.services.first(where: { $0.serviceType == HMServiceTypeLockMechanism })

// Enable passive entry
let passiveEntryCharacteristic = HMCharacteristic()
passiveEntryCharacteristic.characteristicType = HMCharacteristicTypePassiveEntry
passiveEntryCharacteristic.value = true

// Set unlock radius (meters)
let unlockRadiusCharacteristic = HMCharacteristic()
unlockRadiusCharacteristic.characteristicType = HMCharacteristicTypeUnlockRadius
unlockRadiusCharacteristic.value = 1.5  // Unlock at 1.5 meters

// Set UWB ranging mode
let rangingModeCharacteristic = HMCharacteristic()
rangingModeCharacteristic.characteristicType = HMCharacteristicTypeRangingMode
rangingModeCharacteristic.value = "uwb"  // or "ble"
```

**For Hotel Keys (Hospitality):**
```json
// Apple Wallet Pass (PKPass) for hotel room key

{
  "formatVersion": 1,
  "passTypeIdentifier": "pass.com.yourhotel.roomkey",
  "serialNumber": "ROOM-2201-123456",
  "teamIdentifier": "YOUR_TEAM_ID",
  "organizationName": "Grand Luxury Hotel",
  
  "nfc": {
    "message": "Room 2201 Key",
    "encryptionPublicKey": "BASE64_PUBLIC_KEY",
    "requiresAuthentication": false
  },
  
  "passiveEntry": {
    "enabled": true,
    "technology": "uwb",  // or "ble"
    "unlockRadius": 1.5,  // meters
    "direction": "approach"  // only unlock when approaching
  },
  
  "beacons": [
    {
      "proximityUUID": "YOUR_UUID",
      "major": 2201,  // Room number
      "minor": 1,
      "relevantText": "Room 2201 - Tap to unlock"
    }
  ]
}
```

---

## Google Wallet Passive Entry

### Supported Devices

| Device | NFC | BLE | UWB | Passive Entry |
|--------|-----|-----|-----|---------------|
| **Pixel 8 Pro** | ✅ | ✅ | ✅ | ✅ BLE + UWB |
| **Pixel 7 Pro** | ✅ | ✅ | ❌ | ✅ BLE only |
| **Samsung Galaxy S24 Ultra** | ✅ | ✅ | ✅ | ✅ BLE + UWB |
| **Samsung Galaxy S23 Ultra** | ✅ | ✅ | ✅ | ✅ BLE + UWB |
| **Most Android 10+ devices** | ✅ | ✅ | ❌ | ✅ BLE only |

### Google Wallet Features

**Digital Keys:**
- ✅ **Fast Pair** - Automatic provisioning
- ✅ **Passive Entry** - BLE-based hands-free unlock
- ✅ **Smart Lock** - Keep phone unlocked near lock
- ✅ **Guest Access** - Share keys via link
- ✅ **Offline** - Keys stored locally on device

### Implementation

**For Smart Locks (Residential):**
```kotlin
// Android/Kotlin code for Google Wallet Digital Key

import com.google.android.gms.nearby.Nearby
import com.google.android.gms.nearby.connection.*

// Enable BLE advertising
val advertisingOptions = AdvertisingOptions.Builder()
    .setStrategy(Strategy.P2P_CLUSTER)
    .build()

Nearby.getConnectionsClient(context)
    .startAdvertising(
        "Room2201Key",
        SERVICE_ID,
        connectionLifecycleCallback,
        advertisingOptions
    )

// Configure passive entry
val passiveEntryConfig = PassiveEntryConfig.Builder()
    .setUnlockRadius(1.5f)  // meters
    .setTechnology(Technology.BLE)  // or Technology.UWB
    .setDirection(Direction.APPROACHING)
    .build()

// Listen for proximity events
val proximityCallback = object : ProximityCallback() {
    override fun onDistanceChanged(distance: Float) {
        if (distance <= passiveEntryConfig.unlockRadius) {
            unlockDoor()
        }
    }
}
```

**For Hotel Keys:**
```json
// Google Wallet Pass Object with Passive Entry

{
  "classId": "hotel.room.key.YOUR_HOTEL",
  "id": "ROOM_2201_123456",
  "state": "ACTIVE",
  
  "smartTapRedemptionValue": "ENCRYPTED_NFC_DATA",
  
  "passiveEntry": {
    "enabled": true,
    "technology": "ble",  // or "uwb", "hybrid"
    "unlockRadius": 1.5,
    "rssiThreshold": -60,  // Signal strength for unlock
    "direction": "approach"
  },
  
  "locations": [
    {
      "latitude": 37.4220,
      "longitude": -122.0841,
      "kind": "walletobjects#latLongPoint"
    }
  ],
  
  "appLinkData": {
    "androidAppLinkInfo": {
      "appTarget": {
        "targetUri": {
          "uri": "https://yourhotel.com/room/2201",
          "description": "Room 2201"
        }
      }
    }
  }
}
```

---

## BLE (Bluetooth Low Energy) Ranging

### How BLE Ranging Works

**1. Advertising:**
```
iPhone/Android (in pocket)
    ↓
Continuously advertises BLE beacon
    - UUID: Unique to guest/room
    - RSSI: Signal strength (updates every 100ms)
    ↓
Door Lock BLE Reader (always listening)
```

**2. Ranging:**
```
Door Lock calculates distance from RSSI:
    RSSI = -40 dBm  →  ~0.5 meters (very close)
    RSSI = -60 dBm  →  ~1.5 meters (unlock range)
    RSSI = -80 dBm  →  ~5 meters (detection range)
    RSSI < -90 dBm  →  Out of range
```

**3. Unlock Logic:**
```
IF guest_authenticated AND distance <= 1.5m:
    unlock_door()
    
ELSE IF distance <= 5m:
    wake_up_lock()  # Prepare for unlock
    
ELSE:
    sleep()  # Save power
```

### BLE Configuration

```yaml
passive_entry:
  ble:
    enabled: true
    
    # Beacon settings
    beacon:
      uuid: "12345678-1234-1234-1234-123456789012"
      major: 2201  # Room number
      minor: 1
      tx_power: -59  # Calibrated RSSI at 1 meter
    
    # Ranging settings
    ranging:
      detection_radius: 5.0  # meters (wake up lock)
      unlock_radius: 1.5  # meters (unlock door)
      rssi_threshold: -60  # dBm (corresponds to ~1.5m)
      
      # RSSI smoothing (reduce jitter)
      smoothing:
        enabled: true
        window_size: 10  # Average last 10 readings
        min_readings: 5  # Require 5 consecutive readings
    
    # Security
    security:
      mutual_authentication: true
      encryption: "aes128"
      rotating_uuid: true  # Change UUID every 15 minutes
      mac_address_randomization: true
    
    # Power management
    power:
      advertising_interval: 100  # ms
      scan_interval: 1000  # ms (lock scans every 1 second)
      duty_cycle: 0.1  # 10% active, 90% sleep
```

### RSSI-to-Distance Conversion

**Formula:**
```python
def rssi_to_distance(rssi: float, tx_power: float = -59, n: float = 2.0) -> float:
    """
    Convert RSSI to distance in meters
    
    Args:
        rssi: Received Signal Strength Indicator (dBm)
        tx_power: Calibrated RSSI at 1 meter (dBm)
        n: Path loss exponent (2.0 = free space, 2.5-4.0 = indoor)
    
    Returns:
        Distance in meters
    """
    return 10 ** ((tx_power - rssi) / (10 * n))

# Examples:
rssi_to_distance(-40)  # → 0.4 meters
rssi_to_distance(-60)  # → 1.6 meters
rssi_to_distance(-80)  # → 6.3 meters
```

---

## UWB (Ultra-Wideband) Positioning

### How UWB Works

**1. Time-of-Flight (ToF) Measurement:**
```
iPhone (UWB transmitter)
    ↓
Sends UWB pulse (3-10 GHz)
    ↓
Door Lock (UWB receiver)
    ↓
Measures time-of-arrival (ToA)
    ↓
Calculates distance:
    Distance = (ToA × Speed of Light) / 2
    
Accuracy: ±10 cm (vs. BLE's ±1-2 meters)
```

**2. Angle of Arrival (AoA):**
```
Door Lock (multiple UWB antennas)
    ↓
Measures phase difference between antennas
    ↓
Calculates angle (direction) of phone
    ↓
Determines if guest is approaching or leaving
    
Example:
    Angle = 90° (front) → Approaching → Unlock
    Angle = 270° (back) → Leaving → Stay locked
```

**3. Secure Ranging:**
```
iPhone ←→ Door Lock
    ↓
Mutual authentication (challenge-response)
    ↓
Encrypted UWB pulses (AES-128)
    ↓
Prevents relay attacks
```

### UWB Configuration

```yaml
passive_entry:
  uwb:
    enabled: true
    
    # UWB ranging
    ranging:
      frequency: 6489.6  # MHz (Channel 5)
      bandwidth: 499.2  # MHz
      prf: 64  # Pulse Repetition Frequency (MHz)
      
      detection_radius: 10.0  # meters
      unlock_radius: 1.5  # meters
      accuracy: 0.1  # ±10 cm
    
    # Angle of Arrival (AoA)
    aoa:
      enabled: true
      antenna_array: "2x2"  # 4 antennas for precise angle
      approach_angle: 90  # degrees (0-180, front of door)
      approach_tolerance: 45  # ±45 degrees
    
    # Security
    security:
      mutual_authentication: true
      encryption: "aes128"
      secure_ranging: true  # IEEE 802.15.4z
      scrambled_timestamp: true  # Prevent ToF spoofing
    
    # Fallback
    fallback:
      enable_ble: true  # Use BLE if UWB unavailable
      enable_nfc: true  # Use NFC tap if ranging fails
```

### UWB vs. BLE Comparison

| Feature | BLE | UWB |
|---------|-----|-----|
| **Accuracy** | ±1-2 meters | ±10 cm |
| **Update Rate** | 1-10 Hz | 100+ Hz |
| **Range** | 1-50 meters | 0-200 meters |
| **Direction** | ❌ No | ✅ Yes (AoA) |
| **Through Walls** | ✅ Yes | ⚠️ Limited |
| **Power** | Very Low | Low |
| **Cost** | $20-50 | $100-200 |
| **Phone Support** | All (2015+) | iPhone 11+, select Android |

---

## Hardware Requirements

### BLE-Based Passive Entry

**Minimum Requirements:**
- **BLE Reader** - Bluetooth 5.0+ with ranging support
- **Lock Controller** - Electric strike or magnetic lock
- **Power** - PoE (Power over Ethernet) or 12V DC
- **Processing** - Raspberry Pi 4 or equivalent (for RSSI calculation)

**Recommended Hardware:**

| Component | Model | Price | Features |
|-----------|-------|-------|----------|
| **BLE Reader** | Nordic nRF52840 | $10-20 | BLE 5.3, -95 dBm sensitivity, direction finding |
| **Lock** | Assa Abloy Aperio | $200-300 | BLE + NFC, battery or wired |
| **Controller** | Raspberry Pi 4 | $35-75 | Quad-core, WiFi, BLE, GPIO |
| **Complete System** | Salto Space BLE Lock | $300-400 | Integrated BLE + NFC + mobile key support |

### UWB-Based Passive Entry

**Minimum Requirements:**
- **UWB Module** - DWM3000 (Qorvo/Decawave) or equivalent
- **Antenna Array** - 2-4 antennas for AoA (Angle of Arrival)
- **Lock Controller** - Electric strike or magnetic lock
- **Processing** - More powerful CPU for ToF calculation
- **Power** - PoE or 12V DC

**Recommended Hardware:**

| Component | Model | Price | Features |
|-----------|-------|-------|----------|
| **UWB Module** | Qorvo DWM3000 | $30-50 | IEEE 802.15.4z, secure ranging, AoA support |
| **Antenna Array** | 4-element array | $20-40 | Precise AoA calculation |
| **Lock** | Assa Abloy Aperio UWB | $400-600 | Integrated UWB + BLE + NFC |
| **Controller** | Raspberry Pi 4 or CM4 | $35-100 | Sufficient for UWB processing |
| **Complete System** | Apple Home Key lock (Level, Schlage, Yale) | $200-400 | Native Apple Wallet support with UWB |

### Integrated Solutions

**Best options for hotels/residences:**

**1. Salto Space (BLE + NFC):**
- ✅ Native mobile key support
- ✅ Apple Wallet + Google Wallet
- ✅ BLE passive entry (1-5m range)
- ✅ PMS integration (OPERA Cloud, Protel, Mews)
- 💰 $300-500 per lock

**2. Assa Abloy Aperio (BLE + UWB + NFC):**
- ✅ BLE + UWB passive entry
- ✅ Apple Wallet Home Keys (UWB)
- ✅ Multiple credential types
- ✅ Enterprise-grade security
- 💰 $400-700 per lock

**3. DIY MediaControl Gateway:**
- ✅ Raspberry Pi 4 + BLE/UWB module
- ✅ Custom implementation
- ✅ Full control over ranging logic
- ✅ Integration with existing locks
- 💰 $100-200 per lock (hardware only)

---

## Configuration

### Complete Configuration Example

```yaml
# MediaControl Passive Entry Configuration

passive_entry:
  enabled: true
  
  # Entry mode
  mode: "hybrid"  # "ble_only", "uwb_only", "hybrid"
  
  # BLE Configuration
  ble:
    enabled: true
    
    # Hardware
    adapter: "hci0"  # Bluetooth adapter
    
    # Beacon settings
    beacon:
      uuid: "12345678-1234-1234-1234-123456789012"
      tx_power: -59  # Calibrated RSSI at 1 meter (dBm)
    
    # Ranging
    ranging:
      detection_radius: 5.0  # meters (wake up lock)
      unlock_radius: 1.5  # meters (unlock door)
      lock_radius: 3.0  # meters (lock door when guest leaves)
      
      # RSSI to distance conversion
      rssi_threshold: -60  # dBm
      path_loss_exponent: 2.5  # 2.0 = free space, 2.5-4.0 = indoor
      
      # RSSI smoothing
      smoothing:
        enabled: true
        method: "moving_average"  # or "kalman_filter", "exponential"
        window_size: 10  # Average last N readings
        min_readings: 5  # Require N consecutive readings before unlock
    
    # Timeout
    timeout:
      unlock_timeout: 10  # seconds (door unlocks for 10s)
      relock_delay: 5  # seconds (wait 5s before relocking)
      retry_interval: 1  # seconds (check distance every 1s)
  
  # UWB Configuration
  uwb:
    enabled: true
    
    # Hardware
    module: "dwm3000"  # Qorvo/Decawave DWM3000
    spi_device: "/dev/spidev0.0"
    
    # Ranging
    ranging:
      channel: 5  # UWB channel (5 = 6489.6 MHz)
      prf: 64  # Pulse Repetition Frequency (MHz)
      
      detection_radius: 10.0  # meters
      unlock_radius: 1.5  # meters
      accuracy: 0.1  # ±10 cm
      update_rate: 100  # Hz
    
    # Angle of Arrival (AoA)
    aoa:
      enabled: true
      antenna_array:
        type: "2x2"  # 4 antennas
        spacing: 0.05  # meters (5 cm between antennas)
      
      # Only unlock when approaching from front
      approach_angle: 90  # degrees (0 = right, 90 = front, 180 = left)
      approach_tolerance: 45  # ±45 degrees
    
    # Security
    security:
      secure_ranging: true  # IEEE 802.15.4z
      scrambled_timestamp: true
      mutual_authentication: true
  
  # Fallback
  fallback:
    # If passive entry fails, allow these methods
    allow_nfc_tap: true
    allow_pin_code: true
    
    # If UWB unavailable, use BLE
    uwb_to_ble: true
    
    # If BLE unavailable, use NFC only
    ble_to_nfc: true
  
  # Security
  security:
    # Credential rotation
    rotate_credentials: true
    rotation_interval: 900  # 15 minutes
    
    # Anti-replay
    anti_replay: true
    nonce_window: 60  # seconds
    
    # Rate limiting
    rate_limit:
      enabled: true
      max_unlock_attempts: 10  # per hour
      lockout_duration: 3600  # 1 hour
  
  # Notifications
  notifications:
    # Notify guest when door unlocks
    notify_on_unlock: true
    notification_method: "push"  # or "sms", "email"
    
    # Notify host of guest activity
    notify_host: false
  
  # Logging
  logging:
    log_ranging_events: true
    log_unlock_events: true
    log_failed_attempts: true
    retention_days: 90


# Doors with passive entry
doors:
  - id: "door_room_2201"
    name: "Guest Room 2201"
    location: "Floor 22"
    
    # Lock hardware
    lock:
      type: "electric_strike"
      relay_pin: 23
      unlock_duration: 5
    
    # Passive entry
    passive_entry:
      enabled: true
      mode: "hybrid"  # Try UWB first, fallback to BLE
      
      # BLE settings (specific to this door)
      ble:
        beacon:
          major: 2201  # Room number
          minor: 1
        unlock_radius: 1.5  # meters
      
      # UWB settings (specific to this door)
      uwb:
        unlock_radius: 1.5  # meters
        approach_angle: 90  # Front of door
    
    # Authorized credentials
    authorized_credentials:
      - credential_id: "guest_john_wallet_key"
        credential_type: "apple_wallet"
        user_id: "guest_john_2201"
        valid_from: "2026-07-31T15:00:00Z"
        valid_until: "2026-08-03T12:00:00Z"
      
      - credential_id: "guest_jane_wallet_key"
        credential_type: "google_wallet"
        user_id: "guest_jane_2201"
        valid_from: "2026-07-31T15:00:00Z"
        valid_until: "2026-08-03T12:00:00Z"


# Guests/Users
users:
  - id: "guest_john_2201"
    name: "John Smith"
    email: "john@example.com"
    role: "guest"
    
    # Apple Wallet credential
    credentials:
      apple_wallet:
        credential_id: "guest_john_wallet_key"
        uuid: "87654321-4321-4321-4321-210987654321"
        device_id: "iPhone-John"
        
        # Passive entry
        passive_entry:
          enabled: true
          ble_mac_address: "AA:BB:CC:DD:EE:FF"
          uwb_device_id: "UWB-iPhone-John"
    
    # Access
    access:
      doors: ["door_room_2201"]
      check_in: "2026-07-31T15:00:00Z"
      check_out: "2026-08-03T12:00:00Z"
```

---

## Security

### Threat Model

**Threats:**
1. **Relay Attack** - Attacker relays signal from guest's phone to door
2. **Replay Attack** - Attacker captures and replays unlock signal
3. **MITM Attack** - Attacker intercepts communication
4. **Unauthorized Unlock** - Guest's phone unlocks wrong door
5. **Tracking** - Attacker tracks guest via BLE/UWB signals

### Security Measures

**1. Mutual Authentication:**
```
Phone                          Door Lock
  |                                |
  |--- Challenge (Nonce) -------->|
  |                                |
  |<-- Challenge (Nonce) ---------|
  |                                |
  |--- Response (Signed) -------->|
  |                                |
  |<-- Response (Signed) ---------|
  |                                |
  |--- Unlock Request ----------->|
  |                                |
  |<-- Unlock Confirmed -----------|
```

**2. Secure Ranging (UWB):**
- ✅ IEEE 802.15.4z standard
- ✅ Scrambled timestamp sequence (STS)
- ✅ Encrypted ToF measurements
- ✅ Prevents distance spoofing

**3. Credential Rotation:**
```python
# Rotate BLE UUID every 15 minutes
def rotate_ble_uuid(original_uuid: str, timestamp: int) -> str:
    """
    Generate time-based rotating UUID
    Both phone and lock know the rotation algorithm
    """
    rotation_key = hmac_sha256(original_uuid, timestamp // 900)  # 900s = 15min
    return uuid5(original_uuid, rotation_key)

# Example:
# 10:00 AM → UUID: 12345678-1234-1234-1234-123456789012
# 10:15 AM → UUID: 87654321-4321-4321-4321-210987654321
# 10:30 AM → UUID: ABCDEF01-2345-6789-ABCD-EF0123456789
```

**4. Anti-Replay:**
- ✅ Include nonce (random number) in every message
- ✅ Door lock tracks used nonces for 60 seconds
- ✅ Reject duplicate nonces

**5. Privacy:**
- ✅ **MAC Address Randomization** - Phone changes BLE MAC every 15 minutes
- ✅ **Encrypted Advertising** - BLE payload encrypted
- ✅ **No Personal Data** - UUID doesn't contain guest name/room number
- ✅ **Local Processing** - No cloud communication during unlock

**6. Zone Restriction:**
```python
# Only unlock if phone is within correct zone
def check_zone(phone_location: tuple, door_location: tuple) -> bool:
    """
    Ensure phone is near the correct door
    Prevents unlocking wrong door in same building
    """
    distance = calculate_distance(phone_location, door_location)
    return distance <= 10.0  # Within 10 meters
```

**7. Direction Detection (UWB Only):**
```python
# Only unlock if approaching from outside
def check_approach_direction(angle: float, door_front_angle: float = 90.0) -> bool:
    """
    Check if guest is approaching from front of door
    Angle: 0° = right, 90° = front, 180° = left, 270° = back
    """
    angle_diff = abs(angle - door_front_angle)
    return angle_diff <= 45.0  # Within ±45° of front
```

---

## API Reference

### Passive Entry APIs

```http
# Enable passive entry for a guest
POST /api/passive-entry/enable

Request:
{
  "user_id": "guest_john_2201",
  "door_id": "door_room_2201",
  "credential_type": "apple_wallet",  // or "google_wallet"
  "ble_mac_address": "AA:BB:CC:DD:EE:FF",
  "uwb_device_id": "UWB-iPhone-John",
  "unlock_radius": 1.5,  // meters
  "valid_from": "2026-07-31T15:00:00Z",
  "valid_until": "2026-08-03T12:00:00Z"
}

Response:
{
  "passive_entry_id": "pe_abc123",
  "status": "enabled",
  "mode": "hybrid",  // UWB + BLE
  "unlock_radius": 1.5,
  "technologies": ["uwb", "ble", "nfc"]
}

# Disable passive entry
DELETE /api/passive-entry/{passive_entry_id}

# Get passive entry status
GET /api/passive-entry/{passive_entry_id}

Response:
{
  "passive_entry_id": "pe_abc123",
  "user_id": "guest_john_2201",
  "door_id": "door_room_2201",
  "status": "active",
  "last_seen": "2026-07-31T15:45:30Z",
  "distance": 2.3,  // meters (current distance)
  "technology": "uwb",  // Currently using UWB
  "unlock_count": 5,  // Times unlocked today
  "battery_status": "normal"  // Phone battery level
}

# Get ranging data (real-time)
GET /api/passive-entry/{passive_entry_id}/ranging

Response:
{
  "distance": 1.8,  // meters
  "rssi": -58,  // dBm (BLE)
  "angle": 85,  // degrees (UWB AoA)
  "technology": "uwb",
  "accuracy": 0.1,  // meters
  "update_rate": 100,  // Hz
  "timestamp": "2026-07-31T15:45:35.123Z"
}

# Unlock events log
GET /api/passive-entry/logs?door_id=door_room_2201

Response:
{
  "logs": [
    {
      "log_id": "log_789012",
      "door_id": "door_room_2201",
      "user_id": "guest_john_2201",
      "timestamp": "2026-07-31T15:45:35Z",
      "technology": "uwb",
      "distance": 1.4,  // meters
      "angle": 88,  // degrees
      "unlock_duration": 5,  // seconds
      "battery_level": 85  // %
    },
    {
      "log_id": "log_789013",
      "door_id": "door_room_2201",
      "user_id": "guest_john_2201",
      "timestamp": "2026-07-31T18:20:15Z",
      "technology": "ble",  // UWB failed, used BLE
      "distance": 1.6,
      "rssi": -59,
      "unlock_duration": 5
    }
  ]
}
```

### Apple Wallet Integration

```http
# Issue Apple Wallet pass with passive entry
POST /api/hospitality/digital-keys/issue-apple-wallet

Request:
{
  "guest": {
    "name": "John Smith",
    "email": "john@example.com",
    "device_id": "iPhone-John"
  },
  "reservation": {
    "room_number": "2201",
    "check_in": "2026-07-31T15:00:00Z",
    "check_out": "2026-08-03T12:00:00Z"
  },
  "passive_entry": {
    "enabled": true,
    "technologies": ["uwb", "ble"],  // Prefer UWB, fallback to BLE
    "unlock_radius": 1.5
  }
}

Response:
{
  "pass_url": "https://wallet-pass.yourhotel.com/abc123",
  "pass_type_id": "pass.com.yourhotel.roomkey",
  "serial_number": "ROOM-2201-123456",
  "passive_entry": {
    "uuid": "12345678-1234-1234-1234-123456789012",
    "major": 2201,
    "minor": 1,
    "unlock_radius": 1.5,
    "technologies": ["uwb", "ble", "nfc"]
  }
}
```

### Google Wallet Integration

```http
# Issue Google Wallet pass with passive entry
POST /api/hospitality/digital-keys/issue-google-wallet

Request:
{
  "guest": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "device_id": "Pixel-Jane"
  },
  "reservation": {
    "room_number": "2201",
    "check_in": "2026-07-31T15:00:00Z",
    "check_out": "2026-08-03T12:00:00Z"
  },
  "passive_entry": {
    "enabled": true,
    "technology": "ble",  // Android typically uses BLE
    "unlock_radius": 1.5
  }
}

Response:
{
  "pass_url": "https://pay.google.com/gp/v/pass/abc123",
  "class_id": "hotel.room.key.YOUR_HOTEL",
  "object_id": "ROOM_2201_123456",
  "passive_entry": {
    "uuid": "12345678-1234-1234-1234-123456789012",
    "unlock_radius": 1.5,
    "rssi_threshold": -60,
    "technology": "ble"
  }
}
```

---

## Implementation Notes

### Battery Impact

**BLE:**
- ✅ Very low power (1-5 mW)
- ✅ ~0.1% battery drain per day
- ✅ Can run for weeks on single charge

**UWB:**
- ⚠️ Higher power (10-50 mW when active)
- ⚠️ ~0.5-1% battery drain per day
- ✅ Only active when near door (duty cycling)

**Optimization:**
1. Use BLE for wake-up (low power)
2. Activate UWB only when BLE detects phone nearby
3. Turn off UWB after unlock
4. Duty cycle: 90% sleep, 10% active

### User Experience

**Best Practices:**
1. **Clear signage** - "Passive Entry Enabled - Walk up to door"
2. **LED feedback** - Green LED when door unlocks
3. **Audio feedback** - Beep when door unlocks
4. **Notification** - Phone shows "Room 2201 Unlocked"
5. **Fallback** - NFC reader visible for tap-to-unlock

### Troubleshooting

**Issue: Door doesn't unlock automatically**
- Check phone Bluetooth is enabled
- Check app has location permissions (required for BLE ranging)
- Verify passive entry is enabled in settings
- Try tap-to-unlock (NFC) as fallback

**Issue: Door unlocks too early/late**
- Adjust `unlock_radius` in configuration
- Calibrate `tx_power` for accurate RSSI-to-distance
- Check for RF interference (WiFi, microwave)

**Issue: UWB not working**
- Verify phone has UWB chip (iPhone 11+)
- Check UWB is enabled in phone settings
- Fallback to BLE if UWB unavailable

---

**For passive entry integration support:**
- **Email:** passive-entry@mediacontrol.com
- **Website:** https://mediacontrol.com/passive-entry
- **Documentation:** https://docs.mediacontrol.com/passive-entry

**Hardware Vendors:**
- **Salto Systems:** https://saltosystems.com (BLE + NFC)
- **Assa Abloy:** https://assaabloy.com (UWB + BLE + NFC)
- **Qorvo (DWM3000):** https://qorvo.com (UWB modules)
- **Nordic Semiconductor (nRF52840):** https://nordicsemi.com (BLE modules)