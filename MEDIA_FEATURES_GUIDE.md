# COMPREHENSIVE MEDIA FEATURES GUIDE

Complete guide to advanced media features: streaming services, screen recording, EPG alerts, alarms, and music management

---

## ⚖️ LEGAL NOTICE

**IMPORTANT:** MediaControl is a device control system, NOT a content provider.

- ✅ Users MUST have valid subscriptions to all streaming services
- ✅ Users MUST comply with copyright laws and service terms  
- ✅ Content accessed through official APIs with user's credentials only
- ❌ NO piracy tools, DRM bypass, or unauthorized content access

**See [LEGAL_COMPLIANCE.md](../LEGAL_COMPLIANCE.md) for complete legal requirements.**

---

## Table of Contents
1. [Media Services Integration](#media-services-integration)
2. [Screen Recording](#screen-recording)
3. [EPG Alerts & Notifications](#epg-alerts--notifications)
4. [Alarms & Scheduling](#alarms--scheduling)
5. [Music Library Management](#music-library-management)
6. [API Integration](#api-integration)
7. [Mobile App Features](#mobile-app-features)

---

## Media Services Integration

### Supported Services

#### ✅ Fully Integrated:
- **Spotify** - Full playback control, library access, playlist management
- **Apple Music** - Search, playback, library access
- **YouTube** - Video playback, search
- **YouTube Music** - Music playback, playlists
- **Amazon Music** - Playback control
- **Prime Video** - Video streaming
- **SoundCloud** - Audio streaming
- **Tidal** - High-quality audio streaming
- **Deezer** - Music streaming
- **Pandora** - Radio-style streaming

#### 🎬 Video Services:
- **Netflix** - App launching via Apple TV/Android TV
- **Disney+** - App launching
- **Hulu** - App launching
- **HBO Max** - App launching
- **Prime Video** - Full API integration
- **Plex** - Local media server
- **Jellyfin** - Open-source media server

### Features

**Unified Control:**
- Search across all services simultaneously
- Playback control (play/pause/skip)
- Volume management
- Queue management
- Playlist creation and editing

**Smart Integration:**
- Auto-select best quality service
- Cross-service playlists
- Service-specific features preserved
- Offline fallback

**Library Sync:**
- Import favorites from all services
- Unified "My Music" view
- Cross-service search
- Play count tracking

### Setup

#### Spotify Setup
```python
from media_services import MediaServiceManager, MediaServiceType

media_mgr = MediaServiceManager()

# Register Spotify
media_mgr.register_spotify(
    client_id="your_spotify_client_id",
    client_secret="your_spotify_client_secret",
    redirect_uri="http://localhost:8888/callback"
)

# Search Spotify
tracks = await media_mgr.get_service(MediaServiceType.SPOTIFY).search(
    query="Daft Punk",
    limit=10
)

# Play on device
await media_mgr.play_on_service(
    service_type=MediaServiceType.SPOTIFY,
    device_id="kitchen_sonos_spotify",
    track_uri="spotify:track:0DiWol3AO6WpXZgp0goxAV"
)
```

#### Apple Music Setup
```python
# Register Apple Music
media_mgr.register_apple_music(
    developer_token="your_jwt_token",
    user_token="user_music_token"
)

# Search Apple Music
tracks = await media_mgr.get_service(MediaServiceType.APPLE_MUSIC).search(
    query="Taylor Swift"
)
```

#### YouTube Integration
```python
# YouTube Data API
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey=API_KEY)

# Search videos
request = youtube.search().list(
    part="snippet",
    q="music video",
    type="video",
    maxResults=10
)
response = request.execute()
```

### Room Presets with Media Services

```yaml
presets:
  morning_playlist:
    name: "Morning Music"
    actions:
      - type: media_service
        service: spotify
        action: play_playlist
        playlist_uri: "spotify:playlist:37i9dQZF1DX0H9VYs5EqYz"
        device: kitchen_sonos
        volume: 40
  
  workout_mode:
    name: "Workout"
    actions:
      - type: media_service
        service: apple_music
        action: play_playlist
        playlist_id: "pl.workout123"
        device: gym_speakers
        volume: 80
  
  movie_night:
    name: "Movie Night"
    actions:
      - type: display_power
        device: main_tv
        state: on
      - type: source_app
        device: apple_tv
        app: Netflix
      - type: media_service
        service: spotify
        action: stop  # Stop music before movie
```

---

## Screen Recording

### Overview
Record video from any display or HDMI encoder in real-time.

### Features
- **Multiple Quality Settings:** Low (720p), Medium (1080p), High (1080p HQ), Ultra (4K)
- **Flexible Formats:** MP4, MKV, MOV, AVI
- **Auto-Stop:** Schedule max duration
- **Audio Capture:** Include audio from sources
- **Live Status:** Monitor recording progress in real-time

### Use Cases
- **Conference Room Recording:** Record presentations and meetings
- **Training Sessions:** Capture training content
- **Legal/Compliance:** Record for documentation
- **Content Creation:** Create tutorials and demos

### Setup

```python
from screen_recording import RecordingManager, RecordingSettings, RecordingQuality

rec_mgr = RecordingManager()

# Register device for recording
rec_mgr.register_device(
    device_id="conference_room_display",
    device_name="Conference Room Display",
    stream_url="rtsp://192.168.1.100:554/stream1",
    settings=RecordingSettings(
        quality=RecordingQuality.HIGH,
        format=RecordingFormat.MP4,
        audio_enabled=True,
        max_duration_minutes=120,  # Auto-stop after 2 hours
        output_directory="/var/recordings"
    )
)

# Start recording
recording = rec_mgr.start_recording("conference_room_display")

# Check status
status = rec_mgr.get_device_status("conference_room_display")
print(f"Recording: {status['recording']['duration_seconds']}s")
print(f"File size: {status['recording']['file_size_mb']}MB")

# Stop recording
completed_recording = rec_mgr.stop_recording("conference_room_display")
print(f"Saved to: {completed_recording.file_path}")
```

### API Integration

```http
# Start recording
POST /api/v1/recording/start
{
  "device_id": "conference_room_display"
}

# Get status
GET /api/v1/recording/status/conference_room_display

# Stop recording
POST /api/v1/recording/stop
{
  "device_id": "conference_room_display"
}

# Get recording history
GET /api/v1/recordings?limit=50

# Download recording
GET /api/v1/recordings/{recording_id}/download

# Delete recording
DELETE /api/v1/recordings/{recording_id}
```

### Automated Recording with Presets

```yaml
presets:
  record_meeting:
    name: "Record Meeting"
    actions:
      - type: recording_start
        device: conference_display
      - type: display_power
        device: conference_display
        state: on
      - type: notification
        message: "Meeting recording started"
  
  stop_and_share:
    name: "Stop Recording & Share"
    actions:
      - type: recording_stop
        device: conference_display
      - type: notification
        message: "Recording saved. Uploading to cloud..."
      - type: custom
        function: upload_to_cloud
```

---

## EPG Alerts & Notifications

### Overview
Never miss your favorite TV shows with smart EPG reminders and automatic recording scheduling.

### Features
- **Smart Reminders:** Get notified before shows start (configurable lead time)
- **Auto-Recording:** Automatically record shows when alerts trigger
- **Multi-Channel Notifications:** Push, email, SMS, on-screen, webhook
- **Favorite Shows:** Auto-create alerts for your favorite series
- **Recurring Alerts:** Weekly series automatically get alerts for all episodes

### Setup

```python
from epg_alerts import EPGAlertManager, NotificationChannel, AlertType
from epg_client import EPGClient
from screen_recording import RecordingManager

# Initialize
epg_client = EPGClient(epg_url="http://epg.example.com/xmltv.xml")
rec_mgr = RecordingManager()
alert_mgr = EPGAlertManager(epg_client=epg_client, recording_manager=rec_mgr)

# Register notification handlers
alert_mgr.register_notification_handler(
    NotificationChannel.PUSH,
    push_notification_handler
)
alert_mgr.register_notification_handler(
    NotificationChannel.EMAIL,
    email_notification_handler
)

# Create alert for specific show
alert = alert_mgr.create_alert(
    user_id="user_123",
    channel_id="hbo",
    channel_name="HBO",
    show_title="Game of Thrones",
    show_start=datetime(2026, 8, 1, 21, 0),  # 9 PM
    show_end=datetime(2026, 8, 1, 22, 0),
    alert_minutes_before=15,  # Notify 15 min before
    auto_record=True,  # Automatically record
    channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL]
)

# Or create from EPG data
alert = alert_mgr.create_alert_from_epg(
    user_id="user_123",
    channel_id="hbo",
    show_id="show_456",
    alert_minutes_before=15,
    auto_record=True
)

# Start alert manager
await alert_mgr.start()
```

### User Preferences

```yaml
users:
  user_123:
    email: "user@example.com"
    phone: "+1234567890"
    fcm_token: "firebase_push_token"
    
    preferences:
      default_alert_minutes: 10
      notification_channels:
        - push
        - email
      auto_record_favorites: true
    
    favorite_shows:
      - show_title: "Breaking Bad"
        channel_id: "amc"
        auto_record: true
      - show_title: "The Office"
        channel_id: "nbc"
        auto_record: false
```

### API Integration

```http
# Create alert
POST /api/v1/epg/alerts
{
  "user_id": "user_123",
  "channel_id": "hbo",
  "show_id": "show_456",
  "alert_minutes_before": 15,
  "auto_record": true,
  "notification_channels": ["push", "email"]
}

# Get user's alerts
GET /api/v1/epg/alerts?user_id=user_123&upcoming=true

# Delete alert
DELETE /api/v1/epg/alerts/{alert_id}

# Get notifications
GET /api/v1/notifications?user_id=user_123&limit=50
```

---

## Alarms & Scheduling

### Overview
Automate your smart home with powerful scheduling and alarm capabilities.

### Features
- **Multiple Schedule Types:**
  - One-time: Execute once at specific time
  - Daily: Repeat every day
  - Weekly: Repeat on specific days
  - Interval: Repeat every X minutes/hours
  - Cron: Advanced cron expressions

- **Action Types:**
  - Display control (power, input)
  - Source control (power, app launching)
  - Room presets
  - Recording start/stop
  - Audio playback and volume
  - Media service control
  - Notifications
  - KNX scenes
  - Custom functions

### Common Use Cases

#### Morning Wake-Up Routine
```python
from alarm_scheduler import AlarmScheduler, ScheduledAction, ActionType
from datetime import time

scheduler = AlarmScheduler()

morning_actions = [
    ScheduledAction(
        type=ActionType.AUDIO_VOLUME,
        parameters={"device": "bedroom_speakers", "volume": 0}
    ),
    ScheduledAction(
        type=ActionType.MEDIA_SERVICE,
        parameters={
            "service": "spotify",
            "action": "play_playlist",
            "playlist_uri": "spotify:playlist:37i9dQZF1DX0H9VYs5EqYz",
            "device": "bedroom_speakers"
        }
    ),
    ScheduledAction(
        type=ActionType.AUDIO_VOLUME,
        parameters={
            "device": "bedroom_speakers",
            "volume": 30,
            "fade_duration": 30  # Fade in over 30 seconds
        }
    ),
    ScheduledAction(
        type=ActionType.NOTIFICATION,
        parameters={
            "message": "Good morning! Time to wake up.",
            "channels": ["on_screen", "push"]
        }
    )
]

alarm = scheduler.create_daily_alarm(
    user_id="user_123",
    name="Morning Wake-Up",
    time_of_day=time(7, 0),  # 7:00 AM
    actions=morning_actions
)

# Start scheduler
await scheduler.start()
```

#### Weekly Movie Night
```python
movie_night_actions = [
    ScheduledAction(
        type=ActionType.PRESET,
        parameters={"preset": "movie_night"}
    ),
    ScheduledAction(
        type=ActionType.NOTIFICATION,
        parameters={"message": "Movie night! Ready to watch?"}
    )
]

alarm = scheduler.create_weekly_alarm(
    user_id="user_123",
    name="Friday Movie Night",
    time_of_day=time(20, 0),  # 8:00 PM
    days_of_week=[4],  # Friday (0=Monday, 4=Friday)
    actions=movie_night_actions
)
```

#### Bedtime Routine
```python
bedtime_actions = [
    ScheduledAction(
        type=ActionType.NOTIFICATION,
        parameters={
            "message": "Time for bed. Turning off devices in 5 minutes.",
            "channels": ["push", "on_screen"]
        }
    ),
    # Wait 5 minutes (would need interval or custom handler)
    ScheduledAction(
        type=ActionType.AUDIO_VOLUME,
        parameters={
            "device": "all",
            "volume": 0,
            "fade_duration": 60
        }
    ),
    ScheduledAction(
        type=ActionType.DISPLAY_POWER,
        parameters={"device": "all", "state": "off"}
    )
]

alarm = scheduler.create_daily_alarm(
    user_id="user_123",
    name="Bedtime",
    time_of_day=time(22, 30),  # 10:30 PM
    actions=bedtime_actions
)
```

### Advanced Scheduling with Cron

```python
# Every weekday at 8 AM
alarm = scheduler.create_alarm(
    user_id="user_123",
    name="Weekday Morning",
    schedule_type=ScheduleType.CRON,
    cron_expression="0 8 * * 1-5",  # Mon-Fri at 8:00
    actions=morning_actions
)

# Every 2 hours
alarm = scheduler.create_alarm(
    user_id="user_123",
    name="Check System",
    schedule_type=ScheduleType.INTERVAL,
    interval_minutes=120,
    actions=[
        ScheduledAction(
            type=ActionType.CUSTOM,
            parameters={"function": "system_health_check"}
        )
    ]
)
```

---

## Music Library Management

### Overview
Unified music library that aggregates content from all your streaming services.

### Features
- **Multi-Service Library:** Import from Spotify, Apple Music, YouTube Music, etc.
- **Smart Playlists:** Auto-populated playlists based on criteria
- **Play Count Tracking:** See what you listen to most
- **Cross-Service Search:** Find music across all services
- **Favorites & Tags:** Organize your music your way
- **Collections:** Create playlists that span multiple services

### Setup

```python
from music_library import MusicLibrary, LibraryItem, LibraryItemType

# Initialize
library = MusicLibrary(user_id="user_123")

# Import from Spotify
spotify_service = media_mgr.get_service(MediaServiceType.SPOTIFY)
spotify_tracks = await spotify_service.get_user_playlists()

for playlist in spotify_tracks:
    tracks = await spotify_service.get_playlist(playlist.id)
    for track in tracks:
        library_item = LibraryItem(
            id=f"spotify_{track.id}",
            type=LibraryItemType.TRACK,
            title=track.title,
            artist=track.artist,
            album=track.album,
            duration_ms=track.duration_ms,
            service="spotify",
            service_id=track.id
        )
        library.add_item(library_item)

# Import from Apple Music
apple_tracks = await apple_music_service.get_user_library()
# ... similar import process

# Create playlist
gym_playlist = library.create_collection(
    name="Gym Playlist",
    description="High energy workout music"
)

# Add tracks to playlist
workout_tracks = library.search(tags={"workout", "high_energy"})
for track in workout_tracks[:30]:
    library.add_to_collection(gym_playlist.id, track.id)

# Create smart playlist
favorites = library.create_smart_playlist(
    name="My Top 50",
    criteria={
        "favorites_only": True,
        "min_play_count": 5,
        "sort_by": "play_count",
        "max_items": 50
    }
)

# Search library
results = library.search(
    query="Daft Punk",
    type=LibraryItemType.TRACK,
    favorites_only=False
)

# Get stats
recently_played = library.get_recently_played(limit=20)
most_played = library.get_most_played(limit=20)

# Export library
json_export = library.export_to_json()
```

### Smart Playlist Criteria

```python
# High-energy workout music
workout = library.create_smart_playlist(
    name="Workout Mix",
    criteria={
        "tags": {"workout", "high_energy", "edm"},
        "min_play_count": 3,
        "sort_by": "play_count",
        "max_items": 100
    }
)

# Recently added favorites
new_favorites = library.create_smart_playlist(
    name="New Favorites",
    criteria={
        "favorites_only": True,
        "sort_by": "recently_added",
        "max_items": 30
    }
)

# Top Spotify tracks
spotify_top = library.create_smart_playlist(
    name="Spotify Hits",
    criteria={
        "service": "spotify",
        "min_play_count": 10,
        "sort_by": "play_count",
        "max_items": 50
    }
)
```

---

## API Integration

### RESTful API Endpoints

```http
# === Media Services ===
GET    /api/v1/media/search?q=query&services=spotify,apple_music
POST   /api/v1/media/play
POST   /api/v1/media/pause
POST   /api/v1/media/next
GET    /api/v1/media/status

# === Screen Recording ===
POST   /api/v1/recording/start
POST   /api/v1/recording/stop
GET    /api/v1/recording/status/{device_id}
GET    /api/v1/recordings
GET    /api/v1/recordings/{id}/download
DELETE /api/v1/recordings/{id}

# === EPG Alerts ===
POST   /api/v1/epg/alerts
GET    /api/v1/epg/alerts?user_id={id}&upcoming=true
DELETE /api/v1/epg/alerts/{id}
GET    /api/v1/notifications

# === Alarms & Scheduling ===
POST   /api/v1/alarms
GET    /api/v1/alarms?user_id={id}
PATCH  /api/v1/alarms/{id}
DELETE /api/v1/alarms/{id}
POST   /api/v1/alarms/{id}/enable
POST   /api/v1/alarms/{id}/disable

# === Music Library ===
GET    /api/v1/library/search?q=query
POST   /api/v1/library/items
GET    /api/v1/library/favorites
GET    /api/v1/library/recently-played
GET    /api/v1/library/most-played
POST   /api/v1/library/collections
POST   /api/v1/library/smart-playlists
GET    /api/v1/library/export
```

---

## Mobile App Features

### Push Notifications
- EPG show reminders
- Recording started/completed
- Alarm triggers
- System alerts

### Widgets
- Now Playing widget
- Upcoming shows widget
- Quick controls widget
- Recording status widget

### Voice Control
- "Play my morning playlist on kitchen speakers"
- "Record the game on channel 5"
- "Remind me when Breaking Bad starts"
- "Turn on Netflix in the living room at 8 PM"

---

## Summary

This comprehensive media system provides:

✅ **All Major Streaming Services** - Spotify, Apple Music, YouTube, Prime, and more  
✅ **Screen Recording** - Record any display or HDMI source  
✅ **EPG Alerts** - Never miss your favorite shows  
✅ **Smart Scheduling** - Automate everything  
✅ **Unified Music Library** - All your music in one place  
✅ **Multi-Channel Notifications** - Push, email, SMS, on-screen  
✅ **Cross-Platform** - iOS, Android, Web, KNX panels  
✅ **API-First Design** - Easy integration with any system  

This transforms your multimedia system into a complete entertainment automation platform.
