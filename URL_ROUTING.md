# URL ROUTING STRUCTURE

Complete URL schema for organizations, locations, rooms, and devices with friendly slugs

## URL Structure

```
/ app.mediacontrol.com
├── /org/{org_slug}                              # Organization dashboard
│   ├── /org/{org_slug}/location/{location_slug}         # Location dashboard
│   │   ├── /org/{org_slug}/location/{location_slug}/room/{room_slug}  # Room control
│   │   ├── /org/{org_slug}/location/{location_slug}/devices           # All devices
│   │   └── /org/{org_slug}/location/{location_slug}/settings          # Location settings
│   ├── /org/{org_slug}/billing                          # Subscription & billing
│   ├── /org/{org_slug}/users                            # User management
│   └── /org/{org_slug}/settings                         # Organization settings
│
├── /widget/{org_slug}/{location_slug}/{room_slug}  # Embeddable widget
│
└── /api/v1
    ├── /organizations
    │   ├── GET    /organizations                        # List all organizations (super admin)
    │   ├── POST   /organizations                        # Create organization
    │   ├── GET    /organizations/{id}                   # Get organization details
    │   ├── GET    /organizations/slug/{slug}            # Get by slug
    │   └── PATCH  /organizations/{id}                   # Update organization
    │
    ├── /organizations/{org_id}/locations
    │   ├── GET    /organizations/{org_id}/locations     # List locations
    │   ├── POST   /organizations/{org_id}/locations     # Create location
    │   ├── GET    /organizations/{org_id}/locations/{id}  # Get location details
    │   └── PATCH  /organizations/{org_id}/locations/{id}  # Update location
    │
    ├── /locations/{location_id}/rooms
    │   ├── GET    /locations/{location_id}/rooms       # List rooms
    │   ├── POST   /locations/{location_id}/rooms       # Create room
    │   ├── GET    /locations/{location_id}/rooms/{id}  # Get room details
    │   └── PATCH  /locations/{location_id}/rooms/{id}  # Update room
    │
    ├── /rooms/{room_id}/devices
    │   ├── GET    /rooms/{room_id}/devices             # List devices in room
    │   ├── POST   /rooms/{room_id}/devices             # Add device to room
    │   ├── GET    /rooms/{room_id}/devices/{id}        # Get device details
    │   └── DELETE /rooms/{room_id}/devices/{id}        # Remove device
    │
    ├── /rooms/{room_id}/control
    │   ├── POST   /rooms/{room_id}/control/power       # Power control
    │   ├── POST   /rooms/{room_id}/control/source      # Source selection
    │   ├── POST   /rooms/{room_id}/control/volume      # Volume control
    │   └── POST   /rooms/{room_id}/control/command     # Send command (D-pad, etc.)
    │
    └── /devices/{device_id}/control
        ├── POST   /devices/{device_id}/control/power
        ├── POST   /devices/{device_id}/control/command
        └── GET    /devices/{device_id}/status
```

## Example URLs

### Real-World Examples:

**Residential:**
```
Organization: John Smith Family
Location: Home

https://app.mediacontrol.com/org/john-smith-family
https://app.mediacontrol.com/org/john-smith-family/location/home
https://app.mediacontrol.com/org/john-smith-family/location/home/room/living-room
https://app.mediacontrol.com/org/john-smith-family/location/home/room/bedroom
```

**Hotel Chain:**
```
Organization: Hilton Hotels International
Locations: Dubai Marina, Mumbai Central, NYC Times Square

https://app.mediacontrol.com/org/hilton-hotels
https://app.mediacontrol.com/org/hilton-hotels/location/dubai-marina
https://app.mediacontrol.com/org/hilton-hotels/location/dubai-marina/room/suite-301
https://app.mediacontrol.com/org/hilton-hotels/location/mumbai-central/room/presidential-suite
https://app.mediacontrol.com/org/hilton-hotels/location/nyc-times-square/room/conference-a
```

**Corporate:**
```
Organization: Acme Corporation
Locations: HQ Dubai, Regional Office Mumbai, Sales Office London

https://app.mediacontrol.com/org/acme-corp
https://app.mediacontrol.com/org/acme-corp/location/hq-dubai
https://app.mediacontrol.com/org/acme-corp/location/hq-dubai/room/boardroom
https://app.mediacontrol.com/org/acme-corp/location/mumbai-office/room/training-room-1
https://app.mediacontrol.com/org/acme-corp/location/london-sales/room/demo-room
```

**Embeddable Widgets (for KNX panels):**
```
https://widget.mediacontrol.com/hilton-hotels/dubai-marina/suite-301?token=xyz123
https://widget.mediacontrol.com/acme-corp/hq-dubai/boardroom?token=abc456
https://widget.mediacontrol.com/john-smith-family/home/living-room?token=def789
```

## URL Slug Generation

Rules:
- Lowercase only
- Spaces → hyphens
- Remove special characters
- Ensure uniqueness
- Max 50 characters

Examples:
```
"John Smith's Home"      → "john-smiths-home"
"Grand Hotel Dubai"      → "grand-hotel-dubai"
"Conference Room A"      → "conference-room-a"
"Suite 301 (Premium)"    → "suite-301-premium"
```

If duplicate:
```
"Living Room" → "living-room"
"Living Room" (2nd) → "living-room-2"
"Living Room" (3rd) → "living-room-3"
```

## API Request Examples

### Get Organization by Slug
```bash
GET /api/v1/organizations/slug/hilton-hotels
Authorization: Bearer {api_key}

Response:
{
  "id": "org_abc123",
  "name": "Hilton Hotels International",
  "url_slug": "hilton-hotels",
  "organization_type": "hotel_chain",
  "location_count": 18,
  "room_count": 450,
  "device_count": 1350,
  "subscription": {
    "tier": "enterprise",
    "status": "active"
  },
  "urls": {
    "dashboard": "https://app.mediacontrol.com/org/hilton-hotels",
    "locations": "https://app.mediacontrol.com/org/hilton-hotels/locations",
    "api": "https://api.mediacontrol.com/v1/organizations/org_abc123"
  }
}
```

### Get Location by Slug
```bash
GET /api/v1/locations/slug/dubai-marina
Authorization: Bearer {api_key}

Response:
{
  "id": "loc_xyz456",
  "organization_id": "org_abc123",
  "name": "Hilton Dubai Marina",
  "url_slug": "dubai-marina",
  "address": "123 Sheikh Zayed Road, Dubai",
  "room_count": 150,
  "device_count": 450,
  "urls": {
    "dashboard": "https://app.mediacontrol.com/org/hilton-hotels/location/dubai-marina",
    "rooms": "https://app.mediacontrol.com/org/hilton-hotels/location/dubai-marina/rooms",
    "api": "https://api.mediacontrol.com/v1/locations/loc_xyz456"
  }
}
```

### Get Room by Slug
```bash
GET /api/v1/locations/loc_xyz456/rooms/slug/suite-301
Authorization: Bearer {api_key}

Response:
{
  "id": "room_def789",
  "location_id": "loc_xyz456",
  "organization_id": "org_abc123",
  "name": "Suite 301",
  "url_slug": "suite-301",
  "floor": "3",
  "device_count": 3,
  "devices": [
    {
      "id": "dev_001",
      "type": "display",
      "name": "Samsung Flip 85",
      "model": "WM85R"
    },
    {
      "id": "dev_002",
      "type": "stb",
      "name": "OSN STB",
      "provider": "osn"
    },
    {
      "id": "dev_003",
      "type": "apple_tv",
      "name": "Apple TV 4K"
    }
  ],
  "urls": {
    "control": "https://app.mediacontrol.com/org/hilton-hotels/location/dubai-marina/room/suite-301",
    "widget": "https://widget.mediacontrol.com/hilton-hotels/dubai-marina/suite-301",
    "api": "https://api.mediacontrol.com/v1/rooms/room_def789"
  }
}
```

### Control Room Device
```bash
POST /api/v1/rooms/room_def789/control/source
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "preset": "Netflix"
}

Response:
{
  "success": true,
  "actions": [
    "Switched display to HDMI 2",
    "Powered on Apple TV",
    "Launched Netflix app"
  ],
  "active_source": "apple-tv"
}
```

## Flask/FastAPI Implementation

```python
from flask import Flask, jsonify, request
from location_manager import LocationManager

app = Flask(__name__)
location_mgr = LocationManager()

@app.route('/location/<slug>')
def location_dashboard(slug):
    \"\"\"Location dashboard page\"\"\"
    location = location_mgr.get_location_by_slug(slug)
    if not location:
        return "Location not found", 404
    
    rooms = location_mgr.get_location_rooms(location.id)
    devices = location_mgr.get_location_devices(location.id)
    
    return render_template('location_dashboard.html',
                          location=location,
                          rooms=rooms,
                          devices=devices)

@app.route('/location/<location_slug>/room/<room_slug>')
def room_control(location_slug, room_slug):
    \"\"\"Room control page\"\"\"
    location = location_mgr.get_location_by_slug(location_slug)
    if not location:
        return "Location not found", 404
    
    room = location_mgr.get_room_by_slug(location.id, room_slug)
    if not room:
        return "Room not found", 404
    
    devices = location_mgr.get_room_devices(room.id)
    
    return render_template('room_control.html',
                          location=location,
                          room=room,
                          devices=devices)

@app.route('/widget/<location_slug>/<room_slug>')
def widget(location_slug, room_slug):
    \"\"\"Embeddable widget\"\"\"
    token = request.args.get('token')
    
    # Validate token
    # ...
    
    location = location_mgr.get_location_by_slug(location_slug)
    room = location_mgr.get_room_by_slug(location.id, room_slug)
    
    return render_template('widget.html',
                          location=location,
                          room=room)

# API Routes
@app.route('/api/v1/locations/slug/<slug>')
def api_location_by_slug(slug):
    \"\"\"Get location by slug\"\"\"
    location = location_mgr.get_location_by_slug(slug)
    if not location:
        return jsonify({"error": "Not found"}), 404
    
    rooms = location_mgr.get_location_rooms(location.id)
    devices = location_mgr.get_location_devices(location.id)
    
    return jsonify({
        "id": location.id,
        "name": location.name,
        "url_slug": location.url_slug,
        "address": location.address,
        "room_count": len(rooms),
        "device_count": len(devices),
        "urls": {
            "dashboard": f"/location/{location.url_slug}",
            "api": f"/api/v1/locations/{location.id}"
        }
    })

@app.route('/api/v1/locations/<location_id>/rooms/slug/<slug>')
def api_room_by_slug(location_id, slug):
    \"\"\"Get room by slug\"\"\"
    room = location_mgr.get_room_by_slug(location_id, slug)
    if not room:
        return jsonify({"error": "Not found"}), 404
    
    devices = location_mgr.get_room_devices(room.id)
    
    return jsonify({
        "id": room.id,
        "location_id": room.location_id,
        "name": room.name,
        "url_slug": room.url_slug,
        "floor": room.floor,
        "device_count": len(devices),
        "devices": [
            {
                "id": d.id,
                "type": d.type,
                "name": d.name,
                "model": d.model
            }
            for d in devices
        ]
    })
```

## Benefits of This URL Structure

1. **SEO-Friendly**: Descriptive slugs instead of IDs
2. **Shareable**: Easy to remember and share
3. **Hierarchical**: Clear parent-child relationships
4. **Bookmarkable**: Users can bookmark specific rooms
5. **Embeddable**: Clean URLs for iframe widgets
6. **Multi-tenant**: Each location is isolated
7. **Scalable**: Works for 1 room or 1000+ rooms

## Security

Each URL requires authentication:
- Cookie-based session (web app)
- JWT token (API)
- Signed token (embeddable widget)

Access control:
- Users can only access their location
- Admins can see all locations
- Room users can only access assigned rooms
