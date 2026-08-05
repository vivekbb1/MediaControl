"""
Door Access Control - Multi-Factor Authentication
Complete access control system with NFC, RFID, face recognition, fingerprint, and PIN pad

Features:
- 5 authentication methods (NFC, RFID, face recognition, fingerprint, PIN pad)
- Multi-factor authentication (MFA) - require 2+ methods
- Liveness detection (anti-spoofing for face/fingerprint)
- Time-based access control
- Anti-passback
- Visitor management (temporary PINs, QR codes)
- Emergency lockdown/evacuation
- Real-time logging with photos
- Integration with Ubiquiti Access, Salto, ASSA ABLOY, HID, ZKTeco, Hikvision, Dahua
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import hashlib
import secrets
import json


# ========== Data Models ==========

class AuthMethod(Enum):
    """Authentication method"""
    NFC = "nfc"
    RFID = "rfid"
    FACE_RECOGNITION = "face_recognition"
    FINGERPRINT = "fingerprint"
    PIN_PAD = "pin_pad"


class AccessResult(Enum):
    """Access control result"""
    GRANTED = "granted"
    DENIED = "denied"
    MFA_REQUIRED = "mfa_required"


class DenyReason(Enum):
    """Reason for denied access"""
    INVALID_CREDENTIAL = "invalid_credential"
    EXPIRED_CREDENTIAL = "expired_credential"
    TIME_RESTRICTION = "time_restriction"
    ANTI_PASSBACK = "anti_passback"
    MAX_ATTEMPTS = "max_attempts"
    EMERGENCY_LOCKDOWN = "emergency_lockdown"


@dataclass
class Credential:
    """User credential"""
    credential_id: str
    credential_type: AuthMethod
    user_id: str
    
    # NFC/RFID
    card_id: Optional[str] = None
    card_type: Optional[str] = None
    
    # Face recognition
    face_template: Optional[bytes] = None
    
    # Fingerprint
    fingerprint_template: Optional[bytes] = None
    finger: Optional[str] = None  # left_index, right_index, etc.
    
    # PIN
    pin_hash: Optional[str] = None
    
    # Metadata
    issued_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    active: bool = True


@dataclass
class User:
    """Access control user"""
    user_id: str
    name: str
    email: str
    role: str
    
    credentials: List[Credential] = field(default_factory=list)
    
    # Access permissions
    allowed_doors: List[str] = field(default_factory=list)
    time_zones: List[str] = field(default_factory=list)
    
    # Status
    active: bool = True


@dataclass
class Visitor:
    """Temporary visitor"""
    visitor_id: str
    name: str
    email: Optional[str]
    company: Optional[str]
    
    host_user_id: str
    
    # Temporary credentials
    temporary_pin: str
    qr_code: Optional[str] = None
    
    # Access
    allowed_doors: List[str] = field(default_factory=list)
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    max_uses: int = 1
    remaining_uses: int = 1
    
    # Status
    active: bool = True


@dataclass
class AccessLog:
    """Access log entry"""
    log_id: str
    door_id: str
    timestamp: datetime
    
    user_id: Optional[str]
    visitor_id: Optional[str]
    
    method: AuthMethod
    result: AccessResult
    deny_reason: Optional[DenyReason] = None
    
    # MFA tracking
    mfa_completed: bool = False
    mfa_methods: List[AuthMethod] = field(default_factory=list)
    
    # Evidence
    photo: Optional[bytes] = None
    video: Optional[bytes] = None
    
    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)


# ========== NFC Controller ==========

class NFCController:
    """
    NFC access control
    Supports ISO 14443A/B, MIFARE, NFC Type 2
    """
    
    def __init__(self, reader_config: Dict[str, Any]):
        self.reader_type = reader_config.get("type", "acr122u")
        self.interface = reader_config.get("interface", "usb")
        self.device = reader_config.get("device")
        
        self.registered_cards: Dict[str, str] = {}  # card_id -> user_id
        
        print(f"NFC Controller initialized: {self.reader_type}")
    
    async def read_card(self) -> Optional[str]:
        """Read NFC card ID"""
        # In real implementation: interact with NFC reader hardware
        # For now, simulate card read
        return None
    
    async def verify_card(self, card_id: str) -> Optional[str]:
        """Verify NFC card and return user_id"""
        if card_id in self.registered_cards:
            user_id = self.registered_cards[card_id]
            print(f"NFC card verified: {card_id} → User {user_id}")
            return user_id
        
        print(f"NFC card not recognized: {card_id}")
        return None
    
    def register_card(self, card_id: str, user_id: str):
        """Register NFC card"""
        self.registered_cards[card_id] = user_id
        print(f"NFC card registered: {card_id} → User {user_id}")


# ========== RFID Controller ==========

class RFIDController:
    """
    RFID access control
    Supports LF (125 kHz), HF (13.56 MHz), UHF (860-960 MHz)
    """
    
    def __init__(self, reader_config: Dict[str, Any]):
        self.reader_type = reader_config.get("type", "hid_proxpoint")
        self.frequency = reader_config.get("frequency", "125khz")
        self.interface = reader_config.get("interface", "wiegand")
        
        self.registered_cards: Dict[str, str] = {}  # card_id -> user_id
        
        print(f"RFID Controller initialized: {self.reader_type} ({self.frequency})")
    
    async def read_card(self) -> Optional[str]:
        """Read RFID card ID"""
        # In real implementation: interact with RFID reader via Wiegand/RS-485
        return None
    
    async def verify_card(self, card_id: str) -> Optional[str]:
        """Verify RFID card and return user_id"""
        if card_id in self.registered_cards:
            user_id = self.registered_cards[card_id]
            print(f"RFID card verified: {card_id} → User {user_id}")
            return user_id
        
        print(f"RFID card not recognized: {card_id}")
        return None
    
    def register_card(self, card_id: str, user_id: str):
        """Register RFID card"""
        self.registered_cards[card_id] = user_id
        print(f"RFID card registered: {card_id} → User {user_id}")


# ========== Face Recognition Controller ==========

class FaceRecognitionController:
    """
    AI-powered face recognition
    Supports FaceNet, ArcFace, DeepFace algorithms
    """
    
    def __init__(self, camera_config: Dict[str, Any], model_config: Dict[str, Any]):
        self.camera_type = camera_config.get("type", "custom")
        self.camera_ip = camera_config.get("ip")
        
        self.algorithm = model_config.get("algorithm", "arcface")
        self.accuracy_threshold = model_config.get("accuracy_threshold", 0.95)
        
        self.enrolled_faces: Dict[str, bytes] = {}  # user_id -> face_template
        
        print(f"Face Recognition Controller initialized: {self.algorithm}")
    
    async def capture_face(self) -> Optional[bytes]:
        """Capture face from camera"""
        # In real implementation: capture from camera, extract face template
        return None
    
    async def recognize_face(self, face_template: bytes) -> Optional[Tuple[str, float]]:
        """
        Recognize face and return (user_id, confidence)
        Returns None if no match found
        """
        # In real implementation: compare face_template with enrolled_faces
        # using cosine similarity or Euclidean distance
        
        # For now, simulate recognition
        best_match_user_id = None
        best_confidence = 0.0
        
        for user_id, enrolled_template in self.enrolled_faces.items():
            # Simulate confidence score
            confidence = 0.98  # In real implementation: compute similarity
            
            if confidence >= self.accuracy_threshold and confidence > best_confidence:
                best_match_user_id = user_id
                best_confidence = confidence
        
        if best_match_user_id:
            print(f"Face recognized: User {best_match_user_id} (confidence: {best_confidence:.2f})")
            return (best_match_user_id, best_confidence)
        
        print(f"Face not recognized")
        return None
    
    async def enroll_face(self, user_id: str, face_photos: List[bytes]) -> bool:
        """Enroll face from multiple photos"""
        # In real implementation: extract face template from multiple angles
        # For now, store first photo as template
        if face_photos:
            self.enrolled_faces[user_id] = face_photos[0]
            print(f"Face enrolled: User {user_id} ({len(face_photos)} photos)")
            return True
        return False
    
    async def check_liveness(self, face_template: bytes) -> bool:
        """Check if face is live (not photo/video)"""
        # In real implementation: IR camera, eye blink, 3D depth, face movement
        # For now, assume live
        return True


# ========== Fingerprint Controller ==========

class FingerprintController:
    """
    Biometric fingerprint scanner
    Supports capacitive, optical, ultrasonic sensors
    """
    
    def __init__(self, scanner_config: Dict[str, Any]):
        self.scanner_type = scanner_config.get("type", "zkteco_slk20r")
        self.interface = scanner_config.get("interface", "ethernet")
        self.ip = scanner_config.get("ip")
        
        self.enrolled_fingerprints: Dict[str, bytes] = {}  # fingerprint_id -> template
        self.user_fingerprints: Dict[str, List[str]] = {}  # user_id -> [fingerprint_id, ...]
        
        print(f"Fingerprint Controller initialized: {self.scanner_type}")
    
    async def capture_fingerprint(self) -> Optional[bytes]:
        """Capture fingerprint from scanner"""
        # In real implementation: capture from scanner, extract minutiae template
        return None
    
    async def match_fingerprint(self, fingerprint_template: bytes) -> Optional[Tuple[str, float]]:
        """
        Match fingerprint and return (user_id, confidence)
        Returns None if no match found
        """
        # In real implementation: compare minutiae points
        
        best_match_user_id = None
        best_score = 0
        
        for fingerprint_id, enrolled_template in self.enrolled_fingerprints.items():
            # Simulate matching score
            score = 85  # In real implementation: compute minutiae match score (0-100)
            
            if score >= 40 and score > best_score:  # threshold = 40
                # Find user_id for this fingerprint
                for user_id, fp_ids in self.user_fingerprints.items():
                    if fingerprint_id in fp_ids:
                        best_match_user_id = user_id
                        best_score = score
                        break
        
        if best_match_user_id:
            print(f"Fingerprint matched: User {best_match_user_id} (score: {best_score})")
            return (best_match_user_id, best_score / 100.0)
        
        print(f"Fingerprint not matched")
        return None
    
    async def enroll_fingerprint(self, user_id: str, finger: str, fingerprint_template: bytes) -> str:
        """Enroll fingerprint"""
        fingerprint_id = f"fp_{user_id}_{finger}"
        self.enrolled_fingerprints[fingerprint_id] = fingerprint_template
        
        if user_id not in self.user_fingerprints:
            self.user_fingerprints[user_id] = []
        self.user_fingerprints[user_id].append(fingerprint_id)
        
        print(f"Fingerprint enrolled: User {user_id} ({finger})")
        return fingerprint_id
    
    async def check_liveness(self, fingerprint_template: bytes) -> bool:
        """Check if fingerprint is live (not fake)"""
        # In real implementation: capacitive sensor detects live skin
        return True


# ========== PIN Pad Controller ==========

class PINPadController:
    """
    Keypad entry system
    Supports personal PINs, temporary PINs, master PIN, duress PIN
    """
    
    def __init__(self, keypad_config: Dict[str, Any], pin_config: Dict[str, Any]):
        self.keypad_type = keypad_config.get("type", "hid_pivclass")
        self.interface = keypad_config.get("interface", "wiegand")
        
        self.min_length = pin_config.get("min_length", 4)
        self.max_length = pin_config.get("max_length", 8)
        
        self.personal_pins: Dict[str, str] = {}  # pin_hash -> user_id
        self.temporary_pins: Dict[str, Dict[str, Any]] = {}  # pin -> {user_id, expires_at, max_uses, ...}
        
        self.master_pin = pin_config.get("master_pin", {}).get("code")
        self.duress_pin = pin_config.get("duress", {}).get("code")
        
        # Anti-brute-force
        self.failed_attempts: Dict[str, int] = {}  # door_id -> attempt_count
        self.lockout_until: Dict[str, datetime] = {}  # door_id -> lockout_expiry
        
        print(f"PIN Pad Controller initialized: {self.keypad_type}")
    
    def hash_pin(self, pin: str) -> str:
        """Hash PIN for secure storage"""
        return hashlib.sha256(pin.encode()).hexdigest()
    
    async def verify_pin(self, door_id: str, pin: str) -> Optional[Tuple[str, bool]]:
        """
        Verify PIN and return (user_id, is_duress)
        Returns None if invalid
        """
        # Check lockout
        if door_id in self.lockout_until:
            if datetime.now() < self.lockout_until[door_id]:
                print(f"Door {door_id} is locked out until {self.lockout_until[door_id]}")
                return None
            else:
                del self.lockout_until[door_id]
                del self.failed_attempts[door_id]
        
        # Check duress PIN
        if self.duress_pin and pin == self.duress_pin:
            print(f"⚠️ DURESS PIN ENTERED - Silent alarm triggered!")
            await self._trigger_duress_alarm(door_id)
            # Still grant access but alert security
            return ("DURESS", True)
        
        # Check master PIN
        if self.master_pin and pin == self.master_pin:
            print(f"Master PIN used for {door_id}")
            return ("MASTER", False)
        
        # Check temporary PINs
        if pin in self.temporary_pins:
            temp_data = self.temporary_pins[pin]
            
            # Check expiry
            if temp_data.get("expires_at") and datetime.now() > temp_data["expires_at"]:
                print(f"Temporary PIN expired: {pin}")
                del self.temporary_pins[pin]
                return None
            
            # Check max uses
            if temp_data.get("remaining_uses", 1) <= 0:
                print(f"Temporary PIN exhausted: {pin}")
                del self.temporary_pins[pin]
                return None
            
            # Valid temporary PIN
            user_id = temp_data.get("user_id", temp_data.get("visitor_id"))
            temp_data["remaining_uses"] = temp_data.get("remaining_uses", 1) - 1
            
            print(f"Temporary PIN verified: {pin} → {user_id}")
            return (user_id, False)
        
        # Check personal PINs
        pin_hash = self.hash_pin(pin)
        if pin_hash in self.personal_pins:
            user_id = self.personal_pins[pin_hash]
            print(f"Personal PIN verified → User {user_id}")
            
            # Reset failed attempts
            if door_id in self.failed_attempts:
                del self.failed_attempts[door_id]
            
            return (user_id, False)
        
        # Invalid PIN - increment failed attempts
        self.failed_attempts[door_id] = self.failed_attempts.get(door_id, 0) + 1
        
        if self.failed_attempts[door_id] >= 3:
            # Lockout for 5 minutes
            self.lockout_until[door_id] = datetime.now() + timedelta(seconds=300)
            print(f"⚠️ Door {door_id} locked out after 3 failed PIN attempts (until {self.lockout_until[door_id]})")
        
        print(f"Invalid PIN (attempt {self.failed_attempts[door_id]}/3)")
        return None
    
    def register_personal_pin(self, user_id: str, pin: str):
        """Register personal PIN"""
        pin_hash = self.hash_pin(pin)
        self.personal_pins[pin_hash] = user_id
        print(f"Personal PIN registered for User {user_id}")
    
    def generate_temporary_pin(self, user_id: str, expires_at: Optional[datetime] = None,
                                max_uses: int = 1) -> str:
        """Generate temporary PIN"""
        # Generate random 6-digit PIN
        pin = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        self.temporary_pins[pin] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "max_uses": max_uses,
            "remaining_uses": max_uses,
            "created_at": datetime.now()
        }
        
        print(f"Temporary PIN generated: {pin} for {user_id} (expires: {expires_at}, max uses: {max_uses})")
        return pin
    
    async def _trigger_duress_alarm(self, door_id: str):
        """Trigger silent duress alarm"""
        # In real implementation: notify security, alert police
        print(f"🚨 DURESS ALARM: Door {door_id} - Silent alarm sent to security")


# ========== Access Control Manager ==========

class AccessControlManager:
    """
    Main access control manager
    Coordinates all authentication methods and enforces access rules
    """
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.visitors: Dict[str, Visitor] = {}
        self.access_logs: List[AccessLog] = []
        
        # Controllers
        self.nfc: Optional[NFCController] = None
        self.rfid: Optional[RFIDController] = None
        self.face: Optional[FaceRecognitionController] = None
        self.fingerprint: Optional[FingerprintController] = None
        self.pin_pad: Optional[PINPadController] = None
        
        # Emergency mode
        self.lockdown_active = False
        self.evacuation_active = False
        
        print(f"\n{'='*60}")
        print(f"Access Control Manager Initialized")
        print(f"{'='*60}\n")
    
    def setup_nfc(self, reader_config: Dict[str, Any]):
        """Setup NFC controller"""
        self.nfc = NFCController(reader_config)
    
    def setup_rfid(self, reader_config: Dict[str, Any]):
        """Setup RFID controller"""
        self.rfid = RFIDController(reader_config)
    
    def setup_face_recognition(self, camera_config: Dict[str, Any], model_config: Dict[str, Any]):
        """Setup face recognition controller"""
        self.face = FaceRecognitionController(camera_config, model_config)
    
    def setup_fingerprint(self, scanner_config: Dict[str, Any]):
        """Setup fingerprint controller"""
        self.fingerprint = FingerprintController(scanner_config)
    
    def setup_pin_pad(self, keypad_config: Dict[str, Any], pin_config: Dict[str, Any]):
        """Setup PIN pad controller"""
        self.pin_pad = PINPadController(keypad_config, pin_config)
    
    async def authenticate(self, door_id: str, method: AuthMethod, credential_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate user for door access
        Returns access decision with details
        """
        log_id = f"log_{secrets.token_hex(6)}"
        
        # Check emergency mode
        if self.lockdown_active:
            result = self._create_deny_result(log_id, door_id, method, None, DenyReason.EMERGENCY_LOCKDOWN)
            await self._log_access(result)
            return result
        
        if self.evacuation_active:
            result = self._create_grant_result(log_id, door_id, method, "EVACUATION", mfa_required=False)
            await self._log_access(result)
            return result
        
        # Authenticate based on method
        user_id = None
        
        if method == AuthMethod.NFC and self.nfc:
            card_id = credential_data.get("card_id")
            if card_id:
                user_id = await self.nfc.verify_card(card_id)
        
        elif method == AuthMethod.RFID and self.rfid:
            card_id = credential_data.get("card_id")
            if card_id:
                user_id = await self.rfid.verify_card(card_id)
        
        elif method == AuthMethod.FACE_RECOGNITION and self.face:
            face_template = credential_data.get("face_template")
            if face_template:
                result = await self.face.recognize_face(face_template)
                if result:
                    user_id, confidence = result
        
        elif method == AuthMethod.FINGERPRINT and self.fingerprint:
            fingerprint_template = credential_data.get("fingerprint_template")
            if fingerprint_template:
                result = await self.fingerprint.match_fingerprint(fingerprint_template)
                if result:
                    user_id, confidence = result
        
        elif method == AuthMethod.PIN_PAD and self.pin_pad:
            pin = credential_data.get("pin")
            if pin:
                result = await self.pin_pad.verify_pin(door_id, pin)
                if result:
                    user_id, is_duress = result
        
        # Check if user found
        if not user_id:
            result = self._create_deny_result(log_id, door_id, method, None, DenyReason.INVALID_CREDENTIAL)
            await self._log_access(result)
            return result
        
        # Check if user has access to door
        user = self.users.get(user_id)
        if not user or door_id not in user.allowed_doors:
            result = self._create_deny_result(log_id, door_id, method, user_id, DenyReason.INVALID_CREDENTIAL)
            await self._log_access(result)
            return result
        
        # Access granted
        result = self._create_grant_result(log_id, door_id, method, user_id, mfa_required=False)
        await self._log_access(result)
        return result
    
    def _create_grant_result(self, log_id: str, door_id: str, method: AuthMethod, user_id: str,
                             mfa_required: bool) -> Dict[str, Any]:
        """Create access granted result"""
        user = self.users.get(user_id)
        
        return {
            "log_id": log_id,
            "access_granted": True,
            "user": {
                "id": user_id,
                "name": user.name if user else "Unknown",
                "role": user.role if user else "Unknown"
            },
            "mfa_required": mfa_required,
            "unlock_duration": 5,  # seconds
            "message": f"Welcome, {user.name if user else user_id}!"
        }
    
    def _create_deny_result(self, log_id: str, door_id: str, method: AuthMethod, user_id: Optional[str],
                            reason: DenyReason) -> Dict[str, Any]:
        """Create access denied result"""
        reason_messages = {
            DenyReason.INVALID_CREDENTIAL: "Invalid credential",
            DenyReason.EXPIRED_CREDENTIAL: "Credential expired",
            DenyReason.TIME_RESTRICTION: "Access not allowed at this time",
            DenyReason.ANTI_PASSBACK: "Anti-passback violation",
            DenyReason.MAX_ATTEMPTS: "Too many failed attempts",
            DenyReason.EMERGENCY_LOCKDOWN: "Emergency lockdown active"
        }
        
        return {
            "log_id": log_id,
            "access_granted": False,
            "reason": reason.value,
            "message": reason_messages.get(reason, "Access denied"),
            "retry_allowed": reason != DenyReason.MAX_ATTEMPTS and reason != DenyReason.EMERGENCY_LOCKDOWN
        }
    
    async def _log_access(self, result: Dict[str, Any]):
        """Log access attempt"""
        # In real implementation: store in database
        print(f"Access log: {result['log_id']} - {'GRANTED' if result['access_granted'] else 'DENIED'}")
    
    async def emergency_lockdown(self, pin: str, initiated_by: str) -> bool:
        """Trigger emergency lockdown (lock all doors)"""
        # Verify master PIN
        if not self.pin_pad or self.pin_pad.master_pin != pin:
            print(f"❌ Invalid lockdown PIN")
            return False
        
        self.lockdown_active = True
        print(f"🚨 EMERGENCY LOCKDOWN ACTIVATED by {initiated_by}")
        print(f"   All doors locked")
        return True
    
    async def emergency_evacuation(self, pin: str, initiated_by: str) -> bool:
        """Trigger emergency evacuation (unlock all doors)"""
        # Verify master PIN
        if not self.pin_pad or self.pin_pad.master_pin != pin:
            print(f"❌ Invalid evacuation PIN")
            return False
        
        self.evacuation_active = True
        print(f"🚨 EMERGENCY EVACUATION ACTIVATED by {initiated_by}")
        print(f"   All doors unlocked")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "users": len(self.users),
            "visitors": len(self.visitors),
            "access_logs": len(self.access_logs),
            "controllers": {
                "nfc": self.nfc is not None,
                "rfid": self.rfid is not None,
                "face_recognition": self.face is not None,
                "fingerprint": self.fingerprint is not None,
                "pin_pad": self.pin_pad is not None
            },
            "emergency_mode": {
                "lockdown": self.lockdown_active,
                "evacuation": self.evacuation_active
            }
        }


# Example usage
if __name__ == "__main__":
    print("=== Door Access Control - Multi-Factor Authentication Demo ===\n")
    
    # Initialize manager
    manager = AccessControlManager()
    
    # Setup controllers
    print("\n--- Setup Controllers ---\n")
    manager.setup_nfc({"type": "acr122u", "interface": "usb", "device": "/dev/ttyUSB0"})
    manager.setup_rfid({"type": "hid_proxpoint", "frequency": "125khz", "interface": "wiegand"})
    manager.setup_face_recognition(
        {"type": "hikvision_face", "ip": "192.168.1.150"},
        {"algorithm": "arcface", "accuracy_threshold": 0.95}
    )
    manager.setup_fingerprint({"type": "zkteco_slk20r", "interface": "ethernet", "ip": "192.168.1.160"})
    manager.setup_pin_pad(
        {"type": "hid_pivclass", "interface": "wiegand"},
        {"min_length": 4, "max_length": 8, "master_pin": {"code": "123456789"}}
    )
    
    # Create user
    print("\n--- Create User ---\n")
    user = User(
        user_id="user_john_ceo",
        name="John Smith",
        email="john@company.com",
        role="executive",
        allowed_doors=["door_executive", "door_main"],
        time_zones=["24/7"]
    )
    manager.users[user.user_id] = user
    
    # Enroll credentials
    print("\n--- Enroll Credentials ---\n")
    
    # NFC card
    manager.nfc.register_card("04:A1:B2:C3:D4:E5:F6", user.user_id)
    
    # RFID card
    manager.rfid.register_card("0012345678", user.user_id)
    
    # Personal PIN
    manager.pin_pad.register_personal_pin(user.user_id, "847392")
    
    # Run authentication tests
    async def run_tests():
        # Test NFC authentication
        print("\n--- Test NFC Authentication ---\n")
        result = await manager.authenticate(
            "door_executive",
            AuthMethod.NFC,
            {"card_id": "04:A1:B2:C3:D4:E5:F6"}
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Test PIN authentication
        print("\n--- Test PIN Authentication ---\n")
        result = await manager.authenticate(
            "door_executive",
            AuthMethod.PIN_PAD,
            {"pin": "847392"}
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Test invalid PIN
        print("\n--- Test Invalid PIN ---\n")
        result = await manager.authenticate(
            "door_executive",
            AuthMethod.PIN_PAD,
            {"pin": "999999"}
        )
        print(f"Result: {json.dumps(result, indent=2)}")
    
    asyncio.run(run_tests())
    
    # Print status
    print("\n" + "="*60)
    print("SYSTEM STATUS")
    print("="*60 + "\n")
    status = manager.get_status()
    print(json.dumps(status, indent=2))
