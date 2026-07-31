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
class Location:
    """
    Location = Tenant/Customer/Organization
    Top-level entity that subscribes to the service
    Each location gets its own URL: app.mediacontrol.com/location/{location_id}
    """
    id: str
    name: str
    created_at: datetime
    address: Optional[str] = None
    settings: Dict = None
    subscription_id: Optional[str] = None
    url_slug: Optional[str] = None  # For friendly URLs: /location/my-hotel


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
class User:
    """User account"""
    id: str
    email: str
    name: str
    tenant_id: str
    role: UserRole
    created_at: datetime
    password_hash: Optional[str] = None
    api_key: Optional[str] = None
    last_login: Optional[datetime] = None
    enabled: bool = True
    
    # Location access restrictions
    allowed_locations: Optional[List[str]] = None  # None = all locations
    
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
            return True  # Full access
        if self.allowed_locations is None:
            return True  # No restrictions
        return location_id in self.allowed_locations


class TenantManager:
    """
    Manages tenants (organizations) and their isolation
    """
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.users: Dict[str, User] = {}
        self.locations: Dict[str, Location] = {}
        logger.info("TenantManager initialized")
    
    def create_tenant(self, name: str) -> Tenant:
        """Create a new tenant"""
        tenant_id = self._generate_id("tenant")
        tenant = Tenant(
            id=tenant_id,
            name=name,
            created_at=datetime.now(),
            settings={},
        )
        self.tenants[tenant_id] = tenant
        logger.info(f"Created tenant: {name} ({tenant_id})")
        return tenant
    
    def create_location(
        self,
        tenant_id: str,
        name: str,
        address: Optional[str] = None,
        parent_location_id: Optional[str] = None,
    ) -> Optional[Location]:
        """Create a new location"""
        if tenant_id not in self.tenants:
            logger.error(f"Tenant not found: {tenant_id}")
            return None
        
        location_id = self._generate_id("location")
        location = Location(
            id=location_id,
            tenant_id=tenant_id,
            name=name,
            address=address,
            parent_location_id=parent_location_id,
        )
        self.locations[location_id] = location
        logger.info(f"Created location: {name} ({location_id}) for tenant {tenant_id}")
        return location
    
    def create_user(
        self,
        tenant_id: str,
        email: str,
        name: str,
        role: UserRole = UserRole.USER,
        password: Optional[str] = None,
    ) -> Optional[User]:
        """Create a new user"""
        if tenant_id not in self.tenants:
            logger.error(f"Tenant not found: {tenant_id}")
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
            tenant_id=tenant_id,
            role=role,
            created_at=datetime.now(),
            password_hash=self._hash_password(password) if password else None,
            api_key=self._generate_api_key(),
        )
        self.users[user_id] = user
        logger.info(f"Created user: {email} ({user_id}) for tenant {tenant_id}")
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
    
    def get_tenant_users(self, tenant_id: str) -> List[User]:
        """Get all users in a tenant"""
        return [u for u in self.users.values() if u.tenant_id == tenant_id]
    
    def get_tenant_locations(self, tenant_id: str) -> List[Location]:
        """Get all locations in a tenant"""
        return [l for l in self.locations.values() if l.tenant_id == tenant_id]
    
    def restrict_user_to_locations(self, user_id: str, location_ids: List[str]):
        """Restrict user to specific locations"""
        user = self.users.get(user_id)
        if user:
            user.allowed_locations = location_ids
            logger.info(f"Restricted user {user.email} to {len(location_ids)} locations")
    
    def check_access(
        self,
        user_id: str,
        permission: Permission,
        location_id: Optional[str] = None,
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
