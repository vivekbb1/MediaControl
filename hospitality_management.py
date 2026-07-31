"""
Hospitality & Luxury Residence Management
Complete integration for digital wallet keys, in-room dining, household management, and staff communication

Features:
- Digital wallet keys (Apple Wallet, Google Wallet, Samsung Wallet)
- Hotel room key provisioning and lifecycle
- In-room dining (QR menu, ordering, KDS integration)
- Household management (shopping lists, browser)
- Staff communication (butler, housekeeping, nanny, driver)
- PMS integration (OPERA Cloud, Protel, Mews, Cloudbeds)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
import uuid


# ========== Data Models ==========

class WalletType(Enum):
    """Digital wallet type"""
    APPLE_WALLET = "apple_wallet"
    GOOGLE_WALLET = "google_wallet"
    SAMSUNG_WALLET = "samsung_wallet"


class KeyStatus(Enum):
    """Digital key status"""
    PROVISIONED = "provisioned"  # Created but not active
    ACTIVE = "active"  # Can unlock doors
    EXPIRED = "expired"  # Past check-out date
    REVOKED = "revoked"  # Manually deactivated


class OrderStatus(Enum):
    """Dining order status"""
    RECEIVED = "received"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class StaffRequestStatus(Enum):
    """Staff request status"""
    DISPATCHED = "dispatched"
    ACCEPTED = "accepted"
    EN_ROUTE = "en_route"
    ARRIVED = "arrived"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class DigitalKey:
    """Digital wallet key"""
    key_id: str
    wallet_type: WalletType
    
    # Guest info
    guest_name: str
    guest_email: str
    reservation_id: str
    
    # Room info
    room_number: str
    check_in: datetime
    check_out: datetime
    
    # Access levels
    access_levels: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status
    status: KeyStatus = KeyStatus.PROVISIONED
    wallet_pass_url: Optional[str] = None
    activated_at: Optional[datetime] = None


@dataclass
class MenuItem:
    """Menu item"""
    item_id: str
    name: str
    description: str
    price: float
    category: str
    
    image_url: Optional[str] = None
    dietary: List[str] = field(default_factory=list)  # vegetarian, vegan, gluten-free
    allergens: List[str] = field(default_factory=list)  # gluten, dairy, nuts
    
    customizations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiningOrder:
    """In-room dining order"""
    order_id: str
    room_number: str
    guest_name: str
    
    items: List[Dict[str, Any]]
    total: float
    
    payment_method: str  # room_charge, credit_card
    special_instructions: Optional[str] = None
    
    status: OrderStatus = OrderStatus.RECEIVED
    estimated_delivery: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StaffRequest:
    """Staff request"""
    request_id: str
    room_number: str
    guest_name: str
    
    staff_role: str  # butler, housekeeping, nanny, driver
    request_type: str
    message: str
    priority: str  # normal, urgent
    
    photo_url: Optional[str] = None
    
    status: StaffRequestStatus = StaffRequestStatus.DISPATCHED
    staff_member: Optional[str] = None
    estimated_arrival: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


# ========== Digital Wallet Integration ==========

class DigitalWalletController:
    """
    Digital wallet integration
    Supports Apple Wallet, Google Wallet, Samsung Wallet
    """
    
    def __init__(self):
        self.keys: Dict[str, DigitalKey] = {}
        
        print(f"Digital Wallet Controller initialized")
    
    async def issue_key(self, wallet_type: WalletType, guest_info: Dict[str, Any],
                       reservation_info: Dict[str, Any], access_levels: List[Dict[str, Any]]) -> DigitalKey:
        """Issue digital wallet key"""
        key_id = f"key_{uuid.uuid4().hex[:12]}"
        
        digital_key = DigitalKey(
            key_id=key_id,
            wallet_type=wallet_type,
            guest_name=guest_info["name"],
            guest_email=guest_info["email"],
            reservation_id=reservation_info["id"],
            room_number=reservation_info["room_number"],
            check_in=datetime.fromisoformat(reservation_info["check_in"]),
            check_out=datetime.fromisoformat(reservation_info["check_out"]),
            access_levels=access_levels,
            status=KeyStatus.PROVISIONED
        )
        
        # Generate wallet pass URL (in real implementation: call wallet API)
        if wallet_type == WalletType.APPLE_WALLET:
            digital_key.wallet_pass_url = f"https://wallet-pass.apple.com/{key_id}"
        elif wallet_type == WalletType.GOOGLE_WALLET:
            digital_key.wallet_pass_url = f"https://pay.google.com/gp/v/pass/{key_id}"
        elif wallet_type == WalletType.SAMSUNG_WALLET:
            digital_key.wallet_pass_url = f"https://wallet.samsung.com/pass/{key_id}"
        
        self.keys[key_id] = digital_key
        
        print(f"Digital key issued: {key_id} for {guest_info['name']} (Room {reservation_info['room_number']})")
        print(f"  Wallet: {wallet_type.value}")
        print(f"  Check-in: {digital_key.check_in}")
        print(f"  Check-out: {digital_key.check_out}")
        
        return digital_key
    
    async def activate_key(self, key_id: str):
        """Activate key (on check-in)"""
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")
        
        key = self.keys[key_id]
        key.status = KeyStatus.ACTIVE
        key.activated_at = datetime.now()
        
        print(f"Digital key activated: {key_id}")
        print(f"  Guest can now unlock Room {key.room_number}")
    
    async def deactivate_key(self, key_id: str):
        """Deactivate key (on check-out)"""
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")
        
        key = self.keys[key_id]
        key.status = KeyStatus.EXPIRED
        
        print(f"Digital key deactivated: {key_id}")


# ========== PMS Integration ==========

class PMSIntegration:
    """
    Property Management System integration
    Supports OPERA Cloud, Protel, Mews, Cloudbeds
    """
    
    def __init__(self, pms_type: str, api_url: str, api_key: str):
        self.pms_type = pms_type
        self.api_url = api_url
        self.api_key = api_key
        
        print(f"PMS Integration initialized: {pms_type}")
    
    async def verify_guest_checkin(self, room_number: str) -> Dict[str, Any]:
        """Verify guest is checked in (for room charge authorization)"""
        # In real implementation: call PMS API
        # For OPERA Cloud:
        # GET /fof/v1/hotels/{hotelId}/reservations?roomNumber={room_number}&status=IN_HOUSE
        
        return {
            "checked_in": True,
            "guest_name": "John Smith",
            "reservation_id": "RES_123456",
            "check_out_date": "2026-08-03"
        }
    
    async def post_charge_to_folio(self, room_number: str, amount: float, description: str):
        """Post charge to guest folio"""
        # In real implementation: call PMS API
        # For OPERA Cloud:
        # POST /cashiering/v1/hotels/{hotelId}/folios/{folioId}/charges
        
        print(f"Charge posted to Room {room_number} folio: ${amount:.2f} - {description}")


# ========== In-Room Dining System ==========

class InRoomDiningController:
    """
    In-room dining system
    QR menu, ordering, KDS integration
    """
    
    def __init__(self, pms_integration: PMSIntegration):
        self.pms = pms_integration
        
        self.menus: Dict[str, Dict[str, Any]] = {}
        self.orders: Dict[str, DiningOrder] = {}
        
        print(f"In-Room Dining Controller initialized")
    
    def add_menu(self, menu_id: str, menu_data: Dict[str, Any]):
        """Add menu"""
        self.menus[menu_id] = menu_data
        print(f"Menu added: {menu_id} ({menu_data['name']})")
    
    async def get_menu(self, room_number: str) -> Dict[str, Any]:
        """Get menu for room"""
        # Verify guest is checked in
        guest_info = await self.pms.verify_guest_checkin(room_number)
        
        return {
            "room_number": room_number,
            "guest_name": guest_info["guest_name"],
            "menus": list(self.menus.values())
        }
    
    async def place_order(self, room_number: str, items: List[Dict[str, Any]],
                          payment_method: str, special_instructions: Optional[str] = None) -> DiningOrder:
        """Place dining order"""
        order_id = f"ORD_{uuid.uuid4().hex[:8].upper()}"
        
        # Verify guest is checked in
        guest_info = await self.pms.verify_guest_checkin(room_number)
        
        # Calculate total
        total = sum(item["price"] * item["quantity"] for item in items)
        
        # Create order
        order = DiningOrder(
            order_id=order_id,
            room_number=room_number,
            guest_name=guest_info["guest_name"],
            items=items,
            total=total,
            payment_method=payment_method,
            special_instructions=special_instructions,
            status=OrderStatus.RECEIVED,
            estimated_delivery=datetime.now() + timedelta(minutes=30)
        )
        
        self.orders[order_id] = order
        
        print(f"Order placed: {order_id}")
        print(f"  Room: {room_number}")
        print(f"  Total: ${total:.2f}")
        print(f"  Items: {len(items)}")
        
        # Send to kitchen (in real implementation: send to KDS)
        await self._send_to_kitchen(order)
        
        return order
    
    async def _send_to_kitchen(self, order: DiningOrder):
        """Send order to kitchen display system"""
        print(f"→ Order sent to KDS: {order.order_id}")
    
    async def update_order_status(self, order_id: str, status: OrderStatus):
        """Update order status"""
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")
        
        order = self.orders[order_id]
        order.status = status
        
        print(f"Order {order_id} status updated: {status.value}")
        
        # Notify guest (in real implementation: send push/SMS)
        await self._notify_guest(order)
    
    async def _notify_guest(self, order: DiningOrder):
        """Notify guest of order status"""
        status_messages = {
            OrderStatus.RECEIVED: "Your order has been received",
            OrderStatus.PREPARING: "Chef is preparing your order",
            OrderStatus.OUT_FOR_DELIVERY: "Your order is on its way!",
            OrderStatus.DELIVERED: "Enjoy your meal!"
        }
        
        message = status_messages.get(order.status, "Order status updated")
        print(f"📱 Guest notification: {message}")


# ========== Staff Communication System ==========

class StaffCommunicationController:
    """
    Staff communication system
    Butler, housekeeping, nanny, driver requests
    """
    
    def __init__(self):
        self.requests: Dict[str, StaffRequest] = {}
        self.staff_members: Dict[str, Dict[str, Any]] = {}
        
        print(f"Staff Communication Controller initialized")
    
    def register_staff_member(self, role: str, name: str, phone: str, email: str):
        """Register staff member"""
        self.staff_members[role] = {
            "name": name,
            "phone": phone,
            "email": email,
            "available": True
        }
        print(f"Staff registered: {name} ({role})")
    
    async def send_request(self, room_number: str, guest_name: str, staff_role: str,
                           request_type: str, message: str, priority: str = "normal",
                           photo_url: Optional[str] = None) -> StaffRequest:
        """Send staff request"""
        request_id = f"REQ_{uuid.uuid4().hex[:8].upper()}"
        
        request = StaffRequest(
            request_id=request_id,
            room_number=room_number,
            guest_name=guest_name,
            staff_role=staff_role,
            request_type=request_type,
            message=message,
            priority=priority,
            photo_url=photo_url,
            status=StaffRequestStatus.DISPATCHED,
            estimated_arrival=datetime.now() + timedelta(minutes=10)
        )
        
        # Assign to staff member
        if staff_role in self.staff_members:
            request.staff_member = self.staff_members[staff_role]["name"]
        
        self.requests[request_id] = request
        
        print(f"Staff request created: {request_id}")
        print(f"  Role: {staff_role}")
        print(f"  Type: {request_type}")
        print(f"  Priority: {priority}")
        print(f"  Room: {room_number}")
        
        # Dispatch to staff (in real implementation: send push/SMS)
        await self._dispatch_to_staff(request)
        
        return request
    
    async def _dispatch_to_staff(self, request: StaffRequest):
        """Dispatch request to staff member"""
        if request.staff_member:
            print(f"→ Request dispatched to {request.staff_member}")
    
    async def update_request_status(self, request_id: str, status: StaffRequestStatus):
        """Update request status"""
        if request_id not in self.requests:
            raise ValueError(f"Request {request_id} not found")
        
        request = self.requests[request_id]
        request.status = status
        
        print(f"Request {request_id} status updated: {status.value}")
        
        # Notify guest
        await self._notify_guest(request)
    
    async def _notify_guest(self, request: StaffRequest):
        """Notify guest of request status"""
        status_messages = {
            StaffRequestStatus.ACCEPTED: f"{request.staff_member} is on the way",
            StaffRequestStatus.EN_ROUTE: f"{request.staff_member} will arrive shortly",
            StaffRequestStatus.ARRIVED: f"{request.staff_member} has arrived",
            StaffRequestStatus.COMPLETED: "Request completed"
        }
        
        message = status_messages.get(request.status, "Request updated")
        print(f"📱 Guest notification: {message}")


# ========== Hospitality Manager ==========

class HospitalityManager:
    """
    Hospitality & Luxury Residence Manager
    Manages all hospitality features
    """
    
    def __init__(self):
        self.digital_wallet: DigitalWalletController = DigitalWalletController()
        self.pms: Optional[PMSIntegration] = None
        self.dining: Optional[InRoomDiningController] = None
        self.staff_comm: StaffCommunicationController = StaffCommunicationController()
        
        print(f"\n{'='*60}")
        print(f"Hospitality Manager Initialized")
        print(f"{'='*60}\n")
    
    def setup_pms(self, pms_type: str, api_url: str, api_key: str):
        """Setup PMS integration"""
        self.pms = PMSIntegration(pms_type, api_url, api_key)
        self.dining = InRoomDiningController(self.pms)
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "digital_keys": {
                "total": len(self.digital_wallet.keys),
                "active": sum(1 for k in self.digital_wallet.keys.values() if k.status == KeyStatus.ACTIVE)
            },
            "dining_orders": {
                "total": len(self.dining.orders) if self.dining else 0,
                "active": sum(1 for o in (self.dining.orders.values() if self.dining else [])
                             if o.status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED])
            },
            "staff_requests": {
                "total": len(self.staff_comm.requests),
                "active": sum(1 for r in self.staff_comm.requests.values()
                             if r.status not in [StaffRequestStatus.COMPLETED, StaffRequestStatus.CANCELLED])
            }
        }


# Example usage
if __name__ == "__main__":
    print("=== Hospitality & Luxury Residence Management Demo ===\n")
    
    # Initialize manager
    manager = HospitalityManager()
    
    # Setup PMS
    print("\n--- Setup PMS Integration ---\n")
    manager.setup_pms(
        pms_type="opera_cloud",
        api_url="https://api.opera-cloud.com",
        api_key="your_opera_api_key"
    )
    
    # Register staff
    print("\n--- Register Staff ---\n")
    manager.staff_comm.register_staff_member("butler", "James (Head Butler)", "+1-555-123-4567", "james@hotel.com")
    manager.staff_comm.register_staff_member("housekeeping", "Maria (Housekeeper)", "+1-555-234-5678", "maria@hotel.com")
    manager.staff_comm.register_staff_member("nanny", "Sarah (Nanny)", "+1-555-345-6789", "sarah@household.com")
    manager.staff_comm.register_staff_member("driver", "Michael (Driver)", "+1-555-456-7890", "michael@household.com")
    
    # Run simulation
    async def run_simulation():
        # Issue digital key
        print("\n--- Issue Digital Wallet Key ---\n")
        key = await manager.digital_wallet.issue_key(
            wallet_type=WalletType.APPLE_WALLET,
            guest_info={
                "name": "John Smith",
                "email": "john@example.com",
                "phone": "+1-555-111-2222"
            },
            reservation_info={
                "id": "RES_123456",
                "room_number": "2201",
                "check_in": "2026-07-31T15:00:00",
                "check_out": "2026-08-03T12:00:00"
            },
            access_levels=[
                {"type": "ROOM", "roomNumber": "2201"},
                {"type": "COMMON_AREA", "areas": ["POOL", "GYM"]}
            ]
        )
        
        # Activate key (check-in)
        print("\n--- Guest Checks In ---\n")
        await manager.digital_wallet.activate_key(key.key_id)
        
        # Place dining order
        print("\n--- Place In-Room Dining Order ---\n")
        order = await manager.dining.place_order(
            room_number="2201",
            items=[
                {"item_id": "burger", "name": "Burger & Fries", "quantity": 1, "price": 18.00},
                {"item_id": "salad", "name": "Caesar Salad", "quantity": 1, "price": 12.00}
            ],
            payment_method="room_charge",
            special_instructions="No pickles, extra cheese"
        )
        
        # Update order status
        await asyncio.sleep(1)
        await manager.dining.update_order_status(order.order_id, OrderStatus.PREPARING)
        
        # Send staff request
        print("\n--- Send Butler Request ---\n")
        request = await manager.staff_comm.send_request(
            room_number="2201",
            guest_name="John Smith",
            staff_role="butler",
            request_type="Room Service",
            message="Please bring extra towels",
            priority="normal"
        )
        
        # Update request status
        await asyncio.sleep(1)
        await manager.staff_comm.update_request_status(request.request_id, StaffRequestStatus.ACCEPTED)
    
    asyncio.run(run_simulation())
    
    # Print status
    print("\n" + "="*60)
    print("SYSTEM STATUS")
    print("="*60 + "\n")
    status = manager.get_status()
    print(json.dumps(status, indent=2))
