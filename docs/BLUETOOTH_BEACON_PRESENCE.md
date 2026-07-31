# Bluetooth Beacon Proximity & Presence Detection

**Room-Level Location Tracking and Automated Actions**

---

## Table of Contents

1. [Overview](#overview)
2. [Beacon Types](#beacon-types)
3. [Proximity Zones](#proximity-zones)
4. [Presence Detection](#presence-detection)
5. [Use Cases](#use-cases)
6. [Hardware Requirements](#hardware-requirements)
7. [Configuration](#configuration)
8. [API Reference](#api-reference)

---

## Overview

**Bluetooth beacons** are small, battery-powered devices that continuously broadcast their identity. By deploying beacons in each room and scanning for them with smartphones/gateways, you can:

- ✅ **Detect proximity** - Know when a guest/staff is near a room
- ✅ **Detect presence** - Know if someone is currently in a room
- ✅ **Track location** - Know which room a person is in
- ✅ **Trigger automation** - Unlock doors, turn on lights, adjust HVAC automatically
- ✅ **Monitor occupancy** - Know which rooms are occupied for housekeeping
- ✅ **Track assets** - Locate housekeeping carts, equipment, wheelchairs
- ✅ **Staff accountability** - Verify staff visited assigned rooms

---

## Beacon Types

### 1. iBeacon (Apple)

**Format:**
```
UUID: 550e8400-e29b-41d4-a716-446655440000
Major: 1 (building/floor)
Minor: 2201 (room number)
TX Power: -59 dBm (calibrated at 1 meter)
```

**Best for:**
- Apple ecosystem (iPhone, iPad, Apple Watch)
- Passive entry integration
- Apple HomeKit integration

**Example:**
```yaml
beacon:
  type: "ibeacon"
  uuid: "550e8400-e29b-41d4-a716-446655440000"
  major: 22  # Floor 22
  minor: 2201  # Room 2201
  tx_power: -59
```

### 2. Eddystone (Google)

**Formats:**

**Eddystone-UID** (Unique ID):
```
Namespace: AA BB CC DD EE FF 11 22 33 44
Instance: 00 00 00 00 22 01 (room 2201)
TX Power: -59 dBm
```

**Eddystone-URL** (Physical Web):
```
URL: https://hotel.com/room/2201
TX Power: -59 dBm
```

**Eddystone-TLM** (Telemetry):
```
Battery voltage: 3000 mV
Temperature: 22°C
Packet count: 12345
Uptime: 86400 seconds
```

**Best for:**
- Android ecosystem
- Chrome browser integration
- Battery monitoring (TLM)

**Example:**
```yaml
beacon:
  type: "eddystone"
  frames:
    - type: "uid"
      namespace: "AABBCCDDEEFF11223344"
      instance: "000000002201"
      tx_power: -59
    
    - type: "url"
      url: "https://hotel.com/room/2201"
      tx_power: -59
    
    - type: "tlm"
      broadcast_interval: 60  # seconds
```

### 3. AltBeacon (Open Standard)

**Format:**
```
Organization ID: 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
Beacon ID: 00 16 (major 22) 08 99 (minor 2201)
TX Power: -59 dBm
```

**Best for:**
- Cross-platform (iOS + Android)
- Custom applications
- Open source projects

**Example:**
```yaml
beacon:
  type: "altbeacon"
  organization_id: "000102030405060708090A0B0C0D0E0F"
  beacon_id: "00160899"  # major 22, minor 2201
  tx_power: -59
```

---

## Proximity Zones

**RSSI (Received Signal Strength Indicator) determines distance:**

| Zone | RSSI Range | Distance | Description |
|------|------------|----------|-------------|
| **Immediate** | -30 to -59 dBm | < 1 meter | Right next to beacon (touching door) |
| **Near** | -60 to -70 dBm | 1-3 meters | Inside room or very close to door |
| **Far** | -71 to -90 dBm | 3-10 meters | In hallway near room |
| **Unknown** | < -90 dBm | > 10 meters | Too far, signal lost |

### RSSI to Distance Conversion

**Formula:**
```python
distance = 10 ^ ((tx_power - rssi) / (10 * path_loss_exponent))

Where:
- tx_power = Calibrated RSSI at 1 meter (typically -59 dBm)
- rssi = Measured RSSI (e.g., -65 dBm)
- path_loss_exponent = 2.0 (free space), 2.5-4.0 (indoor)
```

**Example:**
```python
# Beacon calibrated at -59 dBm (1 meter)
# Phone receives -65 dBm
# Path loss exponent = 3.0 (typical hotel hallway)

distance = 10 ^ ((-59 - (-65)) / (10 * 3.0))
distance = 10 ^ (6 / 30)
distance = 10 ^ 0.2
distance = 1.58 meters
```

### RSSI Smoothing (Kalman Filter)

**Raw RSSI is noisy** - fluctuates ±10 dBm even when stationary.

**Solution:** Apply Kalman filter for smoothing.

```python
class RSSIKalmanFilter:
    def __init__(self, process_variance=0.01, measurement_variance=4.0):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_rssi = None
        self.error_covariance = 1.0
    
    def update(self, measured_rssi):
        if self.estimated_rssi is None:
            self.estimated_rssi = measured_rssi
            return measured_rssi
        
        # Prediction
        prediction = self.estimated_rssi
        prediction_covariance = self.error_covariance + self.process_variance
        
        # Update
        kalman_gain = prediction_covariance / (prediction_covariance + self.measurement_variance)
        self.estimated_rssi = prediction + kalman_gain * (measured_rssi - prediction)
        self.error_covariance = (1 - kalman_gain) * prediction_covariance
        
        return self.estimated_rssi

# Usage
filter = RSSIKalmanFilter()
smoothed_rssi = filter.update(-65)  # -65 dBm
smoothed_rssi = filter.update(-70)  # -67.5 dBm (smoothed)
smoothed_rssi = filter.update(-63)  # -65.8 dBm (smoothed)
```

---

## Presence Detection

### Enter/Exit Events

**Enter Event:**
```
Trigger: RSSI crosses from "Far" to "Near" (or "Immediate")
Actions:
- Log entry timestamp
- Trigger automation (lights on, HVAC to occupied mode)
- Send notification ("John Smith entered Room 2201")
- Update occupancy status
```

**Exit Event:**
```
Trigger: RSSI crosses from "Near" to "Far" (or "Unknown")
+ No signal for 30 seconds (debounce)
Actions:
- Log exit timestamp
- Calculate dwell time
- Trigger automation (lights off, HVAC to eco mode)
- Send notification ("John Smith left Room 2201")
- Update occupancy status
```

### Dwell Time Tracking

**Track how long someone stays in a room:**

```python
presence_event = {
    "user_id": "guest_john_smith",
    "room_number": "2201",
    "entered_at": "2026-07-31T14:30:00Z",
    "exited_at": "2026-07-31T16:45:00Z",
    "dwell_time_seconds": 8100,  # 2 hours 15 minutes
    "dwell_time_formatted": "2h 15m"
}
```

**Use cases:**
- **Housekeeping:** Track time spent cleaning each room (should be ~30 min)
- **Guests:** Track room usage patterns (mostly in room vs. mostly out)
- **Maintenance:** Verify technician spent adequate time on repair
- **VIPs:** Alert staff when VIP returns to room

### Multi-Beacon Triangulation

**Deploy 3+ beacons per room for accurate positioning:**

```
Room 2201:
    Beacon 1 (Near door):     RSSI = -62 dBm → 1.2 meters
    Beacon 2 (Near window):   RSSI = -75 dBm → 3.5 meters
    Beacon 3 (Near bathroom): RSSI = -80 dBm → 5.0 meters
    
    → Person is near door (1.2m from Beacon 1)
```

**Benefits:**
- More accurate positioning (±0.5-1m vs. ±2-3m)
- Detect which area of room (near bed, near desk, near bathroom)
- Reduce false positives from hallway

---

## Use Cases

### 1. Guest Room Entry (Automatic Unlock + Welcome)

**Scenario:** Guest approaches their room

```yaml
automation:
  - trigger:
      platform: "bluetooth_beacon"
      beacon_id: "room_2201_beacon"
      user: "guest_john_smith"
      zone: "immediate"  # Within 1 meter (at door)
    
    condition:
      - guest_checked_in: true
      - key_active: true
      - time_after: "15:00"  # After check-in time
    
    actions:
      - service: "door_lock.unlock"
        data:
          room: "2201"
          duration: 10  # Auto-lock after 10 seconds
      
      - service: "lights.turn_on"
        data:
          room: "2201"
          scene: "welcome"  # Warm lighting
      
      - service: "hvac.set_mode"
        data:
          room: "2201"
          mode: "cool"
          temperature: 22  # Guest preference from profile
      
      - service: "tv.turn_on"
        data:
          room: "2201"
          source: "welcome_screen"  # Show welcome message
      
      - service: "notification.send"
        data:
          user: "guest_john_smith"
          message: "Welcome back! Your room is ready."
```

### 2. Housekeeping Presence Tracking

**Scenario:** Track housekeeping staff cleaning rooms

```yaml
automation:
  - trigger:
      platform: "bluetooth_beacon"
      beacon_id: "room_2201_beacon"
      user: "staff_maria_housekeeping"
      event: "enter"
    
    actions:
      - service: "housekeeping.log_entry"
        data:
          staff_id: "staff_maria"
          room: "2201"
          task: "daily_cleaning"
          start_time: "{{ now() }}"
      
      - service: "door_lock.unlock"
        data:
          room: "2201"
          master_key: true
      
      - service: "notification.send"
        data:
          user: "supervisor@hotel.com"
          message: "Maria started cleaning Room 2201"
  
  - trigger:
      platform: "bluetooth_beacon"
      beacon_id: "room_2201_beacon"
      user: "staff_maria_housekeeping"
      event: "exit"
    
    condition:
      - dwell_time_min: 1800  # At least 30 minutes
    
    actions:
      - service: "housekeeping.log_exit"
        data:
          staff_id: "staff_maria"
          room: "2201"
          end_time: "{{ now() }}"
          duration: "{{ dwell_time }}"
      
      - service: "housekeeping.mark_complete"
        data:
          room: "2201"
          status: "cleaned"
      
      - service: "notification.send"
        data:
          user: "supervisor@hotel.com"
          message: "Maria finished cleaning Room 2201 ({{ dwell_time_formatted }})"
```

### 3. Guest Absence (Energy Saving Mode)

**Scenario:** Guest leaves room, activate eco mode

```yaml
automation:
  - trigger:
      platform: "bluetooth_beacon"
      beacon_id: "room_2201_beacon"
      user: "guest_john_smith"
      event: "exit"
    
    condition:
      - no_presence_for: 300  # 5 minutes (debounce)
    
    actions:
      - service: "lights.turn_off"
        data:
          room: "2201"
          except: ["bathroom_night_light"]  # Keep night light
      
      - service: "hvac.set_mode"
        data:
          room: "2201"
          mode: "eco"
          temperature: 25  # Raise temp to save energy
      
      - service: "tv.turn_off"
        data:
          room: "2201"
      
      - service: "notification.send"
        data:
          user: "guest_john_smith"
          message: "Energy saving mode activated. Your preferences will restore when you return."
```

### 4. VIP Guest Proximity Alert

**Scenario:** Alert concierge when VIP guest approaches lobby

```yaml
automation:
  - trigger:
      platform: "bluetooth_beacon"
      beacon_id: "lobby_beacon"
      user: "guest_robert_vip"
      zone: "near"  # Within 3 meters
    
    condition:
      - user_profile.vip: true
    
    actions:
      - service: "notification.send"
        data:
          user: "concierge@hotel.com"
          message: "VIP Guest Robert Chen approaching lobby"
          priority: "high"
      
      - service: "display.show_greeting"
        data:
          location: "lobby_screen"
          message: "Welcome back, Mr. Chen!"
```

### 5. Asset Tracking (Housekeeping Cart)

**Scenario:** Track housekeeping cart location

```yaml
beacon:
  id: "housekeeping_cart_3"
  type: "ibeacon"
  uuid: "550e8400-e29b-41d4-a716-446655440000"
  major: 99  # Housekeeping carts
  minor: 3  # Cart #3
  attached_to: "cart"

# Gateway scans for cart beacon
automation:
  - trigger:
      platform: "bluetooth_beacon"
      beacon_id: "housekeeping_cart_3"
      gateway: "floor_22_gateway"
      zone: "near"
    
    actions:
      - service: "asset_tracking.update_location"
        data:
          asset_id: "cart_3"
          location: "floor_22"
          last_seen: "{{ now() }}"
      
      - service: "housekeeping.update_cart_location"
        data:
          cart_id: 3
          floor: 22
```

### 6. Occupancy-Based Housekeeping Scheduling

**Scenario:** Only clean rooms when guest is out

```yaml
automation:
  - trigger:
      platform: "time"
      time: "10:00"  # 10:00 AM
    
    condition:
      - room_occupied: false  # Guest not in room (based on beacon)
      - guest_checkout_today: false
      - room_status: "dirty"
    
    actions:
      - service: "housekeeping.schedule_cleaning"
        data:
          room: "2201"
          priority: "high"
          note: "Guest is out, clean now"
```

### 7. Lost & Found Alert

**Scenario:** Guest left phone/wallet with beacon tag in room

```yaml
automation:
  - trigger:
      platform: "bluetooth_beacon"
      beacon_id: "guest_john_phone_tracker"  # AirTag or Tile
      gateway: "room_2201_gateway"
      zone: "near"
    
    condition:
      - guest_checked_out: true  # Guest already checked out
      - time_after_checkout_minutes: 30
    
    actions:
      - service: "notification.send"
        data:
          user: "guest_john_smith"
          message: "You may have left your phone in Room 2201. We'll hold it at the front desk."
      
      - service: "notification.send"
        data:
          user: "frontdesk@hotel.com"
          message: "Guest John Smith may have left phone in Room 2201 (detected via Bluetooth)"
```

---

## Hardware Requirements

### Beacon Hardware

**Recommended Beacons:**

| Brand | Model | Protocols | Battery Life | Price |
|-------|-------|-----------|--------------|-------|
| **Estimote** | Location Beacon | iBeacon, Eddystone | 2-3 years | $25 |
| **Kontakt.io** | Smart Beacon | iBeacon, Eddystone | 2-4 years | $20 |
| **Radius Networks** | RadBeacon Dot | iBeacon, AltBeacon | 2-3 years | $15 |
| **Minew** | E8 | iBeacon, Eddystone | 2-3 years | $10 |
| **Gimbal** | Series 21 | iBeacon | 2-3 years | $20 |

**Beacon Placement:**

**Option 1: Single Beacon per Room** (Basic)
```
Place beacon:
- Above door frame (inside room)
- Or on wall near door
- 1.5-2m height

Pros: Simple, low cost ($10-25/room)
Cons: Less accurate positioning
```

**Option 2: Triple Beacon per Room** (Advanced)
```
Place beacons:
- Beacon 1: Near door (entry detection)
- Beacon 2: Near bed (occupancy detection)
- Beacon 3: Near window/desk (area detection)

Pros: Accurate positioning, area detection
Cons: Higher cost ($30-75/room)
```

**Option 3: Beacon in Hallway** (Very Basic)
```
Place beacon:
- In hallway outside room door

Pros: Lowest cost, detects approach
Cons: Cannot detect room occupancy
```

### Gateway Hardware

**Option 1: MediaControl Gateway (Built-in BLE Scanner)**
- Every MCG gateway has Bluetooth 5.0/5.1 built-in
- Continuously scans for beacons
- No additional hardware needed

**Option 2: Raspberry Pi Beacon Scanner**
```yaml
# One Pi per floor or building
hardware:
  model: "Raspberry Pi 4"
  bluetooth: "Built-in Bluetooth 5.0"
  range: "10-30 meters (depending on environment)"
  cost: "$35-55"
  
deployment:
  - location: "Floor 22 utility room"
    coverage: "30 rooms (entire floor)"
```

**Option 3: ESP32 Beacon Scanner**
```yaml
# Ultra low-cost option
hardware:
  model: "ESP32-DevKitC"
  bluetooth: "Built-in Bluetooth 4.2/5.0"
  range: "10-20 meters"
  cost: "$5-10"
  power: "USB or PoE"
  
deployment:
  - location: "Hallway junction (every 10 rooms)"
```

### User Devices (Phone/Wearable)

**Guests:**
- iPhone (iOS 7+) - iBeacon support built-in
- Android phone (4.3+) - Eddystone/iBeacon support
- Apple Watch - iBeacon support
- Wear OS watch - Eddystone support

**Staff:**
- Same as guests
- OR dedicated beacon tag (attached to ID badge)

---

## Configuration

### Complete Configuration Example

```yaml
# MediaControl Bluetooth Beacon Configuration

hotel:
  name: "Grand Luxury Hotel"
  floors: [20, 21, 22, 23, 24, 25]

# ============================================================
# BEACON DEPLOYMENT
# ============================================================

beacons:
  # Beacon format
  protocol: "ibeacon"  # or "eddystone", "altbeacon"
  uuid: "550e8400-e29b-41d4-a716-446655440000"
  tx_power: -59  # Calibrated RSSI at 1 meter
  
  # Deployment mode
  deployment:
    mode: "single_per_room"  # or "triple_per_room", "hallway_only"
  
  # Room beacons (auto-generated for all rooms)
  rooms:
    - room_number: "2201"
      beacon:
        type: "ibeacon"
        uuid: "550e8400-e29b-41d4-a716-446655440000"
        major: 22  # Floor
        minor: 2201  # Room number
        location: "above_door_inside"
        height: 2.0  # meters
    
    - room_number: "2202"
      beacon:
        type: "ibeacon"
        uuid: "550e8400-e29b-41d4-a716-446655440000"
        major: 22
        minor: 2202
        location: "above_door_inside"
        height: 2.0
    
    # ... more rooms
  
  # Common area beacons
  common_areas:
    - name: "Lobby"
      beacon:
        type: "ibeacon"
        uuid: "550e8400-e29b-41d4-a716-446655440000"
        major: 0  # Common areas
        minor: 1  # Lobby
        location: "lobby_entrance"
    
    - name: "Pool"
      beacon:
        type: "ibeacon"
        uuid: "550e8400-e29b-41d4-a716-446655440000"
        major: 0
        minor: 2  # Pool
        location: "pool_entrance"
    
    - name: "Gym"
      beacon:
        type: "ibeacon"
        uuid: "550e8400-e29b-41d4-a716-446655440000"
        major: 0
        minor: 3  # Gym
        location: "gym_entrance"
  
  # Asset tracking beacons (carts, wheelchairs, etc.)
  assets:
    - asset_type: "housekeeping_cart"
      asset_id: "cart_1"
      beacon:
        type: "ibeacon"
        uuid: "550e8400-e29b-41d4-a716-446655440000"
        major: 99  # Assets
        minor: 1  # Cart #1
    
    - asset_type: "housekeeping_cart"
      asset_id: "cart_2"
      beacon:
        type: "ibeacon"
        uuid: "550e8400-e29b-41d4-a716-446655440000"
        major: 99
        minor: 2  # Cart #2


# ============================================================
# GATEWAY SCANNERS
# ============================================================

gateways:
  # MediaControl Gateways (built-in BLE)
  - gateway_id: "mcg_floor_22"
    location: "Floor 22 utility room"
    hardware: "MediaControl Gateway Pro"
    bluetooth:
      enabled: true
      scan_interval: 1  # seconds (continuous scanning)
      scan_window: 1  # seconds
    
    coverage:
      floors: [22]
      rooms: ["2201", "2202", ..., "2250"]
  
  # Raspberry Pi Scanner
  - gateway_id: "rpi_floor_23"
    location: "Floor 23 electrical room"
    hardware: "Raspberry Pi 4"
    bluetooth:
      enabled: true
      scan_interval: 1
      adapter: "hci0"
    
    coverage:
      floors: [23]
      rooms: ["2301", "2302", ..., "2350"]


# ============================================================
# PROXIMITY ZONES
# ============================================================

proximity:
  zones:
    immediate:
      rssi_min: -59
      rssi_max: -30
      distance_max: 1.0  # meters
      description: "At door (touching)"
    
    near:
      rssi_min: -70
      rssi_max: -60
      distance_max: 3.0  # meters
      description: "Inside room or very close"
    
    far:
      rssi_min: -90
      rssi_max: -71
      distance_max: 10.0  # meters
      description: "In hallway near room"
    
    unknown:
      rssi_max: -91
      description: "Too far, signal lost"
  
  # RSSI smoothing
  smoothing:
    enabled: true
    method: "kalman"  # or "moving_average"
    kalman:
      process_variance: 0.01
      measurement_variance: 4.0
    moving_average:
      window_size: 5  # Last 5 readings
  
  # Distance calculation
  distance:
    tx_power: -59  # Calibrated RSSI at 1 meter
    path_loss_exponent: 3.0  # 2.0 (free space), 3.0 (typical indoor), 4.0 (dense walls)


# ============================================================
# PRESENCE DETECTION
# ============================================================

presence:
  # Enter/exit detection
  enter_detection:
    zone_threshold: "near"  # Enter when crosses into "near" or "immediate"
    debounce_time: 5  # seconds (must stay in zone for 5s)
  
  exit_detection:
    zone_threshold: "unknown"  # Exit when signal lost
    debounce_time: 30  # seconds (must be gone for 30s)
  
  # Dwell time tracking
  dwell_time:
    enabled: true
    minimum_dwell: 60  # Don't log events < 1 minute
  
  # Multi-user detection
  multi_user:
    enabled: true
    max_users_per_room: 10


# ============================================================
# USER IDENTIFICATION
# ============================================================

users:
  # Guests (identified by phone MAC or beacon)
  guests:
    - user_id: "guest_john_smith"
      name: "John Smith"
      room: "2201"
      
      # Phone Bluetooth MAC address
      bluetooth_devices:
        - mac: "AA:BB:CC:DD:EE:FF"
          device_name: "John's iPhone"
        
        - mac: "11:22:33:44:55:66"
          device_name: "John's Apple Watch"
      
      # Personal beacon (optional)
      beacon:
        type: "ibeacon"
        uuid: "550e8400-e29b-41d4-a716-446655440001"  # Different UUID for users
        major: 1000  # Guest beacons
        minor: 1  # John Smith
  
  # Staff (identified by beacon badge)
  staff:
    - user_id: "staff_maria_housekeeping"
      name: "Maria Garcia"
      role: "housekeeping"
      
      # Staff beacon badge
      beacon:
        type: "ibeacon"
        uuid: "550e8400-e29b-41d4-a716-446655440002"  # Staff UUID
        major: 2000  # Staff beacons
        minor: 42  # Maria's badge #42


# ============================================================
# AUTOMATIONS
# ============================================================

automations:
  # Guest room entry
  - name: "Guest Room Entry - Auto Unlock & Welcome"
    trigger:
      platform: "bluetooth_beacon"
      user: "guest_*"  # Any guest
      beacon_match: "room_{{user.room}}_beacon"
      zone: "immediate"
    
    condition:
      - guest_checked_in: true
      - key_active: true
    
    actions:
      - service: "door_lock.unlock"
        data:
          room: "{{user.room}}"
          duration: 10
      
      - service: "lights.turn_on"
        data:
          room: "{{user.room}}"
          scene: "welcome"
      
      - service: "hvac.set_temperature"
        data:
          room: "{{user.room}}"
          temperature: "{{user.preferences.temperature}}"
  
  # Guest room exit
  - name: "Guest Room Exit - Energy Saving"
    trigger:
      platform: "bluetooth_beacon"
      user: "guest_*"
      beacon_match: "room_{{user.room}}_beacon"
      event: "exit"
    
    condition:
      - no_presence_for: 300  # 5 minutes
    
    actions:
      - service: "lights.turn_off"
        data:
          room: "{{user.room}}"
      
      - service: "hvac.set_mode"
        data:
          room: "{{user.room}}"
          mode: "eco"
  
  # Housekeeping tracking
  - name: "Housekeeping Room Entry"
    trigger:
      platform: "bluetooth_beacon"
      user: "staff_*_housekeeping"
      beacon_match: "room_*_beacon"
      event: "enter"
    
    actions:
      - service: "housekeeping.log_entry"
        data:
          staff_id: "{{user.id}}"
          room: "{{beacon.room}}"
          start_time: "{{now()}}"
  
  - name: "Housekeeping Room Exit"
    trigger:
      platform: "bluetooth_beacon"
      user: "staff_*_housekeeping"
      beacon_match: "room_*_beacon"
      event: "exit"
    
    condition:
      - dwell_time_min: 1800  # At least 30 minutes
    
    actions:
      - service: "housekeeping.log_exit"
        data:
          staff_id: "{{user.id}}"
          room: "{{beacon.room}}"
          duration: "{{dwell_time}}"
      
      - service: "housekeeping.mark_complete"
        data:
          room: "{{beacon.room}}"


# ============================================================
# PRIVACY & SECURITY
# ============================================================

privacy:
  # Guest opt-in/opt-out
  guest_tracking:
    enabled: true
    opt_in_required: true  # Guests must consent
    opt_out_allowed: true
    
    # What data is collected
    collect:
      - room_entry_exit: true
      - dwell_time: true
      - common_area_visits: false  # Don't track pool/gym visits
    
    # Data retention
    retention:
      presence_logs: 90  # days
      dwell_time_stats: 365  # days (anonymized)
  
  # Staff tracking
  staff_tracking:
    enabled: true
    opt_out_allowed: false  # Required for accountability
    
    collect:
      - room_entry_exit: true
      - dwell_time: true
      - location: true
    
    retention:
      presence_logs: 365  # days
      audit_trail: 2555  # 7 years (compliance)
  
  # Anonymization
  anonymization:
    enabled: true
    after_days: 90  # Anonymize after 90 days
    keep_aggregated_stats: true


# ============================================================
# BEACON BATTERY MONITORING
# ============================================================

battery_monitoring:
  enabled: true
  
  # Alerts
  alerts:
    low_battery_threshold: 20  # percent
    critical_battery_threshold: 10  # percent
    
    notify:
      - "maintenance@hotel.com"
    
    schedule:
      daily_report: true
      weekly_report: true
  
  # Replacement schedule
  replacement:
    auto_schedule: true
    lead_time_days: 30  # Schedule replacement 30 days before expected death
    
    estimated_lifespan:
      default: 730  # 2 years (in days)
      by_model:
        "Estimote Location Beacon": 912  # 2.5 years
        "Kontakt Smart Beacon": 1095  # 3 years


# ============================================================
# REPORTING & ANALYTICS
# ============================================================

reporting:
  # Occupancy reports
  occupancy:
    enabled: true
    
    metrics:
      - current_occupancy_by_room
      - current_occupancy_by_floor
      - peak_occupancy_times
      - average_dwell_time_by_room
      - checkout_prediction  # Predict when guest will checkout based on patterns
    
    schedule:
      realtime_dashboard: true
      hourly_report: false
      daily_report: true
      weekly_report: true
  
  # Housekeeping efficiency
  housekeeping:
    enabled: true
    
    metrics:
      - average_cleaning_time_by_staff
      - rooms_cleaned_per_shift
      - idle_time_between_rooms
      - rooms_cleaned_vs_assigned
    
    schedule:
      daily_report: true
      weekly_report: true
  
  # Guest behavior analytics
  guest_analytics:
    enabled: true
    anonymized: true  # No PII
    
    metrics:
      - average_room_dwell_time
      - most_common_entry_exit_times
      - common_area_popularity
      - guest_movement_patterns
    
    schedule:
      monthly_report: true
      quarterly_report: true
```

---

## API Reference

### Beacon Management APIs

```http
# Register new beacon
POST /api/beacons/register

Request:
{
  "beacon_id": "room_2201_beacon",
  "type": "ibeacon",
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "major": 22,
  "minor": 2201,
  "tx_power": -59,
  "location": {
    "room_number": "2201",
    "placement": "above_door_inside",
    "height": 2.0
  },
  "hardware": {
    "manufacturer": "Estimote",
    "model": "Location Beacon",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "battery_type": "CR2477",
    "estimated_battery_life_days": 912
  }
}

Response:
{
  "beacon_id": "room_2201_beacon",
  "status": "registered",
  "registered_at": "2026-07-31T12:00:00Z"
}

# Get beacon status
GET /api/beacons/{beacon_id}

Response:
{
  "beacon_id": "room_2201_beacon",
  "status": "online",
  "last_seen": "2026-07-31T14:30:00Z",
  "battery_level": 85,
  "estimated_days_remaining": 730,
  "signal_strength": -62,
  "temperature": 22
}

# List all beacons
GET /api/beacons?floor=22&status=online

Response:
{
  "beacons": [
    {
      "beacon_id": "room_2201_beacon",
      "room": "2201",
      "status": "online",
      "battery": 85
    },
    {
      "beacon_id": "room_2202_beacon",
      "room": "2202",
      "status": "online",
      "battery": 92
    }
  ],
  "total": 50,
  "online": 49,
  "low_battery": 3
}

# Update beacon battery
POST /api/beacons/{beacon_id}/battery

Request:
{
  "battery_level": 78,
  "voltage": 2900,
  "replaced": false
}

Response:
{
  "beacon_id": "room_2201_beacon",
  "battery_level": 78,
  "estimated_days_remaining": 450,
  "alert": "low_battery"  # If < 20%
}
```

### Presence Detection APIs

```http
# Get current presence in room
GET /api/presence/room/{room_number}

Response:
{
  "room_number": "2201",
  "occupied": true,
  "occupants": [
    {
      "user_id": "guest_john_smith",
      "name": "John Smith",
      "user_type": "guest",
      "entered_at": "2026-07-31T14:30:00Z",
      "dwell_time_seconds": 3600,
      "proximity_zone": "near"
    }
  ],
  "last_movement": "2026-07-31T15:30:00Z"
}

# Get presence history for room
GET /api/presence/room/{room_number}/history?date=2026-07-31

Response:
{
  "room_number": "2201",
  "date": "2026-07-31",
  "events": [
    {
      "event_type": "enter",
      "user_id": "guest_john_smith",
      "user_name": "John Smith",
      "timestamp": "2026-07-31T14:30:00Z",
      "proximity_zone": "immediate"
    },
    {
      "event_type": "exit",
      "user_id": "guest_john_smith",
      "timestamp": "2026-07-31T16:45:00Z",
      "dwell_time_seconds": 8100
    }
  ],
  "total_dwell_time_seconds": 8100,
  "entry_count": 1
}

# Get current occupancy for floor
GET /api/presence/floor/{floor_number}

Response:
{
  "floor": 22,
  "total_rooms": 50,
  "occupied_rooms": 42,
  "vacant_rooms": 8,
  "occupancy_rate": 84,
  "rooms": [
    {"room": "2201", "occupied": true, "occupants": 1},
    {"room": "2202", "occupied": false, "occupants": 0}
  ]
}

# Get staff location
GET /api/presence/staff/{staff_id}

Response:
{
  "staff_id": "staff_maria_housekeeping",
  "staff_name": "Maria Garcia",
  "current_location": {
    "room_number": "2215",
    "entered_at": "2026-07-31T10:30:00Z",
    "dwell_time_seconds": 1200,
    "activity": "cleaning"
  },
  "rooms_visited_today": 8,
  "total_dwell_time_today": 14400
}
```

### Proximity Detection APIs

```http
# Get user proximity to beacon
GET /api/proximity/user/{user_id}/beacon/{beacon_id}

Response:
{
  "user_id": "guest_john_smith",
  "beacon_id": "room_2201_beacon",
  "room_number": "2201",
  "proximity": {
    "zone": "near",  # immediate, near, far, unknown
    "rssi": -65,
    "rssi_smoothed": -66,
    "distance_meters": 1.8,
    "last_seen": "2026-07-31T15:30:00Z"
  }
}

# Get all users near beacon
GET /api/proximity/beacon/{beacon_id}/users

Response:
{
  "beacon_id": "room_2201_beacon",
  "room_number": "2201",
  "users_nearby": [
    {
      "user_id": "guest_john_smith",
      "zone": "near",
      "distance_meters": 1.8,
      "last_seen": "2026-07-31T15:30:00Z"
    },
    {
      "user_id": "staff_maria_housekeeping",
      "zone": "immediate",
      "distance_meters": 0.5,
      "last_seen": "2026-07-31T15:29:00Z"
    }
  ]
}
```

### Automation Trigger APIs

```http
# Create automation
POST /api/automations

Request:
{
  "name": "Guest Room Entry - Auto Unlock",
  "trigger": {
    "type": "bluetooth_beacon",
    "beacon_id": "room_{{user.room}}_beacon",
    "user_pattern": "guest_*",
    "zone": "immediate"
  },
  "conditions": [
    {"guest_checked_in": true},
    {"key_active": true}
  ],
  "actions": [
    {
      "service": "door_lock.unlock",
      "data": {"room": "{{user.room}}", "duration": 10}
    },
    {
      "service": "lights.turn_on",
      "data": {"room": "{{user.room}}", "scene": "welcome"}
    }
  ]
}

Response:
{
  "automation_id": "auto_abc123",
  "status": "active",
  "created_at": "2026-07-31T12:00:00Z"
}

# Test automation (dry run)
POST /api/automations/{automation_id}/test

Request:
{
  "user_id": "guest_john_smith",
  "beacon_id": "room_2201_beacon",
  "zone": "immediate"
}

Response:
{
  "automation_id": "auto_abc123",
  "trigger_matched": true,
  "conditions_met": true,
  "actions_to_execute": [
    {"service": "door_lock.unlock", "room": "2201"},
    {"service": "lights.turn_on", "room": "2201"}
  ],
  "would_execute": true
}
```

### Analytics & Reporting APIs

```http
# Get occupancy report
GET /api/reports/occupancy?date=2026-07-31

Response:
{
  "date": "2026-07-31",
  "hotel_occupancy": {
    "total_rooms": 200,
    "occupied_rooms": 168,
    "occupancy_rate": 84
  },
  "by_floor": [
    {"floor": 22, "occupied": 42, "total": 50, "rate": 84},
    {"floor": 23, "occupied": 38, "total": 50, "rate": 76}
  ],
  "peak_occupancy_time": "20:00",
  "lowest_occupancy_time": "13:00"
}

# Get housekeeping efficiency report
GET /api/reports/housekeeping?date=2026-07-31

Response:
{
  "date": "2026-07-31",
  "staff": [
    {
      "staff_id": "staff_maria_housekeeping",
      "staff_name": "Maria Garcia",
      "rooms_cleaned": 15,
      "average_time_per_room_minutes": 28,
      "total_time_hours": 7.0,
      "efficiency_score": 92
    }
  ],
  "total_rooms_cleaned": 120,
  "average_time_per_room_minutes": 30
}

# Get guest behavior analytics
GET /api/reports/guest-analytics?start_date=2026-07-01&end_date=2026-07-31

Response:
{
  "period": "2026-07-01 to 2026-07-31",
  "anonymized": true,
  "metrics": {
    "average_room_dwell_time_hours": 14.5,
    "most_common_entry_time": "18:00",
    "most_common_exit_time": "10:00",
    "common_area_visits": {
      "pool": 342,
      "gym": 178,
      "restaurant": 523
    }
  }
}
```

---

## Troubleshooting

**Issue: Beacon not detected**
- Check beacon battery (may be dead)
- Verify beacon is broadcasting (use nRF Connect app to scan)
- Check gateway Bluetooth is enabled
- Verify beacon UUID/Major/Minor match configuration
- Check beacon placement (may be blocked by metal/concrete)

**Issue: False positive room entries**
- Increase debounce time (5→10 seconds)
- Adjust proximity zone threshold (immediate instead of near)
- Use multiple beacons for triangulation
- Check for signal interference

**Issue: Guest not detected in room**
- Check guest phone Bluetooth is enabled
- Verify guest has app installed (if using app-based detection)
- Check guest has granted location permissions
- Verify guest MAC address is registered
- Try using personal beacon tag instead of phone

**Issue: Inaccurate distance estimation**
- Re-calibrate TX power at 1 meter
- Adjust path loss exponent for environment
- Enable RSSI smoothing (Kalman filter)
- Check for signal reflections (metal walls, glass)

**Issue: Battery draining too fast**
- Reduce beacon broadcast frequency (1 Hz → 0.5 Hz)
- Lower TX power (if range is sufficient)
- Check for firmware issues
- Replace beacon hardware

---

**For beacon deployment & presence detection support:**
- **Email:** beacons@mediacontrol.com
- **Website:** https://mediacontrol.com/beacons
- **Documentation:** https://docs.mediacontrol.com/beacons

**Recommended Beacon Vendors:**
- **Estimote:** https://estimote.com
- **Kontakt.io:** https://kontakt.io
- **Radius Networks:** https://www.radiusnetworks.com
