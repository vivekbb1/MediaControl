# URL ROUTING STRUCTURE

Complete URL schema for locations, rooms, and devices with friendly slugs

## URL Structure

```
/ app.mediacontrol.com
├── /location/{location_slug}                    # Location dashboard
│   ├── /location/{location_slug}/room/{room_slug}       # Room control
│   ├── /location/{location_slug}/devices                # All devices
│   ├── /location/{location_slug}/settings               # Location settings
│   ├── /location/{location_slug}/billing                # Subscription & billing
│   └── /location/{location_slug}/users                  # User management
│
├── /widget/{location_slug}/{room_slug}          # Embeddable widget
│
└── /api/v1
    ├── /locations
    │   ├── GET    /locations                           # List all locations (admin)
    │   ├── POST   /locations                           # Create location
    │   ├── GET    /locations/{id}                      # Get location details
    │   ├── GET    /locations/slug/{slug}               # Get by slug
    │   └── PATCH  /locations/{id}                      # Update location
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
https://app.mediacontrol.com/location/john-smiths-home
https://app.mediacontrol.com/location/john-smiths-home/room/living-room
https://app.mediacontrol.com/location/john-smiths-home/room/bedroom
```

**Hotel:**
```
https://app.mediacontrol.com/location/grand-hotel-dubai
https://app.mediacontrol.com/location/grand-hotel-dubai/room/suite-301
https://app.mediacontrol.com/location/grand-hotel-dubai/room/conference-a
```

**Corporate:**
```
https://app.mediacontrol.com/location/acme-corp
https://app.mediacontrol.com/location/acme-corp/room/boardroom
https://app.mediacontrol.com/location/acme-corp/room/training-room-2
```

**Embeddable Widgets (for KNX panels):**
```
https://widget.mediacontrol.com/grand-hotel-dubai/suite-301?token=xyz123
https://widget.mediacontrol.com/acme-corp/boardroom?token=abc456
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

### Get Location by Slug
```bash
GET /api/v1/locations/slug/grand-hotel-dubai
Authorization: Bearer {api_key}

Response:
{
  "id": "loc_abc123",
  "name": "Grand Hotel Dubai",
  "url_slug": "grand-hotel-dubai",
  "address": "123 Sheikh Zayed Road, Dubai",
  "room_count": 150,
  "device_count": 450,
  "subscription": {
    "tier": "enterprise",
    "status": "active"
  },
  "urls": {
    "dashboard": "https://app.mediacontrol.com/location/grand-hotel-dubai",
    "rooms": "https://app.mediacontrol.com/location/grand-hotel-dubai/rooms",
    "api": "https://api.mediacontrol.com/v1/locations/loc_abc123"
  }
}
```

### Get Room by Slug
```bash
GET /api/v1/locations/loc_abc123/rooms/slug/suite-301
Authorization: Bearer {api_key}

Response:
{
  "id": "room_xyz789",
  "location_id": "loc_abc123",
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
    "control": "https://app.mediacontrol.com/location/grand-hotel-dubai/room/suite-301",
    "widget": "https://widget.mediacontrol.com/grand-hotel-dubai/suite-301",
    "api": "https://api.mediacontrol.com/v1/rooms/room_xyz789"
  }
}
```

### Control Room Device
```bash
POST /api/v1/rooms/room_xyz789/control/source
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
