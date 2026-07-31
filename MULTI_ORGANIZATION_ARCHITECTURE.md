# MULTI-ORGANIZATION ARCHITECTURE

Enterprise-grade hierarchical structure for managing multiple organizations, locations, rooms, and devices

## Architecture Overview

```
Organization (Company/Hotel Chain/Institution)
  ├── Location 1 (Building/Site)
  │   ├── Room 1A (Zone)
  │   │   ├── Device 1A1 (TV, STB, Apple TV, etc.)
  │   │   ├── Device 1A2
  │   │   └── Device 1A3
  │   ├── Room 1B
  │   │   └── Devices...
  │   └── Room 1C
  │       └── Devices...
  ├── Location 2
  │   ├── Room 2A
  │   └── Room 2B
  └── Location 3
      └── Rooms...
```

## Hierarchy Levels

### 1. Organization
**Top-level customer entity**

- Represents a company, hotel chain, institution, or residential customer
- Owns the subscription (billing entity)
- Can have multiple physical locations
- Has organization-wide settings and branding

**Examples:**
- Hilton Hotels International
- Acme Corporation
- Dubai Healthcare Authority
- John Smith (residential)

**URL Structure:**
```
https://app.mediacontrol.com/org/{org-slug}
```

### 2. Location
**Physical site or building within an organization**

- A specific building, hotel property, office, or home
- Contains rooms/zones
- Has unique address and settings
- Can have location-specific administrators

**Examples:**
- Hilton Dubai Marina (Organization: Hilton Hotels International)
- HQ Building A (Organization: Acme Corporation)
- Main Hospital Campus (Organization: Dubai Healthcare Authority)
- Home (Organization: John Smith)

**URL Structure:**
```
https://app.mediacontrol.com/org/{org-slug}/location/{location-slug}
```

### 3. Room
**Zone or space within a location**

- A specific room, conference space, or area
- Contains devices
- Has unique control interface

**Examples:**
- Suite 301 (Location: Hilton Dubai Marina)
- Boardroom (Location: HQ Building A)
- ICU Room 12 (Location: Main Hospital Campus)
- Living Room (Location: Home)

**URL Structure:**
```
https://app.mediacontrol.com/org/{org-slug}/location/{location-slug}/room/{room-slug}
```

### 4. Device
**Physical hardware in a room**

- Display, STB, Apple TV, Android TV, Matrix Switcher, Encoder, Speaker, etc.
- Controlled via room interface
- Tracked for subscription billing

**Examples:**
- Samsung Flip 85" (Room: Suite 301)
- Broadlink RM4 Pro (Room: Suite 301)
- Apple TV 4K (Room: Boardroom)
- Monoprice HDMI Matrix (Room: ICU Room 12)

## Real-World Use Cases

### 1. Hotel Chain (Enterprise)
```
Organization: Hilton Hotels International
├── Location: Hilton Dubai Marina
│   ├── Room: Suite 301
│   │   ├── Samsung Flip 85"
│   │   ├── OSN STB
│   │   ├── Apple TV 4K
│   │   └── Sonos Arc
│   ├── Room: Suite 302
│   ├── Room: Conference Room A
│   └── Room: Lobby Bar
├── Location: Hilton Mumbai Central
│   ├── Room: Presidential Suite
│   ├── Room: Meeting Room 1
│   └── ...
└── Location: Hilton NYC Times Square
    └── ...

Subscription: Enterprise Tier
  - 20 locations
  - 450 rooms
  - 1,350 devices
  - 50 users
```

### 2. Corporate Office (Business/Enterprise)
```
Organization: Acme Corporation
├── Location: HQ Building - Dubai
│   ├── Room: CEO Office
│   ├── Room: Boardroom
│   ├── Room: Training Room 1
│   └── Room: Reception
├── Location: Regional Office - Mumbai
│   └── ...
└── Location: Sales Office - London
    └── ...

Subscription: Business Tier
  - 3 locations
  - 10 rooms
  - 30 devices
  - 10 users
```

### 3. Healthcare Institution (Enterprise)
```
Organization: Dubai Healthcare Authority
├── Location: Main Hospital Campus
│   ├── Room: ICU Room 12
│   ├── Room: Operating Theater 3
│   ├── Room: Patient Room 204
│   └── Room: Lecture Hall A
└── Location: Outpatient Clinic
    └── ...

Subscription: Enterprise Tier
  - 5 locations
  - 200 rooms
  - 600 devices
  - 30 users
```

### 4. Residential (Home/Home Pro)
```
Organization: John Smith Family
└── Location: Home
    ├── Room: Living Room
    │   ├── Samsung QLED TV
    │   ├── Airtel STB
    │   └── Apple TV 4K
    ├── Room: Bedroom
    │   └── ...
    └── Room: Home Theater
        └── ...

Subscription: Home Pro Tier
  - 1 location
  - 5 rooms
  - 15 devices
  - 5 users (family members)
```

### 5. AV Integrator (Integrator Tier)
```
Organization: ProAV Solutions (Integrator)
├── Sub-Organization: Client A - Grand Hotel
│   ├── Location: Grand Hotel Downtown
│   │   └── ...
│   └── Location: Grand Hotel Airport
│       └── ...
├── Sub-Organization: Client B - Tech Corp
│   └── Location: Tech Corp HQ
│       └── ...
└── Sub-Organization: Client C - Retail Chain
    ├── Location: Store 1
    ├── Location: Store 2
    └── Location: Store 3

Subscription: Integrator Tier
  - Unlimited locations
  - Unlimited rooms
  - Unlimited devices
  - White-label branding
  - Reseller program
```

## User Management & Access Control

### Role-Based Access Control (RBAC)

**Super Admin** (Platform Admin)
- Full access to all organizations
- Platform configuration
- Not customer-facing

**Tenant Admin** (Organization Admin)
- Full access within their organization
- All locations, rooms, devices
- User management
- Billing & subscription
- Settings

**Location Admin** (Building/Site Manager)
- Access to specific locations only
- All rooms within assigned locations
- Can add devices
- Can invite users
- View analytics

**User** (Standard User)
- Access to assigned locations and rooms
- Device control
- View-only settings

**Guest** (Temporary Access)
- Limited room access
- Basic device control only
- No configuration access

### User Assignment Examples

**Hotel Chain:**
```
user: "john.doe@hilton.com"
organization_id: "org_hilton_international"
role: TENANT_ADMIN
allowed_locations: null  # All locations
allowed_rooms: null  # All rooms

user: "maria.manager@hilton.com"
organization_id: "org_hilton_international"
role: LOCATION_ADMIN
allowed_locations: ["loc_hilton_dubai_marina"]  # Only Dubai Marina
allowed_rooms: null  # All rooms in Dubai Marina

user: "guest@example.com"
organization_id: "org_hilton_international"
role: GUEST
allowed_locations: ["loc_hilton_dubai_marina"]
allowed_rooms: ["room_suite_301"]  # Only Suite 301
```

**Corporate:**
```
user: "ceo@acme.com"
organization_id: "org_acme_corp"
role: TENANT_ADMIN
allowed_locations: null  # All offices globally

user: "office.manager@acme.com"
organization_id: "org_acme_corp"
role: LOCATION_ADMIN
allowed_locations: ["loc_hq_dubai"]  # Only Dubai HQ

user: "employee@acme.com"
organization_id: "org_acme_corp"
role: USER
allowed_locations: ["loc_hq_dubai"]
allowed_rooms: ["room_boardroom", "room_training_1"]  # Specific rooms
```

## Subscription Model

### Billing Hierarchy
- **Subscription belongs to Organization** (not individual locations)
- Billing is at the organization level
- Limits apply across all locations

### Subscription Limits

**FREE Tier:**
- 1 location, 1 room, 3 devices

**HOME Tier:**
- 1 location, 2 rooms, 5 devices

**HOME PRO Tier:**
- 1 location, 5 rooms, 15 devices

**BUSINESS Tier:**
- 3 locations, 10 rooms (total), 30 devices

**ENTERPRISE Tier:**
- 20 locations, 150 rooms (total), 300 devices

**INTEGRATOR Tier:**
- Unlimited everything

### Usage Tracking
```python
subscription = {
    "organization_id": "org_hilton_international",
    "tier": "enterprise",
    "device_count": 1350,  # Total across all locations
    "location_count": 18,  # Number of locations
    "room_count": 450,  # Total rooms across all locations
    "limits": {
        "max_devices": 300,  # Can upgrade or purchase add-ons
        "max_locations": 20,
        "max_rooms": 150
    }
}
```

### Overage Handling
1. **Soft Limits:** Warning when approaching limits
2. **Hard Limits:** Block new device/location/room creation
3. **Upgrade Prompt:** Suggest higher tier
4. **Add-on Purchases:** Buy additional device/location packs

## URL Structure

### Web Application URLs
```
/org/{org-slug}
  └── Organization dashboard
      - Overview of all locations
      - Subscription & billing
      - User management
      - Analytics

/org/{org-slug}/location/{location-slug}
  └── Location dashboard
      - All rooms in this location
      - Location-specific settings
      - Device inventory

/org/{org-slug}/location/{location-slug}/room/{room-slug}
  └── Room control interface
      - Device control
      - Presets
      - Video streaming
      - EPG guide
```

### API Endpoints
```
GET  /api/v1/organizations
POST /api/v1/organizations

GET  /api/v1/organizations/{org_id}
GET  /api/v1/organizations/slug/{org-slug}
PATCH /api/v1/organizations/{org_id}

GET  /api/v1/organizations/{org_id}/locations
POST /api/v1/organizations/{org_id}/locations

GET  /api/v1/locations/{location_id}
GET  /api/v1/locations/slug/{location-slug}

GET  /api/v1/locations/{location_id}/rooms
POST /api/v1/locations/{location_id}/rooms

GET  /api/v1/rooms/{room_id}/devices
POST /api/v1/rooms/{room_id}/devices

POST /api/v1/rooms/{room_id}/control/power
POST /api/v1/rooms/{room_id}/control/source
POST /api/v1/rooms/{room_id}/control/command
```

### Embeddable Widget URLs
```
https://widget.mediacontrol.com/{org-slug}/{location-slug}/{room-slug}?token=xyz

Examples:
https://widget.mediacontrol.com/hilton-hotels/dubai-marina/suite-301?token=abc123
https://widget.mediacontrol.com/acme-corp/hq-dubai/boardroom?token=def456
```

## Implementation

### Python Data Classes
```python
@dataclass
class Organization:
    id: str
    name: str
    organization_type: str  # hotel_chain, corporate, retail, residential
    url_slug: str
    subscription_id: str
    parent_org_id: Optional[str]  # For integrator sub-organizations

@dataclass
class Location:
    id: str
    organization_id: str
    name: str
    address: str
    url_slug: str

@dataclass
class Room:
    id: str
    location_id: str
    name: str
    url_slug: str

@dataclass
class Device:
    id: str
    room_id: str
    location_id: str  # Denormalized for faster queries
    type: str  # display, stb, apple_tv, etc.
    name: str

@dataclass
class User:
    id: str
    email: str
    organization_id: str
    role: UserRole
    allowed_locations: Optional[List[str]]  # None = all
    allowed_rooms: Optional[List[str]]  # None = all
```

### Usage Example
```python
from tenant_manager import OrganizationManager

mgr = OrganizationManager()

# Create hotel chain organization
hilton = mgr.create_organization(
    name="Hilton Hotels International",
    organization_type="hotel_chain"
)

# Create locations
dubai_marina = mgr.create_location(
    organization_id=hilton.id,
    name="Hilton Dubai Marina",
    address="123 Sheikh Zayed Road, Dubai"
)

mumbai = mgr.create_location(
    organization_id=hilton.id,
    name="Hilton Mumbai Central",
    address="456 Marine Drive, Mumbai"
)

# Create rooms
suite_301 = mgr.create_room(
    location_id=dubai_marina.id,
    name="Suite 301",
    floor="3"
)

# Create devices
tv = mgr.create_device(
    room_id=suite_301.id,
    device_type="display",
    name="Samsung Flip 85",
    model="WM85R"
)

# Create users
admin = mgr.create_user(
    organization_id=hilton.id,
    email="admin@hilton.com",
    name="Hotel Admin",
    role=UserRole.TENANT_ADMIN
)

location_mgr = mgr.create_user(
    organization_id=hilton.id,
    email="manager@hilton.com",
    name="Dubai Manager",
    role=UserRole.LOCATION_ADMIN
)
mgr.restrict_user_to_locations(location_mgr.id, [dubai_marina.id])

# Access control
can_access = mgr.check_access(
    user_id=location_mgr.id,
    permission=Permission.CONTROL_DEVICE,
    location_id=dubai_marina.id,
    room_id=suite_301.id
)  # Returns True

can_access_mumbai = mgr.check_access(
    user_id=location_mgr.id,
    permission=Permission.CONTROL_DEVICE,
    location_id=mumbai.id
)  # Returns False (restricted to Dubai only)
```

## Benefits

### 1. **Scalability**
- Single organization with 1 location (residential)
- Hotel chain with 200+ locations globally
- Integrator managing 1000+ locations for multiple clients

### 2. **Flexible Access Control**
- Organization-wide admins
- Location-specific managers
- Room-specific guests
- Granular permissions

### 3. **Centralized Management**
- Single subscription for entire organization
- Centralized billing
- Organization-wide analytics
- Bulk configuration

### 4. **Multi-Tenancy**
- Complete isolation between organizations
- Shared infrastructure
- Secure data segregation

### 5. **Easy Expansion**
- Add new locations instantly
- No subscription changes needed (within limits)
- Seamless growth path

### 6. **Integrator Support**
- Manage multiple client organizations
- White-label branding per organization
- Reseller program support
- Parent-child organization relationships

## Migration Path

### From Single-Location to Multi-Location

If a customer starts with a single location and later adds more:

```python
# Initially: Home user
org = create_organization(name="John Smith", type="residential")
home = create_location(org.id, name="Home", address="...")
living_room = create_room(home.id, name="Living Room")

# Later: Add vacation home
vacation_home = create_location(org.id, name="Vacation Home", address="...")
vacation_living = create_room(vacation_home.id, name="Living Room")

# Same subscription, multiple locations
# May need to upgrade tier (HOME → HOME PRO → BUSINESS)
```

## Summary

The multi-organization architecture provides enterprise-grade scalability while remaining simple for residential users:

- **Residential:** 1 organization (family), 1 location (home), multiple rooms
- **SMB:** 1 organization (company), 1-3 locations (offices), multiple rooms
- **Enterprise:** 1 organization (company/chain), 20+ locations (sites), 100+ rooms
- **Integrator:** 1 parent organization, multiple sub-organizations (clients), unlimited locations

This architecture supports every use case from a single-room home setup to a global hotel chain with thousands of rooms.
