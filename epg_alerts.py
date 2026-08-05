"""
EPG Alerts and Notifications System
Set reminders for TV shows, schedule recordings, and get notifications
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import logging
import asyncio
import json

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of alerts"""
    SHOW_REMINDER = "show_reminder"  # Notify before show starts
    SHOW_STARTED = "show_started"    # Show has started
    RECORDING_SCHEDULED = "recording_scheduled"  # Recording will start
    RECORDING_STARTED = "recording_started"
    RECORDING_COMPLETED = "recording_completed"
    RECORDING_FAILED = "recording_failed"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    PUSH = "push"              # Push notification to mobile app
    EMAIL = "email"            # Email notification
    SMS = "sms"                # SMS notification
    ON_SCREEN = "on_screen"    # Display on TV screen
    WEBHOOK = "webhook"        # HTTP webhook
    WEBSOCKET = "websocket"    # Real-time WebSocket notification


@dataclass
class EPGAlert:
    """EPG show alert/reminder"""
    id: str
    user_id: str
    channel_id: str
    channel_name: str
    show_title: str
    show_start: datetime
    show_end: datetime
    alert_time: datetime  # When to trigger alert
    alert_minutes_before: int  # Minutes before show start
    enabled: bool = True
    auto_record: bool = False  # Automatically start recording
    channels: List[NotificationChannel] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    triggered: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Notification:
    """A notification to be delivered"""
    id: str
    alert_id: Optional[str]
    user_id: str
    type: AlertType
    title: str
    message: str
    channels: List[NotificationChannel]
    timestamp: datetime = field(default_factory=datetime.now)
    delivered: bool = False
    delivery_attempts: int = 0
    metadata: Dict = field(default_factory=dict)


class EPGAlertManager:
    """
    Manages EPG alerts and notifications
    """
    
    def __init__(self, epg_client=None, recording_manager=None):
        self.epg_client = epg_client
        self.recording_manager = recording_manager
        
        self.alerts: Dict[str, EPGAlert] = {}
        self.notifications: List[Notification] = []
        self.notification_handlers: Dict[NotificationChannel, Callable] = {}
        
        self.running = False
        self._check_task: Optional[asyncio.Task] = None
        
        logger.info("EPGAlertManager initialized")
    
    def register_notification_handler(
        self,
        channel: NotificationChannel,
        handler: Callable
    ):
        """Register a notification delivery handler"""
        self.notification_handlers[channel] = handler
        logger.info(f"Registered notification handler for {channel.value}")
    
    def create_alert(
        self,
        user_id: str,
        channel_id: str,
        channel_name: str,
        show_title: str,
        show_start: datetime,
        show_end: datetime,
        alert_minutes_before: int = 15,
        auto_record: bool = False,
        channels: Optional[List[NotificationChannel]] = None
    ) -> EPGAlert:
        """Create a new EPG alert"""
        alert_id = f"alert_{user_id}_{show_start.timestamp()}_{channel_id}"
        
        alert_time = show_start - timedelta(minutes=alert_minutes_before)
        
        alert = EPGAlert(
            id=alert_id,
            user_id=user_id,
            channel_id=channel_id,
            channel_name=channel_name,
            show_title=show_title,
            show_start=show_start,
            show_end=show_end,
            alert_time=alert_time,
            alert_minutes_before=alert_minutes_before,
            auto_record=auto_record,
            channels=channels or [NotificationChannel.PUSH],
            metadata={
                "show_duration_minutes": int((show_end - show_start).total_seconds() / 60)
            }
        )
        
        self.alerts[alert_id] = alert
        logger.info(
            f"Created alert for '{show_title}' on {channel_name} "
            f"at {show_start.strftime('%Y-%m-%d %H:%M')}"
        )
        
        return alert
    
    def create_alert_from_epg(
        self,
        user_id: str,
        channel_id: str,
        show_id: str,
        alert_minutes_before: int = 15,
        auto_record: bool = False,
        channels: Optional[List[NotificationChannel]] = None
    ) -> Optional[EPGAlert]:
        """Create alert from EPG show data"""
        if not self.epg_client:
            logger.error("EPG client not configured")
            return None
        
        # Get show details from EPG
        show = self.epg_client.get_show(channel_id, show_id)
        if not show:
            logger.error(f"Show {show_id} not found in EPG")
            return None
        
        return self.create_alert(
            user_id=user_id,
            channel_id=channel_id,
            channel_name=show.get("channel_name", ""),
            show_title=show.get("title", ""),
            show_start=show.get("start"),
            show_end=show.get("end"),
            alert_minutes_before=alert_minutes_before,
            auto_record=auto_record,
            channels=channels
        )
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            logger.info(f"Deleted alert {alert_id}")
            return True
        return False
    
    def get_user_alerts(
        self,
        user_id: str,
        upcoming_only: bool = True
    ) -> List[EPGAlert]:
        """Get all alerts for a user"""
        user_alerts = [
            alert for alert in self.alerts.values()
            if alert.user_id == user_id
        ]
        
        if upcoming_only:
            now = datetime.now()
            user_alerts = [
                alert for alert in user_alerts
                if alert.show_start > now and alert.enabled
            ]
        
        # Sort by show start time
        user_alerts.sort(key=lambda a: a.show_start)
        return user_alerts
    
    async def start(self):
        """Start the alert checking loop"""
        if self.running:
            logger.warning("Alert manager already running")
            return
        
        self.running = True
        self._check_task = asyncio.create_task(self._check_alerts_loop())
        logger.info("EPG alert manager started")
    
    async def stop(self):
        """Stop the alert checking loop"""
        self.running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        logger.info("EPG alert manager stopped")
    
    async def _check_alerts_loop(self):
        """Main loop to check for triggered alerts"""
        while self.running:
            try:
                await self._check_alerts()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in alert check loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_alerts(self):
        """Check for alerts that should be triggered"""
        now = datetime.now()
        
        for alert in self.alerts.values():
            if not alert.enabled or alert.triggered:
                continue
            
            # Check if it's time to trigger this alert
            if now >= alert.alert_time:
                await self._trigger_alert(alert)
    
    async def _trigger_alert(self, alert: EPGAlert):
        """Trigger an alert and send notifications"""
        logger.info(f"Triggering alert for '{alert.show_title}' on {alert.channel_name}")
        
        # Mark as triggered
        alert.triggered = True
        
        # Create notification
        notification = Notification(
            id=f"notif_{alert.id}_{datetime.now().timestamp()}",
            alert_id=alert.id,
            user_id=alert.user_id,
            type=AlertType.SHOW_REMINDER,
            title=f"{alert.show_title} starts soon",
            message=(
                f"{alert.show_title} on {alert.channel_name} starts in "
                f"{alert.alert_minutes_before} minutes at "
                f"{alert.show_start.strftime('%H:%M')}"
            ),
            channels=alert.channels,
            metadata={
                "channel_id": alert.channel_id,
                "show_start": alert.show_start.isoformat(),
                "show_end": alert.show_end.isoformat()
            }
        )
        
        # Send notification
        await self._send_notification(notification)
        
        # Auto-record if enabled
        if alert.auto_record and self.recording_manager:
            await self._schedule_recording(alert)
    
    async def _send_notification(self, notification: Notification):
        """Send notification through all specified channels"""
        self.notifications.append(notification)
        
        for channel in notification.channels:
            handler = self.notification_handlers.get(channel)
            if not handler:
                logger.warning(f"No handler registered for {channel.value}")
                continue
            
            try:
                await handler(notification)
                logger.info(f"Sent notification via {channel.value}: {notification.title}")
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.value}: {e}")
        
        notification.delivered = True
    
    async def _schedule_recording(self, alert: EPGAlert):
        """Schedule automatic recording for a show"""
        if not self.recording_manager:
            logger.warning("Recording manager not available")
            return
        
        # Calculate when to start recording (1 minute before show)
        record_start = alert.show_start - timedelta(minutes=1)
        delay_seconds = (record_start - datetime.now()).total_seconds()
        
        if delay_seconds > 0:
            logger.info(
                f"Scheduling recording for '{alert.show_title}' "
                f"in {delay_seconds / 60:.1f} minutes"
            )
            
            # Wait until start time
            await asyncio.sleep(delay_seconds)
            
            # Start recording
            device_id = alert.metadata.get("recording_device_id")
            if device_id:
                self.recording_manager.start_recording(device_id)
                
                # Notify user
                notif = Notification(
                    id=f"notif_rec_{alert.id}_{datetime.now().timestamp()}",
                    alert_id=alert.id,
                    user_id=alert.user_id,
                    type=AlertType.RECORDING_STARTED,
                    title="Recording started",
                    message=f"Recording '{alert.show_title}' on {alert.channel_name}",
                    channels=alert.channels
                )
                await self._send_notification(notif)
                
                # Schedule auto-stop
                duration_seconds = (alert.show_end - alert.show_start).total_seconds()
                await asyncio.sleep(duration_seconds + 60)  # +1 min buffer
                
                self.recording_manager.stop_recording(device_id)
                
                # Notify completion
                notif_complete = Notification(
                    id=f"notif_rec_done_{alert.id}_{datetime.now().timestamp()}",
                    alert_id=alert.id,
                    user_id=alert.user_id,
                    type=AlertType.RECORDING_COMPLETED,
                    title="Recording completed",
                    message=f"Recorded '{alert.show_title}' on {alert.channel_name}",
                    channels=alert.channels
                )
                await self._send_notification(notif_complete)


# Notification handler examples
async def push_notification_handler(notification: Notification):
    """Send push notification via Firebase/APNs"""
    # Example using Firebase Cloud Messaging
    import aiohttp
    
    fcm_token = notification.metadata.get("fcm_token")
    if not fcm_token:
        logger.warning("No FCM token for user")
        return
    
    payload = {
        "to": fcm_token,
        "notification": {
            "title": notification.title,
            "body": notification.message
        },
        "data": notification.metadata
    }
    
    async with aiohttp.ClientSession() as session:
        await session.post(
            "https://fcm.googleapis.com/fcm/send",
            json=payload,
            headers={"Authorization": f"key={FCM_SERVER_KEY}"}
        )


async def email_notification_handler(notification: Notification):
    """Send email notification"""
    import aiosmtplib
    from email.message import EmailMessage
    
    msg = EmailMessage()
    msg["Subject"] = notification.title
    msg["From"] = "noreply@mediacontrol.com"
    msg["To"] = notification.metadata.get("user_email")
    msg.set_content(notification.message)
    
    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="your_email@gmail.com",
        password="your_password"
    )


async def websocket_notification_handler(notification: Notification):
    """Send real-time notification via WebSocket"""
    # Broadcast to connected WebSocket clients
    import json
    
    message = json.dumps({
        "type": "notification",
        "data": {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "timestamp": notification.timestamp.isoformat(),
            "metadata": notification.metadata
        }
    })
    
    # Send to all connected clients for this user
    # (Implementation depends on your WebSocket server)
    # await websocket_manager.broadcast_to_user(notification.user_id, message)


# Configuration example
EPG_ALERTS_CONFIG = """
# EPG alerts configuration

epg_alerts:
  # Default settings
  default_alert_minutes: 15  # Default minutes before show
  notification_channels:
    - push
    - on_screen
  
  # User preferences
  users:
    user_123:
      email: "user@example.com"
      fcm_token: "firebase_token_here"
      preferences:
        alert_minutes_before: 10
        auto_record_favorites: true
        channels:
          - push
          - email
      
      # Favorite shows (auto-create alerts)
      favorites:
        - show_title: "Game of Thrones"
          channel_id: "hbo"
          auto_record: true
        - show_title: "The Office"
          channel_id: "nbc"
          auto_record: false

# Usage example in API
POST /api/v1/epg/alerts
{
  "user_id": "user_123",
  "channel_id": "hbo",
  "show_id": "show_456",
  "alert_minutes_before": 15,
  "auto_record": true,
  "notification_channels": ["push", "email"]
}
"""
