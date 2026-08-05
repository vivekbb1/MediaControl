"""
Enhanced Scheduled Audio Automation
Advanced scheduling specifically for audio/music automation
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from datetime import time, datetime
import logging

logger = logging.getLogger(__name__)


class AudioScheduleType(Enum):
    """Types of audio schedules"""
    WAKE_UP = "wake_up"              # Gradual volume increase
    SLEEP = "sleep"                   # Gradual volume decrease
    WORKOUT = "workout"               # High-energy playlists
    FOCUS = "focus"                   # Concentration music
    MEDITATION = "meditation"         # Calm, ambient music
    PARTY = "party"                   # Party mode
    DINNER = "dinner"                 # Dinner background music
    READING = "reading"               # Soft background music
    CUSTOM = "custom"


@dataclass
class AudioSchedule:
    """Scheduled audio automation"""
    name: str
    schedule_type: AudioScheduleType
    time: time
    days_of_week: List[int]  # 0=Monday, 6=Sunday
    
    # Audio settings
    service: str  # spotify, apple_music, etc.
    playlist_uri: Optional[str] = None
    artist: Optional[str] = None
    genre: Optional[str] = None
    
    # Device settings
    devices: List[str] = None
    volume_start: Optional[int] = None
    volume_end: Optional[int] = None
    fade_duration_minutes: Optional[int] = None
    
    # DSP settings
    eq_preset: Optional[str] = None
    crossfade_enabled: bool = True
    
    # Advanced
    stop_after_minutes: Optional[int] = None
    enabled: bool = True


class ScheduledAudioManager:
    """
    Manages scheduled audio automation
    Extends the basic alarm_scheduler with audio-specific features
    """
    
    def __init__(self, alarm_scheduler, media_manager, audio_dsp):
        self.alarm_scheduler = alarm_scheduler
        self.media_manager = media_manager
        self.audio_dsp = audio_dsp
        self.schedules: Dict[str, AudioSchedule] = {}
        logger.info("ScheduledAudioManager initialized")
    
    def create_wake_up_schedule(
        self,
        name: str,
        wake_time: time,
        days_of_week: List[int],
        devices: List[str],
        playlist_uri: str = "spotify:playlist:morning",
        fade_minutes: int = 10
    ) -> AudioSchedule:
        """
        Create wake-up audio schedule with gradual volume increase
        
        Args:
            name: Schedule name
            wake_time: Time to complete wake-up (full volume)
            days_of_week: Days to trigger (0=Mon, 6=Sun)
            devices: Audio devices
            playlist_uri: Playlist to play
            fade_minutes: Duration of volume fade-in
            
        Returns:
            AudioSchedule object
        """
        schedule = AudioSchedule(
            name=name,
            schedule_type=AudioScheduleType.WAKE_UP,
            time=wake_time,
            days_of_week=days_of_week,
            service="spotify",
            playlist_uri=playlist_uri,
            devices=devices,
            volume_start=0,
            volume_end=40,
            fade_duration_minutes=fade_minutes,
            eq_preset="vocal",
            crossfade_enabled=True
        )
        
        self.schedules[name] = schedule
        
        # Create alarm with actions
        actions = self._build_wake_up_actions(schedule)
        self.alarm_scheduler.create_alarm(
            user_id="system",
            name=name,
            schedule_type="weekly",
            time_of_day=wake_time,
            days_of_week=days_of_week,
            actions=actions
        )
        
        logger.info(f"Created wake-up schedule: {name} at {wake_time}")
        return schedule
    
    def create_sleep_schedule(
        self,
        name: str,
        sleep_time: time,
        days_of_week: List[int],
        devices: List[str],
        playlist_uri: str = "spotify:playlist:sleep",
        fade_minutes: int = 30
    ) -> AudioSchedule:
        """
        Create sleep audio schedule with gradual volume decrease and auto-stop
        """
        schedule = AudioSchedule(
            name=name,
            schedule_type=AudioScheduleType.SLEEP,
            time=sleep_time,
            days_of_week=days_of_week,
            service="spotify",
            playlist_uri=playlist_uri,
            devices=devices,
            volume_start=30,
            volume_end=0,
            fade_duration_minutes=fade_minutes,
            eq_preset="ambient",
            crossfade_enabled=True,
            stop_after_minutes=fade_minutes
        )
        
        self.schedules[name] = schedule
        
        actions = self._build_sleep_actions(schedule)
        self.alarm_scheduler.create_alarm(
            user_id="system",
            name=name,
            schedule_type="weekly",
            time_of_day=sleep_time,
            days_of_week=days_of_week,
            actions=actions
        )
        
        logger.info(f"Created sleep schedule: {name} at {sleep_time}")
        return schedule
    
    def create_workout_schedule(
        self,
        name: str,
        workout_time: time,
        days_of_week: List[int],
        devices: List[str],
        duration_minutes: int = 60
    ) -> AudioSchedule:
        """Create workout audio schedule"""
        schedule = AudioSchedule(
            name=name,
            schedule_type=AudioScheduleType.WORKOUT,
            time=workout_time,
            days_of_week=days_of_week,
            service="spotify",
            genre="workout",
            devices=devices,
            volume_start=70,
            volume_end=70,
            eq_preset="bass_boost",
            stop_after_minutes=duration_minutes
        )
        
        self.schedules[name] = schedule
        logger.info(f"Created workout schedule: {name}")
        return schedule
    
    def _build_wake_up_actions(self, schedule: AudioSchedule) -> List:
        """Build actions for wake-up schedule"""
        from alarm_scheduler import ScheduledAction, ActionType
        
        actions = []
        
        # Set EQ preset
        if schedule.eq_preset:
            actions.append(
                ScheduledAction(
                    type=ActionType.CUSTOM,
                    parameters={
                        "function": "set_eq_preset",
                        "devices": schedule.devices,
                        "preset": schedule.eq_preset
                    }
                )
            )
        
        # Start music at low volume
        actions.append(
            ScheduledAction(
                type=ActionType.AUDIO_VOLUME,
                parameters={
                    "devices": schedule.devices,
                    "volume": schedule.volume_start
                }
            )
        )
        
        actions.append(
            ScheduledAction(
                type=ActionType.MEDIA_SERVICE,
                parameters={
                    "service": schedule.service,
                    "action": "play",
                    "uri": schedule.playlist_uri,
                    "devices": schedule.devices
                }
            )
        )
        
        # Gradual volume increase
        actions.append(
            ScheduledAction(
                type=ActionType.AUDIO_VOLUME,
                parameters={
                    "devices": schedule.devices,
                    "volume": schedule.volume_end,
                    "fade_duration": schedule.fade_duration_minutes * 60
                }
            )
        )
        
        return actions
    
    def _build_sleep_actions(self, schedule: AudioSchedule) -> List:
        """Build actions for sleep schedule"""
        from alarm_scheduler import ScheduledAction, ActionType
        
        actions = []
        
        # Set EQ preset
        if schedule.eq_preset:
            actions.append(
                ScheduledAction(
                    type=ActionType.CUSTOM,
                    parameters={
                        "function": "set_eq_preset",
                        "devices": schedule.devices,
                        "preset": schedule.eq_preset
                    }
                )
            )
        
        # Start music
        actions.append(
            ScheduledAction(
                type=ActionType.MEDIA_SERVICE,
                parameters={
                    "service": schedule.service,
                    "action": "play",
                    "uri": schedule.playlist_uri,
                    "devices": schedule.devices
                }
            )
        )
        
        actions.append(
            ScheduledAction(
                type=ActionType.AUDIO_VOLUME,
                parameters={
                    "devices": schedule.devices,
                    "volume": schedule.volume_start
                }
            )
        )
        
        # Gradual volume decrease
        actions.append(
            ScheduledAction(
                type=ActionType.AUDIO_VOLUME,
                parameters={
                    "devices": schedule.devices,
                    "volume": schedule.volume_end,
                    "fade_duration": schedule.fade_duration_minutes * 60
                }
            )
        )
        
        # Stop after fade completes
        if schedule.stop_after_minutes:
            actions.append(
                ScheduledAction(
                    type=ActionType.MEDIA_SERVICE,
                    parameters={
                        "service": schedule.service,
                        "action": "stop",
                        "devices": schedule.devices,
                        "delay": schedule.stop_after_minutes * 60
                    }
                )
            )
        
        return actions


# Usage examples
SCHEDULED_AUDIO_EXAMPLES = """
# Wake-up schedule

from scheduled_audio import ScheduledAudioManager
from datetime import time

audio_scheduler = ScheduledAudioManager(
    alarm_scheduler=alarm_mgr,
    media_manager=media_mgr,
    audio_dsp=dsp
)

# Create wake-up schedule (weekdays)
wake_up = audio_scheduler.create_wake_up_schedule(
    name="Weekday Wake-Up",
    wake_time=time(7, 0),  # 7:00 AM
    days_of_week=[0, 1, 2, 3, 4],  # Mon-Fri
    devices=["bedroom_sonos"],
    playlist_uri="spotify:playlist:37i9dQZF1DX0H9VYs5EqYz",
    fade_minutes=10  # Start at 6:50 AM, reach full volume at 7:00 AM
)

# Create sleep schedule (every night)
sleep = audio_scheduler.create_sleep_schedule(
    name="Sleep Timer",
    sleep_time=time(22, 30),  # 10:30 PM
    days_of_week=[0, 1, 2, 3, 4, 5, 6],  # Every day
    devices=["bedroom_sonos"],
    playlist_uri="spotify:playlist:sleep_sounds",
    fade_minutes=30  # Fade out over 30 minutes, stop at 11:00 PM
)

# Workout schedule
workout = audio_scheduler.create_workout_schedule(
    name="Morning Workout",
    workout_time=time(6, 0),
    days_of_week=[1, 3, 5],  # Tue, Thu, Sat
    devices=["gym_speakers"],
    duration_minutes=45
)
"""
