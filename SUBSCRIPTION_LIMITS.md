# SUBSCRIPTION LIMIT ENFORCEMENT

Complete guide to how subscription limits are enforced for locations, rooms, and devices

---

## Overview

The system enforces subscription limits at **three levels**:
1. **Locations** - Number of physical buildings/sites
2. **Rooms** - Total rooms across all locations
3. **Devices** - Total devices across all rooms and locations

All limits are **organization-level** - billing happens at the organization, not per-location.

---

## Subscription Tiers

| Tier | Locations | Rooms (Total) | Devices (Total) | Monthly Cost |
|------|-----------|---------------|-----------------|--------------|
| **FREE** | 1 | 1 | 3 | $0 |
| **HOME** | 1 | 2 | 5 | $9 |
| **HOME PRO** | 1 | 5 | 15 | $29 |
| **BUSINESS** | 3 | 10 | 30 | $99 |
| **ENTERPRISE** | 20 | 150 | 300 | $499 |
| **INTEGRATOR** | ∞ | ∞ | ∞ | Custom |

### Key Points:
- **Locations** = Physical buildings (Home, Office, Hotel Property)
- **Rooms (Total)** = Sum of all rooms across ALL locations
- **Devices (Total)** = Sum of all devices across ALL rooms in ALL locations

---

## How Limits Are Enforced

### 1. Location Creation

When creating a new location, the system:
1. Checks if organization has active subscription
2. Checks if location limit is reached
3. If limit reached, **blocks creation** and suggests upgrade

```python
from tenant_manager import OrganizationManager
from subscription_manager import SubscriptionManager, SubscriptionTier

# Initialize
sub_mgr = SubscriptionManager()
org_mgr = OrganizationManager(subscription_manager=sub_mgr)

# Create organization with HOME tier (1 location max)
org = org_mgr.create_organization(name="John Smith Family")
sub_mgr.activate_subscription(
    organization_id=org.id,
    tier=SubscriptionTier.HOME,
    stripe_subscription_id="sub_xyz"
)

# Create first location - SUCCESS ✅
location1 = org_mgr.create_location(
    organization_id=org.id,
    name="Home",
    address="123 Main St"
)
# Result: Location created

# Try to create second location - BLOCKED ❌
location2 = org_mgr.create_location(
    organization_id=org.id,
    name="Vacation Home",
    address="456 Beach Rd"
)
# Result: None
# Error: "Cannot create location: limit reached (1/1). 
#         Current tier: home. 
#         Please upgrade subscription to add more locations."
```

### 2. Room Creation

When creating a new room, the system:
1. Checks if organization has active subscription
2. Checks if **total room count** across ALL locations is under limit
3. If limit reached, blocks creation

```python
# HOME tier allows 2 rooms total across all locations

# Create first room - SUCCESS ✅
room1 = org_mgr.create_room(
    location_id=location1.id,
    name="Living Room"
)

# Create second room - SUCCESS ✅
room2 = org_mgr.create_room(
    location_id=location1.id,
    name="Bedroom"
)

# Try to create third room - BLOCKED ❌
room3 = org_mgr.create_room(
    location_id=location1.id,
    name="Home Theater"
)
# Result: None
# Error: "Cannot create room: limit reached (2/2). 
#         Current tier: home. 
#         Please upgrade subscription to add more rooms."
```

### 3. Device Creation

When creating a new device, the system:
1. Checks if organization has active subscription
2. Checks if **total device count** across ALL rooms in ALL locations is under limit
3. If limit reached, blocks creation

```python
# HOME tier allows 5 devices total

# Add devices to living room - SUCCESS ✅
tv = org_mgr.create_device(room1.id, "display", "Samsung TV")
apple_tv = org_mgr.create_device(room1.id, "apple_tv", "Apple TV 4K")
sonos = org_mgr.create_device(room1.id, "audio", "Sonos Arc")

# Add devices to bedroom - SUCCESS ✅
bedroom_tv = org_mgr.create_device(room2.id, "display", "LG TV")
bedroom_sonos = org_mgr.create_device(room2.id, "audio", "Sonos One")

# Try to add 6th device - BLOCKED ❌
bedroom_stb = org_mgr.create_device(room2.id, "stb", "Airtel STB")
# Result: None
# Error: "Cannot create device: limit reached (5/5). 
#         Current tier: home. 
#         Please upgrade subscription to add more devices."
```

---

## Real-World Examples

### Example 1: Home User Outgrows FREE Tier

**Scenario:** User starts with FREE tier (1 location, 1 room, 3 devices)

```python
# Initial setup on FREE tier
org = org_mgr.create_organization(name="Bob's Home")
sub_mgr.activate_subscription(org.id, SubscriptionTier.FREE, "sub_123")

location = org_mgr.create_location(org.id, "Home")
living_room = org_mgr.create_room(location.id, "Living Room")

# Add 3 devices - all work
tv = org_mgr.create_device(living_room.id, "display", "TV")
apple_tv = org_mgr.create_device(living_room.id, "apple_tv", "Apple TV")
sonos = org_mgr.create_device(living_room.id, "audio", "Sonos")

# User wants to add bedroom - BLOCKED
bedroom = org_mgr.create_room(location.id, "Bedroom")  # ❌ Room limit reached (1/1)

# Solution: Upgrade to HOME tier (2 rooms, 5 devices)
sub_mgr.upgrade_subscription(org.id, SubscriptionTier.HOME)

# Now can add bedroom ✅
bedroom = org_mgr.create_room(location.id, "Bedroom")
bedroom_tv = org_mgr.create_device(bedroom.id, "display", "Bedroom TV")
```

### Example 2: Small Business on BUSINESS Tier

**Scenario:** Company with 3 offices (locations), 10 rooms total

```python
# BUSINESS tier: 3 locations, 10 rooms, 30 devices
org = org_mgr.create_organization(name="Acme Corp")
sub_mgr.activate_subscription(org.id, SubscriptionTier.BUSINESS, "sub_456")

# Create 3 locations - all work ✅
hq = org_mgr.create_location(org.id, "HQ Dubai", "Sheikh Zayed Rd")
mumbai = org_mgr.create_location(org.id, "Mumbai Office", "Bandra")
london = org_mgr.create_location(org.id, "London Office", "Canary Wharf")

# Try 4th location - BLOCKED ❌
tokyo = org_mgr.create_location(org.id, "Tokyo Office")  # Location limit: 3/3

# Add rooms across all locations (10 total allowed)
# HQ Dubai: 5 rooms
for i in range(5):
    org_mgr.create_room(hq.id, f"Conference Room {i+1}")  # ✅

# Mumbai: 3 rooms
for i in range(3):
    org_mgr.create_room(mumbai.id, f"Meeting Room {i+1}")  # ✅

# London: 2 rooms
for i in range(2):
    org_mgr.create_room(london.id, f"Boardroom {i+1}")  # ✅

# Try 11th room - BLOCKED ❌
org_mgr.create_room(london.id, "Training Room")  # Room limit: 10/10

# Solution: Upgrade to ENTERPRISE tier (20 locations, 150 rooms)
sub_mgr.upgrade_subscription(org.id, SubscriptionTier.ENTERPRISE)

# Now can add Tokyo office and more rooms ✅
tokyo = org_mgr.create_location(org.id, "Tokyo Office", "Shibuya")
training_room = org_mgr.create_room(london.id, "Training Room")
```

### Example 3: Hotel Chain on ENTERPRISE Tier

**Scenario:** Hilton with 18 properties, 450 rooms, 1350 devices

```python
# ENTERPRISE tier: 20 locations, 150 rooms, 300 devices
org = org_mgr.create_organization(
    name="Hilton Hotels International",
    organization_type="hotel_chain"
)
sub_mgr.activate_subscription(org.id, SubscriptionTier.ENTERPRISE, "sub_789")

# Create 18 hotel properties ✅
properties = []
for hotel_name in ["Dubai Marina", "Mumbai Central", "NYC Times Square", ...]:
    property = org_mgr.create_location(
        org.id,
        f"Hilton {hotel_name}",
        address=f"{hotel_name} address"
    )
    properties.append(property)

# Each property has ~25 rooms average (18 * 25 = 450 rooms)
for property in properties:
    for room_num in range(1, 26):  # 25 rooms per property
        room = org_mgr.create_room(
            property.id,
            f"Suite {room_num}",
            floor=str(room_num // 10)
        )
        # Add 3 devices per room (3 * 450 = 1350 devices)
        org_mgr.create_device(room.id, "display", "Samsung Flip")
        org_mgr.create_device(room.id, "stb", "OSN STB")
        org_mgr.create_device(room.id, "apple_tv", "Apple TV 4K")

# At this point:
# - 18 locations (under 20 limit) ✅
# - 450 rooms (over 150 limit!) ❌

# The hotel chain EXCEEDS room limit!
# This configuration would require INTEGRATOR tier or custom pricing
```

---

## Checking Current Usage

### Get Usage Summary

```python
# Get current usage vs limits
usage = org_mgr.get_organization_usage(org.id)

print(f"Tier: {usage['tier']}")
print(f"Status: {usage['status']}")

print(f"\nLocations: {usage['locations']['current']}/{usage['locations']['limit']}")
print(f"  Remaining: {usage['locations']['remaining']}")
print(f"  Usage: {usage['locations']['percentage']}%")

print(f"\nRooms: {usage['rooms']['current']}/{usage['rooms']['limit']}")
print(f"  Remaining: {usage['rooms']['remaining']}")
print(f"  Usage: {usage['rooms']['percentage']}%")

print(f"\nDevices: {usage['devices']['current']}/{usage['devices']['limit']}")
print(f"  Remaining: {usage['devices']['remaining']}")
print(f"  Usage: {usage['devices']['percentage']}%")

print(f"\nCan add location: {usage['can_add_location']}")
print(f"Can add room: {usage['can_add_room']}")
print(f"Can add device: {usage['can_add_device']}")
print(f"Upgrade recommended: {usage['upgrade_recommended']}")
```

**Output Example:**
```
Tier: business
Status: active

Locations: 3/3
  Remaining: 0
  Usage: 100.0%

Rooms: 8/10
  Remaining: 2
  Usage: 80.0%

Devices: 24/30
  Remaining: 6
  Usage: 80.0%

Can add location: False
Can add room: True
Can add device: True
Upgrade recommended: True  # (80%+ usage triggers recommendation)
```

---

## API Integration

### Create Location with Limit Checking

```http
POST /api/v1/organizations/{org_id}/locations
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "name": "New Office",
  "address": "123 Business St"
}

# Success Response (201):
{
  "id": "loc_xyz",
  "name": "New Office",
  "organization_id": "org_abc",
  "created_at": "2026-07-31T08:00:00Z"
}

# Error Response - Limit Reached (403):
{
  "error": "Location limit reached",
  "message": "Cannot create location: limit reached (3/3). Current tier: business. Please upgrade subscription.",
  "current_usage": {
    "locations": 3,
    "limit": 3
  },
  "upgrade_options": [
    {
      "tier": "enterprise",
      "max_locations": 20,
      "price_per_month": 499
    }
  ]
}
```

### Get Usage Endpoint

```http
GET /api/v1/organizations/{org_id}/usage
Authorization: Bearer {api_key}

Response (200):
{
  "organization_id": "org_abc",
  "tier": "business",
  "status": "active",
  "locations": {
    "current": 3,
    "limit": 3,
    "remaining": 0,
    "percentage": 100.0
  },
  "rooms": {
    "current": 8,
    "limit": 10,
    "remaining": 2,
    "percentage": 80.0
  },
  "devices": {
    "current": 24,
    "limit": 30,
    "remaining": 6,
    "percentage": 80.0
  },
  "can_add_location": false,
  "can_add_room": true,
  "can_add_device": true,
  "upgrade_recommended": true
}
```

---

## Deleting Resources (Decrements Counts)

When you delete locations, rooms, or devices, the counts are automatically decremented:

```python
# Delete device - device count decreases
org_mgr.delete_device("dev_123")
# organization device_count: 24 → 23

# Delete room - room count decreases, all devices in room deleted
org_mgr.delete_room("room_456")
# organization room_count: 8 → 7
# organization device_count: 23 → 20 (if room had 3 devices)

# Delete location - location count decreases, all rooms & devices deleted
org_mgr.delete_location("loc_789")
# organization location_count: 3 → 2
# organization room_count: 7 → 5 (if location had 2 rooms)
# organization device_count: 20 → 14 (if those 2 rooms had 6 devices total)
```

---

## Upgrade Workflow

### User Hits Limit

1. User tries to create resource (location/room/device)
2. System checks subscription limits
3. If limit reached, show upgrade prompt in UI
4. User clicks "Upgrade"
5. Redirect to pricing page with current tier highlighted
6. User selects new tier
7. Stripe payment flow
8. Webhook updates subscription tier
9. User can now create more resources

### Example UI Flow

```javascript
// Frontend - Create Location
async function createLocation(orgId, locationData) {
  try {
    const response = await fetch(`/api/v1/organizations/${orgId}/locations`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(locationData)
    });
    
    if (response.status === 403) {
      const error = await response.json();
      // Show upgrade modal
      showUpgradeModal({
        message: error.message,
        currentTier: error.current_usage.tier,
        upgradeOptions: error.upgrade_options
      });
    } else {
      const location = await response.json();
      // Success - show location created
    }
  } catch (error) {
    console.error(error);
  }
}
```

---

## Summary

✅ **Location limits** are enforced when creating locations  
✅ **Room limits** (total across all locations) are enforced when creating rooms  
✅ **Device limits** (total across all rooms) are enforced when creating devices  
✅ All limits are **organization-level** (one subscription per organization)  
✅ Deleting resources **decrements counts** automatically  
✅ **Clear error messages** guide users to upgrade  
✅ **Usage API** provides real-time limit tracking  
✅ **Upgrade recommendations** at 80%+ usage  

This ensures fair usage while providing clear upgrade paths as organizations grow.
