#!/usr/bin/env python3
"""
EPG (Electronic Program Guide) integration for IPTV channels with timezone support.

⚖️ LEGAL COMPLIANCE NOTICE:
- EPG data shows TV schedules only, NOT content access
- Users MUST have valid cable/satellite/IPTV subscriptions
- EPG sources: public broadcasters, open-source projects, user's STB provider
- Does NOT provide pirated IPTV streams or unauthorized content links
- For use with legally subscribed channels only
- See LEGAL_COMPLIANCE.md for full requirements

EPG data ≠ Content access. Users need legal STB/cable subscription.
"""

from __future__ import annotations

import gzip
import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class Channel:
    """TV Channel metadata."""
    id: str
    display_name: str
    icon: str | None = None
    url: str | None = None


@dataclass
class Programme:
    """TV Programme/Show information."""
    channel: str
    start: datetime
    stop: datetime
    title: str
    desc: str | None = None
    category: list[str] | None = None
    icon: str | None = None
    episode_num: str | None = None
    rating: str | None = None
    is_new: bool = False
    is_live: bool = False


class EPGClient:
    """Client for fetching and parsing XMLTV EPG data."""

    def __init__(self, cache_dir: Path | None = None, user_agent: str | None = None):
        self.cache_dir = cache_dir or Path("./epg_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.user_agent = user_agent or "FlipRemote/1.0 EPG Client"
        self.logger = logging.getLogger("epg")

    def fetch_xmltv(self, url: str, use_cache: bool = True) -> Path:
        """
        Fetch XMLTV data from URL and cache it locally.
        
        Args:
            url: URL to XMLTV file (can be .xml or .xml.gz)
            use_cache: Use cached file if exists and recent (< 6 hours)
            
        Returns:
            Path to local XMLTV file (decompressed)
        """
        # Generate cache filename from URL
        url_hash = abs(hash(url)) % (10 ** 10)
        cache_file = self.cache_dir / f"epg_{url_hash}.xml"
        
        # Check cache validity
        if use_cache and cache_file.exists():
            age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if age < 6 * 3600:  # 6 hours
                self.logger.info(f"Using cached EPG: {cache_file}")
                return cache_file
        
        # Fetch from URL
        self.logger.info(f"Fetching EPG from {url}")
        req = Request(url, headers={"User-Agent": self.user_agent})
        
        try:
            with urlopen(req, timeout=30) as response:
                data = response.read()
            
            # Decompress if gzipped
            if url.endswith(".gz") or data[:2] == b'\x1f\x8b':
                self.logger.debug("Decompressing gzipped EPG data")
                data = gzip.decompress(data)
            
            # Save to cache
            cache_file.write_bytes(data)
            self.logger.info(f"Cached EPG to {cache_file}")
            
            return cache_file
            
        except Exception as e:
            self.logger.error(f"Failed to fetch EPG from {url}: {e}")
            # Fall back to cache if available
            if cache_file.exists():
                self.logger.warning(f"Using stale cache: {cache_file}")
                return cache_file
            raise

    def parse_xmltv(
        self,
        xmltv_file: Path,
        target_timezone: timezone = timezone.utc,
        filter_channels: set[str] | None = None
    ) -> tuple[list[Channel], list[Programme]]:
        """
        Parse XMLTV file and extract channels and programmes.
        
        Args:
            xmltv_file: Path to XMLTV file
            target_timezone: Timezone to convert all times to
            filter_channels: Only parse these channel IDs (None = all)
            
        Returns:
            Tuple of (channels, programmes)
        """
        channels: list[Channel] = []
        programmes: list[Programme] = []
        
        try:
            tree = ET.parse(xmltv_file)
            root = tree.getroot()
            
            # Parse channels
            for channel_elem in root.findall("channel"):
                channel_id = channel_elem.get("id", "")
                if filter_channels and channel_id not in filter_channels:
                    continue
                
                display_name = ""
                icon = None
                url = None
                
                name_elem = channel_elem.find("display-name")
                if name_elem is not None and name_elem.text:
                    display_name = name_elem.text
                
                icon_elem = channel_elem.find("icon")
                if icon_elem is not None:
                    icon = icon_elem.get("src")
                
                url_elem = channel_elem.find("url")
                if url_elem is not None and url_elem.text:
                    url = url_elem.text
                
                channels.append(Channel(
                    id=channel_id,
                    display_name=display_name,
                    icon=icon,
                    url=url
                ))
            
            # Parse programmes
            for prog_elem in root.findall("programme"):
                channel_id = prog_elem.get("channel", "")
                if filter_channels and channel_id not in filter_channels:
                    continue
                
                start_str = prog_elem.get("start", "")
                stop_str = prog_elem.get("stop", "")
                
                if not start_str or not stop_str:
                    continue
                
                # Parse times and convert to target timezone
                start = self._parse_xmltv_time(start_str, target_timezone)
                stop = self._parse_xmltv_time(stop_str, target_timezone)
                
                if not start or not stop:
                    continue
                
                title = ""
                title_elem = prog_elem.find("title")
                if title_elem is not None and title_elem.text:
                    title = title_elem.text
                
                desc = None
                desc_elem = prog_elem.find("desc")
                if desc_elem is not None and desc_elem.text:
                    desc = desc_elem.text
                
                categories = []
                for cat_elem in prog_elem.findall("category"):
                    if cat_elem.text:
                        categories.append(cat_elem.text)
                
                icon = None
                icon_elem = prog_elem.find("icon")
                if icon_elem is not None:
                    icon = icon_elem.get("src")
                
                episode_num = None
                ep_elem = prog_elem.find("episode-num")
                if ep_elem is not None and ep_elem.text:
                    episode_num = ep_elem.text
                
                rating = None
                rating_elem = prog_elem.find("rating")
                if rating_elem is not None:
                    value_elem = rating_elem.find("value")
                    if value_elem is not None and value_elem.text:
                        rating = value_elem.text
                
                is_new = prog_elem.find("new") is not None
                is_live = prog_elem.find("live") is not None
                
                programmes.append(Programme(
                    channel=channel_id,
                    start=start,
                    stop=stop,
                    title=title,
                    desc=desc,
                    category=categories if categories else None,
                    icon=icon,
                    episode_num=episode_num,
                    rating=rating,
                    is_new=is_new,
                    is_live=is_live
                ))
            
            self.logger.info(f"Parsed {len(channels)} channels and {len(programmes)} programmes")
            return channels, programmes
            
        except Exception as e:
            self.logger.error(f"Failed to parse XMLTV: {e}")
            return [], []

    def _parse_xmltv_time(self, time_str: str, target_tz: timezone) -> datetime | None:
        """
        Parse XMLTV time format and convert to target timezone.
        
        Format: YYYYMMDDHHmmss +HHMM
        Example: 20260731120000 +0200
        """
        try:
            # Split time and offset
            parts = time_str.split()
            base_time = parts[0]
            
            # Parse base time
            dt = datetime.strptime(base_time[:14], "%Y%m%d%H%M%S")
            
            # Parse timezone offset if present
            if len(parts) > 1:
                offset_str = parts[1]
                # Extract hours and minutes from +HHMM or -HHMM
                sign = 1 if offset_str[0] == '+' else -1
                hours = int(offset_str[1:3])
                minutes = int(offset_str[3:5]) if len(offset_str) > 3 else 0
                offset = timedelta(hours=sign * hours, minutes=sign * minutes)
                dt = dt.replace(tzinfo=timezone(offset))
            else:
                # Assume UTC if no offset
                dt = dt.replace(tzinfo=timezone.utc)
            
            # Convert to target timezone
            return dt.astimezone(target_tz)
            
        except Exception as e:
            self.logger.debug(f"Failed to parse time '{time_str}': {e}")
            return None

    def get_current_programme(self, programmes: list[Programme], channel_id: str) -> Programme | None:
        """Get the currently airing programme for a channel."""
        now = datetime.now(timezone.utc)
        for prog in programmes:
            if prog.channel == channel_id and prog.start <= now < prog.stop:
                return prog
        return None

    def get_programmes_in_range(
        self,
        programmes: list[Programme],
        channel_id: str,
        start: datetime,
        end: datetime
    ) -> list[Programme]:
        """Get all programmes for a channel within a time range."""
        return [
            prog for prog in programmes
            if prog.channel == channel_id and prog.start < end and prog.stop > start
        ]


class ChannelLogoFetcher:
    """Fetch channel logos from tv-logo/tv-logos GitHub repository."""

    BASE_URL = "https://raw.githubusercontent.com/tv-logo/tv-logos/main"
    
    def __init__(self, country_code: str = "us", cache_dir: Path | None = None):
        self.country_code = country_code.lower()
        self.cache_dir = cache_dir or Path("./logo_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("logo_fetcher")

    def normalize_channel_name(self, name: str) -> str:
        """
        Normalize channel name to match tv-logos naming convention.
        
        Rules:
        - All lowercase
        - Spaces replaced with dashes
        - Remove special characters
        - Add country code suffix
        """
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove parentheses and content
        normalized = re.sub(r'\([^)]*\)', '', normalized)
        
        # Remove HD/SD/4K indicators
        normalized = re.sub(r'\b(hd|sd|4k|uhd|fhd)\b', '', normalized, flags=re.IGNORECASE)
        
        # Replace spaces and special chars with dashes
        normalized = re.sub(r'[^\w]+', '-', normalized)
        
        # Remove leading/trailing dashes
        normalized = normalized.strip('-')
        
        # Remove duplicate dashes
        normalized = re.sub(r'-+', '-', normalized)
        
        return f"{normalized}-{self.country_code}.png"

    def get_logo_url(self, channel_name: str, quality: str = "default") -> str:
        """
        Get direct URL to channel logo.
        
        Args:
            channel_name: Channel name (e.g., "CNN", "BBC One")
            quality: "default" or "hd"
            
        Returns:
            URL to logo PNG file
        """
        filename = self.normalize_channel_name(channel_name)
        
        if quality == "hd":
            path = f"countries/{self._get_country_path()}/hd/{filename}"
        else:
            path = f"countries/{self._get_country_path()}/{filename}"
        
        return f"{self.BASE_URL}/{path}"

    def _get_country_path(self) -> str:
        """Get country folder path from country code."""
        country_map = {
            "us": "united-states",
            "uk": "united-kingdom",
            "ca": "canada",
            "au": "australia",
            "de": "germany",
            "fr": "france",
            "es": "spain",
            "it": "italy",
            "br": "brazil",
            "in": "india",
            "jp": "japan",
            "kr": "south-korea",
            "mx": "mexico",
            "ar": "argentina",
            "nl": "netherlands",
            "se": "sweden",
            "no": "norway",
            "dk": "denmark",
            "fi": "finland",
            "pl": "poland",
            "tr": "turkey",
            "sa": "saudi-arabia",
            "ae": "united-arab-emirates",
        }
        return country_map.get(self.country_code, self.country_code)


def load_epg_config(config_file: Path) -> dict[str, Any]:
    """Load EPG configuration from YAML file."""
    if not yaml or not config_file.exists():
        return {}
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logging.error(f"Failed to load EPG config: {e}")
        return {}


# Example usage
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 epg_client.py <epg_url>")
        print("  python3 epg_client.py logo <channel_name> [country_code]")
        sys.exit(1)
    
    if sys.argv[1] == "logo":
        # Logo fetcher test
        channel_name = sys.argv[2] if len(sys.argv) > 2 else "CNN"
        country_code = sys.argv[3] if len(sys.argv) > 3 else "us"
        
        fetcher = ChannelLogoFetcher(country_code)
        url = fetcher.get_logo_url(channel_name)
        print(f"Logo URL for '{channel_name}': {url}")
    
    else:
        # EPG fetcher test
        epg_url = sys.argv[1]
        
        client = EPGClient()
        
        # Fetch EPG
        xmltv_file = client.fetch_xmltv(epg_url)
        
        # Parse with local timezone
        local_tz = datetime.now().astimezone().tzinfo
        channels, programmes = client.parse_xmltv(xmltv_file, local_tz)
        
        print(f"\nFound {len(channels)} channels:")
        for ch in channels[:10]:
            print(f"  {ch.id}: {ch.display_name}")
        
        print(f"\nFound {len(programmes)} programmes")
        
        if channels:
            # Show current programme for first channel
            first_channel = channels[0]
            current = client.get_current_programme(programmes, first_channel.id)
            if current:
                print(f"\nNow on {first_channel.display_name}:")
                print(f"  {current.title}")
                print(f"  {current.start.strftime('%H:%M')} - {current.stop.strftime('%H:%M')}")
                if current.desc:
                    print(f"  {current.desc[:100]}...")
