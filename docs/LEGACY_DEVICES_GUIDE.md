# LEGACY DEVICE INTEGRATION GUIDE

Complete guide for integrating analog/digital legacy devices via IR, RF, RS232, and TCP/IP

---

## Table of Contents
1. [Overview](#overview)
2. [Supported Device Types](#supported-device-types)
3. [Control Protocols](#control-protocols)
4. [Setup Instructions](#setup-instructions)
5. [Device Examples](#device-examples)
6. [Learning IR/RF Commands](#learning-irrf-commands)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Legacy Device Controller provides universal support for any analog or digital device, enabling complete versatility in your automation system. **No device limits** - add unlimited ACs, fans, switches, projectors, and more.

### Why Legacy Device Support?

- ✅ **Universal Compatibility** - Control any device (new or old)
- ✅ **No Device Limits** - Add unlimited devices per room
- ✅ **Multiple Protocols** - IR, RF, RS232, TCP/IP
- ✅ **Easy Learning** - Learn commands from existing remotes
- ✅ **Cost Effective** - Reuse existing equipment
- ✅ **Future Proof** - Never locked into specific brands

---

## Supported Device Types

### Climate Control
- ✅ **Air Conditioners** - Full control (power, mode, temp, fan, swing)
- ✅ **Fans** - Speed, oscillation, timer
- ✅ **Heaters** - Temperature, mode
- ✅ **Thermostats** - Temperature control

### Display & Projection
- ✅ **Projectors** - Power, input, settings
- ✅ **Projection Screens** - Up/down/stop
- ✅ **Document Cameras**
- ✅ **Legacy TVs** (non-smart TVs)

### Audio Equipment
- ✅ **Audio Amplifiers** - Volume, input, power
- ✅ **Audio Receivers** - Full control
- ✅ **CD/DVD Players**
- ✅ **Turntables** with IR control

### Lighting & Shading
- ✅ **IR-Controlled Lights**
- ✅ **Motorized Blinds/Curtains**
- ✅ **Dimmers** (IR/RF)
- ✅ **Scene Controllers**

### Power & Switches
- ✅ **Power Switches** - On/off control
- ✅ **Scene Switches**
- ✅ **RF Outlets** (433MHz)
- ✅ **Smart Plugs** (RF/IR)

### Professional AV Equipment
- ✅ **RS232 Matrix Switchers**
- ✅ **Video Scalers**
- ✅ **Conference Systems**
- ✅ **PTZ Cameras**
- ✅ **Audio DSP Processors**

### Any Other Device
- ✅ **Generic IR Devices**
- ✅ **Generic RF Devices (433MHz, 315MHz, etc.)**
- ✅ **RS232 Equipment**
- ✅ **TCP/IP Controlled Devices**

---

## Control Protocols

### 1. Infrared (IR)

**Hardware:** Broadlink RM4 Mini, RM4 Pro
**Range:** ~8 meters
**Best For:** TVs, ACs, fans, media players

```python
from legacy_devices import LegacyDeviceConfig, ControlProtocol

config = LegacyDeviceConfig(
    device_id="bedroom_ac",
    name="Bedroom AC",
    device_type=LegacyDeviceType.AIR_CONDITIONER,
    control_protocol=ControlProtocol.INFRARED,
    broadlink_device_ip="192.168.1.50",
    broadlink_device_mac="34:ea:34:12:34:56"
)
```

### 2. Radio Frequency (RF 433MHz/315MHz)

**Hardware:** Broadlink RM4 Pro (includes RF)
**Range:** ~30-100 meters (through walls)
**Best For:** RF switches, blinds, outlets, garage doors

```python
config = LegacyDeviceConfig(
    device_id="garage_door",
    name="Garage Door",
    device_type=LegacyDeviceType.GENERIC_RF,
    control_protocol=ControlProtocol.RADIO_FREQUENCY,
    broadlink_device_ip="192.168.1.50",
    broadlink_device_mac="34:ea:34:12:34:56"
)
```

### 3. RS232 (Serial Communication)

**Hardware:** USB-to-RS232 adapter
**Best For:** Projectors, professional AV equipment, matrix switchers

```python
config = LegacyDeviceConfig(
    device_id="conference_projector",
    name="Conference Projector",
    device_type=LegacyDeviceType.PROJECTOR,
    control_protocol=ControlProtocol.RS232,
    serial_port="/dev/ttyUSB0",
    baud_rate=9600,
    data_bits=8,
    stop_bits=1,
    parity="N"
)
```

### 4. TCP/IP (Network)

**Best For:** Network-enabled AV equipment

```python
config = LegacyDeviceConfig(
    device_id="audio_receiver",
    name="Yamaha RX-V6A",
    device_type=LegacyDeviceType.AUDIO_RECEIVER,
    control_protocol=ControlProtocol.TCP_IP,
    tcp_ip="192.168.1.100",
    tcp_port=50000
)
```

---

## Setup Instructions

### Hardware Requirements

| Protocol | Hardware Needed | Cost | Where to Buy |
|----------|----------------|------|--------------|
| **IR** | Broadlink RM4 Mini | ~$25 | Amazon, AliExpress |
| **RF** | Broadlink RM4 Pro | ~$35 | Amazon, AliExpress |
| **RS232** | USB-to-RS232 Adapter | ~$10 | Amazon |
| **TCP/IP** | Network Connection | Free | - |

### Software Setup

1. **Install Dependencies:**
```bash
pip install broadlink pyserial
```

2. **Initialize Controller:**
```python
from legacy_devices import LegacyDeviceController

controller = LegacyDeviceController()
```

3. **Register Devices:**
```python
controller.register_device(device_config)
```

4. **Control Devices:**
```python
controller.control_ac("bedroom_ac", power=True, temperature=24)
```

---

## Device Examples

### Example 1: Air Conditioner (IR Control)

```python
from legacy_devices import (
    LegacyDeviceController, LegacyDeviceConfig,
    LegacyDeviceType, ControlProtocol, ACMode, FanSpeed
)

controller = LegacyDeviceController()

# Configure AC
ac_config = LegacyDeviceConfig(
    device_id="bedroom_ac",
    name="Bedroom Daikin AC",
    device_type=LegacyDeviceType.AIR_CONDITIONER,
    control_protocol=ControlProtocol.INFRARED,
    broadlink_device_ip="192.168.1.50",
    broadlink_device_mac="34:ea:34:12:34:56",
    commands={
        "power_off": "2600500000012a94...",  # Learned IR code
        "cool_24_auto": "2600500000012a95...",
        "cool_22_high": "2600500000012a96...",
        "heat_26_auto": "2600500000012a97...",
    }
)

controller.register_device(ac_config)

# Turn on AC
controller.control_ac(
    device_id="bedroom_ac",
    power=True,
    mode=ACMode.COOL,
    temperature=24,
    fan_speed=FanSpeed.AUTO
)

# Turn off AC
controller.control_ac(device_id="bedroom_ac", power=False)
```

### Example 2: Ceiling Fan (IR Control)

```python
fan_config = LegacyDeviceConfig(
    device_id="living_room_fan",
    name="Living Room Fan",
    device_type=LegacyDeviceType.FAN,
    control_protocol=ControlProtocol.INFRARED,
    broadlink_device_ip="192.168.1.50",
    commands={
        "power_on": "2600300000012b10...",
        "power_off": "2600300000012b11...",
        "speed_1": "2600300000012b12...",
        "speed_2": "2600300000012b13...",
        "speed_3": "2600300000012b14...",
        "oscillation_on": "2600300000012b15...",
        "oscillation_off": "2600300000012b16...",
    }
)

controller.register_device(fan_config)

# Set fan to medium speed
controller.control_fan(
    device_id="living_room_fan",
    power=True,
    speed=FanSpeed.MEDIUM,
    oscillation=True
)
```

### Example 3: Projector (RS232 Control)

```python
projector_config = LegacyDeviceConfig(
    device_id="conference_projector",
    name="Epson EB-2250U",
    device_type=LegacyDeviceType.PROJECTOR,
    control_protocol=ControlProtocol.RS232,
    serial_port="/dev/ttyUSB0",
    baud_rate=9600,
    commands={
        "power_on": "PWR ON\\r",
        "power_off": "PWR OFF\\r",
        "input_hdmi1": "SOURCE 30\\r",
        "input_hdmi2": "SOURCE 31\\r",
        "input_vga": "SOURCE 11\\r",
        "blank_on": "MUTE ON\\r",
        "blank_off": "MUTE OFF\\r",
    }
)

controller.register_device(projector_config)

# Turn on projector and switch to HDMI 1
controller.control_projector(
    device_id="conference_projector",
    power=True,
    input_source="hdmi1"
)
```

### Example 4: Motorized Blinds (RF Control)

```python
blinds_config = LegacyDeviceConfig(
    device_id="bedroom_blinds",
    name="Bedroom Motorized Blinds",
    device_type=LegacyDeviceType.BLINDS,
    control_protocol=ControlProtocol.RADIO_FREQUENCY,
    broadlink_device_ip="192.168.1.50",
    commands={
        "open": "b200200000014c20...",    # RF 433MHz code
        "close": "b200200000014c21...",
        "stop": "b200200000014c22...",
        "partial_50": "b200200000014c23...",
    }
)

controller.register_device(blinds_config)

# Open blinds
controller.send_command("bedroom_blinds", "open")

# Close blinds
controller.send_command("bedroom_blinds", "close")
```

### Example 5: Audio Amplifier (TCP/IP Control)

```python
amp_config = LegacyDeviceConfig(
    device_id="living_room_amp",
    name="Yamaha RX-V6A",
    device_type=LegacyDeviceType.AUDIO_RECEIVER,
    control_protocol=ControlProtocol.TCP_IP,
    tcp_ip="192.168.1.100",
    tcp_port=50000,
    commands={
        "power_on": "PWON\\r\\n",
        "power_off": "PWSTANDBY\\r\\n",
        "volume_up": "VOLUP\\r\\n",
        "volume_down": "VOLDOWN\\r\\n",
        "volume_{level}": "VOL{level}\\r\\n",  # Parameterized
        "input_hdmi1": "SIHDMI1\\r\\n",
        "input_hdmi2": "SIHDMI2\\r\\n",
        "mute_on": "MUTEON\\r\\n",
        "mute_off": "MUTEOFF\\r\\n",
    }
)

controller.register_device(amp_config)

# Power on and select HDMI 1
controller.send_command("living_room_amp", "power_on")
controller.send_command("living_room_amp", "input_hdmi1")

# Set volume to 50
controller.send_command("living_room_amp", "volume_50", {"level": 50})
```

### Example 6: RF Power Switch

```python
switch_config = LegacyDeviceConfig(
    device_id="lamp_switch",
    name="Living Room Lamp",
    device_type=LegacyDeviceType.SWITCH,
    control_protocol=ControlProtocol.RADIO_FREQUENCY,
    broadlink_device_ip="192.168.1.50",
    commands={
        "on": "b200180000015a10...",
        "off": "b200180000015a11...",
    }
)

controller.register_device(switch_config)

# Turn lamp on
controller.control_switch("lamp_switch", True)

# Turn lamp off
controller.control_switch("lamp_switch", False)
```

---

## Learning IR/RF Commands

### Method 1: Learn from Existing Remote

```python
from legacy_devices import LegacyDeviceController

controller = LegacyDeviceController()

# Register device first (even with empty commands)
ac_config = LegacyDeviceConfig(
    device_id="bedroom_ac",
    name="Bedroom AC",
    device_type=LegacyDeviceType.AIR_CONDITIONER,
    control_protocol=ControlProtocol.INFRARED,
    broadlink_device_ip="192.168.1.50",
    commands={}  # Empty - will learn commands
)
controller.register_device(ac_config)

# Learn each command
print("Point remote at Broadlink and press POWER OFF button...")
hex_code = controller.learn_command("bedroom_ac", "power_off", timeout=10)
# Returns: "2600500000012a94..."

print("Point remote at Broadlink and press COOL 24°C button...")
hex_code = controller.learn_command("bedroom_ac", "cool_24_auto", timeout=10)
# Returns: "2600500000012a95..."

# Continue learning all needed commands...
```

### Method 2: Use Pre-Configured Templates

Many common devices have pre-configured IR codes available:
- Check manufacturer's IR code database
- Use community-shared IR codes (irmgr.com, remotecentral.com)
- Copy codes from existing Broadlink apps

```python
# Load pre-configured template
from legacy_devices import DEVICE_TEMPLATES

ac_config = LegacyDeviceConfig(
    device_id="bedroom_ac",
    name="Daikin AC Model XYZ",
    device_type=LegacyDeviceType.AIR_CONDITIONER,
    control_protocol=ControlProtocol.INFRARED,
    broadlink_device_ip="192.168.1.50",
    commands=DEVICE_TEMPLATES["daikin_ac_xyz"]  # Pre-configured
)
```

---

## API Reference

### Device Configuration

```python
@dataclass
class LegacyDeviceConfig:
    device_id: str              # Unique identifier
    name: str                   # Human-readable name
    device_type: LegacyDeviceType
    control_protocol: ControlProtocol
    
    # IR/RF (Broadlink)
    broadlink_device_ip: Optional[str]
    broadlink_device_mac: Optional[str]
    
    # RS232
    serial_port: Optional[str]  # e.g., "/dev/ttyUSB0"
    baud_rate: int = 9600
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = "N"           # N=None, E=Even, O=Odd
    
    # TCP/IP
    tcp_ip: Optional[str]
    tcp_port: int = 23
    
    # Commands (learned or pre-configured)
    commands: Dict[str, str]
    
    # Device-specific settings
    settings: Dict[str, Any]
```

### Control Methods

```python
# Air Conditioner
controller.control_ac(
    device_id: str,
    power: Optional[bool] = None,
    mode: Optional[ACMode] = None,
    temperature: Optional[int] = None,
    fan_speed: Optional[FanSpeed] = None,
    swing: Optional[bool] = None
)

# Fan
controller.control_fan(
    device_id: str,
    power: Optional[bool] = None,
    speed: Optional[FanSpeed] = None,
    oscillation: Optional[bool] = None,
    timer: Optional[int] = None
)

# Switch
controller.control_switch(
    device_id: str,
    state: bool  # True=on, False=off
)

# Projector
controller.control_projector(
    device_id: str,
    power: Optional[bool] = None,
    input_source: Optional[str] = None
)

# Generic Command
controller.send_command(
    device_id: str,
    command: str,
    parameters: Optional[Dict[str, Any]] = None
)

# Learn Command
controller.learn_command(
    device_id: str,
    command_name: str,
    timeout: int = 10
) -> Optional[str]
```

### REST API Endpoints

```http
# Register legacy device
POST /api/v1/legacy-devices
{
  "device_id": "bedroom_ac",
  "name": "Bedroom AC",
  "device_type": "air_conditioner",
  "control_protocol": "infrared",
  "broadlink_device_ip": "192.168.1.50"
}

# Control AC
POST /api/v1/legacy-devices/bedroom_ac/control/ac
{
  "power": true,
  "mode": "cool",
  "temperature": 24,
  "fan_speed": "auto"
}

# Send command
POST /api/v1/legacy-devices/bedroom_ac/command
{
  "command": "cool_24_auto"
}

# Learn command
POST /api/v1/legacy-devices/bedroom_ac/learn
{
  "command_name": "power_off",
  "timeout": 10
}

# Get device state
GET /api/v1/legacy-devices/bedroom_ac/state
```

---

## Integration with Presets

```yaml
# displays.yaml
presets:
  movie_night:
    name: "Movie Night"
    actions:
      # Turn off lights (RF switch)
      - type: legacy_device
        device_id: living_room_lights
        command: off
      
      # Close blinds (RF motor)
      - type: legacy_device
        device_id: living_room_blinds
        command: close
      
      # Turn on projector (RS232)
      - type: legacy_device
        device_id: home_theater_projector
        power: true
        input: hdmi1
      
      # Turn on AV receiver (TCP/IP)
      - type: legacy_device
        device_id: av_receiver
        command: power_on
      
      # Set AC to quiet mode (IR)
      - type: legacy_device
        device_id: living_room_ac
        power: true
        mode: cool
        temperature: 24
        fan_speed: low
  
  bedtime:
    name: "Bedtime"
    actions:
      # Turn off all devices
      - type: legacy_device
        device_id: bedroom_tv
        command: power_off
      
      - type: legacy_device
        device_id: bedroom_fan
        power: true
        speed: medium
      
      - type: legacy_device
        device_id: bedroom_ac
        power: true
        mode: cool
        temperature: 26
      
      # Close blinds
      - type: legacy_device
        device_id: bedroom_blinds
        command: close
```

---

## Troubleshooting

### IR Not Working

**Problem:** IR commands not reaching device

**Solutions:**
- Ensure Broadlink has clear line-of-sight to device
- Position Broadlink within 8 meters
- Learn command again (some remotes require multiple presses)
- Check if device is in "learning mode" (some ACs require this)

### RF Not Working

**Problem:** RF commands not triggering device

**Solutions:**
- Verify Broadlink RM4 Pro (not Mini - doesn't have RF)
- Check RF frequency (433MHz vs 315MHz)
- Increase range (RF works through walls but may need closer placement)
- Learn command multiple times (RF can vary)

### RS232 Not Working

**Problem:** RS232 device not responding

**Solutions:**
- Check serial port: `ls /dev/ttyUSB*`
- Verify baud rate matches device specs
- Check null modem requirement (some devices need crossover cable)
- Test with serial terminal first: `screen /dev/ttyUSB0 9600`
- Verify command format (\\r vs \\n vs \\r\\n)
- Check flow control settings (hardware/software)

### TCP/IP Not Working

**Problem:** Network device not responding

**Solutions:**
- Ping device: `ping 192.168.1.100`
- Check port: `telnet 192.168.1.100 50000`
- Verify firewall rules
- Check if device requires authentication
- Verify command format for specific device

---

## Advanced: Multi-Device Automation

### Climate Control Scenario

```python
# Summer mode: All ACs on, fans off
def activate_summer_mode(rooms: List[str]):
    for room in rooms:
        # Turn on AC
        controller.control_ac(
            device_id=f"{room}_ac",
            power=True,
            mode=ACMode.COOL,
            temperature=24,
            fan_speed=FanSpeed.AUTO
        )
        
        # Turn off ceiling fan
        controller.control_fan(
            device_id=f"{room}_fan",
            power=False
        )
        
        # Close blinds (reduce heat)
        controller.send_command(f"{room}_blinds", "close")
```

### Conference Room Preset

```python
def setup_presentation():
    # Lower projection screen
    controller.send_command("conference_screen", "down")
    
    # Turn on projector and warm up
    controller.control_projector(
        "conference_projector",
        power=True,
        input_source="hdmi1"
    )
    
    # Dim lights
    controller.send_command("conference_lights", "dim_30")
    
    # Set AC to quiet mode
    controller.control_ac(
        "conference_ac",
        mode=ACMode.COOL,
        temperature=23,
        fan_speed=FanSpeed.LOW
    )
    
    # Mute AV receiver
    controller.send_command("av_receiver", "mute_on")
```

---

## Summary

The Legacy Device Controller provides:

✅ **Unlimited Devices** - No limits on how many devices you can add  
✅ **Universal Protocols** - IR, RF, RS232, TCP/IP  
✅ **Easy Learning** - Learn from any existing remote  
✅ **Complete Control** - ACs, fans, switches, projectors, and more  
✅ **Preset Integration** - Combine legacy devices with modern automation  
✅ **Cost Effective** - Reuse existing equipment  
✅ **Future Proof** - Never locked into specific brands  

Perfect for:
- Retrofitting existing buildings
- Controlling professional AV equipment
- Integrating non-smart devices
- Custom installations
- Budget-conscious deployments
- Maximum versatility
