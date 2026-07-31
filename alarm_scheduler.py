"""
Alarm and Scheduling System
Schedule actions, create alarms, automate routines
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta, time
import logging
import asyncio
import json
from croniter import croniter

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Types of schedules"""
    ONE_TIME = "one_time"        # Execute once at specific time
    DAILY = "daily"              # Repeat daily
    WEEKLY = "weekly"            # Repeat weekly
    CRON = "cron"                # Cron expression
    INTERVAL = "interval"        # Repeat every X minutes/hours


class ActionType(Enum):
    """Types of actions that can be scheduled"""
    DISPLAY_POWER = "display_power"
    DISPLAY_INPUT = "display_input"
    SOURCE_POWER = "source_power"
    SOURCE_APP = "source_app"
    PRESET = "preset"
    RECORDING_START = "recording_start"
    RECORDING_STOP = "recording_stop"
    AUDIO_PLAY = "audio_play"
    AUDIO_VOLUME = "audio_volume"
    MEDIA_SERVICE = "media_service"
    NOTIFICATION = "notification"
    SCENE = "scene"
    CUSTOM = "custom"


@dataclass
class ScheduledAction:
    """An action to be executed"""
    type: ActionType
    parameters: Dict[str, Any]
    description: Optional[str] = None


@dataclass
class Alarm:
    """An alarm/scheduled task"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    schedule_type: ScheduleType
    enabled: bool = True
    
    # Scheduling
    execute_at: Optional[datetime] = None  # For ONE_TIME
    time_of_day: Optional[time] = None     # For DAILY/WEEKLY
    days_of_week: Optional[List[int]] = None  # 0=Monday, 6=Sunday (for WEEKLY)
    cron_expression: Optional[str] = None   # For CRON
    interval_minutes: Optional[int] = None  # For INTERVAL
    
    # Actions to execute
    actions: List[ScheduledAction] = field(default_factory=list)
    
    # Execution tracking
    last_executed: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    execution_count: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class AlarmExecution:
    """Record of an alarm execution"""
    id: str
    alarm_id: str
    executed_at: datetime
    success: bool
    actions_executed: int
    actions_failed: int
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None


class AlarmScheduler:
    """
    Manages alarms and scheduled tasks
    """
    
    def __init__(self):
        self.alarms: Dict[str, Alarm] = {}
        self.executions: List[AlarmExecution] = []
        self.action_handlers: Dict[ActionType, Callable] = {}
        
        self.running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        
        logger.info("AlarmScheduler initialized")
    
    def register_action_handler(
        self,
        action_type: ActionType,
        handler: Callable
    ):
        """Register a handler for an action type"""
        self.action_handlers[action_type] = handler
        logger.info(f"Registered action handler for {action_type.value}")
    
    def create_alarm(
        self,
        user_id: str,
        name: str,
        schedule_type: ScheduleType,
        actions: List[ScheduledAction],
        description: Optional[str] = None,
        **schedule_params
    ) -> Alarm:
        """Create a new alarm/scheduled task"""
        alarm_id = f"alarm_{user_id}_{datetime.now().timestamp()}"
        
        alarm = Alarm(
            id=alarm_id,
            user_id=user_id,
            name=name,
            description=description,
            schedule_type=schedule_type,
            actions=actions,
            **schedule_params
        )
        
        # Calculate next execution time
        alarm.next_execution = self._calculate_next_execution(alarm)
        
        self.alarms[alarm_id] = alarm
        logger.info(
            f"Created alarm '{name}' (type: {schedule_type.value}), "
            f"next execution: {alarm.next_execution}"
        )
        
        return alarm
    
    def create_one_time_alarm(
        self,
        user_id: str,
        name: str,
        execute_at: datetime,
        actions: List[ScheduledAction],
        description: Optional[str] = None
    ) -> Alarm:
        """Create a one-time alarm"""
        return self.create_alarm(
            user_id=user_id,
            name=name,
            schedule_type=ScheduleType.ONE_TIME,
            actions=actions,
            description=description,
            execute_at=execute_at
        )
    
    def create_daily_alarm(
        self,
        user_id: str,
        name: str,
        time_of_day: time,
        actions: List[ScheduledAction],
        description: Optional[str] = None
    ) -> Alarm:
        """Create a daily recurring alarm"""
        return self.create_alarm(
            user_id=user_id,
            name=name,
            schedule_type=ScheduleType.DAILY,
            actions=actions,
            description=description,
            time_of_day=time_of_day
        )
    
    def create_weekly_alarm(
        self,
        user_id: str,
        name: str,
        time_of_day: time,
        days_of_week: List[int],
        actions: List[ScheduledAction],
        description: Optional[str] = None
    ) -> Alarm:
        """Create a weekly recurring alarm"""
        return self.create_alarm(
            user_id=user_id,
            name=name,
            schedule_type=ScheduleType.WEEKLY,
            actions=actions,
            description=description,
            time_of_day=time_of_day,
            days_of_week=days_of_week
        )
    
    def delete_alarm(self, alarm_id: str) -> bool:
        """Delete an alarm"""
        if alarm_id in self.alarms:
            del self.alarms[alarm_id]
            logger.info(f"Deleted alarm {alarm_id}")
            return True
        return False
    
    def enable_alarm(self, alarm_id: str) -> bool:
        """Enable an alarm"""
        alarm = self.alarms.get(alarm_id)
        if alarm:
            alarm.enabled = True
            alarm.next_execution = self._calculate_next_execution(alarm)
            logger.info(f"Enabled alarm {alarm_id}")
            return True
        return False
    
    def disable_alarm(self, alarm_id: str) -> bool:
        """Disable an alarm"""
        alarm = self.alarms.get(alarm_id)
        if alarm:
            alarm.enabled = False
            logger.info(f"Disabled alarm {alarm_id}")
            return True
        return False
    
    def get_user_alarms(self, user_id: str) -> List[Alarm]:
        """Get all alarms for a user"""
        user_alarms = [
            alarm for alarm in self.alarms.values()
            if alarm.user_id == user_id
        ]
        user_alarms.sort(key=lambda a: a.next_execution or datetime.max)
        return user_alarms
    
    async def start(self):
        """Start the alarm scheduler"""
        if self.running:
            logger.warning("Alarm scheduler already running")
            return
        
        self.running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Alarm scheduler started")
    
    async def stop(self):
        """Stop the alarm scheduler"""
        self.running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Alarm scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._check_alarms()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_alarms(self):
        """Check for alarms that should be executed"""
        now = datetime.now()
        
        for alarm in self.alarms.values():
            if not alarm.enabled or not alarm.next_execution:
                continue
            
            # Check if it's time to execute
            if now >= alarm.next_execution:
                await self._execute_alarm(alarm)
    
    async def _execute_alarm(self, alarm: Alarm):
        """Execute an alarm"""
        logger.info(f"Executing alarm '{alarm.name}'")
        
        start_time = datetime.now()
        execution_id = f"exec_{alarm.id}_{start_time.timestamp()}"
        
        actions_executed = 0
        actions_failed = 0
        error_messages = []
        
        # Execute each action
        for action in alarm.actions:
            try:
                await self._execute_action(action)
                actions_executed += 1
            except Exception as e:
                actions_failed += 1
                error_msg = f"Action {action.type.value} failed: {e}"
                error_messages.append(error_msg)
                logger.error(error_msg)
        
        # Record execution
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        execution = AlarmExecution(
            id=execution_id,
            alarm_id=alarm.id,
            executed_at=start_time,
            success=actions_failed == 0,
            actions_executed=actions_executed,
            actions_failed=actions_failed,
            error_message="; ".join(error_messages) if error_messages else None,
            duration_ms=duration_ms
        )
        
        self.executions.append(execution)
        
        # Update alarm
        alarm.last_executed = start_time
        alarm.execution_count += 1
        
        # Calculate next execution (for recurring alarms)
        if alarm.schedule_type != ScheduleType.ONE_TIME:
            alarm.next_execution = self._calculate_next_execution(alarm)
            logger.info(f"Next execution for '{alarm.name}': {alarm.next_execution}")
        else:
            alarm.enabled = False  # Disable one-time alarms after execution
            alarm.next_execution = None
    
    async def _execute_action(self, action: ScheduledAction):
        """Execute a single action"""
        handler = self.action_handlers.get(action.type)
        if not handler:
            raise ValueError(f"No handler registered for action type {action.type.value}")
        
        logger.info(f"Executing action: {action.type.value}")
        await handler(action.parameters)
    
    def _calculate_next_execution(self, alarm: Alarm) -> Optional[datetime]:
        """Calculate next execution time for an alarm"""
        now = datetime.now()
        
        if alarm.schedule_type == ScheduleType.ONE_TIME:
            return alarm.execute_at
        
        elif alarm.schedule_type == ScheduleType.DAILY:
            # Next occurrence of time_of_day
            next_time = datetime.combine(now.date(), alarm.time_of_day)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time
        
        elif alarm.schedule_type == ScheduleType.WEEKLY:
            # Next occurrence on specified days of week
            current_weekday = now.weekday()
            days_ahead = None
            
            for day in sorted(alarm.days_of_week):
                if day > current_weekday:
                    days_ahead = day - current_weekday
                    break
            
            if days_ahead is None:
                # Next occurrence is next week
                days_ahead = (7 - current_weekday) + alarm.days_of_week[0]
            
            next_date = now.date() + timedelta(days=days_ahead)
            next_time = datetime.combine(next_date, alarm.time_of_day)
            
            return next_time
        
        elif alarm.schedule_type == ScheduleType.CRON:
            # Use croniter for cron expressions
            cron = croniter(alarm.cron_expression, now)
            return cron.get_next(datetime)
        
        elif alarm.schedule_type == ScheduleType.INTERVAL:
            # Interval from last execution or now
            base_time = alarm.last_executed or now
            return base_time + timedelta(minutes=alarm.interval_minutes)
        
        return None


# Pre-built alarm templates
class AlarmTemplates:
    """Common alarm templates"""
    
    @staticmethod
    def morning_routine(
        user_id: str,
        time: time,
        playlist_uri: str,
        volume: int = 30
    ) -> List[ScheduledAction]:
        """Morning wake-up routine"""
        return [
            ScheduledAction(
                type=ActionType.AUDIO_VOLUME,
                parameters={"device": "bedroom_speakers", "volume": 0}
            ),
            ScheduledAction(
                type=ActionType.MEDIA_SERVICE,
                parameters={
                    "service": "spotify",
                    "action": "play",
                    "device": "bedroom_speakers",
                    "uri": playlist_uri
                }
            ),
            ScheduledAction(
                type=ActionType.AUDIO_VOLUME,
                parameters={
                    "device": "bedroom_speakers",
                    "volume": volume,
                    "fade_duration": 30  # Fade in over 30 seconds
                }
            ),
            ScheduledAction(
                type=ActionType.NOTIFICATION,
                parameters={
                    "message": "Good morning! Time to wake up.",
                    "channels": ["on_screen"]
                }
            )
        ]
    
    @staticmethod
    def movie_night(
        user_id: str,
        time: time,
        day_of_week: int
    ) -> List[ScheduledAction]:
        """Friday movie night routine"""
        return [
            ScheduledAction(
                type=ActionType.DISPLAY_POWER,
                parameters={"device": "living_room_tv", "state": "on"}
            ),
            ScheduledAction(
                type=ActionType.DISPLAY_INPUT,
                parameters={"device": "living_room_tv", "input": "HDMI1"}
            ),
            ScheduledAction(
                type=ActionType.SOURCE_POWER,
                parameters={"device": "apple_tv", "state": "on"}
            ),
            ScheduledAction(
                type=ActionType.SOURCE_APP,
                parameters={"device": "apple_tv", "app": "Netflix"}
            ),
            ScheduledAction(
                type=ActionType.SCENE,
                parameters={"scene": "movie_mode"}  # Lights, etc.
            )
        ]
    
    @staticmethod
    def bedtime(
        user_id: str,
        time: time
    ) -> List[ScheduledAction]:
        """Bedtime routine - turn everything off"""
        return [
            ScheduledAction(
                type=ActionType.NOTIFICATION,
                parameters={
                    "message": "Time for bed. Turning off devices in 5 minutes.",
                    "channels": ["push", "on_screen"]
                }
            ),
            # Wait 5 minutes
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
            ),
            ScheduledAction(
                type=ActionType.SOURCE_POWER,
                parameters={"device": "all", "state": "off"}
            )
        ]


# Configuration example
ALARM_CONFIG = """
# Alarm configuration examples

alarms:
  # Morning alarm
  morning_wakeup:
    user_id: "user_123"
    name: "Morning Wake-Up"
    schedule_type: daily
    time: "07:00"
    actions:
      - type: media_service
        parameters:
          service: spotify
          action: play_playlist
          playlist: "Morning Vibes"
          device: bedroom_speakers
          volume: 30
      - type: notification
        parameters:
          message: "Good morning!"
  
  # Weekly movie night
  friday_movies:
    user_id: "user_123"
    name: "Friday Movie Night"
    schedule_type: weekly
    time: "20:00"
    days_of_week: [4]  # Friday
    actions:
      - type: preset
        parameters:
          preset: "movie_night"
  
  # Interval-based check
  check_updates:
    user_id: "system"
    name: "Check System Updates"
    schedule_type: interval
    interval_minutes: 360  # Every 6 hours
    actions:
      - type: custom
        parameters:
          function: "check_system_updates"

# Usage in API
POST /api/v1/alarms
{
  "user_id": "user_123",
  "name": "Morning Routine",
  "schedule_type": "daily",
  "time": "07:00",
  "actions": [
    {
      "type": "media_service",
      "parameters": {
        "service": "spotify",
        "action": "play",
        "playlist_uri": "spotify:playlist:37i9dQZF1DX0H9VYs5EqYz"
      }
    }
  ]
}
"""
