"""
KNX Smart Home Integration
Bidirectional communication with KNX bus for building automation
"""

from typing import Dict, Optional, Any, List, Callable
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)

# Try to import XKNX (optional dependency)
try:
    from xknx import XKNX
    from xknx.devices import Switch, Light, Sensor, Climate
    from xknx.telegram import GroupAddress
    KNX_AVAILABLE = True
except ImportError:
    KNX_AVAILABLE = False
    logger.warning("xknx not installed. KNX integration will not be available.")
    logger.warning("Install with: pip install xknx")


class KNXDataType(Enum):
    """KNX data point types"""
    BINARY = "1bit"  # On/Off, True/False
    PERCENT = "1byte_percent"  # 0-100%
    VALUE = "1byte"  # 0-255
    FLOAT = "2byte_float"  # Temperature, etc.
    STRING = "string"  # Text


class KNXMediaControl:
    """
    KNX integration for MediaControl
    Maps MediaControl actions to KNX group addresses
    """
    
    def __init__(
        self,
        gateway_ip: str,
        gateway_port: int = 3671,
        local_ip: Optional[str] = None,
    ):
        if not KNX_AVAILABLE:
            raise RuntimeError("xknx library not installed. Cannot create KNXMediaControl.")
        
        self.gateway_ip = gateway_ip
        self.gateway_port = gateway_port
        self.local_ip = local_ip
        
        # Initialize XKNX
        self.xknx = XKNX()
        
        # Device mappings
        self.devices: Dict[str, Any] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        
        logger.info(f"KNXMediaControl initialized (gateway: {gateway_ip})")
    
    async def start(self):
        """Start KNX connection"""
        await self.xknx.start()
        logger.info("KNX connection started")
    
    async def stop(self):
        """Stop KNX connection"""
        await self.xknx.stop()
        logger.info("KNX connection stopped")
    
    def register_display_power(
        self,
        display_id: str,
        group_address: str,
        on_change: Optional[Callable] = None,
    ):
        """
        Register display power control
        
        Args:
            display_id: MediaControl display ID
            group_address: KNX group address (e.g., "1/1/1")
            on_change: Callback when KNX sends power command
        """
        device = Switch(
            self.xknx,
            name=f"{display_id}_power",
            group_address=group_address,
        )
        
        self.devices[f"{display_id}_power"] = device
        
        if on_change:
            device.register_device_updated_cb(
                lambda dev: on_change(display_id, dev.state)
            )
        
        logger.info(f"Registered display power: {display_id} @ {group_address}")
    
    def register_display_volume(
        self,
        display_id: str,
        group_address: str,
        on_change: Optional[Callable] = None,
    ):
        """Register display volume control (0-100%)"""
        device = Light(
            self.xknx,
            name=f"{display_id}_volume",
            group_address_brightness=group_address,
        )
        
        self.devices[f"{display_id}_volume"] = device
        
        if on_change:
            device.register_device_updated_cb(
                lambda dev: on_change(display_id, dev.current_brightness)
            )
        
        logger.info(f"Registered display volume: {display_id} @ {group_address}")
    
    def register_input_selector(
        self,
        display_id: str,
        group_address: str,
        on_change: Optional[Callable] = None,
    ):
        """
        Register input selector (1 byte = input number)
        
        Input mapping:
        1 = HDMI 1
        2 = HDMI 2
        3 = HDMI 3
        4 = HDMI 4
        5 = DisplayPort
        6 = USB-C
        """
        device = Sensor(
            self.xknx,
            name=f"{display_id}_input",
            group_address_state=group_address,
            value_type="1byte",
        )
        
        self.devices[f"{display_id}_input"] = device
        
        if on_change:
            device.register_device_updated_cb(
                lambda dev: on_change(display_id, dev.resolve_state())
            )
        
        logger.info(f"Registered input selector: {display_id} @ {group_address}")
    
    def register_source_selector(
        self,
        group_address: str,
        sources: Dict[int, str],  # value → source_id mapping
        on_change: Optional[Callable] = None,
    ):
        """
        Register source selector
        
        Args:
            group_address: KNX address
            sources: Mapping of KNX values to source IDs
                     e.g., {1: "stb", 2: "apple-tv", 3: "android-stick"}
            on_change: Callback(source_id)
        """
        device = Sensor(
            self.xknx,
            name="source_selector",
            group_address_state=group_address,
            value_type="1byte",
        )
        
        self.devices["source_selector"] = device
        
        if on_change:
            def handle_change(dev):
                value = dev.resolve_state()
                source_id = sources.get(value)
                if source_id:
                    on_change(source_id)
            
            device.register_device_updated_cb(handle_change)
        
        logger.info(f"Registered source selector @ {group_address}")
    
    def register_scene_trigger(
        self,
        group_address: str,
        scenes: Dict[int, str],  # value → scene_name mapping
        on_trigger: Optional[Callable] = None,
    ):
        """
        Register scene trigger
        
        Args:
            group_address: KNX address
            scenes: Mapping of KNX values to scene names
                    e.g., {1: "cinema", 2: "tv", 3: "presentation"}
            on_trigger: Callback(scene_name)
        """
        device = Sensor(
            self.xknx,
            name="scene_trigger",
            group_address_state=group_address,
            value_type="1byte",
        )
        
        self.devices["scene_trigger"] = device
        
        if on_trigger:
            def handle_trigger(dev):
                value = dev.resolve_state()
                scene_name = scenes.get(value)
                if scene_name:
                    on_trigger(scene_name)
            
            device.register_device_updated_cb(handle_trigger)
        
        logger.info(f"Registered scene trigger @ {group_address}")
    
    async def send_display_power(self, display_id: str, state: bool):
        """Send display power state to KNX"""
        device_key = f"{display_id}_power"
        if device_key in self.devices:
            device = self.devices[device_key]
            if state:
                await device.set_on()
            else:
                await device.set_off()
            logger.info(f"Sent display power to KNX: {display_id} = {state}")
    
    async def send_display_volume(self, display_id: str, volume: int):
        """Send display volume to KNX (0-100)"""
        device_key = f"{display_id}_volume"
        if device_key in self.devices:
            device = self.devices[device_key]
            await device.set_brightness(volume)
            logger.info(f"Sent display volume to KNX: {display_id} = {volume}%")
    
    async def send_input_selector(self, display_id: str, input_num: int):
        """Send input selection to KNX"""
        device_key = f"{display_id}_input"
        if device_key in self.devices:
            device = self.devices[device_key]
            # Send raw value to KNX
            await self.xknx.telegrams.put(
                device.remote_value.to_knx(input_num)
            )
            logger.info(f"Sent input selector to KNX: {display_id} = {input_num}")


class KNXSceneManager:
    """
    Manages KNX scene integration
    Maps KNX scenes to MediaControl presets
    """
    
    def __init__(self, knx: KNXMediaControl, preset_manager):
        self.knx = knx
        self.preset_manager = preset_manager
        
        # Scene mappings
        self.scenes: Dict[str, str] = {}  # scene_name → preset_name
        
        logger.info("KNXSceneManager initialized")
    
    def map_scene_to_preset(self, scene_name: str, preset_name: str):
        """Map a KNX scene to a MediaControl preset"""
        self.scenes[scene_name] = preset_name
        logger.info(f"Mapped KNX scene '{scene_name}' → preset '{preset_name}'")
    
    async def handle_scene_trigger(self, scene_name: str):
        """Handle KNX scene trigger"""
        preset_name = self.scenes.get(scene_name)
        if not preset_name:
            logger.warning(f"No preset mapped for scene '{scene_name}'")
            return
        
        logger.info(f"KNX scene '{scene_name}' triggered → activating preset '{preset_name}'")
        
        # Activate MediaControl preset
        # This would call the InputRouter.activate_preset()
        success = self.preset_manager.activate_preset(preset_name)
        
        if success:
            logger.info(f"Preset '{preset_name}' activated successfully")
        else:
            logger.error(f"Failed to activate preset '{preset_name}'")


# Configuration example
KNX_CONFIG_EXAMPLE = """
# knx_config.yaml
knx:
  gateway:
    ip: "192.168.1.100"
    port: 3671
  
  # Display mappings
  displays:
    - id: "display-1"
      name: "Main Display"
      power:
        group_address: "1/1/1"  # DPT 1.001 (on/off)
      volume:
        group_address: "1/1/2"  # DPT 5.001 (0-100%)
      input:
        group_address: "1/1/3"  # DPT 5.010 (0-255)
    
    - id: "display-2"
      name: "Side Display"
      power:
        group_address: "1/2/1"
      volume:
        group_address: "1/2/2"
      input:
        group_address: "1/2/3"
  
  # Source selector
  source_selector:
    group_address: "1/3/1"  # DPT 5.010
    mapping:
      1: "stb-airtel"
      2: "apple-tv"
      3: "android-stick"
  
  # Scene triggers
  scenes:
    group_address: "1/4/1"  # DPT 5.010
    mapping:
      1:
        name: "cinema"
        preset: "Netflix"
      2:
        name: "tv"
        preset: "Star Plus"
      3:
        name: "presentation"
        preset: "All Displays - Apple TV"
      4:
        name: "off"
        action: "power_off_all"

# KNX Group Address Structure (recommended):
# 
# Main Group 1: MediaControl
#   Middle Group 1: Display 1
#     1/1/1: Power (Switch)
#     1/1/2: Volume (Dimmer)
#     1/1/3: Input Select (1 byte)
#   Middle Group 2: Display 2
#     1/2/1: Power
#     1/2/2: Volume
#     1/2/3: Input Select
#   Middle Group 3: Sources
#     1/3/1: Source Selector
#   Middle Group 4: Scenes
#     1/4/1: Scene Trigger
"""


# Example integration with InputRouter
INTEGRATION_EXAMPLE = """
# main.py
import asyncio
from knx_integration import KNXMediaControl, KNXSceneManager
from input_router import InputRouter
from device_abstraction import SourceManager, ContextManager

async def main():
    # Initialize MediaControl components
    source_manager = SourceManager()
    context_manager = ContextManager()
    displays = {...}  # Your displays
    
    input_router = InputRouter(source_manager, context_manager, displays)
    
    # Initialize KNX
    knx = KNXMediaControl(gateway_ip="192.168.1.100")
    
    # Register display controls
    knx.register_display_power(
        display_id="display-1",
        group_address="1/1/1",
        on_change=lambda display_id, state: 
            input_router.set_display_power(display_id, state)
    )
    
    knx.register_input_selector(
        display_id="display-1",
        group_address="1/1/3",
        on_change=lambda display_id, input_num:
            input_router.set_display_input(display_id, input_num)
    )
    
    # Register scene triggers
    scene_manager = KNXSceneManager(knx, input_router)
    scene_manager.map_scene_to_preset("cinema", "Netflix")
    scene_manager.map_scene_to_preset("tv", "Star Plus")
    scene_manager.map_scene_to_preset("presentation", "All Displays - Apple TV")
    
    knx.register_scene_trigger(
        group_address="1/4/1",
        scenes={1: "cinema", 2: "tv", 3: "presentation"},
        on_trigger=scene_manager.handle_scene_trigger
    )
    
    # Start KNX
    await knx.start()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await knx.stop()

if __name__ == "__main__":
    asyncio.run(main())
"""
