"""
Subscription and Licensing System
Device-based licensing with multi-tier support
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SubscriptionTier(Enum):
    """Subscription tiers"""
    FREE = "free"
    HOME = "home"
    HOME_PRO = "home_pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    INTEGRATOR = "integrator"


class SubscriptionStatus(Enum):
    """Subscription status"""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


@dataclass
class TierLimits:
    """Limits for each subscription tier"""
    max_devices: int
    max_rooms: int  # Rooms (zones) within the location
    max_users: int
    max_encoders: int
    features: List[str] = field(default_factory=list)


TIER_CONFIGS = {
    SubscriptionTier.FREE: TierLimits(
        max_devices=3,
        max_locations=1,
        max_users=1,
        max_encoders=0,
        features=["basic_control", "epg"],
    ),
    SubscriptionTier.HOME: TierLimits(
        max_devices=5,
        max_locations=1,
        max_users=1,
        max_encoders=0,
        features=[
            "basic_control",
            "epg",
            "apple_tv",
            "android_tv",
            "presets",
        ],
    ),
    SubscriptionTier.HOME_PRO: TierLimits(
        max_devices=15,
        max_locations=2,
        max_users=3,
        max_encoders=1,
        features=[
            "basic_control",
            "epg",
            "apple_tv",
            "android_tv",
            "presets",
            "hdmi_matrix",
            "video_streaming",
            "advanced_automation",
            "voice_control",
        ],
    ),
    SubscriptionTier.BUSINESS: TierLimits(
        max_devices=30,
        max_locations=5,
        max_users=10,
        max_encoders=3,
        features=[
            "basic_control",
            "epg",
            "apple_tv",
            "android_tv",
            "presets",
            "hdmi_matrix",
            "video_streaming",
            "advanced_automation",
            "voice_control",
            "analytics",
            "centralized_management",
            "role_based_access",
        ],
    ),
    SubscriptionTier.ENTERPRISE: TierLimits(
        max_devices=100,
        max_locations=999,
        max_users=999,
        max_encoders=10,
        features=[
            "basic_control",
            "epg",
            "apple_tv",
            "android_tv",
            "presets",
            "hdmi_matrix",
            "video_streaming",
            "advanced_automation",
            "voice_control",
            "analytics",
            "centralized_management",
            "role_based_access",
            "white_label",
            "knx_integration",
            "api_access",
            "sso",
            "sla",
        ],
    ),
    SubscriptionTier.INTEGRATOR: TierLimits(
        max_devices=999999,
        max_locations=999999,
        max_users=999999,
        max_encoders=999,
        features=[
            # All features
            "basic_control",
            "epg",
            "apple_tv",
            "android_tv",
            "presets",
            "hdmi_matrix",
            "video_streaming",
            "advanced_automation",
            "voice_control",
            "analytics",
            "centralized_management",
            "role_based_access",
            "white_label",
            "knx_integration",
            "api_access",
            "sso",
            "sla",
            "multi_tenant",
            "embeddable_widget",
            "reseller_program",
            "custom_development",
        ],
    ),
}


@dataclass
class Subscription:
    """Subscription instance"""
    id: str
    tenant_id: str
    tier: SubscriptionTier
    status: SubscriptionStatus
    device_count: int
    start_date: datetime
    end_date: Optional[datetime] = None
    trial_ends: Optional[datetime] = None
    stripe_subscription_id: Optional[str] = None
    
    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status == SubscriptionStatus.ACTIVE
    
    def is_trial(self) -> bool:
        """Check if in trial period"""
        if self.status != SubscriptionStatus.TRIAL:
            return False
        if not self.trial_ends:
            return False
        return datetime.now() < self.trial_ends
    
    def days_until_renewal(self) -> Optional[int]:
        """Days until subscription renews"""
        if not self.end_date:
            return None
        delta = self.end_date - datetime.now()
        return delta.days
    
    def get_limits(self) -> TierLimits:
        """Get limits for this tier"""
        return TIER_CONFIGS[self.tier]
    
    def can_add_device(self) -> bool:
        """Check if can add another device"""
        limits = self.get_limits()
        return self.device_count < limits.max_devices
    
    def has_feature(self, feature: str) -> bool:
        """Check if tier includes a feature"""
        limits = self.get_limits()
        return feature in limits.features


class SubscriptionManager:
    """
    Manages subscriptions and enforces limits
    """
    
    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        logger.info("SubscriptionManager initialized")
    
    def create_trial(
        self,
        tenant_id: str,
        tier: SubscriptionTier = SubscriptionTier.HOME,
    ) -> Subscription:
        """Create a trial subscription (14 days)"""
        subscription = Subscription(
            id=f"sub_{tenant_id}",
            tenant_id=tenant_id,
            tier=tier,
            status=SubscriptionStatus.TRIAL,
            device_count=0,
            start_date=datetime.now(),
            trial_ends=datetime.now() + timedelta(days=14),
        )
        self.subscriptions[tenant_id] = subscription
        logger.info(f"Created trial subscription for tenant {tenant_id}")
        return subscription
    
    def activate_subscription(
        self,
        tenant_id: str,
        tier: SubscriptionTier,
        stripe_subscription_id: str,
    ) -> Subscription:
        """Activate paid subscription"""
        subscription = Subscription(
            id=f"sub_{tenant_id}",
            tenant_id=tenant_id,
            tier=tier,
            status=SubscriptionStatus.ACTIVE,
            device_count=0,
            start_date=datetime.now(),
            stripe_subscription_id=stripe_subscription_id,
        )
        self.subscriptions[tenant_id] = subscription
        logger.info(f"Activated {tier.value} subscription for tenant {tenant_id}")
        return subscription
    
    def get_subscription(self, tenant_id: str) -> Optional[Subscription]:
        """Get subscription for tenant"""
        return self.subscriptions.get(tenant_id)
    
    def check_device_limit(self, tenant_id: str) -> bool:
        """Check if tenant can add more devices"""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            logger.warning(f"No subscription found for tenant {tenant_id}")
            return False
        
        if not (subscription.is_active() or subscription.is_trial()):
            logger.warning(f"Subscription not active for tenant {tenant_id}")
            return False
        
        return subscription.can_add_device()
    
    def register_device(self, tenant_id: str) -> bool:
        """Register a device to tenant's subscription"""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            return False
        
        if not subscription.can_add_device():
            logger.error(
                f"Device limit reached for tenant {tenant_id} "
                f"({subscription.device_count}/{subscription.get_limits().max_devices})"
            )
            return False
        
        subscription.device_count += 1
        logger.info(
            f"Registered device for tenant {tenant_id} "
            f"({subscription.device_count}/{subscription.get_limits().max_devices})"
        )
        return True
    
    def unregister_device(self, tenant_id: str) -> bool:
        """Unregister a device from tenant's subscription"""
        subscription = self.get_subscription(tenant_id)
        if not subscription or subscription.device_count == 0:
            return False
        
        subscription.device_count -= 1
        logger.info(f"Unregistered device for tenant {tenant_id}")
        return True
    
    def check_feature_access(self, tenant_id: str, feature: str) -> bool:
        """Check if tenant has access to a feature"""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            return False
        
        if not (subscription.is_active() or subscription.is_trial()):
            return False
        
        return subscription.has_feature(feature)
    
    def upgrade_subscription(
        self,
        tenant_id: str,
        new_tier: SubscriptionTier,
        stripe_subscription_id: Optional[str] = None,
    ) -> bool:
        """Upgrade subscription tier"""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            return False
        
        old_tier = subscription.tier
        subscription.tier = new_tier
        subscription.status = SubscriptionStatus.ACTIVE
        if stripe_subscription_id:
            subscription.stripe_subscription_id = stripe_subscription_id
        
        logger.info(
            f"Upgraded subscription for tenant {tenant_id}: "
            f"{old_tier.value} → {new_tier.value}"
        )
        return True
    
    def cancel_subscription(self, tenant_id: str) -> bool:
        """Cancel subscription (end of billing period)"""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            return False
        
        subscription.status = SubscriptionStatus.CANCELED
        subscription.end_date = datetime.now() + timedelta(days=30)  # Grace period
        logger.info(f"Canceled subscription for tenant {tenant_id}")
        return True
    
    def get_usage_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get usage summary for tenant"""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            return {}
        
        limits = subscription.get_limits()
        
        return {
            "tenant_id": tenant_id,
            "tier": subscription.tier.value,
            "status": subscription.status.value,
            "devices": {
                "current": subscription.device_count,
                "limit": limits.max_devices,
                "remaining": limits.max_devices - subscription.device_count,
            },
            "trial": {
                "is_trial": subscription.is_trial(),
                "days_remaining": (
                    (subscription.trial_ends - datetime.now()).days
                    if subscription.trial_ends
                    else None
                ),
            },
            "features": limits.features,
        }


# Stripe webhook handler example
STRIPE_WEBHOOK_HANDLER = """
# stripe_webhooks.py
import stripe
from subscription_manager import SubscriptionManager

stripe.api_key = "sk_test_..."

def handle_stripe_webhook(payload, sig_header):
    '''Handle Stripe webhook events'''
    
    endpoint_secret = "whsec_..."
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return {"error": "Invalid payload"}, 400
    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}, 400
    
    sub_manager = SubscriptionManager()
    
    # Handle subscription created
    if event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        tenant_id = subscription['metadata']['tenant_id']
        tier = subscription['metadata']['tier']
        
        sub_manager.activate_subscription(
            tenant_id=tenant_id,
            tier=tier,
            stripe_subscription_id=subscription['id'],
        )
    
    # Handle subscription updated
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        tenant_id = subscription['metadata']['tenant_id']
        
        if subscription['status'] == 'past_due':
            sub = sub_manager.get_subscription(tenant_id)
            if sub:
                sub.status = SubscriptionStatus.PAST_DUE
    
    # Handle subscription deleted/canceled
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        tenant_id = subscription['metadata']['tenant_id']
        sub_manager.cancel_subscription(tenant_id)
    
    return {"success": True}, 200
"""
