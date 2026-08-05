"""
Audio Visualizer and Video Streaming
Generate real-time audio visualizations and video streams
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class VisualizerType(Enum):
    """Types of audio visualizations"""
    SPECTRUM = "spectrum"          # Frequency spectrum bars
    WAVEFORM = "waveform"          # Waveform display
    CIRCULAR = "circular"          # Circular spectrum
    PARTICLES = "particles"        # Particle effects
    LYRICS = "lyrics"              # Synchronized lyrics display
    ALBUM_ART = "album_art"        # Album artwork with effects
    VU_METER = "vu_meter"          # VU meters
    OSCILLOSCOPE = "oscilloscope"  # Oscilloscope view


class VisualizerStyle(Enum):
    """Visual styles"""
    MINIMAL = "minimal"
    COLORFUL = "colorful"
    NEON = "neon"
    RETRO = "retro"
    AMBIENT = "ambient"


@dataclass
class VisualizerConfig:
    """Configuration for audio visualizer"""
    type: VisualizerType = VisualizerType.SPECTRUM
    style: VisualizerStyle = VisualizerStyle.COLORFUL
    resolution: str = "1920x1080"
    fps: int = 30
    show_track_info: bool = True
    show_album_art: bool = True
    show_lyrics: bool = False
    color_scheme: Optional[str] = None  # hex colors: "#FF0000,#00FF00,#0000FF"
    blur_background: bool = True
    background_opacity: float = 0.8


class AudioVisualizer:
    """
    Generate video streams with audio visualizations
    Uses FFmpeg with audio analysis filters
    """
    
    def __init__(self):
        self.active_streams: Dict[str, dict] = {}
        logger.info("AudioVisualizer initialized")
    
    def generate_stream_url(
        self,
        audio_source: str,
        config: VisualizerConfig,
        stream_id: Optional[str] = None
    ) -> str:
        """
        Generate streaming URL for audio visualization
        
        Args:
            audio_source: Audio input (RTSP URL, device, or service stream)
            config: Visualizer configuration
            stream_id: Optional ID for this stream
            
        Returns:
            HLS or RTSP URL for the visualization stream
        """
        import uuid
        
        if not stream_id:
            stream_id = f"viz_{uuid.uuid4().hex[:8]}"
        
        # Build FFmpeg command for visualization
        ffmpeg_cmd = self._build_visualizer_command(audio_source, config, stream_id)
        
        # Generate stream URL
        stream_url = f"http://localhost:8080/visualizer/{stream_id}/stream.m3u8"
        
        self.active_streams[stream_id] = {
            "audio_source": audio_source,
            "config": config,
            "stream_url": stream_url,
            "ffmpeg_command": ffmpeg_cmd,
            "status": "active"
        }
        
        logger.info(f"Generated visualizer stream: {stream_url}")
        return stream_url
    
    def _build_visualizer_command(
        self,
        audio_source: str,
        config: VisualizerConfig,
        stream_id: str
    ) -> List[str]:
        """Build FFmpeg command for audio visualization"""
        
        cmd = ["ffmpeg", "-re", "-i", audio_source]
        
        # Video filter based on visualizer type
        if config.type == VisualizerType.SPECTRUM:
            video_filter = (
                f"showfreqs=mode=bar:cmode=combined:"
                f"size={config.resolution}:colors={config.color_scheme or 'rainbow'}"
            )
        
        elif config.type == VisualizerType.WAVEFORM:
            video_filter = (
                f"showwaves=mode=line:s={config.resolution}:"
                f"colors={config.color_scheme or 'white'}"
            )
        
        elif config.type == VisualizerType.CIRCULAR:
            video_filter = (
                f"showcqt=s={config.resolution}:"
                f"count=6:fontcolor=white:font='Helvetica'"
            )
        
        elif config.type == VisualizerType.VU_METER:
            video_filter = (
                f"avectorscope=s={config.resolution}:zoom=1.5:draw=line"
            )
        
        elif config.type == VisualizerType.ALBUM_ART:
            # Static album art with subtle animation
            video_filter = (
                f"scale={config.resolution},"
                f"gblur=sigma=20,"
                f"overlay=album_art.jpg"
            )
        
        else:
            # Default to spectrum
            video_filter = f"showfreqs=s={config.resolution}"
        
        # Add track info overlay if enabled
        if config.show_track_info:
            video_filter += ",drawtext=text='Now Playing\\: %{{metadata\\:title}}':x=10:y=10:fontsize=24:fontcolor=white"
        
        cmd.extend([
            "-filter_complex", video_filter,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-c:a", "copy",
            "-f", "hls",
            "-hls_time", "2",
            "-hls_list_size", "3",
            "-hls_flags", "delete_segments",
            f"/var/stream/{stream_id}/stream.m3u8"
        ])
        
        return cmd
    
    def get_spotify_visualizer_url(
        self,
        spotify_device_id: str,
        config: Optional[VisualizerConfig] = None
    ) -> str:
        """
        Get visualizer URL for Spotify playback
        Captures audio from Spotify and generates visualization
        """
        config = config or VisualizerConfig()
        
        # Spotify audio capture (requires Spotify Connect API)
        audio_source = f"spotify://{spotify_device_id}"
        
        return self.generate_stream_url(audio_source, config, f"spotify_{spotify_device_id}")
    
    def get_airplay_visualizer_url(
        self,
        airplay_device_id: str,
        config: Optional[VisualizerConfig] = None
    ) -> str:
        """Get visualizer URL for AirPlay audio"""
        config = config or VisualizerConfig()
        
        # AirPlay audio capture
        audio_source = f"airplay://{airplay_device_id}"
        
        return self.generate_stream_url(audio_source, config, f"airplay_{airplay_device_id}")
    
    def stop_stream(self, stream_id: str) -> bool:
        """Stop a visualizer stream"""
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
            logger.info(f"Stopped visualizer stream: {stream_id}")
            return True
        return False
    
    def get_active_streams(self) -> List[dict]:
        """Get all active visualizer streams"""
        return list(self.active_streams.values())


class LyricsProvider:
    """
    Fetch synchronized lyrics for tracks
    Integrates with Musixmatch, Genius, or other lyrics APIs
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache: Dict[str, dict] = {}
    
    async def get_lyrics(
        self,
        track_title: str,
        artist: str
    ) -> Optional[dict]:
        """
        Get synchronized lyrics for a track
        
        Returns:
        {
            "lyrics": [
                {"time": 0.5, "text": "First line"},
                {"time": 3.2, "text": "Second line"},
                ...
            ],
            "language": "en",
            "synced": True
        }
        """
        cache_key = f"{artist}_{track_title}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Fetch from Musixmatch API
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Search for track
            search_url = "https://api.musixmatch.com/ws/1.1/track.search"
            params = {
                "apikey": self.api_key,
                "q_track": track_title,
                "q_artist": artist,
                "f_has_lyrics": 1
            }
            
            async with session.get(search_url, params=params) as resp:
                data = await resp.json()
            
            if data["message"]["header"]["status_code"] != 200:
                return None
            
            tracks = data["message"]["body"]["track_list"]
            if not tracks:
                return None
            
            track_id = tracks[0]["track"]["track_id"]
            
            # Get synced lyrics
            lyrics_url = "https://api.musixmatch.com/ws/1.1/track.lyrics.get"
            params = {
                "apikey": self.api_key,
                "track_id": track_id
            }
            
            async with session.get(lyrics_url, params=params) as resp:
                lyrics_data = await resp.json()
            
            if lyrics_data["message"]["header"]["status_code"] != 200:
                return None
            
            lyrics_body = lyrics_data["message"]["body"]["lyrics"]["lyrics_body"]
            
            # Parse lyrics into time-synced format
            lyrics_lines = []
            for line in lyrics_body.split("\n"):
                if line.strip():
                    lyrics_lines.append({
                        "time": 0,  # Would need LRC format for actual timing
                        "text": line
                    })
            
            result = {
                "lyrics": lyrics_lines,
                "language": "en",
                "synced": False  # Would be True with LRC format
            }
            
            self.cache[cache_key] = result
            return result


# Integration with media services
VISUALIZER_INTEGRATION = """
# Integration with Spotify, Apple Music, etc.

from media_services import MediaServiceManager
from audio_visualizer import AudioVisualizer, VisualizerConfig, VisualizerType

media_mgr = MediaServiceManager()
viz = AudioVisualizer()

# Play Spotify with visualizer
spotify = media_mgr.get_service(MediaServiceType.SPOTIFY)
await spotify.play(device_id="living_room_tv", track_uri="spotify:track:xyz")

# Generate visualizer for the playback
viz_config = VisualizerConfig(
    type=VisualizerType.SPECTRUM,
    style=VisualizerStyle.NEON,
    resolution="1920x1080",
    show_track_info=True,
    show_album_art=True
)

viz_url = viz.get_spotify_visualizer_url("living_room_tv", viz_config)

# Display visualizer on screen
# video_player.play(viz_url)

# Stop visualizer
viz.stop_stream("spotify_living_room_tv")
"""

# API endpoints
VISUALIZER_API = """
# Flask/FastAPI endpoints

@app.post("/api/v1/visualizer/create")
async def create_visualizer(request: VisualizerRequest):
    '''Create audio visualizer stream'''
    viz = AudioVisualizer()
    
    config = VisualizerConfig(
        type=request.type,
        style=request.style,
        resolution=request.resolution,
        show_track_info=request.show_track_info
    )
    
    stream_url = viz.generate_stream_url(
        audio_source=request.audio_source,
        config=config
    )
    
    return {
        "stream_url": stream_url,
        "status": "active"
    }

@app.get("/api/v1/visualizer/streams")
def get_visualizer_streams():
    '''Get all active visualizer streams'''
    viz = AudioVisualizer()
    return {"streams": viz.get_active_streams()}

@app.delete("/api/v1/visualizer/{stream_id}")
def stop_visualizer(stream_id: str):
    '''Stop a visualizer stream'''
    viz = AudioVisualizer()
    success = viz.stop_stream(stream_id)
    return {"success": success}

@app.get("/api/v1/lyrics")
async def get_lyrics(track: str, artist: str):
    '''Get synchronized lyrics'''
    lyrics_provider = LyricsProvider(api_key="...")
    lyrics = await lyrics_provider.get_lyrics(track, artist)
    return lyrics or {"error": "Lyrics not found"}
"""

# Room preset with visualizer
PRESET_WITH_VISUALIZER = """
presets:
  party_mode_with_visuals:
    name: "Party Mode with Visuals"
    actions:
      # Start music
      - type: media_service
        service: spotify
        action: play_playlist
        playlist_uri: "spotify:playlist:party"
        device: living_room_sonos
      
      # Create visualizer
      - type: create_visualizer
        audio_source: living_room_sonos
        visualizer_type: spectrum
        style: neon
        resolution: 1920x1080
      
      # Display visualizer on TV
      - type: video_stream
        device: living_room_tv
        source: visualizer_stream
      
      # Set ambient lighting based on music
      - type: knx_scene
        scene: music_reactive_lights
"""
