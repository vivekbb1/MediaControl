"""
Apple TV Device Implementation
Uses pyatv library for network-based control
"""

from typing import Dict, Optional, Any, List
import logging
import asyncio
from device_abstraction import (
    SourceDevice, DeviceType, DeviceState, DeviceCapabilities,
    DeviceConnection, HDMIConnection, App
)

logger = logging.getLogger(__name__)

# Try to import pyatv (optional dependency)
try:
    import pyatv
    from pyatv.const import DeviceState as PyATVState, Protocol
    PYATV_AVAILABLE = True
except ImportError:
    PYATV_AVAILABLE = False
    logger.warning("pyatv not installed. Apple TV control will not be available.")
    logger.warning("Install with: pip install pyatv")


class AppleTVDevice(SourceDevice):
    """
    Apple TV controlled via pyatv library (network protocol)
    """
    
    def __init__(
        self,
        device_id: str,
        name: str,
        connection: DeviceConnection,
        hdmi_connection: Optional[HDMIConnection] = None,
        apps: Optional[List[App]] = None,
    ):
        if not PYATV_AVAILABLE:
            raise RuntimeError("pyatv library not installed. Cannot create AppleTVDevice.")
        
        capabilities = DeviceCapabilities(
            power_control=True,
            navigation=True,
            app_launching=True,
            transport_control=True,
            status_query=True,
            text_input=True,
        )
        
        super().__init__(
            device_id=device_id,
            device_type=DeviceType.APPLE_TV,
            name=name,
            connection=connection,
            hdmi_connection=hdmi_connection,
            capabilities=capabilities,
            apps=apps or self._default_apps(),
        )
        
        self._atv = None
        self._loop = None
    
    @staticmethod
    def _default_apps() -> List[App]:
        """Default Apple TV apps"""
        return [
            App(id="com.netflix.Netflix", name="Netflix", icon="netflix", category="streaming"),
            App(id="com.amazon.aiv.AIVApp", name="Prime Video", icon="prime", category="streaming"),
            App(id="com.disney.disneyplus", name="Disney+", icon="disney", category="streaming"),
            App(id="com.apple.TVWatchList", name="Apple TV+", icon="appletv", category="streaming"),
            App(id="com.google.ios.youtube", name="YouTube", icon="youtube", category="streaming"),
            App(id="com.hulu.plus", name="Hulu", icon="hulu", category="streaming"),
            App(id="com.hbo.hbonow", name="HBO Max", icon="hbo", category="streaming"),
            App(id="com.spotify.client", name="Spotify", icon="spotify", category="music"),
            App(id="com.apple.TVMusic", name="Apple Music", icon="apple_music", category="music"),
        ]
    
    def _get_loop(self):
        """Get or create event loop"""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        loop = self._get_loop()
        if loop.is_running():
            # Already in async context
            return asyncio.ensure_future(coro)
        else:
            return loop.run_until_complete(coro)
    
    async def _discover_and_connect(self) -> bool:
        """Discover and connect to Apple TV"""
        try:
            ip = self.connection.ip
            if not ip:
                logger.error(f"{self.name}: No IP address configured")
                return False
            
            # Scan for Apple TVs at this IP
            atvs = await pyatv.scan(hosts=[ip], timeout=5)
            if not atvs:
                logger.error(f"{self.name}: No Apple TV found at {ip}")
                return False
            
            # Use first device found
            conf = atvs[0]
            
            # Load credentials if available
            if self.connection.credentials_file:
                try:
                    import json
                    with open(self.connection.credentials_file, 'r') as f:
                        creds = json.load(f)
                        for protocol, credentials in creds.items():
                            proto = Protocol[protocol.upper()]
                            conf.set_credentials(proto, credentials)
                except Exception as e:
                    logger.warning(f"{self.name}: Could not load credentials: {e}")
            
            # Connect
            self._atv = await pyatv.connect(conf, loop=self._loop)
            logger.info(f"{self.name}: Connected to Apple TV at {ip}")
            return True
            
        except Exception as e:
            logger.error(f"{self.name}: Connection error: {e}")
            return False
    
    def connect(self) -> bool:
        """Connect to Apple TV"""
        try:
            success = self._run_async(self._discover_and_connect())
            if success:
                self._connected = True
                self._update_state()
            return success
        except Exception as e:
            logger.error(f"{self.name}: Connect failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Apple TV"""
        if self._atv:
            try:
                self._atv.close()
            except Exception as e:
                logger.error(f"{self.name}: Disconnect error: {e}")
        self._atv = None
        self._connected = False
        return True
    
    def _update_state(self):
        """Update device state from Apple TV"""
        if not self._atv:
            self._state = DeviceState.UNKNOWN
            return
        
        try:
            power_state = self._atv.power.power_state
            if power_state == PyATVState.On:
                self._state = DeviceState.ON
            elif power_state == PyATVState.Off:
                self._state = DeviceState.OFF
            else:
                self._state = DeviceState.STANDBY
            
            # Get current app
            app_info = self._atv.metadata.app
            if app_info:
                self._current_app = app_info.identifier
        except Exception as e:
            logger.error(f"{self.name}: Failed to update state: {e}")
    
    def power_on(self) -> bool:
        """Turn Apple TV on"""
        if not self._connected or not self._atv:
            return False
        try:
            self._run_async(self._atv.power.turn_on())
            self._state = DeviceState.ON
            return True
        except Exception as e:
            logger.error(f"{self.name}: Power on failed: {e}")
            return False
    
    def power_off(self) -> bool:
        """Turn Apple TV off"""
        if not self._connected or not self._atv:
            return False
        try:
            self._run_async(self._atv.power.turn_off())
            self._state = DeviceState.OFF
            return True
        except Exception as e:
            logger.error(f"{self.name}: Power off failed: {e}")
            return False
    
    def send_command(self, command: str, params: Optional[Dict] = None) -> bool:
        """Send remote control command"""
        if not self._connected or not self._atv:
            return False
        
        remote = self._atv.remote_control
        
        try:
            # Map commands to pyatv methods
            command_map = {
                "up": remote.up,
                "down": remote.down,
                "left": remote.left,
                "right": remote.right,
                "select": remote.select,
                "menu": remote.menu,
                "home": remote.home,
                "play": remote.play,
                "pause": remote.pause,
                "play_pause": remote.play_pause,
                "stop": remote.stop,
                "next": remote.next,
                "previous": remote.previous,
                "volume_up": remote.volume_up,
                "volume_down": remote.volume_down,
            }
            
            if command in command_map:
                self._run_async(command_map[command]())
                logger.info(f"{self.name}: Sent command '{command}'")
                return True
            else:
                logger.warning(f"{self.name}: Unknown command '{command}'")
                return False
                
        except Exception as e:
            logger.error(f"{self.name}: Command failed: {e}")
            return False
    
    def launch_app(self, app_id: str) -> bool:
        """Launch an app by bundle ID"""
        if not self._connected or not self._atv:
            return False
        
        try:
            self._run_async(self._atv.apps.launch_app(app_id))
            self._current_app = app_id
            logger.info(f"{self.name}: Launched app '{app_id}'")
            return True
        except Exception as e:
            logger.error(f"{self.name}: Failed to launch app '{app_id}': {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize Apple TV device"""
        base = super().to_dict()
        if self._atv:
            try:
                base.update({
                    "device_info": {
                        "model": self._atv.device_info.model,
                        "os_version": self._atv.device_info.version,
                        "mac": self._atv.device_info.mac,
                    }
                })
            except:
                pass
        return base


async def pair_apple_tv(ip: str, output_file: str) -> bool:
    """
    Helper function to pair with Apple TV and save credentials.
    This is a one-time setup process.
    
    Args:
        ip: IP address of Apple TV
        output_file: Where to save credentials JSON
        
    Returns:
        True if pairing successful
    """
    if not PYATV_AVAILABLE:
        print("ERROR: pyatv not installed. Install with: pip install pyatv")
        return False
    
    try:
        print(f"Scanning for Apple TV at {ip}...")
        atvs = await pyatv.scan(hosts=[ip], timeout=5)
        if not atvs:
            print(f"ERROR: No Apple TV found at {ip}")
            return False
        
        conf = atvs[0]
        print(f"Found: {conf.name}")
        
        # Start pairing
        protocol = Protocol.Companion  # Use Companion protocol (most reliable)
        pairing = await pyatv.pair(conf, protocol, loop=asyncio.get_event_loop())
        
        await pairing.begin()
        print("\nPairing started. Check your Apple TV screen for a PIN.")
        pin = input("Enter PIN: ")
        
        pairing.pin(pin)
        await pairing.finish()
        
        if pairing.has_paired:
            credentials = conf.get_service(protocol).credentials
            print(f"\n✓ Pairing successful!")
            print(f"Credentials: {credentials}")
            
            # Save to file
            import json
            creds_dict = {protocol.name.lower(): credentials}
            with open(output_file, 'w') as f:
                json.dump(creds_dict, f, indent=2)
            print(f"✓ Credentials saved to {output_file}")
            return True
        else:
            print("ERROR: Pairing failed")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
