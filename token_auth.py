"""
Token-Based Authentication for Room Access
Generate secure tokens for KNX device integration and embedded widgets

Features:
- Room-specific access tokens
- Token expiration and revocation
- Scoped permissions (read-only, control, admin)
- Token refresh mechanism
- Audit logging
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib
import hmac
import logging
import uuid

logger = logging.getLogger(__name__)


class TokenScope(Enum):
    """Token access scopes"""
    READ_ONLY = "read_only"      # View only, no control
    CONTROL = "control"           # Full device control
    ADMIN = "admin"               # Admin features (settings, user management)


class TokenStatus(Enum):
    """Token status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


@dataclass
class AccessToken:
    """Access token for room/device control"""
    token_id: str
    token: str  # The actual token string (hashed in storage)
    token_hash: str  # SHA-256 hash for secure storage
    
    # Scope
    organization_id: str
    location_id: Optional[str] = None
    room_id: Optional[str] = None  # If None, access to all rooms in location
    
    # Permissions
    scope: TokenScope = TokenScope.CONTROL
    
    # Token metadata
    name: str = "KNX Device Token"
    description: Optional[str] = None
    
    # Lifecycle
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    status: TokenStatus = TokenStatus.ACTIVE
    
    # Usage tracking
    usage_count: int = 0
    max_uses: Optional[int] = None  # None = unlimited
    
    # Security
    created_by: Optional[str] = None  # User ID who created the token
    ip_whitelist: List[str] = field(default_factory=list)  # Allowed IP addresses
    device_id: Optional[str] = None  # Specific device (KNX panel, etc.)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        if self.status != TokenStatus.ACTIVE:
            return False
        
        if self.expires_at and datetime.now() > self.expires_at:
            self.status = TokenStatus.EXPIRED
            return False
        
        if self.max_uses and self.usage_count >= self.max_uses:
            return False
        
        return True
    
    def has_access_to_room(self, room_id: str) -> bool:
        """Check if token has access to specific room"""
        if self.room_id is None:
            # Token has access to all rooms in location
            return True
        return self.room_id == room_id
    
    def can_control(self) -> bool:
        """Check if token has control permissions"""
        return self.scope in [TokenScope.CONTROL, TokenScope.ADMIN]
    
    def can_admin(self) -> bool:
        """Check if token has admin permissions"""
        return self.scope == TokenScope.ADMIN


class TokenManager:
    """
    Manages access tokens for room control URLs
    For KNX devices, embedded widgets, and API access
    """
    
    def __init__(self, secret_key: str):
        self.tokens: Dict[str, AccessToken] = {}  # token_id -> AccessToken
        self.token_lookup: Dict[str, str] = {}  # token_hash -> token_id
        self.secret_key = secret_key
        logger.info("TokenManager initialized")
    
    def generate_token(
        self,
        organization_id: str,
        room_id: Optional[str] = None,
        location_id: Optional[str] = None,
        name: str = "KNX Device Token",
        description: Optional[str] = None,
        scope: TokenScope = TokenScope.CONTROL,
        expires_in_days: Optional[int] = None,
        max_uses: Optional[int] = None,
        created_by: Optional[str] = None,
        ip_whitelist: Optional[List[str]] = None,
        device_id: Optional[str] = None
    ) -> AccessToken:
        """
        Generate a new access token
        
        Args:
            organization_id: Organization ID
            room_id: Room ID (None = all rooms in location)
            location_id: Location ID
            name: Token name
            description: Token description
            scope: Access scope (read_only, control, admin)
            expires_in_days: Token expiration (None = never expires)
            max_uses: Maximum number of uses (None = unlimited)
            created_by: User ID who created the token
            ip_whitelist: List of allowed IP addresses
            device_id: Specific device identifier
            
        Returns:
            AccessToken object
        """
        # Generate secure random token
        token = self._generate_secure_token()
        token_hash = self._hash_token(token)
        
        token_id = f"tok_{uuid.uuid4().hex[:16]}"
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        access_token = AccessToken(
            token_id=token_id,
            token=token,  # Return plaintext once, then discard
            token_hash=token_hash,
            organization_id=organization_id,
            location_id=location_id,
            room_id=room_id,
            name=name,
            description=description,
            scope=scope,
            expires_at=expires_at,
            max_uses=max_uses,
            created_by=created_by,
            ip_whitelist=ip_whitelist or [],
            device_id=device_id
        )
        
        self.tokens[token_id] = access_token
        self.token_lookup[token_hash] = token_id
        
        logger.info(
            f"Generated token {token_id} for organization {organization_id}, "
            f"room {room_id}, scope {scope.value}"
        )
        
        return access_token
    
    def validate_token(
        self,
        token: str,
        room_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Optional[AccessToken]:
        """
        Validate token and return AccessToken if valid
        
        Args:
            token: Token string
            room_id: Room being accessed (for room-specific tokens)
            ip_address: Client IP address (for IP whitelist check)
            
        Returns:
            AccessToken if valid, None otherwise
        """
        token_hash = self._hash_token(token)
        
        # Lookup token
        token_id = self.token_lookup.get(token_hash)
        if not token_id:
            logger.warning(f"Token not found: {token_hash[:16]}...")
            return None
        
        access_token = self.tokens.get(token_id)
        if not access_token:
            logger.warning(f"Token ID {token_id} not found in storage")
            return None
        
        # Check if valid
        if not access_token.is_valid():
            logger.warning(f"Token {token_id} is invalid (status: {access_token.status.value})")
            return None
        
        # Check room access
        if room_id and not access_token.has_access_to_room(room_id):
            logger.warning(f"Token {token_id} does not have access to room {room_id}")
            return None
        
        # Check IP whitelist
        if access_token.ip_whitelist and ip_address:
            if ip_address not in access_token.ip_whitelist:
                logger.warning(
                    f"Token {token_id} used from unauthorized IP: {ip_address}"
                )
                return None
        
        # Update usage
        access_token.usage_count += 1
        access_token.last_used_at = datetime.now()
        
        logger.info(f"Token {token_id} validated (usage: {access_token.usage_count})")
        
        return access_token
    
    def revoke_token(self, token_id: str) -> bool:
        """Revoke a token"""
        if token_id not in self.tokens:
            return False
        
        token = self.tokens[token_id]
        token.status = TokenStatus.REVOKED
        
        logger.info(f"Revoked token {token_id}")
        return True
    
    def suspend_token(self, token_id: str) -> bool:
        """Temporarily suspend a token"""
        if token_id not in self.tokens:
            return False
        
        token = self.tokens[token_id]
        token.status = TokenStatus.SUSPENDED
        
        logger.info(f"Suspended token {token_id}")
        return True
    
    def reactivate_token(self, token_id: str) -> bool:
        """Reactivate a suspended token"""
        if token_id not in self.tokens:
            return False
        
        token = self.tokens[token_id]
        if token.status == TokenStatus.SUSPENDED:
            token.status = TokenStatus.ACTIVE
            logger.info(f"Reactivated token {token_id}")
            return True
        
        return False
    
    def refresh_token(self, token_id: str, extend_days: int = 30) -> bool:
        """Extend token expiration"""
        if token_id not in self.tokens:
            return False
        
        token = self.tokens[token_id]
        
        if token.expires_at:
            token.expires_at = datetime.now() + timedelta(days=extend_days)
        else:
            token.expires_at = datetime.now() + timedelta(days=extend_days)
        
        logger.info(f"Refreshed token {token_id}, new expiration: {token.expires_at}")
        return True
    
    def list_tokens(
        self,
        organization_id: Optional[str] = None,
        room_id: Optional[str] = None,
        status: Optional[TokenStatus] = None
    ) -> List[AccessToken]:
        """List tokens with optional filters"""
        tokens = list(self.tokens.values())
        
        if organization_id:
            tokens = [t for t in tokens if t.organization_id == organization_id]
        
        if room_id:
            tokens = [t for t in tokens if t.room_id == room_id]
        
        if status:
            tokens = [t for t in tokens if t.status == status]
        
        return tokens
    
    def get_token_info(self, token_id: str) -> Optional[Dict[str, Any]]:
        """Get token information (without exposing actual token)"""
        if token_id not in self.tokens:
            return None
        
        token = self.tokens[token_id]
        
        return {
            "token_id": token.token_id,
            "name": token.name,
            "description": token.description,
            "organization_id": token.organization_id,
            "location_id": token.location_id,
            "room_id": token.room_id,
            "scope": token.scope.value,
            "status": token.status.value,
            "created_at": token.created_at.isoformat(),
            "expires_at": token.expires_at.isoformat() if token.expires_at else None,
            "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
            "usage_count": token.usage_count,
            "max_uses": token.max_uses,
            "created_by": token.created_by,
            "device_id": token.device_id,
            "is_valid": token.is_valid()
        }
    
    def generate_room_url(
        self,
        base_url: str,
        organization_slug: str,
        location_slug: str,
        room_slug: str,
        token: str
    ) -> str:
        """
        Generate authenticated URL for room access
        
        Args:
            base_url: Base URL (e.g., "https://app.mediacontrol.com")
            organization_slug: Organization slug
            location_slug: Location slug
            room_slug: Room slug
            token: Access token
            
        Returns:
            Authenticated URL
        """
        url = f"{base_url}/org/{organization_slug}/location/{location_slug}/room/{room_slug}?token={token}"
        return url
    
    def generate_widget_url(
        self,
        base_url: str,
        room_id: str,
        token: str,
        theme: str = "dark"
    ) -> str:
        """
        Generate authenticated URL for embedded widget
        
        Args:
            base_url: Base URL
            room_id: Room ID
            token: Access token
            theme: Theme (dark/light)
            
        Returns:
            Widget URL for iframe embedding
        """
        url = f"{base_url}/widget/room/{room_id}?token={token}&theme={theme}"
        return url
    
    def _generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def _hash_token(self, token: str) -> str:
        """Hash token for secure storage"""
        return hashlib.sha256(
            f"{self.secret_key}:{token}".encode('utf-8')
        ).hexdigest()
    
    def verify_token_signature(self, token: str, signature: str) -> bool:
        """Verify token signature (for additional security)"""
        expected_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            token.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


# Usage examples
TOKEN_USAGE_EXAMPLES = """
# Example 1: Generate token for KNX device

from token_auth import TokenManager, TokenScope

token_mgr = TokenManager(secret_key="your-secret-key-here")

# Generate token for living room
token = token_mgr.generate_token(
    organization_id="org123",
    location_id="loc456",
    room_id="room789",
    name="Living Room KNX Panel",
    description="KNX touch panel in living room",
    scope=TokenScope.CONTROL,
    expires_in_days=365,  # Valid for 1 year
    device_id="knx_panel_living_room"
)

# Get the URL
room_url = token_mgr.generate_room_url(
    base_url="https://app.mediacontrol.com",
    organization_slug="myhotel",
    location_slug="dubai-downtown",
    room_slug="presidential-suite",
    token=token.token
)

print(f"URL for KNX device: {room_url}")
# Output: https://app.mediacontrol.com/org/myhotel/location/dubai-downtown/room/presidential-suite?token=abc123xyz...


# Example 2: Generate token for embedded widget

widget_token = token_mgr.generate_token(
    organization_id="org123",
    room_id="room789",
    name="Lobby Widget",
    description="Embedded control widget for lobby display",
    scope=TokenScope.READ_ONLY,  # View only
    expires_in_days=None,  # Never expires
    ip_whitelist=["192.168.1.100"]  # Only from lobby display IP
)

widget_url = token_mgr.generate_widget_url(
    base_url="https://app.mediacontrol.com",
    room_id="room789",
    token=widget_token.token,
    theme="dark"
)

print(f"Widget URL: {widget_url}")
# Embed in KNX visualization:
# <iframe src="{widget_url}" width="1920" height="1080"></iframe>


# Example 3: Validate token in API endpoint

# In your Flask/FastAPI endpoint:
@app.get("/org/{org_slug}/location/{loc_slug}/room/{room_slug}")
def get_room(org_slug: str, loc_slug: str, room_slug: str, token: str, request: Request):
    '''Get room with token authentication'''
    
    # Validate token
    access_token = token_mgr.validate_token(
        token=token,
        room_id=room_slug,
        ip_address=request.client.host
    )
    
    if not access_token:
        return {"error": "Invalid or expired token"}, 401
    
    # Check permissions
    if not access_token.can_control():
        return {"error": "Insufficient permissions"}, 403
    
    # Return room data
    return {
        "room_id": room_slug,
        "devices": [...],
        "permissions": {
            "can_control": access_token.can_control(),
            "can_admin": access_token.can_admin()
        }
    }


# Example 4: Token management

# List all active tokens
active_tokens = token_mgr.list_tokens(
    organization_id="org123",
    status=TokenStatus.ACTIVE
)

# Revoke compromised token
token_mgr.revoke_token("tok_abc123")

# Refresh expiring token
token_mgr.refresh_token("tok_xyz789", extend_days=90)

# Get token usage info
info = token_mgr.get_token_info("tok_abc123")
print(f"Token used {info['usage_count']} times")
print(f"Last used: {info['last_used_at']}")
"""

# API endpoints
TOKEN_API_EXAMPLES = """
# Flask/FastAPI endpoints

@app.post("/api/v1/tokens")
def create_token(request: CreateTokenRequest):
    '''Generate new access token'''
    token_mgr = TokenManager(secret_key=SECRET_KEY)
    
    token = token_mgr.generate_token(
        organization_id=request.organization_id,
        room_id=request.room_id,
        location_id=request.location_id,
        name=request.name,
        description=request.description,
        scope=TokenScope(request.scope),
        expires_in_days=request.expires_in_days,
        created_by=current_user.id
    )
    
    # Return token ONCE (never show again)
    return {
        "token_id": token.token_id,
        "token": token.token,  # Show once
        "url": token_mgr.generate_room_url(
            base_url="https://app.mediacontrol.com",
            organization_slug=request.org_slug,
            location_slug=request.loc_slug,
            room_slug=request.room_slug,
            token=token.token
        ),
        "expires_at": token.expires_at.isoformat() if token.expires_at else None,
        "warning": "Save this token now. It will not be shown again."
    }

@app.get("/api/v1/tokens")
def list_tokens(organization_id: str):
    '''List all tokens for organization'''
    token_mgr = TokenManager(secret_key=SECRET_KEY)
    
    tokens = token_mgr.list_tokens(organization_id=organization_id)
    
    return {
        "tokens": [
            token_mgr.get_token_info(t.token_id)
            for t in tokens
        ]
    }

@app.delete("/api/v1/tokens/{token_id}")
def revoke_token(token_id: str):
    '''Revoke token'''
    token_mgr = TokenManager(secret_key=SECRET_KEY)
    success = token_mgr.revoke_token(token_id)
    
    return {"success": success}

@app.post("/api/v1/tokens/{token_id}/refresh")
def refresh_token(token_id: str, extend_days: int = 30):
    '''Refresh token expiration'''
    token_mgr = TokenManager(secret_key=SECRET_KEY)
    success = token_mgr.refresh_token(token_id, extend_days)
    
    return {"success": success}

@app.get("/api/v1/tokens/{token_id}")
def get_token_info(token_id: str):
    '''Get token info (without exposing token)'''
    token_mgr = TokenManager(secret_key=SECRET_KEY)
    info = token_mgr.get_token_info(token_id)
    
    if not info:
        return {"error": "Token not found"}, 404
    
    return info
"""

# KNX Integration Example
KNX_INTEGRATION_EXAMPLE = """
# KNX Visualization Configuration

## In KNX ETS or Visualization Software:

1. Generate token via MediaControl API or dashboard
2. Get authenticated URL
3. Configure web page element in KNX visualization:

URL: https://app.mediacontrol.com/org/myhotel/location/dubai/room/101?token=abc123xyz...
Width: 1920px
Height: 1080px
Refresh: Auto

## For EIBPort / KNX panels:

<WebPage>
  <URL>https://app.mediacontrol.com/widget/room/101?token=abc123xyz&theme=dark</URL>
  <Width>1920</Width>
  <Height>1080</Height>
  <Scroll>false</Scroll>
  <Border>false</Border>
</WebPage>

## For Gira HomeServer / X1:

Add Web View element
URL: https://app.mediacontrol.com/widget/room/101?token=abc123xyz
Enable fullscreen mode
Disable browser chrome

## Security Notes:

- Use READ_ONLY scope for public displays
- Use CONTROL scope only for trusted devices
- Set IP whitelist for fixed-IP KNX panels
- Set expiration for temporary deployments
- Rotate tokens annually for security
"""
