"""
Audio Queue Management
Advanced queue control: add, remove, reorder, play next, save as playlist

⚖️ LEGAL COMPLIANCE NOTICE:
- Queue management for legally licensed content only
- Users MUST have valid subscriptions to streaming services
- See LEGAL_COMPLIANCE.md for full requirements
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class RepeatMode(Enum):
    """Queue repeat modes"""
    OFF = "off"           # No repeat
    ONE = "one"           # Repeat current track
    ALL = "all"           # Repeat entire queue


class ShuffleMode(Enum):
    """Shuffle modes"""
    OFF = "off"
    ON = "on"


@dataclass
class QueueTrack:
    """Track in the playback queue"""
    queue_id: str  # Unique ID for this queue entry
    track_id: str  # Service-specific track ID
    title: str
    artist: str
    album: Optional[str] = None
    duration_ms: int = 0
    artwork_url: Optional[str] = None
    service: str = "spotify"  # spotify, apple_music, youtube, etc.
    service_uri: Optional[str] = None  # e.g., spotify:track:xyz
    added_at: datetime = field(default_factory=datetime.now)
    added_by: Optional[str] = None  # User who added this track
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaybackQueue:
    """Complete playback queue state"""
    queue_id: str
    device_id: str  # Which device this queue belongs to
    tracks: List[QueueTrack] = field(default_factory=list)
    current_index: int = 0
    repeat_mode: RepeatMode = RepeatMode.OFF
    shuffle_mode: ShuffleMode = ShuffleMode.OFF
    
    # Shuffle state
    original_order: Optional[List[int]] = None  # Indices before shuffle
    shuffle_history: List[int] = field(default_factory=list)  # Already played in shuffle
    
    # Queue metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def current_track(self) -> Optional[QueueTrack]:
        """Get currently playing track"""
        if 0 <= self.current_index < len(self.tracks):
            return self.tracks[self.current_index]
        return None
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next track"""
        if self.repeat_mode == RepeatMode.ONE:
            return True
        if self.repeat_mode == RepeatMode.ALL:
            return len(self.tracks) > 0
        return self.current_index < len(self.tracks) - 1
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous track"""
        if self.repeat_mode == RepeatMode.ONE:
            return True
        if self.repeat_mode == RepeatMode.ALL:
            return len(self.tracks) > 0
        return self.current_index > 0
    
    @property
    def remaining_tracks(self) -> int:
        """Number of tracks remaining in queue"""
        return len(self.tracks) - self.current_index - 1
    
    @property
    def total_duration_ms(self) -> int:
        """Total duration of all tracks"""
        return sum(track.duration_ms for track in self.tracks)
    
    @property
    def remaining_duration_ms(self) -> int:
        """Duration of remaining tracks"""
        if self.current_index < len(self.tracks):
            return sum(
                track.duration_ms 
                for track in self.tracks[self.current_index + 1:]
            )
        return 0


class QueueManager:
    """
    Manages playback queues for audio devices
    Supports: add, remove, reorder, play next, shuffle, repeat, save as playlist
    """
    
    def __init__(self, media_service_manager=None):
        self.queues: Dict[str, PlaybackQueue] = {}  # device_id -> queue
        self.media_service_manager = media_service_manager
        logger.info("QueueManager initialized")
    
    def create_queue(self, device_id: str) -> PlaybackQueue:
        """Create a new empty queue for a device"""
        queue = PlaybackQueue(
            queue_id=f"queue_{uuid.uuid4().hex[:12]}",
            device_id=device_id
        )
        self.queues[device_id] = queue
        logger.info(f"Created queue for device {device_id}")
        return queue
    
    def get_queue(self, device_id: str) -> Optional[PlaybackQueue]:
        """Get queue for a device"""
        if device_id not in self.queues:
            return self.create_queue(device_id)
        return self.queues[device_id]
    
    def add_to_queue(
        self,
        device_id: str,
        track: QueueTrack,
        position: Optional[int] = None
    ) -> bool:
        """
        Add track to queue
        
        Args:
            device_id: Device ID
            track: Track to add
            position: Optional position (None = add to end)
            
        Returns:
            True if added successfully
        """
        queue = self.get_queue(device_id)
        
        if position is None:
            # Add to end
            queue.tracks.append(track)
            logger.info(f"Added '{track.title}' to end of queue for {device_id}")
        else:
            # Insert at position
            position = max(0, min(position, len(queue.tracks)))
            queue.tracks.insert(position, track)
            logger.info(f"Inserted '{track.title}' at position {position} for {device_id}")
        
        queue.updated_at = datetime.now()
        return True
    
    def play_next(
        self,
        device_id: str,
        track: QueueTrack
    ) -> bool:
        """
        Add track to play next (after current track)
        
        Args:
            device_id: Device ID
            track: Track to play next
            
        Returns:
            True if added successfully
        """
        queue = self.get_queue(device_id)
        
        # Insert after current track
        insert_position = queue.current_index + 1
        queue.tracks.insert(insert_position, track)
        
        logger.info(f"Set '{track.title}' to play next for {device_id}")
        queue.updated_at = datetime.now()
        return True
    
    def remove_from_queue(
        self,
        device_id: str,
        queue_id: Optional[str] = None,
        index: Optional[int] = None
    ) -> bool:
        """
        Remove track from queue
        
        Args:
            device_id: Device ID
            queue_id: Queue track ID to remove
            index: Or index to remove
            
        Returns:
            True if removed successfully
        """
        queue = self.get_queue(device_id)
        
        if queue_id:
            # Remove by queue_id
            for i, track in enumerate(queue.tracks):
                if track.queue_id == queue_id:
                    removed = queue.tracks.pop(i)
                    logger.info(f"Removed '{removed.title}' from queue for {device_id}")
                    
                    # Adjust current_index if needed
                    if i < queue.current_index:
                        queue.current_index -= 1
                    elif i == queue.current_index:
                        # Removed current track, stay at same index (will play next)
                        pass
                    
                    queue.updated_at = datetime.now()
                    return True
        
        elif index is not None:
            # Remove by index
            if 0 <= index < len(queue.tracks):
                removed = queue.tracks.pop(index)
                logger.info(f"Removed '{removed.title}' at index {index} for {device_id}")
                
                # Adjust current_index
                if index < queue.current_index:
                    queue.current_index -= 1
                elif index == queue.current_index:
                    pass
                
                queue.updated_at = datetime.now()
                return True
        
        logger.warning(f"Track not found for removal in queue for {device_id}")
        return False
    
    def reorder_queue(
        self,
        device_id: str,
        from_index: int,
        to_index: int
    ) -> bool:
        """
        Reorder tracks in queue
        
        Args:
            device_id: Device ID
            from_index: Source index
            to_index: Destination index
            
        Returns:
            True if reordered successfully
        """
        queue = self.get_queue(device_id)
        
        if not (0 <= from_index < len(queue.tracks)):
            logger.error(f"Invalid from_index: {from_index}")
            return False
        
        to_index = max(0, min(to_index, len(queue.tracks) - 1))
        
        # Move track
        track = queue.tracks.pop(from_index)
        queue.tracks.insert(to_index, track)
        
        # Adjust current_index if needed
        if from_index == queue.current_index:
            # Moved current track
            queue.current_index = to_index
        elif from_index < queue.current_index <= to_index:
            queue.current_index -= 1
        elif to_index <= queue.current_index < from_index:
            queue.current_index += 1
        
        logger.info(f"Moved track from {from_index} to {to_index} for {device_id}")
        queue.updated_at = datetime.now()
        return True
    
    def clear_queue(self, device_id: str, keep_current: bool = False) -> bool:
        """
        Clear the queue
        
        Args:
            device_id: Device ID
            keep_current: If True, keep only the current track
            
        Returns:
            True if cleared successfully
        """
        queue = self.get_queue(device_id)
        
        if keep_current and queue.current_track:
            current = queue.current_track
            queue.tracks = [current]
            queue.current_index = 0
            logger.info(f"Cleared queue for {device_id}, kept current track")
        else:
            queue.tracks = []
            queue.current_index = 0
            logger.info(f"Cleared entire queue for {device_id}")
        
        queue.updated_at = datetime.now()
        return True
    
    def next_track(self, device_id: str) -> Optional[QueueTrack]:
        """
        Move to next track
        
        Returns:
            Next track, or None if no next track
        """
        queue = self.get_queue(device_id)
        
        if self.repeat_mode == RepeatMode.ONE:
            # Repeat current track
            return queue.current_track
        
        if self.shuffle_mode == ShuffleMode.ON:
            return self._next_shuffle_track(queue)
        
        # Normal next
        if queue.current_index < len(queue.tracks) - 1:
            queue.current_index += 1
            logger.info(f"Advanced to track {queue.current_index} for {device_id}")
            return queue.current_track
        
        # At end of queue
        if queue.repeat_mode == RepeatMode.ALL and len(queue.tracks) > 0:
            queue.current_index = 0
            logger.info(f"Looped to start of queue for {device_id}")
            return queue.current_track
        
        logger.info(f"Reached end of queue for {device_id}")
        return None
    
    def previous_track(self, device_id: str) -> Optional[QueueTrack]:
        """
        Move to previous track
        
        Returns:
            Previous track, or None if no previous track
        """
        queue = self.get_queue(device_id)
        
        if queue.repeat_mode == RepeatMode.ONE:
            return queue.current_track
        
        if queue.current_index > 0:
            queue.current_index -= 1
            logger.info(f"Moved back to track {queue.current_index} for {device_id}")
            return queue.current_track
        
        # At beginning
        if queue.repeat_mode == RepeatMode.ALL and len(queue.tracks) > 0:
            queue.current_index = len(queue.tracks) - 1
            logger.info(f"Looped to end of queue for {device_id}")
            return queue.current_track
        
        logger.info(f"At beginning of queue for {device_id}")
        return None
    
    def jump_to_track(self, device_id: str, index: int) -> Optional[QueueTrack]:
        """Jump to specific track in queue"""
        queue = self.get_queue(device_id)
        
        if 0 <= index < len(queue.tracks):
            queue.current_index = index
            logger.info(f"Jumped to track {index} for {device_id}")
            return queue.current_track
        
        logger.error(f"Invalid track index {index} for {device_id}")
        return None
    
    def set_repeat_mode(self, device_id: str, mode: RepeatMode) -> bool:
        """Set repeat mode"""
        queue = self.get_queue(device_id)
        queue.repeat_mode = mode
        logger.info(f"Set repeat mode to {mode.value} for {device_id}")
        return True
    
    def set_shuffle_mode(self, device_id: str, mode: ShuffleMode) -> bool:
        """Set shuffle mode"""
        queue = self.get_queue(device_id)
        
        if mode == ShuffleMode.ON and queue.shuffle_mode == ShuffleMode.OFF:
            # Enabling shuffle
            self._enable_shuffle(queue)
        elif mode == ShuffleMode.OFF and queue.shuffle_mode == ShuffleMode.ON:
            # Disabling shuffle
            self._disable_shuffle(queue)
        
        queue.shuffle_mode = mode
        logger.info(f"Set shuffle mode to {mode.value} for {device_id}")
        return True
    
    def _enable_shuffle(self, queue: PlaybackQueue):
        """Enable shuffle - save original order and shuffle"""
        import random
        
        # Save original order
        queue.original_order = list(range(len(queue.tracks)))
        
        # Keep current track at current position
        current_track = queue.current_track
        
        # Shuffle tracks after current
        remaining = queue.tracks[queue.current_index + 1:]
        random.shuffle(remaining)
        
        # Rebuild queue
        if current_track:
            queue.tracks = (
                queue.tracks[:queue.current_index + 1] + 
                remaining
            )
        
        queue.shuffle_history = []
        logger.info("Enabled shuffle")
    
    def _disable_shuffle(self, queue: PlaybackQueue):
        """Disable shuffle - restore original order"""
        if not queue.original_order:
            return
        
        # Find current track's original index
        current_track = queue.current_track
        
        # Restore original order
        # (Simplified - in production, track original indices properly)
        queue.shuffle_history = []
        queue.original_order = None
        logger.info("Disabled shuffle")
    
    def _next_shuffle_track(self, queue: PlaybackQueue) -> Optional[QueueTrack]:
        """Get next track in shuffle mode"""
        import random
        
        available_indices = [
            i for i in range(len(queue.tracks))
            if i not in queue.shuffle_history and i != queue.current_index
        ]
        
        if not available_indices:
            # Shuffled through all tracks
            if queue.repeat_mode == RepeatMode.ALL:
                queue.shuffle_history = []
                available_indices = list(range(len(queue.tracks)))
            else:
                return None
        
        next_index = random.choice(available_indices)
        queue.shuffle_history.append(queue.current_index)
        queue.current_index = next_index
        
        return queue.current_track
    
    def save_queue_as_playlist(
        self,
        device_id: str,
        playlist_name: str,
        service: str = "spotify",
        user_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Save current queue as a playlist
        
        Args:
            device_id: Device ID
            playlist_name: Name for the new playlist
            service: Service to save playlist to (spotify, apple_music, etc.)
            user_id: User ID for the playlist
            
        Returns:
            Playlist ID/URI if successful, None otherwise
        """
        queue = self.get_queue(device_id)
        
        if not queue.tracks:
            logger.error(f"Cannot save empty queue as playlist for {device_id}")
            return None
        
        if not self.media_service_manager:
            logger.error("No media service manager configured")
            return None
        
        try:
            # Get media service
            media_service = self.media_service_manager.get_service_by_name(service)
            
            if not media_service:
                logger.error(f"Service {service} not found")
                return None
            
            # Extract track URIs
            track_uris = [
                track.service_uri 
                for track in queue.tracks 
                if track.service_uri and track.service == service
            ]
            
            if not track_uris:
                logger.error(f"No tracks from {service} in queue")
                return None
            
            # Create playlist via media service
            playlist_id = media_service.create_playlist(
                name=playlist_name,
                track_uris=track_uris,
                user_id=user_id
            )
            
            logger.info(
                f"Saved queue as playlist '{playlist_name}' on {service}: "
                f"{len(track_uris)} tracks"
            )
            
            return playlist_id
        
        except Exception as e:
            logger.error(f"Failed to save queue as playlist: {e}")
            return None
    
    def load_playlist_to_queue(
        self,
        device_id: str,
        playlist_id: str,
        service: str = "spotify",
        clear_existing: bool = True
    ) -> bool:
        """
        Load playlist into queue
        
        Args:
            device_id: Device ID
            playlist_id: Playlist ID/URI
            service: Service the playlist is from
            clear_existing: Clear existing queue first
            
        Returns:
            True if loaded successfully
        """
        if not self.media_service_manager:
            logger.error("No media service manager configured")
            return False
        
        try:
            # Get media service
            media_service = self.media_service_manager.get_service_by_name(service)
            
            if not media_service:
                logger.error(f"Service {service} not found")
                return False
            
            # Get playlist tracks
            playlist_tracks = media_service.get_playlist_tracks(playlist_id)
            
            if not playlist_tracks:
                logger.error(f"Playlist {playlist_id} not found or empty")
                return False
            
            # Clear existing queue if requested
            if clear_existing:
                self.clear_queue(device_id)
            
            # Add tracks to queue
            queue = self.get_queue(device_id)
            
            for track_data in playlist_tracks:
                queue_track = QueueTrack(
                    queue_id=f"qt_{uuid.uuid4().hex[:12]}",
                    track_id=track_data.get("id"),
                    title=track_data.get("title", "Unknown"),
                    artist=track_data.get("artist", "Unknown"),
                    album=track_data.get("album"),
                    duration_ms=track_data.get("duration_ms", 0),
                    artwork_url=track_data.get("artwork_url"),
                    service=service,
                    service_uri=track_data.get("uri")
                )
                queue.tracks.append(queue_track)
            
            logger.info(f"Loaded playlist {playlist_id} ({len(playlist_tracks)} tracks) to {device_id}")
            queue.updated_at = datetime.now()
            return True
        
        except Exception as e:
            logger.error(f"Failed to load playlist to queue: {e}")
            return False
    
    def get_queue_state(self, device_id: str) -> Dict[str, Any]:
        """Get complete queue state for API/UI"""
        queue = self.get_queue(device_id)
        
        return {
            "queue_id": queue.queue_id,
            "device_id": device_id,
            "current_index": queue.current_index,
            "current_track": self._serialize_track(queue.current_track) if queue.current_track else None,
            "tracks": [self._serialize_track(track) for track in queue.tracks],
            "total_tracks": len(queue.tracks),
            "remaining_tracks": queue.remaining_tracks,
            "total_duration_ms": queue.total_duration_ms,
            "remaining_duration_ms": queue.remaining_duration_ms,
            "repeat_mode": queue.repeat_mode.value,
            "shuffle_mode": queue.shuffle_mode.value,
            "has_next": queue.has_next,
            "has_previous": queue.has_previous,
            "created_at": queue.created_at.isoformat(),
            "updated_at": queue.updated_at.isoformat()
        }
    
    def _serialize_track(self, track: QueueTrack) -> Dict[str, Any]:
        """Serialize track for API response"""
        return {
            "queue_id": track.queue_id,
            "track_id": track.track_id,
            "title": track.title,
            "artist": track.artist,
            "album": track.album,
            "duration_ms": track.duration_ms,
            "artwork_url": track.artwork_url,
            "service": track.service,
            "service_uri": track.service_uri,
            "added_at": track.added_at.isoformat(),
            "added_by": track.added_by
        }


# API Examples
QUEUE_API_EXAMPLES = """
# Flask/FastAPI API endpoints

@app.get("/api/v1/queue/{device_id}")
def get_queue(device_id: str):
    '''Get queue state'''
    queue_mgr = QueueManager()
    return queue_mgr.get_queue_state(device_id)

@app.post("/api/v1/queue/{device_id}/add")
def add_to_queue(device_id: str, track: TrackRequest):
    '''Add track to queue'''
    queue_mgr = QueueManager()
    
    queue_track = QueueTrack(
        queue_id=f"qt_{uuid.uuid4().hex[:12]}",
        track_id=track.track_id,
        title=track.title,
        artist=track.artist,
        service=track.service,
        service_uri=track.uri
    )
    
    success = queue_mgr.add_to_queue(device_id, queue_track)
    return {"success": success}

@app.post("/api/v1/queue/{device_id}/play-next")
def play_next(device_id: str, track: TrackRequest):
    '''Add track to play next'''
    queue_mgr = QueueManager()
    
    queue_track = QueueTrack(
        queue_id=f"qt_{uuid.uuid4().hex[:12]}",
        track_id=track.track_id,
        title=track.title,
        artist=track.artist
    )
    
    success = queue_mgr.play_next(device_id, queue_track)
    return {"success": success}

@app.delete("/api/v1/queue/{device_id}/tracks/{queue_id}")
def remove_from_queue(device_id: str, queue_id: str):
    '''Remove track from queue'''
    queue_mgr = QueueManager()
    success = queue_mgr.remove_from_queue(device_id, queue_id=queue_id)
    return {"success": success}

@app.put("/api/v1/queue/{device_id}/reorder")
def reorder_queue(device_id: str, request: ReorderRequest):
    '''Reorder tracks in queue'''
    queue_mgr = QueueManager()
    success = queue_mgr.reorder_queue(device_id, request.from_index, request.to_index)
    return {"success": success}

@app.post("/api/v1/queue/{device_id}/next")
def next_track(device_id: str):
    '''Skip to next track'''
    queue_mgr = QueueManager()
    track = queue_mgr.next_track(device_id)
    return {"track": track if track else None}

@app.post("/api/v1/queue/{device_id}/previous")
def previous_track(device_id: str):
    '''Go to previous track'''
    queue_mgr = QueueManager()
    track = queue_mgr.previous_track(device_id)
    return {"track": track if track else None}

@app.put("/api/v1/queue/{device_id}/repeat")
def set_repeat(device_id: str, mode: str):
    '''Set repeat mode'''
    queue_mgr = QueueManager()
    repeat_mode = RepeatMode(mode)
    success = queue_mgr.set_repeat_mode(device_id, repeat_mode)
    return {"success": success, "mode": mode}

@app.put("/api/v1/queue/{device_id}/shuffle")
def set_shuffle(device_id: str, enabled: bool):
    '''Set shuffle mode'''
    queue_mgr = QueueManager()
    shuffle_mode = ShuffleMode.ON if enabled else ShuffleMode.OFF
    success = queue_mgr.set_shuffle_mode(device_id, shuffle_mode)
    return {"success": success, "shuffle": enabled}

@app.post("/api/v1/queue/{device_id}/save-playlist")
def save_as_playlist(device_id: str, request: SavePlaylistRequest):
    '''Save queue as playlist'''
    queue_mgr = QueueManager(media_service_manager=media_mgr)
    
    playlist_id = queue_mgr.save_queue_as_playlist(
        device_id=device_id,
        playlist_name=request.name,
        service=request.service,
        user_id=request.user_id
    )
    
    return {
        "success": playlist_id is not None,
        "playlist_id": playlist_id
    }

@app.delete("/api/v1/queue/{device_id}")
def clear_queue(device_id: str, keep_current: bool = False):
    '''Clear queue'''
    queue_mgr = QueueManager()
    success = queue_mgr.clear_queue(device_id, keep_current=keep_current)
    return {"success": success}
"""
