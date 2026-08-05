"""
Unified Media Service Integration Layer
Supports: Spotify, Apple Music, YouTube, Amazon Music, SoundCloud, and more

⚖️ LEGAL COMPLIANCE NOTICE:
- This module provides control interfaces for streaming services
- Users MUST have valid, paid subscriptions to all services
- All integrations use official APIs and require user authentication
- NO piracy, DRM bypass, or unauthorized content access
- See LEGAL_COMPLIANCE.md for full requirements

Integration Flow:
1. User provides their own API credentials (client_id, client_secret)
2. User completes OAuth authentication with service provider
3. MediaControl controls playback on user's authorized devices
4. User remains responsible for subscription and licensing compliance
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import logging
import asyncio
import json

logger = logging.getLogger(__name__)


class MediaServiceType(Enum):
    """Supported media services"""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    PRIME_VIDEO = "prime_video"
    SOUNDCLOUD = "soundcloud"
    TIDAL = "tidal"
    DEEZER = "deezer"
    PANDORA = "pandora"
    NETFLIX = "netflix"
    DISNEY_PLUS = "disney_plus"
    HULU = "hulu"
    HBO_MAX = "hbo_max"
    PLEX = "plex"
    JELLYFIN = "jellyfin"


class MediaType(Enum):
    """Media content types"""
    AUDIO = "audio"
    VIDEO = "video"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    LIVESTREAM = "livestream"


class PlaybackState(Enum):
    """Playback states"""
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    BUFFERING = "buffering"
    ERROR = "error"


@dataclass
class MediaTrack:
    """Represents a media track (song, video, etc.)"""
    id: str
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    artwork_url: Optional[str] = None
    media_type: MediaType = MediaType.AUDIO
    service: Optional[MediaServiceType] = None
    uri: Optional[str] = None  # Service-specific URI (e.g., spotify:track:xyz)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Playlist:
    """Media playlist"""
    id: str
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    track_count: int = 0
    duration_ms: Optional[int] = None
    artwork_url: Optional[str] = None
    service: Optional[MediaServiceType] = None
    uri: Optional[str] = None
    tracks: List[MediaTrack] = field(default_factory=list)


@dataclass
class PlaybackStatus:
    """Current playback status"""
    state: PlaybackState
    track: Optional[MediaTrack] = None
    position_ms: Optional[int] = None
    volume: Optional[int] = None
    is_shuffling: bool = False
    is_repeating: bool = False
    device_id: Optional[str] = None
    updated_at: datetime = field(default_factory=datetime.now)


class MediaServiceInterface:
    """
    Base interface for all media services
    Each service implements this interface for unified control
    """
    
    def __init__(self, service_type: MediaServiceType, credentials: Dict[str, str]):
        self.service_type = service_type
        self.credentials = credentials
        self.authenticated = False
        logger.info(f"Initialized {service_type.value} service")
    
    async def authenticate(self) -> bool:
        """Authenticate with the service"""
        raise NotImplementedError
    
    async def search(
        self,
        query: str,
        media_type: Optional[MediaType] = None,
        limit: int = 20
    ) -> List[MediaTrack]:
        """Search for media"""
        raise NotImplementedError
    
    async def get_track(self, track_id: str) -> Optional[MediaTrack]:
        """Get track details"""
        raise NotImplementedError
    
    async def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """Get playlist details"""
        raise NotImplementedError
    
    async def get_user_playlists(self) -> List[Playlist]:
        """Get user's playlists"""
        raise NotImplementedError
    
    async def play(
        self,
        device_id: str,
        track_uri: Optional[str] = None,
        context_uri: Optional[str] = None
    ) -> bool:
        """Start playback"""
        raise NotImplementedError
    
    async def pause(self, device_id: str) -> bool:
        """Pause playback"""
        raise NotImplementedError
    
    async def resume(self, device_id: str) -> bool:
        """Resume playback"""
        raise NotImplementedError
    
    async def next_track(self, device_id: str) -> bool:
        """Skip to next track"""
        raise NotImplementedError
    
    async def previous_track(self, device_id: str) -> bool:
        """Go to previous track"""
        raise NotImplementedError
    
    async def seek(self, device_id: str, position_ms: int) -> bool:
        """Seek to position"""
        raise NotImplementedError
    
    async def set_volume(self, device_id: str, volume: int) -> bool:
        """Set volume (0-100)"""
        raise NotImplementedError
    
    async def get_playback_status(self, device_id: str) -> Optional[PlaybackStatus]:
        """Get current playback status"""
        raise NotImplementedError
    
    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get available playback devices"""
        raise NotImplementedError


class SpotifyService(MediaServiceInterface):
    """
    Spotify integration via Spotipy library
    Requires: spotipy, spotify client_id, client_secret, redirect_uri
    """
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(MediaServiceType.SPOTIFY, credentials)
        self.sp = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Spotify"""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth
            
            scope = "user-read-playback-state,user-modify-playback-state,playlist-read-private,user-library-read"
            
            auth_manager = SpotifyOAuth(
                client_id=self.credentials.get("client_id"),
                client_secret=self.credentials.get("client_secret"),
                redirect_uri=self.credentials.get("redirect_uri"),
                scope=scope
            )
            
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.authenticated = True
            logger.info("Spotify authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Spotify authentication failed: {e}")
            return False
    
    async def search(
        self,
        query: str,
        media_type: Optional[MediaType] = None,
        limit: int = 20
    ) -> List[MediaTrack]:
        """Search Spotify"""
        if not self.authenticated:
            await self.authenticate()
        
        try:
            search_type = "track"
            if media_type == MediaType.PODCAST:
                search_type = "episode"
            
            results = self.sp.search(q=query, type=search_type, limit=limit)
            
            tracks = []
            for item in results.get("tracks", {}).get("items", []):
                track = MediaTrack(
                    id=item["id"],
                    title=item["name"],
                    artist=", ".join([a["name"] for a in item["artists"]]),
                    album=item["album"]["name"],
                    duration_ms=item["duration_ms"],
                    artwork_url=item["album"]["images"][0]["url"] if item["album"]["images"] else None,
                    media_type=MediaType.AUDIO,
                    service=MediaServiceType.SPOTIFY,
                    uri=item["uri"],
                    metadata=item
                )
                tracks.append(track)
            
            return tracks
            
        except Exception as e:
            logger.error(f"Spotify search failed: {e}")
            return []
    
    async def get_user_playlists(self) -> List[Playlist]:
        """Get user's Spotify playlists"""
        if not self.authenticated:
            await self.authenticate()
        
        try:
            results = self.sp.current_user_playlists()
            playlists = []
            
            for item in results.get("items", []):
                playlist = Playlist(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description"),
                    owner=item["owner"]["display_name"],
                    track_count=item["tracks"]["total"],
                    artwork_url=item["images"][0]["url"] if item["images"] else None,
                    service=MediaServiceType.SPOTIFY,
                    uri=item["uri"]
                )
                playlists.append(playlist)
            
            return playlists
            
        except Exception as e:
            logger.error(f"Failed to get playlists: {e}")
            return []
    
    async def play(
        self,
        device_id: str,
        track_uri: Optional[str] = None,
        context_uri: Optional[str] = None
    ) -> bool:
        """Start playback on Spotify"""
        try:
            kwargs = {"device_id": device_id}
            if track_uri:
                kwargs["uris"] = [track_uri]
            elif context_uri:
                kwargs["context_uri"] = context_uri
            
            self.sp.start_playback(**kwargs)
            return True
        except Exception as e:
            logger.error(f"Spotify play failed: {e}")
            return False
    
    async def pause(self, device_id: str) -> bool:
        """Pause Spotify playback"""
        try:
            self.sp.pause_playback(device_id=device_id)
            return True
        except Exception as e:
            logger.error(f"Spotify pause failed: {e}")
            return False
    
    async def get_playback_status(self, device_id: str) -> Optional[PlaybackStatus]:
        """Get current Spotify playback status"""
        try:
            current = self.sp.current_playback()
            if not current:
                return None
            
            track_data = current.get("item")
            track = None
            if track_data:
                track = MediaTrack(
                    id=track_data["id"],
                    title=track_data["name"],
                    artist=", ".join([a["name"] for a in track_data["artists"]]),
                    album=track_data["album"]["name"],
                    duration_ms=track_data["duration_ms"],
                    artwork_url=track_data["album"]["images"][0]["url"] if track_data["album"]["images"] else None,
                    service=MediaServiceType.SPOTIFY,
                    uri=track_data["uri"]
                )
            
            state_map = {
                "playing": PlaybackState.PLAYING,
                "paused": PlaybackState.PAUSED
            }
            
            return PlaybackStatus(
                state=state_map.get(current.get("is_playing", False) and "playing" or "paused", PlaybackState.STOPPED),
                track=track,
                position_ms=current.get("progress_ms"),
                volume=current.get("device", {}).get("volume_percent"),
                is_shuffling=current.get("shuffle_state", False),
                is_repeating=current.get("repeat_state") != "off",
                device_id=device_id
            )
        except Exception as e:
            logger.error(f"Failed to get playback status: {e}")
            return None


class AppleMusicService(MediaServiceInterface):
    """
    Apple Music integration via MusicKit
    Requires: Apple Music API credentials (developer token, user token)
    """
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(MediaServiceType.APPLE_MUSIC, credentials)
        self.developer_token = credentials.get("developer_token")
        self.user_token = credentials.get("user_token")
    
    async def authenticate(self) -> bool:
        """Authenticate with Apple Music"""
        # Apple Music uses JWT tokens
        if self.developer_token and self.user_token:
            self.authenticated = True
            logger.info("Apple Music authentication successful")
            return True
        return False
    
    async def search(
        self,
        query: str,
        media_type: Optional[MediaType] = None,
        limit: int = 20
    ) -> List[MediaTrack]:
        """Search Apple Music catalog"""
        import aiohttp
        
        if not self.authenticated:
            await self.authenticate()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.developer_token}",
                "Music-User-Token": self.user_token
            }
            
            params = {
                "term": query,
                "types": "songs",
                "limit": limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.music.apple.com/v1/catalog/us/search",
                    headers=headers,
                    params=params
                ) as resp:
                    data = await resp.json()
            
            tracks = []
            for item in data.get("results", {}).get("songs", {}).get("data", []):
                attrs = item.get("attributes", {})
                track = MediaTrack(
                    id=item["id"],
                    title=attrs.get("name"),
                    artist=attrs.get("artistName"),
                    album=attrs.get("albumName"),
                    duration_ms=attrs.get("durationInMillis"),
                    artwork_url=attrs.get("artwork", {}).get("url"),
                    media_type=MediaType.AUDIO,
                    service=MediaServiceType.APPLE_MUSIC,
                    uri=f"apple:track:{item['id']}",
                    metadata=item
                )
                tracks.append(track)
            
            return tracks
            
        except Exception as e:
            logger.error(f"Apple Music search failed: {e}")
            return []


class MediaServiceManager:
    """
    Manages all media service integrations
    Provides unified interface for controlling any service
    """
    
    def __init__(self):
        self.services: Dict[MediaServiceType, MediaServiceInterface] = {}
        self.active_service: Optional[MediaServiceType] = None
        logger.info("MediaServiceManager initialized")
    
    def register_service(
        self,
        service_type: MediaServiceType,
        service: MediaServiceInterface
    ):
        """Register a media service"""
        self.services[service_type] = service
        logger.info(f"Registered {service_type.value} service")
    
    def register_spotify(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ):
        """Quick registration for Spotify"""
        spotify = SpotifyService({
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        })
        self.register_service(MediaServiceType.SPOTIFY, spotify)
    
    def register_apple_music(
        self,
        developer_token: str,
        user_token: str
    ):
        """Quick registration for Apple Music"""
        apple_music = AppleMusicService({
            "developer_token": developer_token,
            "user_token": user_token
        })
        self.register_service(MediaServiceType.APPLE_MUSIC, apple_music)
    
    async def search_all(
        self,
        query: str,
        media_type: Optional[MediaType] = None,
        limit: int = 20
    ) -> Dict[MediaServiceType, List[MediaTrack]]:
        """Search across all registered services"""
        results = {}
        
        for service_type, service in self.services.items():
            try:
                tracks = await service.search(query, media_type, limit)
                results[service_type] = tracks
            except Exception as e:
                logger.error(f"Search failed for {service_type.value}: {e}")
                results[service_type] = []
        
        return results
    
    async def play_on_service(
        self,
        service_type: MediaServiceType,
        device_id: str,
        track_uri: Optional[str] = None,
        context_uri: Optional[str] = None
    ) -> bool:
        """Play media on a specific service"""
        service = self.services.get(service_type)
        if not service:
            logger.error(f"Service {service_type.value} not registered")
            return False
        
        return await service.play(device_id, track_uri, context_uri)
    
    def get_service(self, service_type: MediaServiceType) -> Optional[MediaServiceInterface]:
        """Get a specific service"""
        return self.services.get(service_type)


# Service configuration examples
SERVICE_CONFIG_EXAMPLE = """
# Configuration example for media services

# Spotify
spotify:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  redirect_uri: "http://localhost:8888/callback"

# Apple Music
apple_music:
  developer_token: "your_jwt_token"
  user_token: "user_music_token"

# YouTube (via YouTube Data API)
youtube:
  api_key: "your_youtube_api_key"

# Amazon Music
amazon_music:
  client_id: "your_amazon_client_id"
  client_secret: "your_amazon_secret"

# Usage with room presets
presets:
  morning_playlist:
    name: "Morning Routine"
    actions:
      - type: media_service
        service: spotify
        action: play_playlist
        playlist_id: "37i9dQZF1DX0H9VYs5EqYz"  # Spotify playlist ID
        device: living_room_sonos
        volume: 40
      
  workout_music:
    name: "Workout Music"
    actions:
      - type: media_service
        service: apple_music
        action: play_playlist
        playlist_id: "pl.123abc"
        device: gym_speakers
        volume: 70
"""

# Integration with existing audio devices
AUDIO_DEVICE_INTEGRATION = """
# Integrate media services with audio devices

from audio_devices import SonosDevice, AirPlaySpeaker
from media_services import MediaServiceManager, MediaServiceType

# Setup
media_mgr = MediaServiceManager()
media_mgr.register_spotify(
    client_id="...",
    client_secret="...",
    redirect_uri="..."
)

# Play Spotify on Sonos
sonos = SonosDevice(device_id="kitchen", host="192.168.1.160")
sonos.connect()

# Option 1: Direct Sonos Spotify integration (native)
sonos.play_spotify_uri("spotify:playlist:37i9dQZF1DX0H9VYs5EqYz")

# Option 2: Via Spotify API (for remote control)
await media_mgr.play_on_service(
    service_type=MediaServiceType.SPOTIFY,
    device_id="kitchen_sonos_spotify_id",
    context_uri="spotify:playlist:37i9dQZF1DX0H9VYs5EqYz"
)
"""
