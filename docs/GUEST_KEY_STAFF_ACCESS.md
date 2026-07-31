# Guest Key Lifecycle & Staff Access Management

**Automatic Key Activation/Deactivation and Staff Master Keys**

---

## Table of Contents

1. [Overview](#overview)
2. [Guest Key Lifecycle](#guest-key-lifecycle)
3. [Automatic Key Expiry](#automatic-key-expiry)
4. [Staff Access Management](#staff-access-management)
5. [Master Keys](#master-keys)
6. [Configuration](#configuration)
7. [API Reference](#api-reference)

---

## Overview

**Guest keys** and **staff keys** have different lifecycles and access levels:

| User Type | Access Level | Duration | Auto-Expire | Typical Use |
|-----------|--------------|----------|-------------|-------------|
| **Guest** | Single room + common areas | Check-in to check-out | ✅ Yes | Hotel guests |
| **Staff - Housekeeping** | All rooms (master key) | Shift hours | ❌ No | Room cleaning, turndown |
| **Staff - Maintenance** | All rooms (master key) | Shift hours | ❌ No | Repairs, HVAC |
| **Staff - Security** | All rooms + restricted areas | 24/7 | ❌ No | Security patrol |
| **Staff - Manager** | All rooms + restricted areas | 24/7 | ❌ No | Management oversight |
| **Contractor** | Specific rooms | Limited time | ✅ Yes | Renovations, special projects |

---

## Guest Key Lifecycle

### Phases

**1. Pre-Check-In (Provisioning):**
```
Reservation Created (T-14 days)
    ↓
Guest receives "Add to Wallet" link (T-24 hours)
    ↓
Key provisioned to Apple/Google Wallet
    ↓
Status: PROVISIONED (not active yet)
    ↓
Guest taps reader → "Key not active until 3:00 PM"
```

**2. Check-In (Activation):**
```
Check-in time: 3:00 PM (or when guest checks in at front desk)
    ↓
Key automatically activated
    ↓
Status: ACTIVE
    ↓
Guest taps reader → Door unlocks
    ↓
Push notification: "Welcome! Your room key is now active."
```

**3. During Stay:**
```
Guest uses key to access room
    ↓
Key remains ACTIVE
    ↓
Optional: Extend checkout (update expiry)
```

**4. Check-Out (Deactivation):**
```
Check-out time: 12:00 PM (noon)
    ↓
Key automatically deactivated
    ↓
Status: EXPIRED
    ↓
Guest taps reader → "Key expired - Please see front desk"
    ↓
Key auto-archived in Apple Wallet (for record-keeping)
```

**5. Post-Check-Out (Grace Period - Optional):**
```
Check-out time: 12:00 PM
    ↓
Grace period: 2 hours (until 2:00 PM)
    ↓
Key still works (for late checkout, luggage retrieval)
    ↓
After grace period → Permanently deactivated
```

### Key Validity Windows

```yaml
guest_key_lifecycle:
  # When to provision (send "Add to Wallet" link)
  provision_before_checkin: 24  # hours
  
  # When to activate
  activate_on:
    method: "scheduled"  # or "manual" (at front desk)
    scheduled_time: "15:00"  # 3:00 PM (local time)
    # OR activate immediately on front desk check-in
  
  # When to deactivate
  deactivate_on:
    method: "scheduled"  # or "manual" (at front desk)
    scheduled_time: "12:00"  # 12:00 PM (noon)
  
  # Grace period (optional late checkout)
  grace_period:
    enabled: true
    duration: 7200  # 2 hours (in seconds)
  
  # Early check-in (if available)
  early_checkin:
    enabled: true
    earliest_time: "12:00"  # Can check in starting at noon
  
  # Late checkout (if extended)
  late_checkout:
    enabled: true
    max_extension: 14400  # 4 hours max (in seconds)
    requires_approval: true
```

---

## Automatic Key Expiry

### Time-Based Expiry

**Example: Standard 3-night stay**

```
Reservation: July 31 - August 3, 2026

Timeline:
    July 30, 2026 03:00 PM ────────── Provision key (T-24h)
                                       Status: PROVISIONED
                                       Guest receives "Add to Wallet"
    
    July 31, 2026 03:00 PM ────────── Check-in time
                                       Status: ACTIVE (auto-activated)
                                       Push: "Welcome! Key active"
    
    July 31 - August 2 ───────────────  Key active (guest uses room)
    
    August 3, 2026 12:00 PM ───────── Check-out time
                                       Status: EXPIRED (auto-deactivated)
                                       Push: "Thank you for staying!"
    
    August 3, 2026 02:00 PM ───────── Grace period ends
                                       Key permanently deactivated
```

### Activation Rules

**Rule 1: Scheduled Activation**
```python
if current_time >= check_in_datetime:
    activate_key()
    send_notification("Your room key is now active!")
else:
    deny_access("Key activates at {check_in_datetime}")
```

**Rule 2: Manual Activation (Front Desk)**
```python
# Guest checks in early at front desk
guest_checks_in_at_front_desk()
    ↓
activate_key_immediately()
    ↓
send_notification("Checked in! Key active now.")
```

**Rule 3: Early Check-In (Room Ready)**
```python
if room_ready and current_time >= earliest_checkin_time:
    activate_key()
    send_notification("Room ready! Early check-in granted.")
```

### Deactivation Rules

**Rule 1: Scheduled Deactivation**
```python
if current_time >= check_out_datetime:
    if grace_period_enabled:
        if current_time < (check_out_datetime + grace_period):
            keep_active()  # Still within grace period
        else:
            deactivate_key()  # Grace period ended
    else:
        deactivate_key()  # No grace period
    
    send_notification("Key deactivated. Thank you!")
```

**Rule 2: Manual Deactivation (Front Desk)**
```python
# Guest checks out early at front desk
guest_checks_out_at_front_desk()
    ↓
deactivate_key_immediately()
    ↓
send_notification("Checked out. Key deactivated.")
```

**Rule 3: Late Checkout Extension**
```python
# Guest requests late checkout
guest_requests_late_checkout(hours=2)
    ↓
if approved:
    extend_checkout(hours=2)
    send_notification(f"Late checkout approved until {new_checkout_time}")
```

### Timezone Handling

**Critical: Handle timezones correctly!**

```yaml
guest_key:
  reservation_id: "RES_123456"
  guest_name: "John Smith"
  room_number: "2201"
  
  # Use ISO 8601 format with timezone
  check_in: "2026-07-31T15:00:00-07:00"  # 3:00 PM Pacific Time
  check_out: "2026-08-03T12:00:00-07:00"  # 12:00 PM Pacific Time
  
  # Server converts to UTC for storage
  check_in_utc: "2026-07-31T22:00:00Z"
  check_out_utc: "2026-08-03T19:00:00Z"
  
  # Lock uses local property timezone
  property_timezone: "America/Los_Angeles"
```

**Why this matters:**
- Guest books room while in New York (EST) for Los Angeles hotel (PST)
- Check-in time must be 3:00 PM **Pacific Time**, not Eastern Time
- Server stores in UTC, lock converts to local property time

---

## Staff Access Management

### Staff Types

**1. Housekeeping:**
```yaml
staff:
  - id: "staff_maria_housekeeping"
    name: "Maria Garcia"
    role: "housekeeping"
    department: "Housekeeping"
    
    access:
      # Master key - access ALL guest rooms
      master_key: true
      
      # Access level
      access_level:
        - "all_guest_rooms"
        - "housekeeping_closets"
        - "laundry_room"
      
      # Restricted areas (cannot access)
      restricted_areas:
        - "executive_suites"  # Requires supervisor approval
        - "vault"
        - "server_room"
      
      # Time restrictions (shift hours)
      time_zones:
        - name: "Morning Shift"
          days: ["MON", "TUE", "WED", "THU", "FRI"]
          start_time: "08:00"
          end_time: "16:00"
      
      # Notifications
      notify_on_access: true  # Alert supervisor on each room entry
      
      # Limits
      max_rooms_per_day: 20  # Prevent abuse
```

**2. Maintenance:**
```yaml
staff:
  - id: "staff_john_maintenance"
    name: "John Lee"
    role: "maintenance"
    department: "Engineering"
    
    access:
      master_key: true
      
      access_level:
        - "all_guest_rooms"
        - "all_common_areas"
        - "mechanical_rooms"
        - "electrical_rooms"
        - "roof_access"
      
      # 24/7 access (emergencies)
      time_zones:
        - name: "24/7"
          days: ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
          start_time: "00:00"
          end_time: "23:59"
      
      # Emergency access
      emergency_access:
        enabled: true
        pin: "5678"  # Emergency PIN for after-hours
```

**3. Security:**
```yaml
staff:
  - id: "staff_sarah_security"
    name: "Sarah Johnson"
    role: "security"
    department: "Security"
    
    access:
      master_key: true
      
      access_level:
        - "all_rooms"  # Including restricted areas
        - "security_office"
        - "camera_room"
        - "all_emergency_exits"
      
      # 24/7 access
      time_zones:
        - name: "24/7"
      
      # Emergency override
      emergency_override:
        enabled: true
        pin: "9999"
```

**4. Manager:**
```yaml
staff:
  - id: "staff_robert_manager"
    name: "Robert Chen"
    role: "manager"
    department: "Management"
    
    access:
      master_key: true
      super_master_key: true  # Access even restricted areas
      
      access_level:
        - "all_rooms"
        - "all_restricted_areas"
        - "vault"
        - "server_room"
      
      # 24/7 access
      time_zones:
        - name: "24/7"
      
      # Can override any lock
      override_all_locks: true
```

---

## Master Keys

### Key Hierarchy

```
Level 1: Guest Key
    ↓
    Access: Single room (e.g., Room 2201)
    
Level 2: Section Master Key (Housekeeping)
    ↓
    Access: All rooms on one floor (e.g., Floor 22)
    
Level 3: Building Master Key (Supervisor)
    ↓
    Access: All guest rooms in building
    
Level 4: Grand Master Key (Manager)
    ↓
    Access: All rooms including restricted areas
    
Level 5: Emergency Master Key (Owner/GM)
    ↓
    Access: Everything, overrides all locks
```

### Master Key Configuration

```yaml
master_keys:
  # Floor master key (housekeeping supervisor)
  - id: "master_floor_22"
    name: "Floor 22 Master Key"
    level: "section_master"
    
    access:
      rooms:
        - pattern: "22*"  # All rooms starting with "22"
        # Matches: 2201, 2202, ..., 2250
      
      holders:
        - "staff_maria_housekeeping"
        - "staff_linda_supervisor_22"
      
      time_zones:
        - name: "Business Hours"
          start_time: "08:00"
          end_time: "18:00"
  
  # Building master key (head housekeeper)
  - id: "master_building_west"
    name: "West Building Master Key"
    level: "building_master"
    
    access:
      rooms:
        - pattern: "*"  # All guest rooms
        exclude:
          - "executive_suites"
          - "presidential_suite"
      
      holders:
        - "staff_jennifer_head_housekeeper"
      
      time_zones:
        - name: "24/7"
  
  # Grand master key (general manager)
  - id: "master_grand"
    name: "Grand Master Key"
    level: "grand_master"
    
    access:
      rooms:
        - pattern: "*"  # ALL rooms
        include_restricted: true
      
      areas:
        - "vault"
        - "server_room"
        - "security_office"
      
      holders:
        - "staff_robert_manager"
        - "staff_lisa_gm"
      
      time_zones:
        - name: "24/7"
      
      # Audit trail
      notify_on_use: true  # Alert security on each use
      requires_reason: true  # Must enter reason for access
```

### Master Key Security

**Access Logging:**
```python
# Log every master key use
master_key_log = {
    "timestamp": "2026-07-31T10:30:00Z",
    "staff_id": "staff_maria_housekeeping",
    "staff_name": "Maria Garcia",
    "master_key_id": "master_floor_22",
    "room_accessed": "2215",
    "reason": "Daily cleaning",
    "duration": 1200,  # 20 minutes in room
    "photo": "base64_image",  # Photo of staff member at door
    "supervisor_notified": true
}
```

**Alerts:**
```yaml
master_key_alerts:
  # Alert on after-hours access
  - condition: "access_outside_shift_hours"
    alert:
      - "supervisor@hotel.com"
      - "security@hotel.com"
    message: "Staff {staff_name} accessed {room} outside shift hours"
  
  # Alert on restricted area access
  - condition: "restricted_area_accessed"
    alert:
      - "manager@hotel.com"
      - "security@hotel.com"
    message: "Grand master key used for {room}"
  
  # Alert on excessive access
  - condition: "more_than_30_rooms_per_day"
    alert:
      - "supervisor@hotel.com"
    message: "Staff {staff_name} accessed {count} rooms today (limit: 20)"
```

---

## Configuration

### Complete Configuration Example

```yaml
# MediaControl Guest Key Lifecycle & Staff Access Configuration

hotel:
  name: "Grand Luxury Hotel"
  property_timezone: "America/Los_Angeles"

# ============================================================
# GUEST KEY LIFECYCLE
# ============================================================

guest_keys:
  # Provisioning
  provisioning:
    # When to send "Add to Wallet" link
    send_link_before_checkin: 24  # hours
    
    # Delivery methods
    delivery:
      email: true
      sms: true
      push: false
    
    # Email template
    email:
      subject: "Your Digital Room Key - {hotel_name}"
      body: |
        Hi {guest_name},
        
        Your room key for {hotel_name} is ready!
        
        Check-in: {check_in_date} at {check_in_time}
        Check-out: {check_out_date} at {check_out_time}
        Room: {room_number}
        
        Add your key to Apple Wallet or Google Wallet:
        {wallet_link}
        
        Your key will activate automatically at check-in time.
        
        See you soon!
  
  # Activation
  activation:
    method: "scheduled"  # or "manual" (at front desk)
    
    # Scheduled activation time
    scheduled_time: "15:00"  # 3:00 PM (property local time)
    
    # Early check-in
    early_checkin:
      enabled: true
      earliest_time: "12:00"  # Noon
      requires_room_ready: true
    
    # Notification on activation
    notification:
      enabled: true
      methods: ["push", "email"]
      message: "Welcome to {hotel_name}! Your room key is now active."
  
  # Expiry
  expiry:
    method: "scheduled"  # or "manual" (at front desk)
    
    # Scheduled deactivation time
    scheduled_time: "12:00"  # Noon (property local time)
    
    # Grace period (late checkout tolerance)
    grace_period:
      enabled: true
      duration: 7200  # 2 hours (in seconds)
    
    # Late checkout extension
    late_checkout:
      enabled: true
      max_extension: 14400  # 4 hours max
      requires_approval: true
      approval_methods: ["front_desk", "mobile_app"]
    
    # Notification on expiry
    notification:
      enabled: true
      methods: ["push", "email"]
      message: "Thank you for staying at {hotel_name}! Your key has been deactivated."
  
  # Post-checkout
  post_checkout:
    # Auto-archive in Apple Wallet
    archive_in_wallet: true
    
    # Keep key in database for records
    keep_in_database: true
    retention_days: 365  # 1 year


# ============================================================
# STAFF ACCESS
# ============================================================

staff_access:
  enabled: true
  
  # Master key system
  master_keys:
    enabled: true
    
    # Key levels
    levels:
      # Level 1: Guest key (single room)
      - level: 1
        name: "Guest Key"
        access: "single_room"
      
      # Level 2: Section master (one floor)
      - level: 2
        name: "Section Master Key"
        access: "floor"
        roles: ["housekeeping", "housekeeping_supervisor"]
      
      # Level 3: Building master (all guest rooms)
      - level: 3
        name: "Building Master Key"
        access: "all_guest_rooms"
        roles: ["head_housekeeper", "maintenance"]
      
      # Level 4: Grand master (all rooms including restricted)
      - level: 4
        name: "Grand Master Key"
        access: "all_rooms"
        roles: ["manager", "gm", "security"]
      
      # Level 5: Emergency master (override everything)
      - level: 5
        name: "Emergency Master Key"
        access: "emergency_override"
        roles: ["owner", "gm"]
  
  # Staff roles
  roles:
    # Housekeeping
    - role: "housekeeping"
      department: "Housekeeping"
      master_key_level: 2  # Section master
      
      access:
        rooms: "assigned_floor"  # Only assigned floor
        common_areas: ["housekeeping_closet", "laundry"]
      
      restrictions:
        time_zones:
          - name: "Shift Hours"
            days: ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            start_time: "08:00"
            end_time: "16:00"
        
        max_rooms_per_day: 20
        
        notify_supervisor_on_access: true
    
    # Housekeeping Supervisor
    - role: "housekeeping_supervisor"
      department: "Housekeeping"
      master_key_level: 3  # Building master
      
      access:
        rooms: "all_guest_rooms"
        common_areas: ["housekeeping_office", "storage"]
      
      restrictions:
        time_zones:
          - name: "Extended Hours"
            start_time: "07:00"
            end_time: "19:00"
    
    # Maintenance
    - role: "maintenance"
      department: "Engineering"
      master_key_level: 3  # Building master
      
      access:
        rooms: "all_guest_rooms"
        common_areas: ["mechanical_rooms", "electrical_rooms", "roof"]
        restricted_areas: ["server_room"]
      
      restrictions:
        time_zones:
          - name: "24/7"  # Emergencies
      
      emergency_access:
        enabled: true
        pin: "5678"
    
    # Security
    - role: "security"
      department: "Security"
      master_key_level: 4  # Grand master
      
      access:
        rooms: "all_rooms"
        restricted_areas: ["security_office", "camera_room"]
      
      restrictions:
        time_zones:
          - name: "24/7"
      
      emergency_override: true
    
    # Manager
    - role: "manager"
      department: "Management"
      master_key_level: 4  # Grand master
      
      access:
        rooms: "all_rooms"
        restricted_areas: "all"
      
      restrictions:
        time_zones:
          - name: "24/7"
      
      override_all_locks: true
  
  # Audit trail
  audit:
    enabled: true
    log_every_access: true
    
    # Photo on access
    capture_photo: true
    
    # Alerts
    alerts:
      - condition: "after_hours_access"
        notify: ["supervisor@hotel.com"]
      
      - condition: "restricted_area_access"
        notify: ["manager@hotel.com", "security@hotel.com"]
      
      - condition: "excessive_access"  # More than limit
        notify: ["supervisor@hotel.com"]
      
      - condition: "grand_master_key_use"
        notify: ["gm@hotel.com", "security@hotel.com"]
    
    # Reporting
    reports:
      daily_access_summary: true
      weekly_audit_report: true
      recipients: ["manager@hotel.com"]


# ============================================================
# EXAMPLE STAFF MEMBERS
# ============================================================

staff:
  # Housekeeper
  - id: "staff_maria_housekeeping"
    name: "Maria Garcia"
    email: "maria@hotel.com"
    role: "housekeeping"
    
    credentials:
      nfc_card:
        card_id: "04:C1:D2:E3:F4:A5:B6"
      
      apple_wallet:
        enabled: true
      
      personal_pin: "1234"
    
    access:
      master_key_level: 2  # Floor 22 master
      assigned_floor: 22
      
      time_zones:
        - name: "Morning Shift"
          days: ["MON", "TUE", "WED", "THU", "FRI"]
          start_time: "08:00"
          end_time: "16:00"
  
  # Maintenance
  - id: "staff_john_maintenance"
    name: "John Lee"
    email: "john@hotel.com"
    role: "maintenance"
    
    credentials:
      nfc_card:
        card_id: "04:D1:E2:F3:A4:B5:C6"
    
    access:
      master_key_level: 3  # Building master
      
      time_zones:
        - name: "24/7"
      
      emergency_pin: "5678"
  
  # Security
  - id: "staff_sarah_security"
    name: "Sarah Johnson"
    email: "sarah@hotel.com"
    role: "security"
    
    credentials:
      nfc_card:
        card_id: "04:E1:F2:A3:B4:C5:D6"
    
    access:
      master_key_level: 4  # Grand master
      
      time_zones:
        - name: "Night Shift"
          start_time: "22:00"
          end_time: "06:00"
  
  # Manager
  - id: "staff_robert_manager"
    name: "Robert Chen"
    email: "robert@hotel.com"
    role: "manager"
    
    credentials:
      nfc_card:
        card_id: "04:F1:A2:B3:C4:D5:E6"
      
      fingerprint:
        enabled: true
    
    access:
      master_key_level: 4  # Grand master
      override_all_locks: true
      
      time_zones:
        - name: "24/7"
```

---

## API Reference

### Guest Key Lifecycle APIs

```http
# Issue guest key with auto-expiry
POST /api/hospitality/guest-keys/issue

Request:
{
  "reservation_id": "RES_123456",
  "guest": {
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "+1-555-123-4567"
  },
  "room": {
    "room_number": "2201",
    "building": "West Tower"
  },
  "schedule": {
    "check_in": "2026-07-31T15:00:00-07:00",  # ISO 8601 with timezone
    "check_out": "2026-08-03T12:00:00-07:00",
    "provision_before": 24,  # hours
    "grace_period": 7200  # 2 hours in seconds
  },
  "wallet_type": "apple_wallet",  # or "google_wallet"
  "passive_entry": {
    "enabled": true,
    "technology": "hybrid"  # UWB + BLE
  }
}

Response:
{
  "key_id": "key_abc123",
  "status": "provisioned",  # Will activate at check-in
  "wallet_pass_url": "https://wallet-pass.com/abc123",
  "activation": {
    "scheduled_time": "2026-07-31T15:00:00-07:00",
    "time_until_activation": 86400,  # seconds
    "auto_activate": true
  },
  "expiry": {
    "scheduled_time": "2026-08-03T12:00:00-07:00",
    "grace_period": 7200,
    "final_expiry": "2026-08-03T14:00:00-07:00"
  }
}

# Check key status
GET /api/hospitality/guest-keys/{key_id}/status

Response:
{
  "key_id": "key_abc123",
  "status": "active",  # provisioned, active, expired, revoked
  "guest_name": "John Smith",
  "room_number": "2201",
  "check_in": "2026-07-31T15:00:00-07:00",
  "check_out": "2026-08-03T12:00:00-07:00",
  "activated_at": "2026-07-31T15:00:05Z",
  "expires_in": 172800,  # seconds (48 hours)
  "last_used": "2026-07-31T18:45:00Z",
  "usage_count": 5
}

# Manually activate key (front desk check-in)
POST /api/hospitality/guest-keys/{key_id}/activate

Request:
{
  "activated_by": "staff_lisa_frontdesk",
  "reason": "Early check-in - room ready",
  "override_schedule": true
}

Response:
{
  "key_id": "key_abc123",
  "status": "active",
  "activated_at": "2026-07-31T12:30:00Z",
  "message": "Key activated 2.5 hours early"
}

# Extend checkout (late checkout)
POST /api/hospitality/guest-keys/{key_id}/extend

Request:
{
  "extension_hours": 2,
  "approved_by": "staff_robert_manager",
  "reason": "Late checkout approved"
}

Response:
{
  "key_id": "key_abc123",
  "original_checkout": "2026-08-03T12:00:00-07:00",
  "new_checkout": "2026-08-03T14:00:00-07:00",
  "extension_hours": 2,
  "additional_charge": 50.00  # USD (optional late checkout fee)
}

# Manually deactivate key (front desk check-out)
POST /api/hospitality/guest-keys/{key_id}/deactivate

Request:
{
  "deactivated_by": "staff_lisa_frontdesk",
  "reason": "Early checkout"
}

Response:
{
  "key_id": "key_abc123",
  "status": "expired",
  "deactivated_at": "2026-08-03T10:15:00Z",
  "message": "Key deactivated 1.75 hours early"
}

# Bulk key status (for PMS integration)
GET /api/hospitality/guest-keys/batch?date=2026-07-31

Response:
{
  "date": "2026-07-31",
  "total_keys": 150,
  "by_status": {
    "provisioned": 20,  # Awaiting check-in
    "active": 120,  # Currently active
    "expired": 10  # Checked out
  },
  "activations_today": 25,
  "expirations_today": 15
}
```

### Staff Access APIs

```http
# Issue staff key (master key)
POST /api/hospitality/staff-keys/issue

Request:
{
  "staff_id": "staff_maria_housekeeping",
  "staff": {
    "name": "Maria Garcia",
    "email": "maria@hotel.com",
    "role": "housekeeping",
    "department": "Housekeeping"
  },
  "master_key": {
    "level": 2,  # Section master (floor 22)
    "assigned_floor": 22
  },
  "schedule": {
    "days": ["MON", "TUE", "WED", "THU", "FRI"],
    "start_time": "08:00",
    "end_time": "16:00"
  },
  "restrictions": {
    "max_rooms_per_day": 20,
    "notify_supervisor": true
  },
  "wallet_type": "apple_wallet"
}

Response:
{
  "key_id": "key_staff_maria",
  "status": "active",
  "master_key_level": 2,
  "access": {
    "rooms": ["2201", "2202", ..., "2250"],  # All floor 22
    "common_areas": ["housekeeping_closet_22", "laundry"]
  },
  "restrictions": {
    "active_hours": "08:00-16:00 Mon-Fri",
    "max_rooms_per_day": 20
  }
}

# Log master key access
POST /api/hospitality/staff-keys/log-access

Request:
{
  "key_id": "key_staff_maria",
  "room_accessed": "2215",
  "timestamp": "2026-07-31T10:30:00Z",
  "reason": "Daily cleaning",
  "photo": "base64_image"  # Photo of staff at door
}

Response:
{
  "log_id": "log_789012",
  "staff_name": "Maria Garcia",
  "room": "2215",
  "duration": 1200,  # 20 minutes
  "supervisor_notified": true,
  "rooms_accessed_today": 8  # Out of 20 limit
}

# Get staff access logs
GET /api/hospitality/staff-keys/logs?staff_id=staff_maria&date=2026-07-31

Response:
{
  "staff_id": "staff_maria_housekeeping",
  "staff_name": "Maria Garcia",
  "date": "2026-07-31",
  "total_accesses": 15,
  "rooms_accessed": [
    {
      "room": "2201",
      "timestamp": "2026-07-31T08:15:00Z",
      "duration": 1800,  # 30 minutes
      "reason": "Daily cleaning"
    },
    {
      "room": "2202",
      "timestamp": "2026-07-31T08:50:00Z",
      "duration": 1500,
      "reason": "Daily cleaning"
    }
    // ... more rooms
  ],
  "within_limits": true,
  "alerts": []
}

# Get master key access report
GET /api/hospitality/staff-keys/report?start_date=2026-07-01&end_date=2026-07-31

Response:
{
  "period": "2026-07-01 to 2026-07-31",
  "total_staff": 50,
  "total_accesses": 15000,
  "by_role": {
    "housekeeping": 12000,
    "maintenance": 2000,
    "security": 800,
    "management": 200
  },
  "alerts": [
    {
      "date": "2026-07-15",
      "staff_id": "staff_john_maintenance",
      "alert_type": "after_hours_access",
      "room": "2305",
      "timestamp": "2026-07-15T23:45:00Z"
    }
  ],
  "top_accessed_rooms": [
    {"room": "2201", "accesses": 31},
    {"room": "2202", "accesses": 30}
  ]
}
```

### PMS Integration APIs

```http
# Sync with Property Management System
POST /api/hospitality/pms/sync

Request:
{
  "pms_type": "opera_cloud",  # or "protel", "mews", "cloudbeds"
  "sync_type": "full",  # or "incremental"
  "date": "2026-07-31"
}

Response:
{
  "sync_id": "sync_abc123",
  "started_at": "2026-07-31T00:00:00Z",
  "reservations_synced": 150,
  "keys_created": 25,
  "keys_activated": 20,
  "keys_expired": 15,
  "errors": 0
}

# Webhook from PMS (check-in event)
POST /api/hospitality/pms/webhook

Request (from PMS):
{
  "event": "guest_checked_in",
  "reservation_id": "RES_123456",
  "room_number": "2201",
  "guest_name": "John Smith",
  "check_in_time": "2026-07-31T14:30:00Z",
  "check_out_time": "2026-08-03T12:00:00Z"
}

Response:
{
  "key_activated": true,
  "key_id": "key_abc123",
  "message": "Guest key activated"
}

# Webhook from PMS (check-out event)
POST /api/hospitality/pms/webhook

Request (from PMS):
{
  "event": "guest_checked_out",
  "reservation_id": "RES_123456",
  "room_number": "2201",
  "check_out_time": "2026-08-03T10:15:00Z"
}

Response:
{
  "key_deactivated": true,
  "key_id": "key_abc123",
  "message": "Guest key deactivated"
}
```

---

## Best Practices

### Guest Keys

1. **Provision Early** - Send wallet link 24 hours before check-in
2. **Auto-Activate** - Activate at scheduled check-in time (not manual)
3. **Grace Period** - Allow 2-hour grace period for late checkout
4. **Notifications** - Send push notifications on activation/expiry
5. **Archive** - Keep keys in database for 1 year (audit trail)

### Staff Keys

1. **Master Key Levels** - Use appropriate level (don't give everyone grand master)
2. **Time Restrictions** - Enforce shift hours for housekeeping
3. **Audit Trail** - Log every master key access with photo
4. **Alerts** - Alert supervisor on after-hours access
5. **Limits** - Enforce max rooms per day (prevent abuse)

### Security

1. **Timezone Handling** - Always use property local time with timezone
2. **Mutual Authentication** - Both phone and lock verify identity
3. **Credential Rotation** - Rotate credentials every 15 minutes
4. **Emergency Override** - Provide master PIN for emergencies
5. **Compliance** - Keep logs for 90-365 days (regulatory requirements)

---

## Troubleshooting

**Issue: Guest key not activating at check-in time**
- Check timezone configuration (property local time)
- Verify reservation dates in PMS
- Check if manual activation required
- Look for errors in key provisioning

**Issue: Guest key working after check-out**
- Check grace period setting (default 2 hours)
- Verify check-out time in PMS
- Check if late checkout was approved
- Manually deactivate key if needed

**Issue: Staff master key not working**
- Check shift hours (may be outside time window)
- Verify master key level (section vs. building vs. grand)
- Check room restrictions (executive suites may require higher level)
- Verify staff key is still active (not revoked)

**Issue: Too many master key alerts**
- Review max rooms per day limit (may be too low)
- Check shift hours configuration
- Verify alert conditions (after-hours may be legitimate)
- Adjust alert thresholds

---

**For guest key lifecycle & staff access support:**
- **Email:** keys@mediacontrol.com
- **Website:** https://mediacontrol.com/guest-keys
- **Documentation:** https://docs.mediacontrol.com/guest-keys

**PMS Integration Partners:**
- **Oracle OPERA Cloud:** https://docs.oracle.com/hospitality
- **Protel:** https://www.protel.net/support
- **Mews:** https://mews-systems.com/developers
- **Cloudbeds:** https://cloudbeds.com/api