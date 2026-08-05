"""
Multi-Tenancy and User Management
Organization/tenant isolation with role-based access control
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from datetime import datetime
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles"""
    SUPER_ADMIN = "super_admin"  # Platform administrator
    TENANT_ADMIN = "tenant_admin"  # Organization admin
    LOCATION_ADMIN = "location_admin"  # Building/site manager
    USER = "user"  # Standard user
    GUEST = "guest"  # Limited access guest


class Permission(Enum):
    """Fine-grained permissions"""
    # Device control
    CONTROL_DEVICE = "control_device"
    VIEW_DEVICE = "view_device"
    ADD_DEVICE = "add_device"
    EDIT_DEVICE = "edit_device"
    DELETE_DEVICE = "delete_device"
    
    # User management
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    INVITE_USERS = "invite_users"
    
    # Location management
    MANAGE_LOCATIONS = "manage_locations"
    VIEW_LOCATIONS = "view_locations"
    
    # Billing & subscription
    VIEW_BILLING = "view_billing"
    MANAGE_SUBSCRIPTION = "manage_subscription"
    
    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_ANALYTICS = "export_analytics"
    
    # Configuration
    EDIT_SETTINGS = "edit_settings"
    VIEW_SETTINGS = "view_settings"
    
    # KNX integration
    MANAGE_KNX = "manage_knx"


# Role-permission mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.SUPER_ADMIN: set(Permission),  # All permissions
    
    UserRole.TENANT_ADMIN: {
        Permission.CONTROL_DEVICE,
        Permission.VIEW_DEVICE,
        Permission.ADD_DEVICE,
        Permission.EDIT_DEVICE,
        Permission.DELETE_DEVICE,
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS,
        Permission.INVITE_USERS,
        Permission.MANAGE_LOCATIONS,
        Permission.VIEW_LOCATIONS,
        Permission.VIEW_BILLING,
        Permission.MANAGE_SUBSCRIPTION,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.EDIT_SETTINGS,
        Permission.VIEW_SETTINGS,
        Permission.MANAGE_KNX,
    },
    
    UserRole.LOCATION_ADMIN: {
        Permission.CONTROL_DEVICE,
        Permission.VIEW_DEVICE,
        Permission.ADD_DEVICE,
        Permission.EDIT_DEVICE,
        Permission.INVITE_USERS,
        Permission.VIEW_USERS,
        Permission.VIEW_LOCATIONS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_SETTINGS,
    },
    
    UserRole.USER: {
        Permission.CONTROL_DEVICE,
        Permission.VIEW_DEVICE,
        Permission.VIEW_LOCATIONS,
    },
    
    UserRole.GUEST: {
        Permission.CONTROL_DEVICE,  # Limited to assigned devices
        Permission.VIEW_DEVICE,
    },
}


@dataclass
class Organization:
    """
    Organization = Top-level customer entity (company, hotel chain, institution)
    One organization can have multiple locations (buildings, sites)
    Each organization gets its own URL: app.mediacontrol.com/org/{org_slug}
    """
    id: str
    name: str
    created_at: datetime
    organization_type: Optional[str] = None  # hotel_chain, corporate, retail, residential, integrator
    settings: Dict = None
    subscription_id: Optional[str] = None
    url_slug: Optional[str] = None  # For friendly URLs: /org/hilton-hotels
    parent_org_id: Optional[str] = None  # For integrator sub-organizations


@dataclass
class Location:
    """
    Location = Physical site/building within an organization
    Examples: "Hilton Dubai Marina", "Corporate HQ Building A", "John's Home"
    Each location gets its own URL: app.mediacontrol.com/org/{org_slug}/location/{location_slug}
    """
    id: str
    organization_id: str
    name: str
    created_at: datetime
    address: Optional[str] = None
    settings: Dict = None
    url_slug: Optional[str] = None  # For friendly URLs: /location/dubai-marina


@dataclass
class Room:
    """
    Room = Zone within a location
    Contains devices (displays, STBs, etc.)
    Each room gets its own URL: app.mediacontrol.com/location/{location_id}/room/{room_id}
    """
    id: str
    location_id: str
    name: str
    description: Optional[str] = None
    floor: Optional[str] = None
    url_slug: Optional[str] = None  # For friendly URLs: /room/conference-a


@dataclass
class Device:
    """
    Device within a room
    Can be: display, STB, Apple TV, Android TV, matrix, encoder, etc.
    """
    id: str
    room_id: str
    location_id: str
    type: str  # display, stb, apple_tv, android_tv, matrix, encoder
    name: str
    model: Optional[str] = None
    connection_details: Dict = None


@dataclass
class User:
    """User account"""
    id: str
    email: str
    name: str
    organization_id: str  # User belongs to an organization
    role: UserRole
    created_at: datetime
    password_hash: Optional[str] = None
    api_key: Optional[str] = None
    last_login: Optional[datetime] = None
    enabled: bool = True
    
    # Location/room access restrictions
    allowed_locations: Optional[List[str]] = None  # None = all locations in org (for org admins)
    allowed_rooms: Optional[List[str]] = None  # None = all rooms in allowed locations
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a permission"""
        if not self.enabled:
            return False
        return permission in ROLE_PERMISSIONS.get(self.role, set())
    
    def can_access_location(self, location_id: str) -> bool:
        """Check if user can access a location"""
        if not self.enabled:
            return False
        if self.role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]:
            return True  # Full access within organization
        if self.allowed_locations is None:
            return True  # No restrictions
        return location_id in self.allowed_locations
    
    def can_access_room(self, room_id: str) -> bool:
        """Check if user can access a room"""
        if not self.enabled:
            return False
        if self.role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]:
            return True  # Full access within organization
        if self.allowed_rooms is None:
            return True  # No restrictions
        return room_id in self.allowed_rooms


class OrganizationManager:
    """
    Manages organizations, locations, rooms, and devices
    
    Hierarchy:
    Organization (Company/Hotel Chain) → Locations (Buildings/Sites) → Rooms (Zones) → Devices
    
    Examples:
    - Hilton Hotels International → Hilton Dubai Marina → Suite 301 → TV, STB, Apple TV
    - Acme Corporation → HQ Building → Boardroom → Display, Matrix, Encoders
    - John Smith (residential) → Home → Living Room → TV, Apple TV
    """
    
    def __init__(self, subscription_manager=None):
        self.organizations: Dict[str, Organization] = {}
        self.locations: Dict[str, Location] = {}
        self.rooms: Dict[str, Room] = {}
        self.devices: Dict[str, Device] = {}
        self.users: Dict[str, User] = {}
        self.subscription_manager = subscription_manager  # Inject subscription manager
        logger.info("OrganizationManager initialized")
    
    def create_organization(
        self,
        name: str,
        organization_type: str = "corporate",
        url_slug: Optional[str] = None,
        parent_org_id: Optional[str] = None,
    ) -> Organization:
        """
        Create a new organization (top-level customer entity)
        This is the entity that subscribes to the service
        """
        org_id = self._generate_id("org")
        
        # Generate URL slug if not provided
        if not url_slug:
            url_slug = name.lower().replace(' ', '-').replace('_', '-')
            # Ensure uniqueness
            counter = 1
            base_slug = url_slug
            while any(org.url_slug == url_slug for org in self.organizations.values()):
                url_slug = f"{base_slug}-{counter}"
                counter += 1
        
        organization = Organization(
            id=org_id,
            name=name,
            created_at=datetime.now(),
            organization_type=organization_type,
            settings={},
            url_slug=url_slug,
            parent_org_id=parent_org_id,
        )
        self.organizations[org_id] = organization
        logger.info(f"Created organization: {name} ({org_id}) - URL: /org/{url_slug}")
        return organization
    
    def create_location(
        self,
        organization_id: str,
        name: str,
        address: Optional[str] = None,
        url_slug: Optional[str] = None,
    ) -> Optional[Location]:
        """
        Create a new location (physical site) within an organization
        Enforces subscription location limits
        """
        if organization_id not in self.organizations:
            logger.error(f"Organization not found: {organization_id}")
            return None
        
        # Check subscription limits
        if self.subscription_manager:
            if not self.subscription_manager.check_location_limit(organization_id):
                subscription = self.subscription_manager.get_subscription(organization_id)
                if subscription:
                    limits = subscription.get_limits()
                    logger.error(
                        f"Cannot create location: limit reached "
                        f"({subscription.location_count}/{limits.max_locations}). "
                        f"Current tier: {subscription.tier.value}. "
                        f"Please upgrade subscription to add more locations."
                    )
                else:
                    logger.error(f"No active subscription found for organization {organization_id}")
                return None
        
        location_id = self._generate_id("loc")
        
        # Generate URL slug if not provided
        if not url_slug:
            url_slug = name.lower().replace(' ', '-').replace('_', '-')
            # Ensure uniqueness within organization
            counter = 1
            base_slug = url_slug
            org_locations = [l for l in self.locations.values() if l.organization_id == organization_id]
            while any(l.url_slug == url_slug for l in org_locations):
                url_slug = f"{base_slug}-{counter}"
                counter += 1
        
        location = Location(
            id=location_id,
            organization_id=organization_id,
            name=name,
            created_at=datetime.now(),
            address=address,
            settings={},
            url_slug=url_slug,
        )
        self.locations[location_id] = location
        
        # Register with subscription
        if self.subscription_manager:
            self.subscription_manager.register_location(organization_id)
        
        logger.info(f"Created location: {name} ({location_id}) in organization {organization_id}")
        return location
    
    def create_room(
        self,
        location_id: str,
        name: str,
        description: Optional[str] = None,
        floor: Optional[str] = None,
        url_slug: Optional[str] = None,
    ) -> Optional[Room]:
        """
        Create a new room (zone) within a location
        Enforces subscription room limits
        """
        if location_id not in self.locations:
            logger.error(f"Location not found: {location_id}")
            return None
        
        location = self.locations[location_id]
        organization_id = location.organization_id
        
        # Check subscription limits
        if self.subscription_manager:
            if not self.subscription_manager.check_room_limit(organization_id):
                subscription = self.subscription_manager.get_subscription(organization_id)
                if subscription:
                    limits = subscription.get_limits()
                    logger.error(
                        f"Cannot create room: limit reached "
                        f"({subscription.room_count}/{limits.max_rooms}). "
                        f"Current tier: {subscription.tier.value}. "
                        f"Please upgrade subscription to add more rooms."
                    )
                else:
                    logger.error(f"No active subscription found for organization {organization_id}")
                return None
        
        room_id = self._generate_id("room")
        
        # Generate URL slug if not provided
        if not url_slug:
            url_slug = name.lower().replace(' ', '-').replace('_', '-')
            # Ensure uniqueness within location
            counter = 1
            base_slug = url_slug
            location_rooms = [r for r in self.rooms.values() if r.location_id == location_id]
            while any(r.url_slug == url_slug for r in location_rooms):
                url_slug = f"{base_slug}-{counter}"
                counter += 1
        
        room = Room(
            id=room_id,
            location_id=location_id,
            name=name,
            description=description,
            floor=floor,
            url_slug=url_slug,
        )
        self.rooms[room_id] = room
        
        # Register with subscription
        if self.subscription_manager:
            self.subscription_manager.register_room(organization_id)
        
        logger.info(f"Created room: {name} ({room_id}) in location {location_id}")
        return room
    
    def create_device(
        self,
        room_id: str,
        device_type: str,
        name: str,
        model: Optional[str] = None,
        connection_details: Optional[Dict] = None,
    ) -> Optional[Device]:
        """
        Create a new device within a room
        Enforces subscription device limits
        """
        room = self.rooms.get(room_id)
        if not room:
            logger.error(f"Room not found: {room_id}")
            return None
        
        location = self.locations.get(room.location_id)
        if not location:
            logger.error(f"Location not found: {room.location_id}")
            return None
        
        organization_id = location.organization_id
        
        # Check subscription limits
        if self.subscription_manager:
            if not self.subscription_manager.check_device_limit(organization_id):
                subscription = self.subscription_manager.get_subscription(organization_id)
                if subscription:
                    limits = subscription.get_limits()
                    logger.error(
                        f"Cannot create device: limit reached "
                        f"({subscription.device_count}/{limits.max_devices}). "
                        f"Current tier: {subscription.tier.value}. "
                        f"Please upgrade subscription to add more devices."
                    )
                else:
                    logger.error(f"No active subscription found for organization {organization_id}")
                return None
        
        device_id = self._generate_id("dev")
        device = Device(
            id=device_id,
            room_id=room_id,
            location_id=room.location_id,
            type=device_type,
            name=name,
            model=model,
            connection_details=connection_details or {},
        )
        self.devices[device_id] = device
        
        # Register with subscription
        if self.subscription_manager:
            self.subscription_manager.register_device(organization_id)
        
        logger.info(f"Created device: {name} ({device_id}) in room {room_id}")
        return device
    
    def create_user(
        self,
        organization_id: str,
        email: str,
        name: str,
        role: UserRole = UserRole.USER,
        password: Optional[str] = None,
    ) -> Optional[User]:
        """Create a new user for an organization"""
        if organization_id not in self.organizations:
            logger.error(f"Organization not found: {organization_id}")
            return None
        
        # Check if email already exists
        if any(u.email == email for u in self.users.values()):
            logger.error(f"Email already exists: {email}")
            return None
        
        user_id = self._generate_id("user")
        user = User(
            id=user_id,
            email=email,
            name=name,
            organization_id=organization_id,
            role=role,
            created_at=datetime.now(),
            password_hash=self._hash_password(password) if password else None,
            api_key=self._generate_api_key(),
        )
        self.users[user_id] = user
        logger.info(f"Created user: {email} ({user_id}) for organization {organization_id}")
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email/password"""
        user = next((u for u in self.users.values() if u.email == email), None)
        if not user:
            return None
        
        if not user.enabled:
            logger.warning(f"User account disabled: {email}")
            return None
        
        if not user.password_hash:
            logger.warning(f"User has no password set: {email}")
            return None
        
        if self._hash_password(password) == user.password_hash:
            user.last_login = datetime.now()
            logger.info(f"User authenticated: {email}")
            return user
        
        logger.warning(f"Invalid password for user: {email}")
        return None
    
    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate user by API key"""
        user = next((u for u in self.users.values() if u.api_key == api_key), None)
        if not user:
            return None
        
        if not user.enabled:
            logger.warning(f"User account disabled: {user.email}")
            return None
        
        logger.info(f"User authenticated via API key: {user.email}")
        return user
    
    def get_organization_users(self, organization_id: str) -> List[User]:
        """Get all users in an organization"""
        return [u for u in self.users.values() if u.organization_id == organization_id]
    
    def get_organization_locations(self, organization_id: str) -> List[Location]:
        """Get all locations in an organization"""
        return [l for l in self.locations.values() if l.organization_id == organization_id]
    
    def get_location_rooms(self, location_id: str) -> List[Room]:
        """Get all rooms in a location"""
        return [r for r in self.rooms.values() if r.location_id == location_id]
    
    def get_organization_rooms(self, organization_id: str) -> List[Room]:
        """Get all rooms across all locations in an organization"""
        location_ids = [l.id for l in self.get_organization_locations(organization_id)]
        return [r for r in self.rooms.values() if r.location_id in location_ids]
    
    def get_room_devices(self, room_id: str) -> List[Device]:
        """Get all devices in a room"""
        return [d for d in self.devices.values() if d.room_id == room_id]
    
    def get_location_devices(self, location_id: str) -> List[Device]:
        """Get all devices in a location (across all rooms)"""
        return [d for d in self.devices.values() if d.location_id == location_id]
    
    def get_organization_devices(self, organization_id: str) -> List[Device]:
        """Get all devices across all locations in an organization"""
        location_ids = [l.id for l in self.get_organization_locations(organization_id)]
        return [d for d in self.devices.values() if d.location_id in location_ids]
    
    def get_user_alarms(self, user_id: str) -> List[User]:
        """Get all users for an organization (keeping method for compatibility)"""
        # This method name seems wrong but keeping for backwards compatibility
        return []
    
    def delete_location(self, location_id: str) -> bool:
        """Delete a location and unregister from subscription"""
        location = self.locations.get(location_id)
        if not location:
            logger.error(f"Location not found: {location_id}")
            return False
        
        organization_id = location.organization_id
        
        # Delete all rooms in this location first
        location_rooms = [r for r in self.rooms.values() if r.location_id == location_id]
        for room in location_rooms:
            self.delete_room(room.id)
        
        # Delete the location
        del self.locations[location_id]
        
        # Unregister from subscription
        if self.subscription_manager:
            self.subscription_manager.unregister_location(organization_id)
        
        logger.info(f"Deleted location: {location_id}")
        return True
    
    def delete_room(self, room_id: str) -> bool:
        """Delete a room and unregister from subscription"""
        room = self.rooms.get(room_id)
        if not room:
            logger.error(f"Room not found: {room_id}")
            return False
        
        location = self.locations.get(room.location_id)
        if not location:
            logger.error(f"Location not found for room: {room_id}")
            return False
        
        organization_id = location.organization_id
        
        # Delete all devices in this room first
        room_devices = [d for d in self.devices.values() if d.room_id == room_id]
        for device in room_devices:
            self.delete_device(device.id)
        
        # Delete the room
        del self.rooms[room_id]
        
        # Unregister from subscription
        if self.subscription_manager:
            self.subscription_manager.unregister_room(organization_id)
        
        logger.info(f"Deleted room: {room_id}")
        return True
    
    def delete_device(self, device_id: str) -> bool:
        """Delete a device and unregister from subscription"""
        device = self.devices.get(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            return False
        
        location = self.locations.get(device.location_id)
        if not location:
            logger.error(f"Location not found for device: {device_id}")
            return False
        
        organization_id = location.organization_id
        
        # Delete the device
        del self.devices[device_id]
        
        # Unregister from subscription
        if self.subscription_manager:
            self.subscription_manager.unregister_device(organization_id)
        
        logger.info(f"Deleted device: {device_id}")
        return True
    
    def get_organization_usage(self, organization_id: str) -> Dict:
        """Get current usage vs limits for an organization"""
        if not self.subscription_manager:
            return {"error": "Subscription manager not configured"}
        
        subscription = self.subscription_manager.get_subscription(organization_id)
        if not subscription:
            return {"error": "No subscription found"}
        
        limits = subscription.get_limits()
        
        return {
            "organization_id": organization_id,
            "tier": subscription.tier.value,
            "status": subscription.status.value,
            "locations": {
                "current": subscription.location_count,
                "limit": limits.max_locations,
                "remaining": limits.max_locations - subscription.location_count,
                "percentage": round((subscription.location_count / limits.max_locations) * 100, 1) if limits.max_locations > 0 else 0
            },
            "rooms": {
                "current": subscription.room_count,
                "limit": limits.max_rooms,
                "remaining": limits.max_rooms - subscription.room_count,
                "percentage": round((subscription.room_count / limits.max_rooms) * 100, 1) if limits.max_rooms > 0 else 0
            },
            "devices": {
                "current": subscription.device_count,
                "limit": limits.max_devices,
                "remaining": limits.max_devices - subscription.device_count,
                "percentage": round((subscription.device_count / limits.max_devices) * 100, 1) if limits.max_devices > 0 else 0
            },
            "can_add_location": subscription.location_count < limits.max_locations,
            "can_add_room": subscription.room_count < limits.max_rooms,
            "can_add_device": subscription.device_count < limits.max_devices,
            "upgrade_recommended": (
                subscription.location_count >= limits.max_locations * 0.8 or
                subscription.room_count >= limits.max_rooms * 0.8 or
                subscription.device_count >= limits.max_devices * 0.8
            )
        }
        """Restrict user to specific locations"""
        user = self.users.get(user_id)
        if user:
            user.allowed_locations = location_ids
            logger.info(f"Restricted user {user.email} to {len(location_ids)} locations")
    
    def restrict_user_to_rooms(self, user_id: str, room_ids: List[str]):
        """Restrict user to specific rooms"""
        user = self.users.get(user_id)
        if user:
            user.allowed_rooms = room_ids
            logger.info(f"Restricted user {user.email} to {len(room_ids)} rooms")
    
    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by URL slug"""
        for org in self.organizations.values():
            if org.url_slug == slug:
                return org
        return None
    
    def get_location_by_slug(self, organization_id: str, slug: str) -> Optional[Location]:
        """Get location by URL slug within an organization"""
        for location in self.locations.values():
            if location.organization_id == organization_id and location.url_slug == slug:
                return location
        return None
    
    def get_room_by_slug(self, location_id: str, slug: str) -> Optional[Room]:
        """Get room by URL slug within a location"""
        for room in self.rooms.values():
            if room.location_id == location_id and room.url_slug == slug:
                return room
        return None
    
    def check_access(
        self,
        user_id: str,
        permission: Permission,
        location_id: Optional[str] = None,
        room_id: Optional[str] = None,
    ) -> bool:
        """Check if user has permission for an action"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        # Check permission
        if not user.has_permission(permission):
            return False
        
        # Check location access
        if location_id and not user.can_access_location(location_id):
            return False
        
        # Check room access
        if room_id and not user.can_access_room(room_id):
            return False
        
        return True
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        return f"{prefix}_{secrets.token_urlsafe(16)}"
    
    def _generate_api_key(self) -> str:
        """Generate API key"""
        return f"mcp_{secrets.token_urlsafe(32)}"
    
    def _hash_password(self, password: str) -> str:
        """Hash password (simple SHA-256, use bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()


# API middleware example
API_MIDDLEWARE_EXAMPLE = """
# auth_middleware.py
from functools import wraps
from flask import request, jsonify
from tenant_manager import TenantManager, Permission

tenant_manager = TenantManager()

def require_auth(permission: Permission = None):
    '''
    Decorator to require authentication and optionally check permission
    '''
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get auth token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing authorization'}), 401
            
            api_key = auth_header.split('Bearer ')[1]
            
            # Authenticate
            user = tenant_manager.authenticate_api_key(api_key)
            if not user:
                return jsonify({'error': 'Invalid API key'}), 401
            
            # Check permission if specified
            if permission:
                location_id = request.view_args.get('location_id')
                if not tenant_manager.check_access(user.id, permission, location_id):
                    return jsonify({'error': 'Permission denied'}), 403
            
            # Inject user into request context
            request.current_user = user
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# Usage example
@app.route('/api/locations/<location_id>/devices', methods=['GET'])
@require_auth(Permission.VIEW_DEVICE)
def list_devices(location_id):
    '''List devices in a location'''
    user = request.current_user
    
    # User is authenticated and has VIEW_DEVICE permission
    # and has access to this location
    
    devices = get_devices(location_id, user.tenant_id)
    return jsonify(devices)


@app.route('/api/locations/<location_id>/devices', methods=['POST'])
@require_auth(Permission.ADD_DEVICE)
def add_device(location_id):
    '''Add a device to a location'''
    user = request.current_user
    
    # Check subscription limits
    from subscription_manager import SubscriptionManager
    sub_manager = SubscriptionManager()
    
    if not sub_manager.check_device_limit(user.tenant_id):
        return jsonify({
            'error': 'Device limit reached. Please upgrade your subscription.'
        }), 403
    
    # Add device
    device = create_device(location_id, request.json)
    sub_manager.register_device(user.tenant_id)
    
    return jsonify(device), 201
"""
