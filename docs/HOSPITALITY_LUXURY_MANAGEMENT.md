# Hospitality & Luxury Residence Management

**Complete Digital Wallet Integration, In-Room Dining, Household Management, and Staff Communication**

---

## Table of Contents

1. [Overview](#overview)
2. [Digital Wallet Keyless Access](#digital-wallet-keyless-access)
3. [Hotel Room Key Access](#hotel-room-key-access)
4. [In-Room Dining Management](#in-room-dining-management)
5. [Household Management](#household-management)
6. [Staff Communication](#staff-communication)
7. [Configuration](#configuration)
8. [API Reference](#api-reference)

---

## Overview

**MediaControl Hospitality & Luxury Residence Management** transforms hotels and high-end residences with:

| Feature | Hotels | Luxury Residences | Support |
|---------|--------|-------------------|---------|
| **Digital Wallet Keys** | ✅ Apple, Google, Samsung | ✅ Apple HomeKit, Google Home | NFC |
| **Room Key Access** | ✅ Check-in to check-out | ✅ Long-term access | Auto-deactivation |
| **In-Room Dining** | ✅ QR menu, ordering | ✅ Kitchen ordering | PMS integration |
| **Grocery/Shopping List** | ⚠️ Limited | ✅ Full management | Cloud sync |
| **Internet Browser** | ✅ In-room browser | ✅ Family browser | Content filtering |
| **Butler Requests** | ✅ Guest services | ✅ Household staff | Real-time dispatch |
| **Laundry Pickup** | ✅ Housekeeping | ✅ Domestic help | Scheduling |
| **Staff Call Buttons** | ✅ Concierge, housekeeping | ✅ Butler, nanny, driver | Direct communication |

### Architecture

```
MediaControl Gateway (In-Room/Residence)
    ↓
┌─────────────────────────────────────────────────────────┐
│  Digital Wallet Integration (Apple/Google/Samsung)      │
│  → NFC reader for keyless access                        │
│  → Multi-room key provisioning                          │
│  → Express Mode (no unlock required)                    │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  Hotel Property Management System (PMS)                 │
│  → OPERA Cloud, Protel, Mews, Cloudbeds                │
│  → Guest check-in/check-out                             │
│  → Room folio posting                                   │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  In-Room Services                                       │
│  → Dining (QR menu, ordering, KDS)                     │
│  → Household management (lists, browser, requests)      │
│  → Staff communication (call buttons, dispatch)         │
└─────────────────────────────────────────────────────────┘
```

---

## Digital Wallet Keyless Access

### Overview

**Digital wallet keys** allow guests and residents to unlock doors using their smartphones, without physical keys or cards.

**Supported Wallets:**
- ✅ **Apple Wallet** (iPhone, Apple Watch)
- ✅ **Google Wallet** (Android phones, Wear OS watches)
- ✅ **Samsung Wallet** (Samsung Galaxy phones, watches)

### Technology

**NFC (Near Field Communication):**
- Tap phone/watch on door reader
- No app launch required (Express Mode)
- Works in Power Reserve mode (5 hours after battery dies on iPhone)
- Secure Element storage (keys never leave device)

**BLE (Bluetooth Low Energy) - Alternative:**
- For locks without NFC support
- Requires app interaction
- Longer range (unlock while approaching)

### Apple Wallet Integration

#### Features

| Feature | Hotel Keys | Home Keys | Support |
|---------|-----------|-----------|---------|
| **Express Mode** | ✅ Default | ✅ Default | No unlock required |
| **Power Reserve** | ✅ 5 hours | ✅ 5 hours | Works after battery dies |
| **Multi-Room** | ✅ Supported | ✅ Multi-door | Single pass |
| **Key Sharing** | ✅ iMessage | ✅ Home app | Granular permissions |
| **Auto-Archive** | ✅ Post-checkout | ❌ N/A | Keeps wallet clean |

#### Setup (Hotels)

**1. PMS Integration:**
```yaml
pms:
  type: "opera_cloud"  # or "protel", "mews", "cloudbeds"
  connection:
    api_url: "https://api.opera-cloud.com"
    api_key: "your_opera_api_key"
    tenant_code: "YOUR_HOTEL_CODE"
  
  digital_keys:
    enabled: true
    wallet_provider: "apple_wallet"
    lock_system: "salto_space"  # Salto, ASSA ABLOY, dormakaba
```

**2. Key Provisioning Workflow:**

```
Guest Books Room (via hotel app/website)
    ↓
Guest Checks In (mobile check-in or front desk)
    ↓
PMS Sends "Add to Apple Wallet" Button
    ↓
Guest Taps Button → Key Added to Wallet
    ↓
Guest Taps iPhone on Door Reader → Door Unlocks
    ↓
Guest Checks Out → Key Auto-Deactivated
```

**3. API Integration:**

```http
# Issue digital key (PMS → Door Lock System)
POST https://api.opera-cloud.com/fof/v1/hotels/{hotelId}/reservations/{reservationId}/roomKeys

Headers:
  Authorization: Bearer {api_key}
  Content-Type: application/json

Body:
{
  "keyType": "MOBILE",
  "roomNumber": "2201",
  "guestName": "John Smith",
  "checkInDate": "2026-07-31",
  "checkOutDate": "2026-08-03",
  "walletProvider": "APPLE_WALLET",
  "accessLevels": [
    {
      "type": "ROOM",
      "roomNumber": "2201"
    },
    {
      "type": "COMMON_AREA",
      "areas": ["POOL", "GYM", "ELEVATOR"]
    }
  ]
}

Response:
{
  "keyId": "key_abc123",
  "walletPass": {
    "passUrl": "https://wallet-pass-url.com/abc123",
    "serialNumber": "HOTEL-2201-123456",
    "expiryDate": "2026-08-03T12:00:00Z"
  },
  "track3Data": "encrypted_key_data_for_nfc"
}
```

#### Setup (Residential)

**1. HomeKit Integration:**

```yaml
digital_keys:
  residential:
    type: "apple_homekit"
    
    locks:
      - id: "lock_front_door"
        name: "Front Door"
        manufacturer: "August"  # or Schlage, Yale, Kwikset
        model: "Wi-Fi Smart Lock Pro"
        
        homekit:
          pairing_code: "123-45-678"
          accessory_id: "12:34:56:78:9A:BC"
      
      - id: "lock_garage_entry"
        name: "Garage Entry Door"
        manufacturer: "Schlage"
        model: "Encode Plus"
    
    # Home Keys (Apple Wallet)
    home_keys:
      enabled: true
      owner: "owner@example.com"
      shared_users:
        - email: "family@example.com"
          access_level: "admin"  # admin, user, guest
        - email: "guest@example.com"
          access_level: "guest"
          expiry: "2026-08-31"
```

**2. Key Sharing:**

Via **Home app** (iOS):
- Home app → Select lock → Invite People
- Granular permissions (24/7 access, time-limited, specific days)
- Revoke anytime

Via **iMessage**:
- Share Home Key directly via iMessage
- Recipient taps link → Key added to Wallet

### Google Wallet Integration

#### Features

| Feature | Hotel Keys | Home Keys | Support |
|---------|-----------|-----------|---------|
| **Screen On** | ✅ Default | ✅ Default | No unlock required |
| **Gmail Auto-Import** | ✅ Automatic | ❌ Manual | From reservation email |
| **Multi-Room** | ✅ Supported | ✅ Multi-door | Single pass |
| **Device Unlock** | ⚠️ Optional | ⚠️ Optional | Can require unlock |

#### Setup

**1. Hotel Integration:**

```yaml
digital_keys:
  google_wallet:
    enabled: true
    
    # Google Wallet Pass Class
    pass_class_id: "hotel.room.key.YOUR_HOTEL"
    issuer_id: "3388000000012345678"
    
    # SMTP for pass delivery
    smtp:
      enabled: true
      from: "noreply@yourhotel.com"
      subject: "Your Digital Room Key"
      
    # Gmail auto-import
    gmail_auto_import:
      enabled: true
      structured_data: true  # Use schema.org markup in email
```

**2. Pass Provisioning:**

```json
// Google Wallet Pass Object
{
  "classId": "hotel.room.key.YOUR_HOTEL",
  "id": "RESERVATION_123456",
  "state": "ACTIVE",
  "barcode": {
    "type": "QR_CODE",
    "value": "ROOM_KEY_DATA",
    "alternateText": "Room 2201"
  },
  "cardTitle": {
    "defaultValue": {
      "language": "en-US",
      "value": "Room Key - Grand Hotel"
    }
  },
  "header": {
    "defaultValue": {
      "language": "en-US",
      "value": "Room 2201"
    }
  },
  "textModulesData": [
    {
      "header": "Check-in",
      "body": "July 31, 2026 3:00 PM"
    },
    {
      "header": "Check-out",
      "body": "August 3, 2026 12:00 PM"
    }
  ],
  "validTimeInterval": {
    "start": {
      "date": "2026-07-31T15:00:00Z"
    },
    "end": {
      "date": "2026-08-03T12:00:00Z"
    }
  },
  "locations": [
    {
      "latitude": 37.4220,
      "longitude": -122.0841
    }
  ],
  "smartTapRedemptionValue": "ENCRYPTED_NFC_DATA"
}
```

### Samsung Wallet Integration

**Features:**
- ✅ Hotel room keys (NFC)
- ✅ Digital home keys (SmartThings integration)
- ✅ Car keys (select brands: BMW, Genesis, Hyundai)
- ✅ Knox security (EAL5+ Secure Element)

**Setup:**

```yaml
digital_keys:
  samsung_wallet:
    enabled: true
    
    # SmartThings integration (for residential)
    smartthings:
      enabled: true
      api_key: "your_smartthings_api_key"
      
      locks:
        - device_id: "smartthings_lock_123"
          name: "Front Door"
```

---

## Hotel Room Key Access

### Property Management System (PMS) Integration

**Supported PMS Platforms:**

| PMS | Vendor | Digital Key Support | API |
|-----|--------|-------------------|-----|
| **OPERA Cloud** | Oracle | ✅ Apple, Google, Samsung | REST (OHIP) |
| **Protel** | Protel | ✅ Via partners (FLEXIPASS) | SOAP |
| **Mews** | Mews Systems | ✅ Apple, Google | REST |
| **Cloudbeds** | Cloudbeds | ✅ Apple, Google | REST |
| **Apaleo** | Apaleo | ✅ Apple, Google | REST |

### Key Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│  Pre-Arrival (Up to 24 hours before check-in)          │
│  → Guest receives "Add to Wallet" link via email/SMS   │
│  → Key provisioned but NOT active yet                  │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  Check-In (Day of arrival, after room assignment)      │
│  → Guest checks in (mobile or front desk)              │
│  → Key activated remotely                              │
│  → Guest can now unlock room                           │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  During Stay                                            │
│  → Guest taps phone on door reader to unlock            │
│  → Multi-room access if suite/adjoining rooms          │
│  → Common area access (pool, gym, elevator)            │
│  → Key update if stay extended                         │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  Check-Out (On departure)                              │
│  → Guest checks out (mobile or front desk)             │
│  → Key deactivated remotely                            │
│  → Key auto-archived in wallet (Apple, Google)         │
└─────────────────────────────────────────────────────────┘
```

### Multi-Room Access

**Use Cases:**
- **Suites** - Master bedroom + living room
- **Adjoining Rooms** - Family with kids in connecting rooms
- **Presidential Suite** - Multiple rooms + private lounge
- **Staff Access** - Housekeeping multi-room access

**Configuration:**

```yaml
hotel_key:
  reservation_id: "RES_123456"
  guest_name: "John Smith"
  
  rooms:
    - room_number: "2201"
      room_type: "Master Bedroom"
      access_level: "FULL"
    
    - room_number: "2202"
      room_type: "Kids Room"
      access_level: "FULL"
  
  common_areas:
    - "POOL"
    - "GYM"
    - "BUSINESS_CENTER"
    - "EXECUTIVE_LOUNGE"
    - "ELEVATOR_FLOORS_20_22"
```

---

## In-Room Dining Management

### Overview

**QR-Based Digital Menu System** - No app download required, instant ordering, real-time kitchen dispatch.

**Features:**
- ✅ **QR Code Menus** - Scan to order (no app needed)
- ✅ **Multilingual** - Auto-detect guest language preference
- ✅ **Photo-Rich** - High-quality food images
- ✅ **Customization** - Allergies, spice level, extras
- ✅ **Real-Time Tracking** - Live ETA updates
- ✅ **Payment Options** - Room charge, credit card, Apple Pay, Google Pay
- ✅ **PMS Integration** - Auto-post to guest folio
- ✅ **Kitchen Display System (KDS)** - Real-time order dispatch

### Architecture

```
Guest Scans QR Code in Room
    ↓
Web-Based Menu Opens (No App!)
    ↓
Guest Browses Menu, Customizes Order
    ↓
Guest Selects Payment (Room Charge or Card)
    ↓
Order Verified Against PMS Check-In
    ↓
Order Sent to Kitchen Display System (KDS)
    ↓
Kitchen Prepares, Updates Status
    ↓
Guest Receives Live ETA
    ↓
Staff Delivers to Room
    ↓
Charge Posted to Guest Folio (if room charge)
```

### Setup

```yaml
in_room_dining:
  enabled: true
  
  # QR Code Configuration
  qr_codes:
    per_room: true  # Unique QR per room
    url_format: "https://dining.yourhotel.com/room/{room_number}"
    design: "custom"  # custom or standard
    placement:
      - "In-Room Folder"
      - "Bedside Table Tent"
      - "TV Welcome Screen"
  
  # Menu Management
  menus:
    - id: "breakfast"
      name: "Breakfast Menu"
      availability:
        days: ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        start_time: "06:00"
        end_time: "11:00"
      
      categories:
        - name: "Continental"
          items:
            - id: "item_croissant"
              name: "Butter Croissant"
              description: "Freshly baked, flaky French croissant"
              price: 8.00
              image: "/images/croissant.jpg"
              dietary: ["vegetarian"]
              allergens: ["gluten", "dairy"]
            
            - id: "item_fruit_plate"
              name: "Fresh Fruit Plate"
              description: "Seasonal fruits, Greek yogurt, honey"
              price: 12.00
              dietary: ["vegetarian", "gluten-free"]
    
    - id: "all_day"
      name: "All Day Dining"
      availability:
        start_time: "11:00"
        end_time: "23:00"
      
      categories:
        - name: "Appetizers"
        - name: "Main Courses"
        - name: "Desserts"
        - name: "Beverages"
  
  # Payment Options
  payment:
    room_charge:
      enabled: true
      verification: "pms_checkin"  # Verify guest is checked in
    
    credit_card:
      enabled: true
      processor: "stripe"  # or "square", "adyen"
      api_key: "sk_live_..."
    
    digital_wallets:
      apple_pay: true
      google_pay: true
      samsung_pay: true
  
  # Kitchen Integration
  kitchen:
    # Option 1: Kitchen Display System (KDS)
    kds:
      enabled: true
      type: "tablet"  # tablet, screen, printer
      stations:
        - name: "Hot Kitchen"
          categories: ["Main Courses"]
        - name: "Cold Kitchen"
          categories: ["Appetizers", "Desserts"]
        - name: "Bar"
          categories: ["Beverages"]
    
    # Option 2: Traditional Printer
    printer:
      enabled: false
      ip: "192.168.1.200"
      port: 9100
    
    # Option 3: Email
    email:
      enabled: false
      to: "kitchen@yourhotel.com"
  
  # PMS Integration
  pms_integration:
    enabled: true
    auto_post_to_folio: true
    revenue_center: "IN_ROOM_DINING"

# Multilingual Support
languages:
  default: "en"
  supported:
    - "en"  # English
    - "es"  # Spanish
    - "fr"  # French
    - "de"  # German
    - "zh"  # Chinese
    - "ar"  # Arabic
    - "ja"  # Japanese
```

### Guest Experience

**1. Scan QR Code:**
- Guest uses phone camera to scan QR code
- No app download, opens in mobile browser
- Auto-detects room number from QR code

**2. Browse Menu:**
- Swipe through categories (Breakfast, Lunch, Dinner, Drinks)
- View photos, descriptions, prices
- Filter by dietary preferences (vegetarian, vegan, gluten-free)
- View allergen information

**3. Customize Order:**
- Select item → Customize
- Spice level (mild, medium, hot)
- Special requests (no onions, extra cheese)
- Allergies/dietary restrictions

**4. Add to Cart:**
- Items added to cart
- Running total displayed
- Modify quantities

**5. Checkout:**
- Select payment method:
  - **Room Charge** - Verified against PMS
  - **Credit Card** - Secure payment form
  - **Apple Pay / Google Pay** - One-tap payment
- Add delivery instructions (e.g., "Knock quietly, baby sleeping")
- Place order

**6. Order Tracking:**
- **Received** - Kitchen received order
- **Preparing** - Chef is cooking
- **Out for Delivery** - Staff delivering
- **Delivered** - Enjoy your meal!
- Estimated delivery time displayed

### Kitchen Workflow

**1. Order Arrives on KDS:**
```
┌─────────────────────────────────────────────────┐
│  NEW ORDER - Room 2201                          │
│  Guest: John Smith                              │
│  Time: 12:35 PM                                 │
│                                                 │
│  1x Burger & Fries                              │
│     - No pickles                                │
│     - Extra cheese                              │
│  1x Caesar Salad                                │
│  2x Coca-Cola                                   │
│                                                 │
│  Special: Knock quietly, baby sleeping          │
│                                                 │
│  [ACCEPT]  [REJECT]                            │
└─────────────────────────────────────────────────┘
```

**2. Chef Accepts:**
- Order moves to "Preparing" status
- Guest notified via push/SMS

**3. Chef Completes:**
- Chef taps "Ready for Delivery"
- Order moves to "Out for Delivery"
- Staff dispatched

**4. Staff Delivers:**
- Staff taps "Delivered"
- Guest receives notification
- Feedback request sent (optional)

### Revenue & Analytics

**Dashboard (for hotel management):**
- Orders by time of day
- Popular items
- Average order value
- Revenue by room/guest type
- Kitchen prep time
- Delivery time

**Reports:**
- Daily sales by menu
- Weekly/monthly trends
- Staff performance
- Guest satisfaction ratings

---

## Household Management

### Overview

**Luxury residence features** for household management, shopping, browsing, and daily tasks.

### Grocery/Shopping List

**Features:**
- ✅ **Voice Input** - "Add milk to shopping list"
- ✅ **Categorization** - Auto-sort by store department
- ✅ **Cloud Sync** - Share list with family/staff
- ✅ **Recipe Integration** - Add ingredients from recipes
- ✅ **Smart Suggestions** - Based on purchase history
- ✅ **Store Integration** - Order directly from Instacart, Amazon Fresh

**Configuration:**

```yaml
household:
  shopping_lists:
    enabled: true
    
    # Cloud sync
    cloud_sync:
      enabled: true
      service: "icloud"  # or "google_drive", "dropbox"
    
    # Shared users
    shared_users:
      - name: "Family Members"
        email: "family@example.com"
        permissions: "edit"
      
      - name: "Household Staff"
        email: "staff@example.com"
        permissions: "view"
    
    # Categories (auto-sort)
    categories:
      - "Produce"
      - "Dairy"
      - "Meat & Seafood"
      - "Bakery"
      - "Frozen"
      - "Pantry"
      - "Beverages"
      - "Household"
      - "Personal Care"
    
    # Store integrations
    stores:
      - type: "instacart"
        api_key: "instacart_api_key"
        enabled: true
      
      - type: "amazon_fresh"
        api_key: "amazon_api_key"
        enabled: true
```

**UI Features:**

```
┌─────────────────────────────────────────────────┐
│  Shopping List                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ 🎤 Add item...                            │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  Produce                                        │
│  ☐ Milk (2 gallons)                            │
│  ☐ Eggs (1 dozen)                              │
│  ☐ Spinach                                     │
│                                                 │
│  Meat & Seafood                                │
│  ☐ Chicken breasts (2 lbs)                     │
│  ☐ Salmon (4 fillets)                          │
│                                                 │
│  Pantry                                        │
│  ☐ Olive oil                                   │
│  ☐ Pasta (spaghetti)                           │
│                                                 │
│  [Share List]  [Order on Instacart]           │
└─────────────────────────────────────────────────┘
```

### Internet Browser

**Features:**
- ✅ **Full Web Browser** - Chromium-based
- ✅ **Content Filtering** - Parental controls, safe search
- ✅ **Bookmarks Sync** - Sync across devices
- ✅ **Private Browsing** - No history/cookies
- ✅ **Voice Search** - "Search for best restaurants nearby"
- ✅ **Smart Home Controls** - Quick access panel

**Configuration:**

```yaml
household:
  browser:
    enabled: true
    engine: "chromium"
    
    # Content filtering
    content_filter:
      enabled: true
      mode: "family_safe"  # strict, moderate, family_safe, off
      blocked_categories:
        - "adult"
        - "gambling"
        - "violence"
      
      safe_search:
        google: true
        bing: true
        youtube: "restricted"
    
    # Bookmarks
    bookmarks:
      - name: "Hotel Website"
        url: "https://yourhotel.com"
      - name: "Local Attractions"
        url: "https://visitcity.com"
      - name: "Weather"
        url: "https://weather.com"
    
    # Homepage
    homepage: "https://yourhotel.com/guest-portal"
```

---

## Staff Communication

### Overview

**Direct communication channels** for butler, housekeeping, nanny, driver, and other household staff.

### Multiple Call Buttons

**Features:**
- ✅ **One-Tap Call** - Direct to specific staff member
- ✅ **Priority Levels** - Urgent, normal, low priority
- ✅ **Status Tracking** - Request received, en route, completed
- ✅ **Chat Messages** - Text-based requests
- ✅ **Photo Attachments** - "Fix this light bulb" + photo
- ✅ **Recurring Requests** - Schedule daily tasks

**Configuration:**

```yaml
staff_communication:
  enabled: true
  
  # Staff roles
  staff_roles:
    - id: "butler"
      name: "Butler"
      priority: "high"
      icon: "🤵"
      dispatch_method: "push"  # push, sms, call, pager
      contacts:
        - name: "James (Head Butler)"
          phone: "+1-555-123-4567"
          email: "james@household.com"
          available_hours:
            start: "06:00"
            end: "22:00"
    
    - id: "housekeeping"
      name: "Housekeeping"
      priority: "normal"
      icon: "🧹"
      dispatch_method: "push"
      contacts:
        - name: "Maria (Housekeeper)"
          phone: "+1-555-234-5678"
    
    - id: "nanny"
      name: "Nanny"
      priority: "high"
      icon: "👶"
      dispatch_method: "call"  # Urgent - call immediately
      contacts:
        - name: "Sarah (Nanny)"
          phone: "+1-555-345-6789"
    
    - id: "driver"
      name: "Driver"
      priority: "normal"
      icon: "🚗"
      dispatch_method: "push"
      contacts:
        - name: "Michael (Driver)"
          phone: "+1-555-456-7890"
    
    - id: "chef"
      name: "Private Chef"
      priority: "normal"
      icon: "👨‍🍳"
      dispatch_method: "push"
      contacts:
        - name: "Chef Pierre"
          phone: "+1-555-567-8901"
    
    - id: "maintenance"
      name: "Maintenance"
      priority: "normal"
      icon: "🔧"
      dispatch_method: "push"
      contacts:
        - name: "Maintenance Team"
          phone: "+1-555-678-9012"
  
  # Request types
  request_types:
    butler:
      - "Room Service"
      - "Concierge Assistance"
      - "Reservation Request"
      - "Special Arrangement"
      - "General Inquiry"
    
    housekeeping:
      - "Room Cleaning"
      - "Fresh Towels"
      - "Extra Pillows/Blankets"
      - "Laundry Pickup"
      - "Turndown Service"
    
    nanny:
      - "Urgent - Need Assistance"
      - "Schedule Change"
      - "Meal Request"
      - "Activity Planning"
    
    driver:
      - "Airport Transfer"
      - "City Tour"
      - "Restaurant Reservation"
      - "Schedule Pickup"
    
    maintenance:
      - "Repair Request"
      - "Light Bulb Replacement"
      - "Plumbing Issue"
      - "HVAC Adjustment"
      - "General Maintenance"
```

### UI (Guest/Resident)

```
┌─────────────────────────────────────────────────┐
│  Staff Requests                                 │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ 🤵 Butler                     [CALL NOW] │  │
│  │ Available 6:00 AM - 10:00 PM            │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ 🧹 Housekeeping               [REQUEST]  │  │
│  │ Available Now                           │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ 👶 Nanny                      [URGENT]   │  │
│  │ Available Now                           │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ 🚗 Driver                     [SCHEDULE] │  │
│  │ Available 7:00 AM - 11:00 PM            │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ 👨‍🍳 Private Chef              [REQUEST]  │  │
│  │ Available for Meal Planning             │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  Recent Requests:                               │
│  ✓ Laundry pickup - Completed (30 min ago)     │
│  ⏳ Room cleaning - In progress                │
└─────────────────────────────────────────────────┘
```

### Request Workflow

**1. Guest Taps "Call Butler":**
```
Guest: Taps "Butler" → "Request"
    ↓
System: Shows request form
    - Request type dropdown
    - Message text box
    - Photo attachment (optional)
    - Priority selector (Normal/Urgent)
    ↓
Guest: Fills form, submits
    ↓
System: Dispatches to butler (push notification)
    ↓
Butler: Receives notification on staff app
    - "New request from Room 2201"
    - Request details
    - Tap "Accept" or "Decline"
    ↓
Butler: Accepts, updates status
    - "En Route" → Guest notified
    - "Arrived" → Guest notified
    - "Completed" → Request closed
```

### Laundry Pickup

**Features:**
- ✅ **Schedule Pickup** - Select date/time
- ✅ **Laundry Preferences** - Wash/dry/fold, dry clean
- ✅ **Special Instructions** - Delicate items, stain notes
- ✅ **Tracking** - Picked up → In progress → Ready → Delivered
- ✅ **Recurring Schedule** - Weekly pickup (e.g., every Monday)

**Configuration:**

```yaml
staff_communication:
  laundry:
    enabled: true
    
    # Pickup schedule
    pickup_schedule:
      days: ["MON", "WED", "FRI"]
      times:
        morning: "09:00"
        afternoon: "14:00"
        evening: "18:00"
    
    # Service types
    services:
      - id: "wash_dry_fold"
        name: "Wash, Dry, Fold"
        price_per_lb: 2.50
      
      - id: "dry_clean"
        name: "Dry Cleaning"
        price_per_item: 8.00
      
      - id: "press_only"
        name: "Press Only"
        price_per_item: 3.00
    
    # Tracking
    tracking:
      enabled: true
      sms_notifications: true
      email_notifications: false
```

---

## Configuration

### Complete Configuration Example

```yaml
# MediaControl Hospitality & Luxury Residence Configuration

hospitality:
  # Type: "hotel" or "residence"
  type: "hotel"
  
  property_name: "Grand Luxury Hotel"
  property_code: "GLH"
  
  # Digital Wallet Keys
  digital_keys:
    apple_wallet:
      enabled: true
      lock_system: "salto_space"
    
    google_wallet:
      enabled: true
      pass_class_id: "hotel.room.key.GLH"
    
    samsung_wallet:
      enabled: true
  
  # PMS Integration
  pms:
    type: "opera_cloud"
    api_url: "https://api.opera-cloud.com"
    api_key: "YOUR_OPERA_API_KEY"
    tenant_code: "GLH"
  
  # In-Room Dining
  in_room_dining:
    enabled: true
    qr_codes:
      per_room: true
    payment:
      room_charge: true
      credit_card: true
      digital_wallets: true
    kitchen:
      kds:
        enabled: true
        type: "tablet"
  
  # Household Management (for residences)
  household:
    shopping_lists:
      enabled: true
      cloud_sync: true
    browser:
      enabled: true
      content_filter:
        mode: "family_safe"
  
  # Staff Communication
  staff_communication:
    enabled: true
    staff_roles:
      - id: "butler"
        name: "Butler"
        priority: "high"
      - id: "housekeeping"
        name: "Housekeeping"
      - id: "driver"
        name: "Driver"
```

---

## API Reference

### Digital Keys API

```http
# Issue digital key
POST /api/hospitality/digital-keys/issue

Request:
{
  "wallet_type": "apple_wallet",  // apple_wallet, google_wallet, samsung_wallet
  "guest": {
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "+1-555-123-4567"
  },
  "reservation": {
    "id": "RES_123456",
    "room_number": "2201",
    "check_in": "2026-07-31T15:00:00Z",
    "check_out": "2026-08-03T12:00:00Z"
  },
  "access_levels": [
    {"type": "ROOM", "roomNumber": "2201"},
    {"type": "COMMON_AREA", "areas": ["POOL", "GYM"]}
  ]
}

Response:
{
  "key_id": "key_abc123",
  "wallet_pass_url": "https://wallet-pass.com/abc123",
  "status": "PROVISIONED",
  "active": false,  // Activated on check-in
  "expiry_date": "2026-08-03T12:00:00Z"
}

# Activate key (on check-in)
POST /api/hospitality/digital-keys/{key_id}/activate

# Deactivate key (on check-out)
POST /api/hospitality/digital-keys/{key_id}/deactivate
```

### In-Room Dining API

```http
# Get menu
GET /api/hospitality/dining/menu?room={room_number}

Response:
{
  "room_number": "2201",
  "guest_name": "John Smith",
  "menus": [
    {
      "id": "breakfast",
      "name": "Breakfast Menu",
      "available": true,
      "categories": [...]
    }
  ]
}

# Place order
POST /api/hospitality/dining/orders

Request:
{
  "room_number": "2201",
  "items": [
    {
      "item_id": "item_burger",
      "quantity": 1,
      "customizations": {
        "no_pickles": true,
        "extra_cheese": true
      }
    }
  ],
  "payment_method": "room_charge",  // or "credit_card"
  "special_instructions": "Knock quietly, baby sleeping"
}

Response:
{
  "order_id": "ORD_789012",
  "status": "RECEIVED",
  "estimated_delivery": "2026-07-31T13:15:00Z",
  "total": 28.50
}

# Track order
GET /api/hospitality/dining/orders/{order_id}

Response:
{
  "order_id": "ORD_789012",
  "status": "PREPARING",  // RECEIVED, PREPARING, OUT_FOR_DELIVERY, DELIVERED
  "estimated_delivery": "2026-07-31T13:15:00Z"
}
```

### Staff Communication API

```http
# Send staff request
POST /api/hospitality/staff/requests

Request:
{
  "room_number": "2201",
  "staff_role": "butler",
  "request_type": "Room Service",
  "message": "Please bring extra towels",
  "priority": "normal",  // normal, urgent
  "photo_url": "https://..."  // optional
}

Response:
{
  "request_id": "REQ_345678",
  "status": "DISPATCHED",
  "staff_member": "James (Head Butler)",
  "estimated_arrival": "2026-07-31T12:45:00Z"
}

# Track request
GET /api/hospitality/staff/requests/{request_id}

Response:
{
  "request_id": "REQ_345678",
  "status": "EN_ROUTE",  // DISPATCHED, EN_ROUTE, ARRIVED, COMPLETED
  "staff_member": "James",
  "arrival_eta": "2026-07-31T12:45:00Z"
}
```

---

**For hospitality integration support:**
- **Email:** hospitality@mediacontrol.com
- **Website:** https://mediacontrol.com/hospitality
- **Documentation:** https://docs.mediacontrol.com/hospitality

**Vendor Support:**
- **Salto (Locks):** https://saltosystems.com/support
- **OPERA Cloud (PMS):** https://docs.oracle.com/hospitality
- **Protel (PMS):** https://www.protel.net/support
