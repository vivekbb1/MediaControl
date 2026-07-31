"""
Screen Recording System
Capture video from displays, HDMI encoders, and sources

⚖️ LEGAL COMPLIANCE NOTICE:
- Screen recording is for PERSONAL, NON-COMMERCIAL use only
- Users MUST comply with copyright laws and content provider terms
- Prohibited uses: commercial redistribution, DRM bypass, piracy
- Permitted uses: time-shifting, personal archiving, accessibility
- Recording copyrighted content for redistribution is ILLEGAL
- See LEGAL_COMPLIANCE.md for full requirements

This feature does NOT bypass content protection (HDCP, DRM).
Users are solely responsible for their content usage.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import logging
import asyncio
import subprocess
import os

logger = logging.getLogger(__name__)


class RecordingQuality(Enum):
    """Recording quality presets"""
    LOW = "low"          # 720p, lower bitrate
    MEDIUM = "medium"    # 1080p, standard bitrate
    HIGH = "high"        # 1080p, high bitrate
    ULTRA = "ultra"      # 4K, max bitrate


class RecordingFormat(Enum):
    """Output file formats"""
    MP4 = "mp4"
    MKV = "mkv"
    MOV = "mov"
    AVI = "avi"


class RecordingState(Enum):
    """Recording states"""
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class RecordingSettings:
    """Recording configuration"""
    quality: RecordingQuality = RecordingQuality.MEDIUM
    format: RecordingFormat = RecordingFormat.MP4
    fps: int = 30
    audio_enabled: bool = True
    max_duration_minutes: Optional[int] = None  # Auto-stop after duration
    output_directory: str = "/var/media_recordings"
    filename_template: str = "{device}_{timestamp}.{format}"
    
    # Quality-specific settings
    resolution: Optional[str] = None  # e.g., "1920x1080"
    video_bitrate: Optional[str] = None  # e.g., "4000k"
    audio_bitrate: Optional[str] = None  # e.g., "192k"


@dataclass
class Recording:
    """Represents an active or completed recording"""
    id: str
    device_id: str
    device_name: str
    state: RecordingState
    settings: RecordingSettings
    start_time: datetime
    end_time: Optional[datetime] = None
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class ScreenRecorder:
    """
    Screen recording for HDMI encoders and displays
    Uses FFmpeg for video capture
    """
    
    def __init__(
        self,
        device_id: str,
        device_name: str,
        stream_url: str,
        settings: Optional[RecordingSettings] = None
    ):
        self.device_id = device_id
        self.device_name = device_name
        self.stream_url = stream_url  # RTSP, HTTP, etc.
        self.settings = settings or RecordingSettings()
        
        self.recording: Optional[Recording] = None
        self.process: Optional[subprocess.Popen] = None
        self.state = RecordingState.IDLE
        
        logger.info(f"ScreenRecorder initialized for {device_name}")
    
    def start_recording(self) -> Recording:
        """Start recording"""
        if self.state == RecordingState.RECORDING:
            logger.warning(f"Recording already in progress for {self.device_id}")
            return self.recording
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.settings.filename_template.format(
            device=self.device_id,
            timestamp=timestamp,
            format=self.settings.format.value
        )
        output_path = os.path.join(self.settings.output_directory, filename)
        
        # Ensure output directory exists
        os.makedirs(self.settings.output_directory, exist_ok=True)
        
        # Create recording object
        recording_id = f"rec_{timestamp}_{self.device_id}"
        self.recording = Recording(
            id=recording_id,
            device_id=self.device_id,
            device_name=self.device_name,
            state=RecordingState.RECORDING,
            settings=self.settings,
            start_time=datetime.now(),
            file_path=output_path,
            metadata={
                "stream_url": self.stream_url,
                "quality": self.settings.quality.value
            }
        )
        
        # Build FFmpeg command
        cmd = self._build_ffmpeg_command(self.stream_url, output_path)
        
        try:
            # Start FFmpeg process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.state = RecordingState.RECORDING
            logger.info(f"Started recording {self.device_name} to {output_path}")
            
            # Schedule auto-stop if max duration is set
            if self.settings.max_duration_minutes:
                asyncio.create_task(self._auto_stop_recording())
            
            return self.recording
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.recording.state = RecordingState.ERROR
            self.recording.error_message = str(e)
            self.state = RecordingState.ERROR
            return self.recording
    
    def stop_recording(self) -> Recording:
        """Stop recording"""
        if self.state != RecordingState.RECORDING:
            logger.warning(f"No active recording for {self.device_id}")
            return self.recording
        
        self.state = RecordingState.STOPPING
        
        try:
            # Send SIGTERM to FFmpeg for graceful shutdown
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=10)
            
            # Update recording metadata
            self.recording.end_time = datetime.now()
            self.recording.duration_seconds = int(
                (self.recording.end_time - self.recording.start_time).total_seconds()
            )
            
            # Get file size
            if self.recording.file_path and os.path.exists(self.recording.file_path):
                self.recording.file_size_bytes = os.path.getsize(self.recording.file_path)
            
            self.recording.state = RecordingState.COMPLETED
            self.state = RecordingState.IDLE
            
            logger.info(
                f"Stopped recording {self.device_name}. "
                f"Duration: {self.recording.duration_seconds}s, "
                f"Size: {self.recording.file_size_bytes / 1024 / 1024:.2f}MB"
            )
            
            return self.recording
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            self.recording.state = RecordingState.ERROR
            self.recording.error_message = str(e)
            self.state = RecordingState.ERROR
            return self.recording
    
    def pause_recording(self) -> bool:
        """Pause recording (if supported)"""
        # FFmpeg doesn't support pause natively
        # Would need to stop and resume in a new segment
        logger.warning("Pause not supported with FFmpeg recording")
        return False
    
    def get_status(self) -> Dict:
        """Get current recording status"""
        if not self.recording:
            return {"state": self.state.value, "recording": None}
        
        status = {
            "state": self.state.value,
            "recording": {
                "id": self.recording.id,
                "device": self.recording.device_name,
                "start_time": self.recording.start_time.isoformat(),
                "duration_seconds": None,
                "file_path": self.recording.file_path,
                "file_size_mb": None
            }
        }
        
        if self.state == RecordingState.RECORDING:
            # Calculate current duration
            duration = (datetime.now() - self.recording.start_time).total_seconds()
            status["recording"]["duration_seconds"] = int(duration)
            
            # Get current file size
            if self.recording.file_path and os.path.exists(self.recording.file_path):
                size_bytes = os.path.getsize(self.recording.file_path)
                status["recording"]["file_size_mb"] = round(size_bytes / 1024 / 1024, 2)
        
        return status
    
    def _build_ffmpeg_command(self, input_url: str, output_path: str) -> List[str]:
        """Build FFmpeg command based on settings"""
        cmd = ["ffmpeg", "-i", input_url]
        
        # Video codec and settings
        cmd.extend(["-c:v", "libx264"])
        
        # Quality presets
        if self.settings.quality == RecordingQuality.LOW:
            cmd.extend(["-s", "1280x720", "-b:v", "2000k"])
        elif self.settings.quality == RecordingQuality.MEDIUM:
            cmd.extend(["-s", "1920x1080", "-b:v", "4000k"])
        elif self.settings.quality == RecordingQuality.HIGH:
            cmd.extend(["-s", "1920x1080", "-b:v", "8000k"])
        elif self.settings.quality == RecordingQuality.ULTRA:
            cmd.extend(["-s", "3840x2160", "-b:v", "20000k"])
        
        # Override with custom settings if provided
        if self.settings.resolution:
            cmd.extend(["-s", self.settings.resolution])
        if self.settings.video_bitrate:
            cmd.extend(["-b:v", self.settings.video_bitrate])
        
        # FPS
        cmd.extend(["-r", str(self.settings.fps)])
        
        # Audio settings
        if self.settings.audio_enabled:
            cmd.extend(["-c:a", "aac", "-b:a", self.settings.audio_bitrate or "192k"])
        else:
            cmd.extend(["-an"])  # No audio
        
        # Output format
        cmd.extend(["-f", self.settings.format.value])
        
        # Other settings
        cmd.extend([
            "-preset", "fast",
            "-movflags", "+faststart",  # Web-friendly MP4
            output_path
        ])
        
        return cmd
    
    async def _auto_stop_recording(self):
        """Auto-stop recording after max duration"""
        duration_seconds = self.settings.max_duration_minutes * 60
        await asyncio.sleep(duration_seconds)
        
        if self.state == RecordingState.RECORDING:
            logger.info(f"Auto-stopping recording after {self.settings.max_duration_minutes} minutes")
            self.stop_recording()


class RecordingManager:
    """
    Manages screen recordings across multiple devices
    """
    
    def __init__(self):
        self.recorders: Dict[str, ScreenRecorder] = {}
        self.recordings: Dict[str, Recording] = {}  # All recordings (active + completed)
        logger.info("RecordingManager initialized")
    
    def register_device(
        self,
        device_id: str,
        device_name: str,
        stream_url: str,
        settings: Optional[RecordingSettings] = None
    ):
        """Register a device for recording"""
        recorder = ScreenRecorder(device_id, device_name, stream_url, settings)
        self.recorders[device_id] = recorder
        logger.info(f"Registered recording device: {device_name}")
    
    def start_recording(self, device_id: str) -> Optional[Recording]:
        """Start recording a device"""
        recorder = self.recorders.get(device_id)
        if not recorder:
            logger.error(f"Device {device_id} not registered for recording")
            return None
        
        recording = recorder.start_recording()
        self.recordings[recording.id] = recording
        return recording
    
    def stop_recording(self, device_id: str) -> Optional[Recording]:
        """Stop recording a device"""
        recorder = self.recorders.get(device_id)
        if not recorder:
            logger.error(f"Device {device_id} not registered for recording")
            return None
        
        return recorder.stop_recording()
    
    def get_active_recordings(self) -> List[Recording]:
        """Get all active recordings"""
        return [
            recorder.recording
            for recorder in self.recorders.values()
            if recorder.recording and recorder.state == RecordingState.RECORDING
        ]
    
    def get_recording_history(self, limit: int = 50) -> List[Recording]:
        """Get recording history"""
        sorted_recordings = sorted(
            self.recordings.values(),
            key=lambda r: r.start_time,
            reverse=True
        )
        return sorted_recordings[:limit]
    
    def get_device_status(self, device_id: str) -> Optional[Dict]:
        """Get recording status for a device"""
        recorder = self.recorders.get(device_id)
        if not recorder:
            return None
        
        return recorder.get_status()
    
    def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording file"""
        recording = self.recordings.get(recording_id)
        if not recording:
            return False
        
        try:
            if recording.file_path and os.path.exists(recording.file_path):
                os.remove(recording.file_path)
                logger.info(f"Deleted recording: {recording.file_path}")
            
            del self.recordings[recording_id]
            return True
        except Exception as e:
            logger.error(f"Failed to delete recording: {e}")
            return False


# Configuration example
RECORDING_CONFIG_EXAMPLE = """
# Recording configuration for displays/encoders

recording_devices:
  main_display:
    device_id: "display_1"
    device_name: "Main Conference Room Display"
    stream_url: "rtsp://192.168.1.100:554/stream1"
    settings:
      quality: high
      format: mp4
      max_duration_minutes: 120  # Auto-stop after 2 hours
      output_directory: "/var/recordings"
  
  presentation_capture:
    device_id: "hdmi_encoder_1"
    device_name: "Presentation HDMI Capture"
    stream_url: "http://192.168.1.101:8080/stream.mjpg"
    settings:
      quality: ultra
      format: mkv
      audio_enabled: true
      max_duration_minutes: 60

# Usage in presets
presets:
  record_meeting:
    name: "Record Meeting"
    actions:
      - type: start_recording
        device: main_display
      - type: display_power
        device: main_display
        state: on
      - type: display_input
        device: main_display
        input: HDMI1
  
  stop_recording:
    name: "Stop Recording"
    actions:
      - type: stop_recording
        device: main_display
      - type: notification
        message: "Recording saved"
"""
