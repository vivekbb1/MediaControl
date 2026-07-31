"""
Input Router
Maps source devices to display inputs and handles automatic switching
"""

from typing import Dict, Optional, Any, List
import logging
import time
from dataclasses import dataclass
from device_abstraction import SourceDevice, SourceManager, ContextManager

logger = logging.getLogger(__name__)


@dataclass
class SourcePreset:
    """
    A preset configuration for quick source switching
    Example: "Netflix" → launches Netflix on Apple TV on Display 1
    """
    name: str
    source_id: str
    display_ids: List[str]
    action: Dict[str, Any]  # {type: "launch_app", app_id: "..."}
    icon: Optional[str] = None
    category: Optional[str] = None


class InputRouter:
    """
    Manages routing of source devices to display inputs.
    Handles automatic input switching when source is selected.
    """
    
    def __init__(
        self,
        source_manager: SourceManager,
        context_manager: ContextManager,
        displays: Dict[str, Any],  # display_id → display controller
    ):
        self.source_manager = source_manager
        self.context_manager = context_manager
        self.displays = displays
        self.presets: Dict[str, SourcePreset] = {}
        logger.info("InputRouter initialized")
    
    def add_preset(self, preset: SourcePreset):
        """Register a source preset"""
        self.presets[preset.name] = preset
        logger.info(f"Added preset: {preset.name}")
    
    def get_preset(self, name: str) -> Optional[SourcePreset]:
        """Get preset by name"""
        return self.presets.get(name)
    
    def get_all_presets(self) -> Dict[str, SourcePreset]:
        """Get all presets"""
        return self.presets
    
    def switch_to_source(
        self,
        source_id: str,
        display_id: str,
        auto_power_on: bool = True,
    ) -> bool:
        """
        Switch a display to a specific source device.
        
        Steps:
        1. Get source device and its HDMI connection
        2. Switch display to correct HDMI input
        3. Optionally power on source device
        4. Update context (active source)
        
        Args:
            source_id: ID of source device
            display_id: ID of display to switch
            auto_power_on: Whether to power on source device
            
        Returns:
            True if successful
        """
        # Get source device
        source = self.source_manager.get_device(source_id)
        if not source:
            logger.error(f"Source device not found: {source_id}")
            return False
        
        # Get display controller
        display = self.displays.get(display_id)
        if not display:
            logger.error(f"Display not found: {display_id}")
            return False
        
        # Check HDMI connection
        if not source.hdmi_connection:
            logger.error(f"Source {source.name} has no HDMI connection configured")
            return False
        
        if source.hdmi_connection.display_id != display_id:
            logger.error(
                f"Source {source.name} not connected to display {display_id}"
                f" (connected to {source.hdmi_connection.display_id})"
            )
            return False
        
        try:
            # Step 1: Power on source if requested
            if auto_power_on and source.capabilities.power_control:
                logger.info(f"Powering on {source.name}...")
                source.power_on()
                time.sleep(1)  # Give device time to wake
            
            # Step 2: Switch display input
            input_port = source.hdmi_connection.input_port
            logger.info(f"Switching display {display_id} to {input_port}...")
            
            # Convert input_port name to MDC input code
            input_map = {
                "hdmi1": 0x21,
                "hdmi2": 0x23,
                "hdmi3": 0x31,
                "hdmi4": 0x33,
                "displayport": 0x25,
                "usb-c": 0x1F,
            }
            
            input_code = input_map.get(input_port.lower())
            if input_code:
                # Assuming display has a send_command method
                if hasattr(display, 'send_command'):
                    display.send_command('set_input', {'input': input_code})
                elif hasattr(display, 'set_input'):
                    display.set_input(input_code)
                else:
                    logger.warning(f"Display {display_id} has no input switching method")
            
            # Step 3: Update context
            self.context_manager.set_active_source(display_id, source_id)
            
            logger.info(f"✓ Switched display {display_id} to source {source.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch to source: {e}")
            return False
    
    def activate_preset(self, preset_name: str) -> bool:
        """
        Activate a source preset.
        
        Handles complex scenarios like:
        - Launching Netflix on Apple TV
        - Tuning to specific channel on STB
        - Switching multiple displays to same source
        
        Args:
            preset_name: Name of preset to activate
            
        Returns:
            True if successful
        """
        preset = self.get_preset(preset_name)
        if not preset:
            logger.error(f"Preset not found: {preset_name}")
            return False
        
        source = self.source_manager.get_device(preset.source_id)
        if not source:
            logger.error(f"Source device not found: {preset.source_id}")
            return False
        
        try:
            logger.info(f"Activating preset: {preset_name}")
            
            # Switch all target displays to this source
            for display_id in preset.display_ids:
                success = self.switch_to_source(
                    preset.source_id,
                    display_id,
                    auto_power_on=True,
                )
                if not success:
                    logger.warning(f"Failed to switch display {display_id}")
                    continue
                
                time.sleep(0.5)  # Brief delay between display switches
            
            # Execute preset action
            action_type = preset.action.get("type")
            
            if action_type == "launch_app":
                app_id = preset.action.get("app_id")
                if not app_id:
                    logger.error(f"Preset {preset_name}: No app_id specified")
                    return False
                
                if not source.capabilities.app_launching:
                    logger.error(f"Source {source.name} does not support app launching")
                    return False
                
                logger.info(f"Launching app {app_id} on {source.name}...")
                time.sleep(2)  # Wait for source to be ready
                success = source.launch_app(app_id)
                
                if success:
                    logger.info(f"✓ Preset '{preset_name}' activated successfully")
                    return True
                else:
                    logger.error(f"Failed to launch app {app_id}")
                    return False
            
            elif action_type == "tune_channel":
                channel = preset.action.get("channel")
                if channel is None:
                    logger.error(f"Preset {preset_name}: No channel specified")
                    return False
                
                if not source.capabilities.channel_tuning:
                    logger.error(f"Source {source.name} does not support channel tuning")
                    return False
                
                # Import STBDevice to access tune_channel
                from stb_device import STBDevice
                if isinstance(source, STBDevice):
                    logger.info(f"Tuning to channel {channel} on {source.name}...")
                    time.sleep(1)
                    success = source.tune_channel(channel)
                    
                    if success:
                        logger.info(f"✓ Preset '{preset_name}' activated successfully")
                        return True
                    else:
                        logger.error(f"Failed to tune to channel {channel}")
                        return False
            
            elif action_type == "send_command":
                command = preset.action.get("command")
                params = preset.action.get("params", {})
                if not command:
                    logger.error(f"Preset {preset_name}: No command specified")
                    return False
                
                logger.info(f"Sending command {command} to {source.name}...")
                time.sleep(1)
                success = source.send_command(command, params)
                
                if success:
                    logger.info(f"✓ Preset '{preset_name}' activated successfully")
                    return True
                else:
                    logger.error(f"Failed to send command {command}")
                    return False
            
            else:
                logger.warning(f"Unknown action type: {action_type}")
                # Still count as success if we switched inputs
                return True
        
        except Exception as e:
            logger.error(f"Failed to activate preset '{preset_name}': {e}")
            return False
    
    def route_command_to_active_source(
        self,
        display_id: str,
        command: str,
        params: Optional[Dict] = None,
    ) -> bool:
        """
        Route a command (e.g., D-pad navigation) to the currently active source
        for a given display.
        
        This enables contextual control:
        - If Apple TV is active, D-pad controls Apple TV
        - If STB is active, D-pad controls STB
        
        Args:
            display_id: Which display the command is for
            command: Command to send (up, down, select, etc.)
            params: Optional command parameters
            
        Returns:
            True if command was sent successfully
        """
        # Get active source for this display
        source_id = self.context_manager.get_active_source(display_id)
        if not source_id:
            logger.warning(f"No active source for display {display_id}")
            return False
        
        # Get source device
        source = self.source_manager.get_device(source_id)
        if not source:
            logger.error(f"Active source not found: {source_id}")
            return False
        
        # Check if source supports navigation
        if command in ["up", "down", "left", "right", "select", "ok"] and \
           not source.capabilities.navigation:
            logger.warning(f"Source {source.name} does not support navigation")
            return False
        
        # Send command to source
        logger.info(f"Routing '{command}' to {source.name} (active on {display_id})")
        return source.send_command(command, params)
    
    def get_routing_status(self) -> Dict[str, Any]:
        """Get current routing status for all displays"""
        status = {}
        
        for display_id in self.displays.keys():
            active_source_id = self.context_manager.get_active_source(display_id)
            
            if active_source_id:
                source = self.source_manager.get_device(active_source_id)
                status[display_id] = {
                    "active_source_id": active_source_id,
                    "active_source_name": source.name if source else "Unknown",
                    "active_source_type": source.type.value if source else None,
                    "current_app": source.get_current_app() if source else None,
                }
            else:
                status[display_id] = {
                    "active_source_id": None,
                    "active_source_name": None,
                    "active_source_type": None,
                    "current_app": None,
                }
        
        return status
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize router state"""
        return {
            "presets": {
                name: {
                    "name": preset.name,
                    "source_id": preset.source_id,
                    "display_ids": preset.display_ids,
                    "action": preset.action,
                    "icon": preset.icon,
                    "category": preset.category,
                }
                for name, preset in self.presets.items()
            },
            "routing_status": self.get_routing_status(),
        }
