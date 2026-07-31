"""
Video Streaming Integration
Support for HDMI-to-IP encoders and live video streaming
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StreamProtocol(Enum):
    """Video streaming protocols"""
    RTSP = "rtsp"
    HLS = "hls"
    WEBRTC = "webrtc"
    NDI = "ndi"
    HTTP_MJPEG = "http_mjpeg"


class StreamQuality(Enum):
    """Stream quality presets"""
    LOW = "low"  # 480p, lower bitrate
    MEDIUM = "medium"  # 720p, medium bitrate
    HIGH = "high"  # 1080p, high bitrate
    ULTRA = "ultra"  # 4K, ultra bitrate


@dataclass
class StreamSource:
    """
    A streamable video source (encoder or camera)
    """
    id: str
    name: str
    protocol: StreamProtocol
    url: str
    quality: StreamQuality = StreamQuality.HIGH
    audio_enabled: bool = True
    latency_mode: str = "normal"  # "low", "normal", "high"
    credentials: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = None


class HDMIEncoder:
    """
    HDMI-to-IP Encoder for streaming display/source output
    """
    
    def __init__(
        self,
        encoder_id: str,
        name: str,
        ip: str,
        port: int = 554,  # RTSP default
        protocol: StreamProtocol = StreamProtocol.RTSP,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.id = encoder_id
        self.name = name
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.username = username
        self.password = password
        
        # Stream sources (different quality/audio options)
        self.streams: Dict[StreamQuality, StreamSource] = {}
        self._generate_stream_urls()
    
    def _generate_stream_urls(self):
        """Generate stream URLs for different qualities"""
        base_url = self._get_base_url()
        
        # RTSP streams (most common for encoders)
        if self.protocol == StreamProtocol.RTSP:
            self.streams[StreamQuality.HIGH] = StreamSource(
                id=f"{self.id}-high",
                name=f"{self.name} (1080p)",
                protocol=StreamProtocol.RTSP,
                url=f"{base_url}/stream1",
                quality=StreamQuality.HIGH,
            )
            self.streams[StreamQuality.MEDIUM] = StreamSource(
                id=f"{self.id}-medium",
                name=f"{self.name} (720p)",
                protocol=StreamProtocol.RTSP,
                url=f"{base_url}/stream2",
                quality=StreamQuality.MEDIUM,
            )
            self.streams[StreamQuality.LOW] = StreamSource(
                id=f"{self.id}-low",
                name=f"{self.name} (480p)",
                protocol=StreamProtocol.RTSP,
                url=f"{base_url}/stream3",
                quality=StreamQuality.LOW,
            )
        
        # HLS streams
        elif self.protocol == StreamProtocol.HLS:
            self.streams[StreamQuality.HIGH] = StreamSource(
                id=f"{self.id}-high",
                name=f"{self.name} (HLS)",
                protocol=StreamProtocol.HLS,
                url=f"{base_url}/stream/high/playlist.m3u8",
                quality=StreamQuality.HIGH,
            )
    
    def _get_base_url(self) -> str:
        """Get base URL with credentials if needed"""
        if self.protocol == StreamProtocol.RTSP:
            if self.username and self.password:
                return f"rtsp://{self.username}:{self.password}@{self.ip}:{self.port}"
            return f"rtsp://{self.ip}:{self.port}"
        
        elif self.protocol == StreamProtocol.HLS:
            return f"http://{self.ip}:{self.port}"
        
        return f"http://{self.ip}:{self.port}"
    
    def get_stream(self, quality: StreamQuality = StreamQuality.HIGH) -> Optional[StreamSource]:
        """Get stream URL for a specific quality"""
        return self.streams.get(quality)
    
    def get_all_streams(self) -> List[StreamSource]:
        """Get all available stream qualities"""
        return list(self.streams.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize encoder"""
        return {
            "id": self.id,
            "name": self.name,
            "ip": self.ip,
            "protocol": self.protocol.value,
            "streams": [
                {
                    "id": stream.id,
                    "name": stream.name,
                    "url": stream.url,
                    "quality": stream.quality.value,
                    "protocol": stream.protocol.value,
                }
                for stream in self.streams.values()
            ],
        }


class StreamManager:
    """
    Manages video streams from encoders and sources
    """
    
    def __init__(self):
        self.encoders: Dict[str, HDMIEncoder] = {}
        self.active_streams: Dict[str, StreamSource] = {}  # client_id → stream
        logger.info("StreamManager initialized")
    
    def add_encoder(self, encoder: HDMIEncoder):
        """Register an encoder"""
        self.encoders[encoder.id] = encoder
        logger.info(f"Added encoder: {encoder.name} ({encoder.id})")
    
    def get_encoder(self, encoder_id: str) -> Optional[HDMIEncoder]:
        """Get encoder by ID"""
        return self.encoders.get(encoder_id)
    
    def get_all_streams(self) -> List[StreamSource]:
        """Get all available streams from all encoders"""
        streams = []
        for encoder in self.encoders.values():
            streams.extend(encoder.get_all_streams())
        return streams
    
    def start_stream(
        self,
        client_id: str,
        encoder_id: str,
        quality: StreamQuality = StreamQuality.HIGH,
    ) -> Optional[StreamSource]:
        """
        Start streaming for a client
        
        Args:
            client_id: Unique client identifier
            encoder_id: Encoder to stream from
            quality: Stream quality
        
        Returns:
            StreamSource if successful
        """
        encoder = self.get_encoder(encoder_id)
        if not encoder:
            logger.error(f"Encoder not found: {encoder_id}")
            return None
        
        stream = encoder.get_stream(quality)
        if not stream:
            logger.error(f"Stream not available: {encoder_id} @ {quality}")
            return None
        
        self.active_streams[client_id] = stream
        logger.info(f"Started stream for client {client_id}: {stream.url}")
        return stream
    
    def stop_stream(self, client_id: str):
        """Stop streaming for a client"""
        if client_id in self.active_streams:
            del self.active_streams[client_id]
            logger.info(f"Stopped stream for client {client_id}")
    
    def get_active_stream(self, client_id: str) -> Optional[StreamSource]:
        """Get active stream for a client"""
        return self.active_streams.get(client_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize stream manager state"""
        return {
            "encoders": [encoder.to_dict() for encoder in self.encoders.values()],
            "active_streams": {
                client_id: {
                    "stream_id": stream.id,
                    "url": stream.url,
                    "quality": stream.quality.value,
                }
                for client_id, stream in self.active_streams.items()
            },
        }


# Popular encoder configurations
ENCODER_PRESETS = {
    "magewell": {
        "protocol": StreamProtocol.RTSP,
        "port": 554,
        "stream_paths": {
            StreamQuality.HIGH: "/stream1",
            StreamQuality.MEDIUM: "/stream2",
            StreamQuality.LOW: "/stream3",
        },
    },
    "blackmagic_webpresenter": {
        "protocol": StreamProtocol.HLS,
        "port": 80,
        "stream_paths": {
            StreamQuality.HIGH: "/stream/high/playlist.m3u8",
        },
    },
    "epiphan": {
        "protocol": StreamProtocol.RTSP,
        "port": 554,
        "stream_paths": {
            StreamQuality.HIGH: "/stream.sdp",
        },
    },
}


# Frontend video player component
VIDEO_PLAYER_REACT = """
// VideoPlayer.tsx
import React, { useEffect, useRef, useState } from 'react';

interface Stream {
  id: string;
  name: string;
  url: string;
  quality: string;
  protocol: string;
}

interface Props {
  stream: Stream | null;
  onError?: (error: string) => void;
  onQualityChange?: (quality: string) => void;
}

export const VideoPlayer: React.FC<Props> = ({ stream, onError, onQualityChange }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!stream || !videoRef.current) return;

    setLoading(true);
    setError(null);

    // HLS streams (requires hls.js)
    if (stream.protocol === 'hls') {
      if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        videoRef.current.src = stream.url;
      } else if (window.Hls && Hls.isSupported()) {
        // Use hls.js for other browsers
        const hls = new Hls();
        hls.loadSource(stream.url);
        hls.attachMedia(videoRef.current);
        
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          setLoading(false);
          videoRef.current?.play();
        });
        
        hls.on(Hls.Events.ERROR, (event, data) => {
          const errorMsg = `HLS Error: ${data.type} - ${data.details}`;
          setError(errorMsg);
          setLoading(false);
          onError?.(errorMsg);
        });
        
        return () => {
          hls.destroy();
        };
      }
    }
    
    // RTSP streams (requires WebRTC gateway or RTSP-to-HLS transcoding)
    else if (stream.protocol === 'rtsp') {
      // Most browsers can't play RTSP directly
      // Need server-side transcoding to HLS or WebRTC
      const transcodedUrl = `/api/stream/transcode?url=${encodeURIComponent(stream.url)}`;
      videoRef.current.src = transcodedUrl;
    }
    
    // HTTP-based streams
    else {
      videoRef.current.src = stream.url;
    }

    videoRef.current.onloadstart = () => setLoading(true);
    videoRef.current.onloadeddata = () => setLoading(false);
    videoRef.current.onerror = () => {
      const err = 'Failed to load video stream';
      setError(err);
      setLoading(false);
      onError?.(err);
    };

  }, [stream]);

  if (!stream) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900 text-gray-400">
        <p>No stream selected</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full bg-black">
      <video
        ref={videoRef}
        className="w-full h-full"
        autoPlay
        playsInline
        muted={false}
      />
      
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75">
          <div className="text-white">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
            <p>Loading stream...</p>
          </div>
        </div>
      )}
      
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-900 bg-opacity-75">
          <div className="text-white text-center">
            <p className="font-bold mb-2">Stream Error</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}
      
      {/* Stream Info Overlay */}
      <div className="absolute top-4 right-4 bg-black bg-opacity-75 px-3 py-2 rounded text-white text-sm">
        <p className="font-bold">{stream.name}</p>
        <p className="text-gray-300">{stream.quality} • {stream.protocol.toUpperCase()}</p>
      </div>
    </div>
  );
};
"""
