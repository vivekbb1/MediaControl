"""
Music Library Management
Unified library for managing music across all services
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class LibraryItemType(Enum):
    """Types of library items"""
    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"
    ARTIST = "artist"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"


@dataclass
class LibraryItem:
    """An item in the music library"""
    id: str
    type: LibraryItemType
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    artwork_url: Optional[str] = None
    service: Optional[str] = None  # Which service this came from
    service_id: Optional[str] = None  # ID in that service
    added_at: datetime = field(default_factory=datetime.now)
    play_count: int = 0
    last_played: Optional[datetime] = None
    favorite: bool = False
    tags: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)


@dataclass
class MusicCollection:
    """A collection of music (playlist, album, etc.)"""
    id: str
    name: str
    description: Optional[str] = None
    type: LibraryItemType = LibraryItemType.PLAYLIST
    owner_id: str = None
    items: List[LibraryItem] = field(default_factory=list)
    artwork_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    collaborative: bool = False
    public: bool = False
    tags: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)
    
    @property
    def track_count(self) -> int:
        return len(self.items)
    
    @property
    def total_duration_ms(self) -> int:
        return sum(item.duration_ms or 0 for item in self.items)


class MusicLibrary:
    """
    Unified music library across all services
    Aggregates content from Spotify, Apple Music, YouTube, etc.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.items: Dict[str, LibraryItem] = {}
        self.collections: Dict[str, MusicCollection] = {}
        
        # Smart playlists (auto-populated based on criteria)
        self.smart_playlists: Dict[str, dict] = {}
        
        logger.info(f"MusicLibrary initialized for user {user_id}")
    
    def add_item(self, item: LibraryItem) -> str:
        """Add an item to the library"""
        if item.id in self.items:
            logger.warning(f"Item {item.id} already in library")
            return item.id
        
        self.items[item.id] = item
        logger.info(f"Added {item.type.value} '{item.title}' to library")
        return item.id
    
    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the library"""
        if item_id in self.items:
            item = self.items[item_id]
            del self.items[item_id]
            logger.info(f"Removed '{item.title}' from library")
            return True
        return False
    
    def get_item(self, item_id: str) -> Optional[LibraryItem]:
        """Get an item by ID"""
        return self.items.get(item_id)
    
    def search(
        self,
        query: Optional[str] = None,
        type: Optional[LibraryItemType] = None,
        service: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        favorites_only: bool = False
    ) -> List[LibraryItem]:
        """Search the library"""
        results = list(self.items.values())
        
        # Filter by type
        if type:
            results = [item for item in results if item.type == type]
        
        # Filter by service
        if service:
            results = [item for item in results if item.service == service]
        
        # Filter by tags
        if tags:
            results = [item for item in results if tags.issubset(item.tags)]
        
        # Filter favorites
        if favorites_only:
            results = [item for item in results if item.favorite]
        
        # Search query
        if query:
            query_lower = query.lower()
            results = [
                item for item in results
                if query_lower in item.title.lower()
                or (item.artist and query_lower in item.artist.lower())
                or (item.album and query_lower in item.album.lower())
            ]
        
        return results
    
    def get_favorites(self, type: Optional[LibraryItemType] = None) -> List[LibraryItem]:
        """Get favorite items"""
        return self.search(type=type, favorites_only=True)
    
    def get_recently_played(self, limit: int = 50) -> List[LibraryItem]:
        """Get recently played items"""
        items_with_play_time = [
            item for item in self.items.values()
            if item.last_played
        ]
        
        items_with_play_time.sort(key=lambda x: x.last_played, reverse=True)
        return items_with_play_time[:limit]
    
    def get_most_played(self, limit: int = 50) -> List[LibraryItem]:
        """Get most played items"""
        items_sorted = sorted(
            self.items.values(),
            key=lambda x: x.play_count,
            reverse=True
        )
        return items_sorted[:limit]
    
    def mark_as_played(self, item_id: str):
        """Mark an item as played"""
        item = self.items.get(item_id)
        if item:
            item.play_count += 1
            item.last_played = datetime.now()
            logger.debug(f"Marked '{item.title}' as played (count: {item.play_count})")
    
    def toggle_favorite(self, item_id: str) -> bool:
        """Toggle favorite status of an item"""
        item = self.items.get(item_id)
        if item:
            item.favorite = not item.favorite
            logger.info(f"{'Favorited' if item.favorite else 'Unfavorited'} '{item.title}'")
            return item.favorite
        return False
    
    def create_collection(
        self,
        name: str,
        type: LibraryItemType = LibraryItemType.PLAYLIST,
        description: Optional[str] = None
    ) -> MusicCollection:
        """Create a new collection (playlist, album, etc.)"""
        collection_id = f"collection_{self.user_id}_{datetime.now().timestamp()}"
        
        collection = MusicCollection(
            id=collection_id,
            name=name,
            description=description,
            type=type,
            owner_id=self.user_id
        )
        
        self.collections[collection_id] = collection
        logger.info(f"Created {type.value} '{name}'")
        return collection
    
    def add_to_collection(self, collection_id: str, item_id: str) -> bool:
        """Add an item to a collection"""
        collection = self.collections.get(collection_id)
        item = self.items.get(item_id)
        
        if not collection or not item:
            return False
        
        if item not in collection.items:
            collection.items.append(item)
            collection.updated_at = datetime.now()
            logger.info(f"Added '{item.title}' to {collection.name}")
            return True
        
        return False
    
    def remove_from_collection(self, collection_id: str, item_id: str) -> bool:
        """Remove an item from a collection"""
        collection = self.collections.get(collection_id)
        item = self.items.get(item_id)
        
        if not collection or not item:
            return False
        
        if item in collection.items:
            collection.items.remove(item)
            collection.updated_at = datetime.now()
            logger.info(f"Removed '{item.title}' from {collection.name}")
            return True
        
        return False
    
    def create_smart_playlist(
        self,
        name: str,
        criteria: dict
    ) -> MusicCollection:
        """
        Create a smart playlist that auto-populates based on criteria
        
        Example criteria:
        {
            "tags": {"workout", "high_energy"},
            "min_play_count": 10,
            "favorites_only": True,
            "service": "spotify",
            "max_items": 50
        }
        """
        playlist_id = f"smart_{self.user_id}_{datetime.now().timestamp()}"
        
        playlist = MusicCollection(
            id=playlist_id,
            name=name,
            type=LibraryItemType.PLAYLIST,
            owner_id=self.user_id,
            metadata={"smart_playlist": True, "criteria": criteria}
        )
        
        # Populate based on criteria
        self._update_smart_playlist(playlist)
        
        self.collections[playlist_id] = playlist
        self.smart_playlists[playlist_id] = criteria
        
        logger.info(f"Created smart playlist '{name}' with {playlist.track_count} tracks")
        return playlist
    
    def _update_smart_playlist(self, playlist: MusicCollection):
        """Update a smart playlist based on its criteria"""
        criteria = playlist.metadata.get("criteria", {})
        
        # Search based on criteria
        results = self.search(
            tags=criteria.get("tags"),
            service=criteria.get("service"),
            favorites_only=criteria.get("favorites_only", False)
        )
        
        # Apply additional filters
        if "min_play_count" in criteria:
            results = [r for r in results if r.play_count >= criteria["min_play_count"]]
        
        # Sort
        sort_by = criteria.get("sort_by", "recently_added")
        if sort_by == "play_count":
            results.sort(key=lambda x: x.play_count, reverse=True)
        elif sort_by == "last_played":
            results = [r for r in results if r.last_played]
            results.sort(key=lambda x: x.last_played, reverse=True)
        else:  # recently_added
            results.sort(key=lambda x: x.added_at, reverse=True)
        
        # Limit
        max_items = criteria.get("max_items", 100)
        playlist.items = results[:max_items]
        playlist.updated_at = datetime.now()
    
    def update_smart_playlists(self):
        """Update all smart playlists"""
        for playlist_id in self.smart_playlists:
            playlist = self.collections.get(playlist_id)
            if playlist:
                self._update_smart_playlist(playlist)
                logger.info(f"Updated smart playlist '{playlist.name}' - {playlist.track_count} tracks")
    
    def import_from_service(self, service_name: str, service_data: List[dict]):
        """Import music from a service"""
        imported_count = 0
        
        for data in service_data:
            item = LibraryItem(
                id=f"{service_name}_{data.get('id')}",
                type=LibraryItemType.TRACK,
                title=data.get("title", ""),
                artist=data.get("artist"),
                album=data.get("album"),
                duration_ms=data.get("duration_ms"),
                artwork_url=data.get("artwork_url"),
                service=service_name,
                service_id=data.get("id"),
                metadata=data
            )
            
            self.add_item(item)
            imported_count += 1
        
        logger.info(f"Imported {imported_count} items from {service_name}")
        return imported_count
    
    def export_to_json(self) -> str:
        """Export library to JSON"""
        export_data = {
            "user_id": self.user_id,
            "exported_at": datetime.now().isoformat(),
            "item_count": len(self.items),
            "collection_count": len(self.collections),
            "items": [
                {
                    "id": item.id,
                    "type": item.type.value,
                    "title": item.title,
                    "artist": item.artist,
                    "album": item.album,
                    "service": item.service,
                    "favorite": item.favorite,
                    "play_count": item.play_count,
                    "tags": list(item.tags)
                }
                for item in self.items.values()
            ],
            "collections": [
                {
                    "id": col.id,
                    "name": col.name,
                    "type": col.type.value,
                    "track_count": col.track_count,
                    "items": [item.id for item in col.items]
                }
                for col in self.collections.values()
            ]
        }
        
        return json.dumps(export_data, indent=2)


# Usage examples
MUSIC_LIBRARY_USAGE = """
# Initialize library
library = MusicLibrary(user_id="user_123")

# Import from Spotify
spotify_tracks = spotify_service.get_user_saved_tracks()
library.import_from_service("spotify", spotify_tracks)

# Import from Apple Music
apple_tracks = apple_music_service.get_library_songs()
library.import_from_service("apple_music", apple_tracks)

# Search
workout_music = library.search(tags={"workout", "high_energy"})

# Create playlist
gym_playlist = library.create_collection(
    name="Gym Playlist",
    description="High energy workout music"
)

for track in workout_music[:20]:
    library.add_to_collection(gym_playlist.id, track.id)

# Create smart playlist
favorites = library.create_smart_playlist(
    name="My Top Favorites",
    criteria={
        "favorites_only": True,
        "min_play_count": 5,
        "sort_by": "play_count",
        "max_items": 50
    }
)

# Get stats
recently_played = library.get_recently_played(limit=10)
most_played = library.get_most_played(limit=10)

# Mark as played (for tracking)
library.mark_as_played(track_id)

# Toggle favorite
library.toggle_favorite(track_id)

# Export library
json_export = library.export_to_json()
"""
