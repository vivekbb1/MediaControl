# ADVANCED AUDIO FEATURES GUIDE

Complete guide to advanced audio features: visualizers, voice control, DSP, and scheduled automation

---

## Table of Contents
1. [Audio Visualizers & Video Streaming](#audio-visualizers--video-streaming)
2. [Voice Control (Alexa & Google Assistant)](#voice-control)
3. [Advanced Audio DSP](#advanced-audio-dsp)
4. [Scheduled Audio Automation](#scheduled-audio-automation)
5. [Enhanced Media Service Integration](#enhanced-media-service-integration)

---

## Audio Visualizers & Video Streaming

### Overview
Generate real-time audio visualizations and stream them to displays alongside music playback.

### Supported Visualizer Types:
- **Spectrum** - Frequency spectrum bars (classic equalizer view)
- **Waveform** - Audio waveform display
- **Circular** - Circular spectrum (iTunes-style)
- **Particles** - Particle effects synchronized to music
- **Album Art** - Album artwork with animated effects
- **VU Meter** - Classic VU meters
- **Lyrics** - Synchronized lyrics display (via Musixmatch API)
- **Oscilloscope** - Oscilloscope view

### Visual Styles:
- Minimal, Colorful, Neon, Retro, Ambient

### Usage

```python
from audio_visualizer import AudioVisualizer, VisualizerConfig, VisualizerType, VisualizerStyle

viz = AudioVisualizer()

# Create visualizer for Spotify playback
viz_config = VisualizerConfig(
    type=VisualizerType.SPECTRUM,
    style=VisualizerStyle.NEON,
    resolution="1920x1080",
    fps=30,
    show_track_info=True,
    show_album_art=True,
    show_lyrics=True,
    color_scheme="#FF0066,#00FFFF,#FFFF00"
)

# Generate visualizer stream
viz_url = viz.get_spotify_visualizer_url(
    spotify_device_id="living_room_tv",
    config=viz_config
)

# Play visualizer on TV
# video_player.play(viz_url)
# Returns: http://localhost:8080/visualizer/spotify_living_room_tv/stream.m3u8
```

### Room Preset with Visualizer

```yaml
presets:
  party_mode_visual:
    name: "Party Mode with Visuals"
    actions:
      # Start music on Sonos
      - type: media_service
        service: spotify
        action: play_playlist
        playlist_uri: "spotify:playlist:party"
        device: living_room_sonos
      
      # Create visualizer stream
      - type: create_visualizer
        audio_source: living_room_sonos
        visualizer_type: spectrum
        style: neon
        resolution: 1920x1080
      
      # Display visualizer on TV
      - type: video_stream
        device: living_room_tv
        source: visualizer_stream
      
      # Sync KNX lighting to music
      - type: knx_scene
        scene: music_reactive_lights
```

### API Endpoints

```http
# Create visualizer
POST /api/v1/visualizer/create
{
  "audio_source": "living_room_sonos",
  "type": "spectrum",
  "style": "neon",
  "resolution": "1920x1080",
  "show_track_info": true,
  "show_lyrics": true
}

# Response
{
  "stream_url": "http://localhost:8080/visualizer/xyz/stream.m3u8",
  "status": "active"
}

# Get all active visualizers
GET /api/v1/visualizer/streams

# Stop visualizer
DELETE /api/v1/visualizer/{stream_id}

# Get synchronized lyrics
GET /api/v1/lyrics?track=Bohemian+Rhapsody&artist=Queen
```

---

## Voice Control

### Overview
Control your media system using Alexa or Google Assistant voice commands.

### Supported Voice Assistants:
- ✅ Amazon Alexa (via Alexa Skills Kit)
- ✅ Google Assistant (via Actions on Google)
- ✅ Siri (via HomeKit integration - future)

### Supported Commands:

**Music Control:**
- "Alexa, play music in the living room"
- "Alexa, play Daft Punk in the bedroom"
- "Alexa, play my workout playlist"
- "Alexa, pause music"
- "Alexa, next track"
- "Alexa, volume to 50"

**Device Control:**
- "Alexa, turn on the TV in the living room"
- "Alexa, turn off the bedroom TV"
- "Alexa, switch to HDMI 2"

**Presets:**
- "Alexa, activate movie night"
- "Alexa, start party mode"
- "Alexa, activate morning routine"

**TV Control:**
- "Alexa, tune to channel 5"
- "Alexa, record Breaking Bad"
- "Alexa, open Netflix"

### Setup

#### Alexa Skill

```python
from voice_control import AlexaSkillHandler

# Initialize handler
alexa = AlexaSkillHandler(
    skill_id="amzn1.ask.skill.xyz",
    device_manager=device_mgr,
    media_manager=media_mgr
)

# Handle Alexa request (Flask endpoint)
@app.post("/alexa")
def alexa_skill():
    alexa_request = request.json
    response = alexa.handle_request(alexa_request)
    return response
```

#### Google Assistant Action

```python
from voice_control import GoogleAssistantHandler

# Initialize handler
assistant = GoogleAssistantHandler(
    project_id="mediacontrol-project",
    device_manager=device_mgr,
    media_manager=media_mgr
)

# Handle Google Assistant request
@app.post("/google-assistant")
def google_assistant_action():
    assistant_request = request.json
    response = assistant.handle_request(assistant_request)
    return response
```

### Alexa Skill Configuration

**Invocation Name:** "media control"

**Intents:**
- PlayMusicIntent
- PowerControlIntent
- VolumeControlIntent
- PresetIntent
- TuneChannelIntent
- RecordShowIntent

**Example Utterances:**
```
PlayMusicIntent:
  - play music in the {Room}
  - play {Artist} in the {Room}
  - play {Playlist} playlist
  - play some {Genre} music

PowerControlIntent:
  - turn {Action} the {Device} in the {Room}
  - power {Action} the {Device}

PresetIntent:
  - activate {Preset}
  - start {Preset} mode
```

### Room-Specific Control

Voice commands automatically detect room context:
- "Alexa, play music" (from Echo in living room) → plays in living room
- "Alexa, play music in the bedroom" → plays in bedroom
- "Alexa, play music everywhere" → plays in all rooms

---

## Advanced Audio DSP

### Overview
Professional-grade audio processing with equalizer, crossfade, ducking, compression, and limiting.

### Features

#### 1. Equalizer (EQ)

**10-Band Parametric EQ:**
- Frequencies: 32Hz, 64Hz, 125Hz, 250Hz, 500Hz, 1kHz, 2kHz, 4kHz, 8kHz, 16kHz
- Gain range: -12dB to +12dB per band
- Adjustable Q-factor (bandwidth)

**Presets:**
- Flat, Bass Boost, Treble Boost, Vocal
- Rock, Jazz, Classical, Electronic, Pop, Hip-Hop

```python
from audio_dsp import AudioDSPProcessor, EQPreset, EQBand

dsp = AudioDSPProcessor()

# Use preset
dsp.set_eq_preset("living_room_sonos", EQPreset.BASS_BOOST)

# Custom EQ
custom_eq = [
    EQBand(frequency=60, gain=6.0, q_factor=1.0),   # Deep bass boost
    EQBand(frequency=230, gain=3.0, q_factor=1.5),  # Mid-bass boost
    EQBand(frequency=1000, gain=-2.0, q_factor=2.0), # Midrange cut
    EQBand(frequency=4000, gain=4.0, q_factor=1.0),  # Presence boost
    EQBand(frequency=10000, gain=2.0, q_factor=1.0)  # Air boost
]
dsp.set_custom_eq("living_room_sonos", custom_eq)
```

#### 2. Crossfade

Smooth transitions between tracks with configurable duration and curve.

```python
# Enable crossfade
dsp.enable_crossfade(
    device_id="living_room_sonos",
    duration_ms=5000  # 5 second crossfade
)
```

**Curves:**
- Linear - Constant fade rate
- Exponential - Slow start, fast finish
- Logarithmic - Fast start, slow finish

#### 3. Audio Ducking

Automatically lower music volume during notifications, voice assistants, or announcements.

```python
# Enable ducking
dsp.enable_ducking(
    device_id="living_room_sonos",
    duck_level=0.2,      # Duck to 20% volume
    fade_in_ms=300       # 300ms fade
)

# Trigger ducking (e.g., during Alexa response)
dsp.apply_ducking("living_room_sonos", trigger=True)  # Duck
# ... Alexa speaks ...
dsp.apply_ducking("living_room_sonos", trigger=False)  # Restore
```

#### 4. Dynamic Range Compression

Control dynamic range for consistent loudness.

```python
from audio_dsp import AudioDSPConfig, CompressorConfig

config = AudioDSPConfig()
config.compressor = CompressorConfig(
    enabled=True,
    threshold=-20.0,  # dB
    ratio=4.0,        # 4:1 compression
    attack=5.0,       # ms
    release=100.0,    # ms
    makeup_gain=3.0   # dB
)

dsp.set_device_config("living_room_sonos", config)
```

#### 5. Limiter

Prevent audio clipping and protect speakers.

```python
config.limiter = LimiterConfig(
    enabled=True,
    threshold=-1.0,  # dB (brick wall)
    release=50.0     # ms
)
```

### Complete DSP Configuration

```python
from audio_dsp import (
    AudioDSPConfig, EqualizerConfig, CrossfadeConfig,
    DuckingConfig, CompressorConfig, LimiterConfig
)

# Complete config
config = AudioDSPConfig(
    equalizer=EqualizerConfig(
        preset=EQPreset.ROCK,
        enabled=True
    ),
    crossfade=CrossfadeConfig(
        enabled=True,
        duration_ms=4000,
        curve="exponential"
    ),
    ducking=DuckingConfig(
        enabled=True,
        duck_level=0.25,
        fade_in_ms=500,
        fade_out_ms=300
    ),
    compressor=CompressorConfig(
        enabled=True,
        threshold=-18.0,
        ratio=3.0
    ),
    limiter=LimiterConfig(
        enabled=True,
        threshold=-0.5
    ),
    master_volume=0.85
)

dsp.set_device_config("living_room_system", config)
```

### API Endpoints

```http
# Set EQ preset
POST /api/v1/audio/{device_id}/eq
{
  "preset": "bass_boost"
}

# Custom EQ
POST /api/v1/audio/{device_id}/eq
{
  "bands": [
    {"frequency": 60, "gain": 6.0},
    {"frequency": 1000, "gain": -2.0}
  ]
}

# Enable crossfade
POST /api/v1/audio/{device_id}/crossfade
{
  "duration_ms": 5000
}

# Enable ducking
POST /api/v1/audio/{device_id}/ducking
{
  "duck_level": 0.3,
  "fade_in_ms": 500
}

# Get complete DSP config
GET /api/v1/audio/{device_id}/dsp-config
```

### Room Presets with DSP

```yaml
presets:
  hifi_listening:
    name: "Hi-Fi Listening Mode"
    actions:
      - type: audio_dsp
        device: living_room_system
        equalizer:
          preset: classical
        compressor:
          enabled: true
          threshold: -20
          ratio: 2.5
        limiter:
          enabled: true
      
      - type: media_service
        service: tidal
        action: play_playlist
        playlist: "Classical Masters"
        quality: "HiFi"  # Lossless quality
  
  party_mode:
    name: "Party Mode"
    actions:
      - type: audio_dsp
        device: all_speakers
        equalizer:
          preset: bass_boost
        crossfade:
          enabled: true
          duration_ms: 5000
        ducking:
          enabled: false  # No ducking during party!
```

---

## Scheduled Audio Automation

### Overview
Advanced audio scheduling with gradual volume fades, automatic playlists, and genre-based automation.

### Features

- ✅ **Wake-up schedules** - Gradual volume increase over time
- ✅ **Sleep timers** - Gradual volume decrease and auto-stop
- ✅ **Workout schedules** - High-energy music at set times
- ✅ **Focus mode** - Concentration music during work hours
- ✅ **Dinner music** - Background ambience
- ✅ **Custom schedules** - Fully configurable

### Wake-Up Schedule

```python
from scheduled_audio import ScheduledAudioManager
from datetime import time

audio_scheduler = ScheduledAudioManager(
    alarm_scheduler=alarm_mgr,
    media_manager=media_mgr,
    audio_dsp=dsp
)

# Create wake-up schedule
wake_up = audio_scheduler.create_wake_up_schedule(
    name="Weekday Wake-Up",
    wake_time=time(7, 0),  # Target wake time: 7:00 AM
    days_of_week=[0, 1, 2, 3, 4],  # Monday-Friday
    devices=["bedroom_sonos"],
    playlist_uri="spotify:playlist:morning_vibes",
    fade_minutes=10  # Start at 6:50 AM, fade to full volume by 7:00 AM
)
```

**What happens:**
1. 6:50 AM - Music starts playing at 0% volume
2. 6:50-7:00 AM - Volume gradually increases from 0% to 40%
3. 7:00 AM - Full wake-up volume reached
4. EQ set to "vocal" preset for clear, crisp sound
5. Crossfade enabled for smooth track transitions

### Sleep Schedule

```python
# Create sleep schedule
sleep = audio_scheduler.create_sleep_schedule(
    name="Sleep Timer",
    sleep_time=time(22, 30),  # Start: 10:30 PM
    days_of_week=[0, 1, 2, 3, 4, 5, 6],  # Every day
    devices=["bedroom_sonos"],
    playlist_uri="spotify:playlist:sleep_sounds",
    fade_minutes=30  # Fade out over 30 minutes
)
```

**What happens:**
1. 10:30 PM - Sleep music starts at 30% volume
2. 10:30-11:00 PM - Volume gradually decreases to 0%
3. 11:00 PM - Music automatically stops
4. EQ set to "ambient" preset for soothing sound

### Workout Schedule

```python
# Create workout schedule
workout = audio_scheduler.create_workout_schedule(
    name="Morning Workout",
    workout_time=time(6, 0),
    days_of_week=[1, 3, 5],  # Tuesday, Thursday, Saturday
    devices=["gym_speakers"],
    duration_minutes=45
)
```

**What happens:**
1. 6:00 AM - Workout music starts at 70% volume
2. EQ set to "bass_boost" for motivation
3. Plays high-energy workout playlists
4. 6:45 AM - Automatically stops

### Custom Schedule

```yaml
# YAML configuration
scheduled_audio:
  focus_hours:
    name: "Focus Time"
    schedule_type: focus
    time: "09:00"
    days_of_week: [0, 1, 2, 3, 4]  # Weekdays
    service: spotify
    genre: "lo-fi beats"
    devices: [office_speakers]
    volume_start: 25
    volume_end: 25
    eq_preset: "flat"
    stop_after_minutes: 120  # 2 hours
  
  dinner_ambience:
    name: "Dinner Time"
    schedule_type: dinner
    time: "18:30"
    days_of_week: [0, 1, 2, 3, 4, 5, 6]
    service: apple_music
    playlist_uri: "pl.dinner_jazz"
    devices: [kitchen_sonos, dining_sonos]
    volume_start: 30
    eq_preset: "jazz"
    crossfade_enabled: true
    stop_after_minutes: 90
```

---

## Enhanced Media Service Integration

### Tidal Integration

High-fidelity audio streaming with MQA support.

```python
# Already included in media_services.py
# Usage same as Spotify/Apple Music

from media_services import MediaServiceType

# Play Tidal HiFi
await media_mgr.play_on_service(
    service_type=MediaServiceType.TIDAL,
    device_id="living_room_system",
    track_uri="tidal:track:12345",
    quality="HiFi"  # Lossless quality
)
```

### Multi-Service Smart Selection

Automatically choose best quality/availability across services:

```python
# Search all services
results = await media_mgr.search_all(
    query="Daft Punk - Get Lucky",
    limit=1
)

# Results from all services
{
    "spotify": [track1],
    "apple_music": [track2],
    "tidal": [track3_hifi],  # ← Best quality
    "youtube_music": [track4]
}

# Auto-select Tidal (highest quality available)
best_track = select_best_quality(results)
await media_mgr.play(best_track)
```

---

## Complete Integration Example

### "Morning Routine" with All Features

```yaml
presets:
  morning_routine:
    name: "Complete Morning Routine"
    trigger: scheduled  # Weekdays at 6:50 AM
    actions:
      # 1. Audio DSP Setup
      - type: audio_dsp
        device: bedroom_sonos
        equalizer:
          preset: vocal
        ducking:
          enabled: true
          duck_level: 0.3
      
      # 2. Start Music with Gradual Fade
      - type: scheduled_audio
        schedule: wake_up
        playlist: "Morning Vibes"
        volume_start: 0
        volume_end: 40
        fade_minutes: 10
      
      # 3. Create Visualizer
      - type: create_visualizer
        audio_source: bedroom_sonos
        visualizer_type: waveform
        style: minimal
        show_track_info: true
      
      # 4. Display on TV (optional)
      - type: display_control
        device: bedroom_tv
        action: power_on
        input: visualizer_stream
      
      # 5. Voice Announcement (with ducking)
      - type: tts
        text: "Good morning! It's 7 AM. Have a great day!"
        device: alexa_bedroom
        # Music automatically ducks during announcement
      
      # 6. Lights (KNX integration)
      - type: knx_scene
        scene: morning_lights
```

---

## API Summary

```http
# Visualizers
POST   /api/v1/visualizer/create
GET    /api/v1/visualizer/streams
DELETE /api/v1/visualizer/{stream_id}
GET    /api/v1/lyrics

# Voice Control
POST   /alexa
POST   /google-assistant

# Audio DSP
POST   /api/v1/audio/{device_id}/eq
POST   /api/v1/audio/{device_id}/crossfade
POST   /api/v1/audio/{device_id}/ducking
GET    /api/v1/audio/{device_id}/dsp-config

# Scheduled Audio
POST   /api/v1/audio/schedule/wake-up
POST   /api/v1/audio/schedule/sleep
POST   /api/v1/audio/schedule/workout
GET    /api/v1/audio/schedules
DELETE /api/v1/audio/schedules/{schedule_id}
```

---

## System Requirements

### Software:
- FFmpeg 4.4+ (for visualizers and DSP)
- Python 3.9+
- Redis (optional, for caching)

### Hardware (Recommended):
- 4GB RAM minimum
- Quad-core CPU (for real-time DSP)
- SSD storage (for fast media access)

### Network:
- Gigabit Ethernet (for 4K visualizers)
- Low-latency network (<10ms for audio sync)

---

## Summary

These advanced features transform the MediaControl system into a **professional-grade audio automation platform**:

✅ **Audio Visualizers** - Real-time visual feedback for music  
✅ **Voice Control** - Alexa & Google Assistant integration  
✅ **Advanced DSP** - Professional EQ, crossfade, ducking, compression, limiting  
✅ **Scheduled Automation** - Wake-up, sleep, workout schedules with gradual fades  
✅ **Tidal Integration** - Hi-Fi lossless audio support  
✅ **Multi-Service Selection** - Auto-select best quality across all services  

Perfect for audiophiles, smart homes, hotels, spas, gyms, and any environment where audio quality and automation matter.
