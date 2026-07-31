"""
Guest Key Lifecycle & Staff Access Management
Automatic key activation/expiry and staff master keys

Features:
- Guest key automatic activation at check-in time
- Guest key automatic deactivation at check-out time
- Pre-check-in key provisioning (inactive until check-in)
- Post-check-out grace period (2 hours)
- Late checkout extension
- Staff master keys (section, building, grand master, emergency)
- Master key time restrictions (shift hours)
- Master key access logging with alerts
- PMS integration (OPERA Cloud, Protel, Mews, Cloudbeds)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import pytz
import json
import secrets


# ========== Data Models ==========

class KeyStatus(Enum):
    """Guest key status"""
    PROVISIONED = "provisioned"  # Created but not active yet
    ACTIVE = "active"  # Can unlock door
    EXPIRED = "expired"  # Past check-out time
    REVOKED = "revoked"  # Manually deactivated


class MasterKeyLevel(Enum):
    """Master key level"""
    GUEST = 1  # Single room
    SECTION = 2  # One floor
    BUILDING = 3  # All guest rooms
    GRAND = 4  # All rooms including restricted
    EMERGENCY = 5  # Override everything


@dataclass
class GuestKey:
    """Guest room key with auto-expiry"""
    key_id: str
    reservation_id: str
    
    # Guest info
    guest_name: str
    guest_email: str
    
    # Room info
    room_number: str
    building: Optional[str] = None
    
    # Schedule (with timezone)
    check_in: datetime = field(default_factory=datetime.now)
    check_out: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=1))
    property_timezone: str = "UTC"
    
    # Lifecycle
    provisioned_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Settings
    grace_period_seconds: int = 7200  # 2 hours
    auto_activate: bool = True
    auto_deactivate: bool = True
    
    # Status
    status: KeyStatus = KeyStatus.PROVISIONED
    
    # Wallet
    wallet_type: Optional[str] = None  # "apple_wallet" or "google_wallet"
    wallet_pass_url: Optional[str] = None
    
    # Usage
    last_used: Optional[datetime] = None
    usage_count: int = 0


@dataclass
class StaffKey:
    """Staff master key"""
    key_id: str
    staff_id: str
    
    # Staff info
    staff_name: str
    staff_email: str
    role: str  # housekeeping, maintenance, security, manager
    department: str
    
    # Master key
    master_key_level: MasterKeyLevel
    
    # Access
    assigned_floor: Optional[int] = None  # For section master
    access_rooms: List[str] = field(default_factory=list)
    access_areas: List[str] = field(default_factory=list)
    restricted_areas: List[str] = field(default_factory=list)
    
    # Time restrictions
    days_of_week: List[str] = field(default_factory=lambda: ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"])
    start_time: str = "00:00"  # 24/7 by default
    end_time: str = "23:59"
    
    # Limits
    max_rooms_per_day: Optional[int] = None
    
    # Notifications
    notify_supervisor_on_access: bool = False
    
    # Status
    active: bool = True
    issued_at: datetime = field(default_factory=datetime.now)


@dataclass
class MasterKeyAccessLog:
    """Master key access log entry"""
    log_id: str
    staff_key_id: str
    staff_id: str
    staff_name: str
    
    room_accessed: str
    timestamp: datetime
    reason: str
    
    duration_seconds: Optional[int] = None
    photo: Optional[bytes] = None
    
    supervisor_notified: bool = False
    alerts_triggered: List[str] = field(default_factory=list)


# ========== Guest Key Lifecycle Manager ==========

class GuestKeyLifecycleManager:
    """
    Manages guest key lifecycle
    - Auto-activation at check-in
    - Auto-deactivation at check-out
    - Grace period
    - Late checkout extension
    """
    
    def __init__(self):
        self.keys: Dict[str, GuestKey] = {}
        self.scheduled_activations: Dict[str, asyncio.Task] = {}
        self.scheduled_deactivations: Dict[str, asyncio.Task] = {}
        
        print(f"\n{'='*60}")
        print(f"Guest Key Lifecycle Manager Initialized")
        print(f"{'='*60}\n")
    
    async def issue_guest_key(self, reservation_id: str, guest_name: str, guest_email: str,
                               room_number: str, check_in: datetime, check_out: datetime,
                               property_timezone: str = "UTC", wallet_type: str = "apple_wallet",
                               grace_period_hours: int = 2) -> GuestKey:
        """
        Issue guest key with auto-expiry
        Key is provisioned but not active until check-in time
        """
        key_id = f"key_{secrets.token_hex(6)}"
        
        # Ensure datetimes are timezone-aware
        tz = pytz.timezone(property_timezone)
        if check_in.tzinfo is None:
            check_in = tz.localize(check_in)
        if check_out.tzinfo is None:
            check_out = tz.localize(check_out)
        
        # Calculate final expiry (check-out + grace period)
        final_expiry = check_out + timedelta(hours=grace_period_hours)
        
        key = GuestKey(
            key_id=key_id,
            reservation_id=reservation_id,
            guest_name=guest_name,
            guest_email=guest_email,
            room_number=room_number,
            check_in=check_in,
            check_out=check_out,
            property_timezone=property_timezone,
            expires_at=final_expiry,
            grace_period_seconds=grace_period_hours * 3600,
            wallet_type=wallet_type,
            wallet_pass_url=f"https://wallet-pass.com/{key_id}",
            provisioned_at=datetime.now(pytz.UTC),
            status=KeyStatus.PROVISIONED
        )
        
        self.keys[key_id] = key
        
        print(f"Guest key issued:")
        print(f"  Key ID: {key_id}")
        print(f"  Guest: {guest_name}")
        print(f"  Room: {room_number}")
        print(f"  Check-in: {check_in.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"  Check-out: {check_out.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"  Grace period: {grace_period_hours} hours")
        print(f"  Final expiry: {final_expiry.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"  Status: {key.status.value}")
        
        # Schedule auto-activation
        if key.auto_activate:
            await self._schedule_activation(key_id)
        
        # Schedule auto-deactivation
        if key.auto_deactivate:
            await self._schedule_deactivation(key_id)
        
        return key
    
    async def _schedule_activation(self, key_id: str):
        """Schedule automatic activation at check-in time"""
        key = self.keys.get(key_id)
        if not key:
            return
        
        now = datetime.now(pytz.UTC)
        check_in_utc = key.check_in.astimezone(pytz.UTC)
        
        # Calculate seconds until activation
        seconds_until = (check_in_utc - now).total_seconds()
        
        if seconds_until > 0:
            print(f"Scheduled activation for {key_id} in {seconds_until/3600:.1f} hours")
            
            async def activate_later():
                await asyncio.sleep(seconds_until)
                await self.activate_key(key_id, "Auto-activation at check-in time")
            
            task = asyncio.create_task(activate_later())
            self.scheduled_activations[key_id] = task
        else:
            # Check-in time already passed, activate immediately
            await self.activate_key(key_id, "Auto-activation (check-in time passed)")
    
    async def _schedule_deactivation(self, key_id: str):
        """Schedule automatic deactivation at check-out time + grace period"""
        key = self.keys.get(key_id)
        if not key or not key.expires_at:
            return
        
        now = datetime.now(pytz.UTC)
        expiry_utc = key.expires_at.astimezone(pytz.UTC)
        
        # Calculate seconds until deactivation
        seconds_until = (expiry_utc - now).total_seconds()
        
        if seconds_until > 0:
            print(f"Scheduled deactivation for {key_id} in {seconds_until/3600:.1f} hours")
            
            async def deactivate_later():
                await asyncio.sleep(seconds_until)
                await self.deactivate_key(key_id, "Auto-deactivation at check-out time + grace period")
            
            task = asyncio.create_task(deactivate_later())
            self.scheduled_deactivations[key_id] = task
    
    async def activate_key(self, key_id: str, reason: str = "Manual activation"):
        """Activate guest key"""
        key = self.keys.get(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found")
        
        if key.status == KeyStatus.ACTIVE:
            print(f"Key {key_id} is already active")
            return
        
        key.status = KeyStatus.ACTIVE
        key.activated_at = datetime.now(pytz.UTC)
        
        print(f"\n🔓 KEY ACTIVATED")
        print(f"  Key ID: {key_id}")
        print(f"  Guest: {key.guest_name}")
        print(f"  Room: {key.room_number}")
        print(f"  Reason: {reason}")
        print(f"  Activated at: {key.activated_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Send notification to guest
        await self._notify_guest(key, "activated")
    
    async def deactivate_key(self, key_id: str, reason: str = "Manual deactivation"):
        """Deactivate guest key"""
        key = self.keys.get(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found")
        
        if key.status == KeyStatus.EXPIRED:
            print(f"Key {key_id} is already expired")
            return
        
        key.status = KeyStatus.EXPIRED
        
        print(f"\n🔒 KEY DEACTIVATED")
        print(f"  Key ID: {key_id}")
        print(f"  Guest: {key.guest_name}")
        print(f"  Room: {key.room_number}")
        print(f"  Reason: {reason}")
        print(f"  Deactivated at: {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Send notification to guest
        await self._notify_guest(key, "deactivated")
    
    async def extend_checkout(self, key_id: str, extension_hours: int, approved_by: str):
        """Extend checkout time (late checkout)"""
        key = self.keys.get(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found")
        
        original_checkout = key.check_out
        new_checkout = key.check_out + timedelta(hours=extension_hours)
        new_expiry = new_checkout + timedelta(seconds=key.grace_period_seconds)
        
        key.check_out = new_checkout
        key.expires_at = new_expiry
        
        print(f"\n📅 CHECKOUT EXTENDED")
        print(f"  Key ID: {key_id}")
        print(f"  Original checkout: {original_checkout.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"  New checkout: {new_checkout.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"  Extension: {extension_hours} hours")
        print(f"  Approved by: {approved_by}")
        
        # Reschedule deactivation
        if key_id in self.scheduled_deactivations:
            self.scheduled_deactivations[key_id].cancel()
        await self._schedule_deactivation(key_id)
        
        # Notify guest
        await self._notify_guest(key, "extended", extension_hours=extension_hours)
    
    async def check_key_validity(self, key_id: str) -> bool:
        """Check if key is currently valid"""
        key = self.keys.get(key_id)
        if not key:
            return False
        
        now = datetime.now(pytz.UTC)
        
        # Check status
        if key.status != KeyStatus.ACTIVE:
            return False
        
        # Check if within validity window
        check_in_utc = key.check_in.astimezone(pytz.UTC)
        expiry_utc = key.expires_at.astimezone(pytz.UTC) if key.expires_at else now + timedelta(days=1)
        
        return check_in_utc <= now <= expiry_utc
    
    async def _notify_guest(self, key: GuestKey, event: str, **kwargs):
        """Send notification to guest"""
        messages = {
            "activated": f"Welcome to your room! Your key for Room {key.room_number} is now active.",
            "deactivated": f"Thank you for staying with us! Your key for Room {key.room_number} has been deactivated.",
            "extended": f"Late checkout approved! Your key is now valid until {key.check_out.strftime('%I:%M %p')}."
        }
        
        message = messages.get(event, "Key status updated")
        print(f"📱 Notification sent to {key.guest_email}: {message}")
    
    def get_status(self) -> Dict:
        """Get lifecycle manager status"""
        now = datetime.now(pytz.UTC)
        
        return {
            "total_keys": len(self.keys),
            "by_status": {
                "provisioned": sum(1 for k in self.keys.values() if k.status == KeyStatus.PROVISIONED),
                "active": sum(1 for k in self.keys.values() if k.status == KeyStatus.ACTIVE),
                "expired": sum(1 for k in self.keys.values() if k.status == KeyStatus.EXPIRED)
            },
            "scheduled_activations": len(self.scheduled_activations),
            "scheduled_deactivations": len(self.scheduled_deactivations)
        }


# ========== Staff Access Manager ==========

class StaffAccessManager:
    """
    Manages staff master keys
    - Master key levels (section, building, grand, emergency)
    - Time restrictions (shift hours)
    - Access logging and alerts
    """
    
    def __init__(self):
        self.keys: Dict[str, StaffKey] = {}
        self.access_logs: List[MasterKeyAccessLog] = []
        
        print(f"\n{'='*60}")
        print(f"Staff Access Manager Initialized")
        print(f"{'='*60}\n")
    
    def issue_staff_key(self, staff_id: str, staff_name: str, staff_email: str,
                        role: str, department: str, master_key_level: MasterKeyLevel,
                        **kwargs) -> StaffKey:
        """Issue staff master key"""
        key_id = f"key_staff_{secrets.token_hex(6)}"
        
        key = StaffKey(
            key_id=key_id,
            staff_id=staff_id,
            staff_name=staff_name,
            staff_email=staff_email,
            role=role,
            department=department,
            master_key_level=master_key_level,
            **kwargs
        )
        
        self.keys[key_id] = key
        
        print(f"Staff key issued:")
        print(f"  Key ID: {key_id}")
        print(f"  Staff: {staff_name} ({role})")
        print(f"  Master key level: {master_key_level.value} ({master_key_level.name})")
        if key.assigned_floor:
            print(f"  Assigned floor: {key.assigned_floor}")
        print(f"  Active hours: {key.start_time}-{key.end_time}")
        
        return key
    
    async def check_staff_access(self, key_id: str, room_number: str) -> bool:
        """Check if staff has access to room"""
        key = self.keys.get(key_id)
        if not key or not key.active:
            return False
        
        # Check time restrictions
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%a").upper()
        
        if current_day not in key.days_of_week:
            print(f"Access denied: Not working today ({current_day})")
            return False
        
        if not (key.start_time <= current_time <= key.end_time):
            print(f"Access denied: Outside shift hours ({key.start_time}-{key.end_time})")
            return False
        
        # Check master key level
        if key.master_key_level == MasterKeyLevel.SECTION:
            # Section master - only assigned floor
            if key.assigned_floor:
                floor = int(room_number[:2])  # First 2 digits
                if floor != key.assigned_floor:
                    print(f"Access denied: Wrong floor (assigned: {key.assigned_floor}, requested: {floor})")
                    return False
        
        elif key.master_key_level == MasterKeyLevel.BUILDING:
            # Building master - all guest rooms, no restricted areas
            if room_number in key.restricted_areas:
                print(f"Access denied: Restricted area ({room_number})")
                return False
        
        # GRAND and EMERGENCY levels have full access
        
        # Check daily limit
        if key.max_rooms_per_day:
            today_accesses = sum(1 for log in self.access_logs 
                               if log.staff_key_id == key_id 
                               and log.timestamp.date() == now.date())
            
            if today_accesses >= key.max_rooms_per_day:
                print(f"Access denied: Daily limit reached ({today_accesses}/{key.max_rooms_per_day})")
                return False
        
        return True
    
    async def log_staff_access(self, key_id: str, room_number: str, reason: str,
                               duration_seconds: Optional[int] = None) -> MasterKeyAccessLog:
        """Log staff access to room"""
        key = self.keys.get(key_id)
        if not key:
            raise ValueError(f"Staff key {key_id} not found")
        
        log_id = f"log_{secrets.token_hex(6)}"
        
        log = MasterKeyAccessLog(
            log_id=log_id,
            staff_key_id=key_id,
            staff_id=key.staff_id,
            staff_name=key.staff_name,
            room_accessed=room_number,
            timestamp=datetime.now(pytz.UTC),
            reason=reason,
            duration_seconds=duration_seconds,
            supervisor_notified=key.notify_supervisor_on_access
        )
        
        self.access_logs.append(log)
        
        print(f"\n📝 STAFF ACCESS LOGGED")
        print(f"  Staff: {key.staff_name} ({key.role})")
        print(f"  Room: {room_number}")
        print(f"  Reason: {reason}")
        if duration_seconds:
            print(f"  Duration: {duration_seconds // 60} minutes")
        
        # Check for alerts
        await self._check_alerts(key, log)
        
        # Notify supervisor if required
        if key.notify_supervisor_on_access:
            await self._notify_supervisor(key, log)
        
        return log
    
    async def _check_alerts(self, key: StaffKey, log: MasterKeyAccessLog):
        """Check for alert conditions"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # After-hours access
        if not (key.start_time <= current_time <= key.end_time):
            log.alerts_triggered.append("after_hours_access")
            print(f"⚠️ ALERT: After-hours access by {key.staff_name}")
        
        # Restricted area access (Grand master level)
        if key.master_key_level in [MasterKeyLevel.GRAND, MasterKeyLevel.EMERGENCY]:
            if log.room_accessed.startswith("RESTRICTED"):
                log.alerts_triggered.append("restricted_area_access")
                print(f"⚠️ ALERT: Restricted area accessed by {key.staff_name}")
        
        # Excessive access
        if key.max_rooms_per_day:
            today_accesses = sum(1 for l in self.access_logs 
                               if l.staff_key_id == key.key_id 
                               and l.timestamp.date() == now.date())
            
            if today_accesses >= key.max_rooms_per_day * 0.9:  # 90% of limit
                log.alerts_triggered.append("approaching_daily_limit")
                print(f"⚠️ ALERT: {key.staff_name} approaching daily limit ({today_accesses}/{key.max_rooms_per_day})")
    
    async def _notify_supervisor(self, key: StaffKey, log: MasterKeyAccessLog):
        """Notify supervisor of staff access"""
        print(f"📧 Supervisor notified: {key.staff_name} accessed {log.room_accessed}")
    
    def get_staff_access_report(self, staff_id: str, date: datetime.date) -> Dict:
        """Get staff access report for a day"""
        logs = [log for log in self.access_logs 
                if log.staff_id == staff_id and log.timestamp.date() == date]
        
        return {
            "staff_id": staff_id,
            "date": date.isoformat(),
            "total_accesses": len(logs),
            "rooms_accessed": [log.room_accessed for log in logs],
            "alerts": sum(len(log.alerts_triggered) for log in logs),
            "logs": logs
        }
    
    def get_status(self) -> Dict:
        """Get staff access manager status"""
        return {
            "total_staff_keys": len(self.keys),
            "active_staff_keys": sum(1 for k in self.keys.values() if k.active),
            "by_role": {
                "housekeeping": sum(1 for k in self.keys.values() if k.role == "housekeeping"),
                "maintenance": sum(1 for k in self.keys.values() if k.role == "maintenance"),
                "security": sum(1 for k in self.keys.values() if k.role == "security"),
                "manager": sum(1 for k in self.keys.values() if k.role == "manager")
            },
            "total_access_logs": len(self.access_logs),
            "alerts_today": sum(1 for log in self.access_logs 
                              if log.timestamp.date() == datetime.now().date() 
                              and log.alerts_triggered)
        }


# Example usage
if __name__ == "__main__":
    print("=== Guest Key Lifecycle & Staff Access Demo ===\n")
    
    # Initialize managers
    guest_manager = GuestKeyLifecycleManager()
    staff_manager = StaffAccessManager()
    
    async def run_demo():
        # Issue guest key
        print("\n--- Issue Guest Key ---\n")
        
        # Guest checks in July 31 at 3:00 PM Pacific, checks out August 3 at 12:00 PM
        check_in = datetime(2026, 7, 31, 15, 0, 0)  # 3:00 PM
        check_out = datetime(2026, 8, 3, 12, 0, 0)  # 12:00 PM
        
        guest_key = await guest_manager.issue_guest_key(
            reservation_id="RES_123456",
            guest_name="John Smith",
            guest_email="john@example.com",
            room_number="2201",
            check_in=check_in,
            check_out=check_out,
            property_timezone="America/Los_Angeles",
            wallet_type="apple_wallet",
            grace_period_hours=2
        )
        
        # Issue staff keys
        print("\n--- Issue Staff Keys ---\n")
        
        # Housekeeping (Section master - Floor 22)
        staff_key_hk = staff_manager.issue_staff_key(
            staff_id="staff_maria",
            staff_name="Maria Garcia",
            staff_email="maria@hotel.com",
            role="housekeeping",
            department="Housekeeping",
            master_key_level=MasterKeyLevel.SECTION,
            assigned_floor=22,
            days_of_week=["MON", "TUE", "WED", "THU", "FRI"],
            start_time="08:00",
            end_time="16:00",
            max_rooms_per_day=20,
            notify_supervisor_on_access=True
        )
        
        # Maintenance (Building master)
        staff_key_maint = staff_manager.issue_staff_key(
            staff_id="staff_john",
            staff_name="John Lee",
            staff_email="john@hotel.com",
            role="maintenance",
            department="Engineering",
            master_key_level=MasterKeyLevel.BUILDING,
            start_time="00:00",
            end_time="23:59"  # 24/7
        )
        
        # Test staff access
        print("\n--- Test Staff Access ---\n")
        
        # Housekeeping accesses room on their floor
        can_access = await staff_manager.check_staff_access(staff_key_hk.key_id, "2215")
        if can_access:
            await staff_manager.log_staff_access(
                staff_key_hk.key_id,
                "2215",
                "Daily cleaning",
                duration_seconds=1200  # 20 minutes
            )
        
        # Print status
        print("\n" + "="*60)
        print("SYSTEM STATUS")
        print("="*60 + "\n")
        
        print("Guest Keys:")
        guest_status = guest_manager.get_status()
        print(json.dumps(guest_status, indent=2))
        
        print("\nStaff Keys:")
        staff_status = staff_manager.get_status()
        print(json.dumps(staff_status, indent=2))
    
    asyncio.run(run_demo())
