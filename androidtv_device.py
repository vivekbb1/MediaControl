"""
Android TV Device Implementation
Uses ADB (Android Debug Bridge) over network for control
"""

from typing import Dict, Optional, Any, List
import logging
import subprocess
import time
from device_abstraction import (
    SourceDevice, DeviceType, DeviceState, DeviceCapabilities,
    DeviceConnection, HDMIConnection, App
)

logger = logging.getLogger(__name__)


class AndroidTVDevice(SourceDevice):
    """
    Android TV / Fire TV controlled via ADB over network
    Requires: adb command-line tool or pure-python-adb library
    """
    
    def __init__(
        self,
        device_id: str,
        name: str,
        connection: DeviceConnection,
        hdmi_connection: Optional[HDMIConnection] = None,
        apps: Optional[List[App]] = None,
        use_fire_tv_defaults: bool = False,
    ):
        capabilities = DeviceCapabilities(
            power_control=True,
            navigation=True,
            app_launching=True,
            transport_control=True,
            status_query=True,
            text_input=True,
        )
        
        device_type = DeviceType.FIRE_TV if use_fire_tv_defaults else DeviceType.ANDROID_TV
        
        super().__init__(
            device_id=device_id,
            device_type=device_type,
            name=name,
            connection=connection,
            hdmi_connection=hdmi_connection,
            capabilities=capabilities,
            apps=apps or self._default_apps(use_fire_tv_defaults),
        )
        
        self._adb_address = f"{connection.ip}:{connection.port or 5555}"
        self._connected = False
    
    @staticmethod
    def _default_apps(fire_tv: bool = False) -> List[App]:
        """Default Android TV / Fire TV apps"""
        if fire_tv:
            return [
                App(id="com.netflix.ninja/.MainActivity", name="Netflix", icon="netflix", category="streaming"),
                App(id="com.amazon.avod/.client.android.app.HomeActivity", name="Prime Video", icon="prime", category="streaming"),
                App(id="com.disney.disneyplus/.StartActivity", name="Disney+", icon="disney", category="streaming"),
                App(id="com.google.android.youtube.tv/.activity.ShellActivity", name="YouTube", icon="youtube", category="streaming"),
                App(id="com.plexapp.android/.features.splash.SplashActivity", name="Plex", icon="plex", category="streaming"),
            ]
        else:
            return [
                App(id="com.netflix.ninja/.MainActivity", name="Netflix", icon="netflix", category="streaming"),
                App(id="com.amazon.amazonvideo.livingroom/.startup.StartupActivity", name="Prime Video", icon="prime", category="streaming"),
                App(id="com.disney.disneyplus/.StartActivity", name="Disney+", icon="disney", category="streaming"),
                App(id="com.google.android.youtube.tv/.activity.ShellActivity", name="YouTube", icon="youtube", category="streaming"),
                App(id="com.hotstar.streaming/.MainActivity", name="Hotstar", icon="hotstar", category="streaming"),
                App(id="tv.zee5/.MainActivity", name="Zee5", icon="zee5", category="streaming"),
                App(id="com.sonyliv/.MainActivity", name="SonyLIV", icon="sonyliv", category="streaming"),
                App(id="com.spotify.tv.android/.SpotifyTVActivity", name="Spotify", icon="spotify", category="music"),
            ]
    
    def _run_adb(self, command: List[str], timeout: int = 5) -> tuple[bool, str]:
        """
        Run ADB command and return (success, output)
        """
        try:
            full_cmd = ["adb", "-s", self._adb_address] + command
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            success = result.returncode == 0
            output = result.stdout.strip() if success else result.stderr.strip()
            return (success, output)
        except subprocess.TimeoutExpired:
            logger.error(f"{self.name}: ADB command timed out")
            return (False, "timeout")
        except FileNotFoundError:
            logger.error(f"{self.name}: adb command not found. Install Android SDK Platform Tools.")
            return (False, "adb not found")
        except Exception as e:
            logger.error(f"{self.name}: ADB error: {e}")
            return (False, str(e))
    
    def connect(self) -> bool:
        """Connect to Android TV via ADB"""
        if not self.connection.ip:
            logger.error(f"{self.name}: No IP address configured")
            return False
        
        # Try to connect
        success, output = self._run_adb(["connect", self._adb_address])
        if not success:
            logger.error(f"{self.name}: ADB connect failed: {output}")
            return False
        
        # Verify connection
        time.sleep(1)
        success, output = self._run_adb(["shell", "echo", "test"])
        if success and output == "test":
            self._connected = True
            self._state = DeviceState.ON  # If we can connect, it's on
            logger.info(f"{self.name}: Connected via ADB to {self._adb_address}")
            return True
        else:
            logger.error(f"{self.name}: ADB connection verification failed")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Android TV"""
        if self._connected:
            self._run_adb(["disconnect", self._adb_address])
        self._connected = False
        return True
    
    def power_on(self) -> bool:
        """Wake Android TV"""
        if not self._connected:
            return False
        
        # Send KEYCODE_WAKEUP
        success, _ = self._run_adb(["shell", "input", "keyevent", "KEYCODE_WAKEUP"])
        if success:
            self._state = DeviceState.ON
            logger.info(f"{self.name}: Powered on")
        return success
    
    def power_off(self) -> bool:
        """Sleep Android TV"""
        if not self._connected:
            return False
        
        # Send KEYCODE_SLEEP
        success, _ = self._run_adb(["shell", "input", "keyevent", "KEYCODE_SLEEP"])
        if success:
            self._state = DeviceState.STANDBY
            logger.info(f"{self.name}: Powered off (sleep)")
        return success
    
    def send_command(self, command: str, params: Optional[Dict] = None) -> bool:
        """Send remote control command"""
        if not self._connected:
            return False
        
        # Map commands to Android keycodes
        keycode_map = {
            "up": "KEYCODE_DPAD_UP",
            "down": "KEYCODE_DPAD_DOWN",
            "left": "KEYCODE_DPAD_LEFT",
            "right": "KEYCODE_DPAD_RIGHT",
            "select": "KEYCODE_DPAD_CENTER",
            "ok": "KEYCODE_DPAD_CENTER",
            "back": "KEYCODE_BACK",
            "home": "KEYCODE_HOME",
            "menu": "KEYCODE_MENU",
            "play": "KEYCODE_MEDIA_PLAY",
            "pause": "KEYCODE_MEDIA_PAUSE",
            "play_pause": "KEYCODE_MEDIA_PLAY_PAUSE",
            "stop": "KEYCODE_MEDIA_STOP",
            "next": "KEYCODE_MEDIA_NEXT",
            "previous": "KEYCODE_MEDIA_PREVIOUS",
            "rewind": "KEYCODE_MEDIA_REWIND",
            "fast_forward": "KEYCODE_MEDIA_FAST_FORWARD",
            "volume_up": "KEYCODE_VOLUME_UP",
            "volume_down": "KEYCODE_VOLUME_DOWN",
            "mute": "KEYCODE_VOLUME_MUTE",
        }
        
        keycode = keycode_map.get(command)
        if not keycode:
            logger.warning(f"{self.name}: Unknown command '{command}'")
            return False
        
        success, _ = self._run_adb(["shell", "input", "keyevent", keycode])
        if success:
            logger.info(f"{self.name}: Sent command '{command}' (keycode: {keycode})")
        return success
    
    def launch_app(self, app_id: str) -> bool:
        """
        Launch an app by package/activity name.
        app_id should be in format: "package/.ActivityName"
        or just "package" to launch default activity
        """
        if not self._connected:
            return False
        
        try:
            # Parse package and activity
            if "/" in app_id:
                package, activity = app_id.rsplit("/", 1)
                component = f"{package}/{activity}"
            else:
                # Launch default activity
                package = app_id
                component = None
            
            # Stop app first (optional, ensures clean start)
            self._run_adb(["shell", "am", "force-stop", package])
            time.sleep(0.5)
            
            # Launch app
            if component:
                cmd = ["shell", "am", "start", "-n", component]
            else:
                cmd = ["shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"]
            
            success, output = self._run_adb(cmd)
            if success:
                self._current_app = app_id
                logger.info(f"{self.name}: Launched app '{app_id}'")
                return True
            else:
                logger.error(f"{self.name}: Failed to launch app '{app_id}': {output}")
                return False
                
        except Exception as e:
            logger.error(f"{self.name}: App launch error: {e}")
            return False
    
    def send_text(self, text: str) -> bool:
        """Send text input to Android TV"""
        if not self._connected:
            return False
        
        # Escape text for shell
        escaped = text.replace(" ", "%s").replace("'", "")
        success, _ = self._run_adb(["shell", "input", "text", escaped])
        if success:
            logger.info(f"{self.name}: Sent text input")
        return success
    
    def get_current_app(self) -> Optional[str]:
        """Get currently running app package"""
        if not self._connected:
            return None
        
        success, output = self._run_adb([
            "shell",
            "dumpsys",
            "window",
            "windows",
            "|",
            "grep",
            "-E",
            "'mCurrentFocus|mFocusedApp'"
        ])
        
        if success and output:
            # Parse package name from output
            # Format: mCurrentFocus=Window{... u0 package/activity}
            import re
            match = re.search(r'([a-z0-9.]+)/([a-zA-Z0-9.]+)', output)
            if match:
                self._current_app = f"{match.group(1)}/{match.group(2)}"
                return self._current_app
        
        return None
    
    def get_installed_packages(self) -> List[str]:
        """Get list of installed packages"""
        if not self._connected:
            return []
        
        success, output = self._run_adb(["shell", "pm", "list", "packages"])
        if success:
            # Output format: package:com.example.app
            packages = [
                line.replace("package:", "")
                for line in output.split("\n")
                if line.startswith("package:")
            ]
            return packages
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize Android TV device"""
        base = super().to_dict()
        base.update({
            "adb_address": self._adb_address,
        })
        return base


def setup_android_tv_instructions():
    """
    Print instructions for setting up Android TV for ADB control
    """
    print("""
=== Android TV / Fire TV Setup for ADB Control ===

1. ENABLE DEVELOPER OPTIONS:
   - Go to Settings → About
   - Find "Build Number" (may be under "Android TV OS Build")
   - Click "Build Number" 7 times
   - You should see "You are now a developer"

2. ENABLE USB DEBUGGING:
   - Go to Settings → Device Preferences → Developer Options
   - Enable "USB Debugging"
   - Enable "Network Debugging" (if available)

3. ENABLE ADB OVER NETWORK:
   - On Android TV, go to Settings → Developer Options
   - Find "Network debugging" and enable it
   - Note the IP address (Settings → Network & Internet → Your WiFi → Advanced)

4. CONNECT FROM YOUR COMPUTER:
   - Install Android SDK Platform Tools (includes adb)
   - Run: adb connect <ANDROID_TV_IP>:5555
   - Confirm connection on TV screen (first time only)
   - Test: adb -s <ANDROID_TV_IP>:5555 shell echo test

5. FIND APP PACKAGE NAMES:
   - List all: adb shell pm list packages
   - Find specific: adb shell pm list packages | grep netflix
   - Get main activity: adb shell dumpsys package <package> | grep -i activity

=== COMMON APP PACKAGE/ACTIVITY NAMES ===

Netflix: com.netflix.ninja/.MainActivity
Prime Video: com.amazon.avod/.client.android.app.HomeActivity
Disney+: com.disney.disneyplus/.StartActivity
YouTube: com.google.android.youtube.tv/.activity.ShellActivity
Hotstar: com.hotstar.streaming/.MainActivity
Zee5: tv.zee5/.MainActivity
SonyLIV: com.sonyliv/.MainActivity
Spotify: com.spotify.tv.android/.SpotifyTVActivity

=== TROUBLESHOOTING ===

- If "adb: command not found": Install Android SDK Platform Tools
- If connection refused: Check USB Debugging is enabled
- If unauthorized: Check TV screen for authorization prompt
- If app won't launch: Try "adb shell pm list packages" to find correct name
""")
