# Broadlink IR/RF Integration Guide

## Overview

This system now supports **Broadlink RM4 Mini and RM4 Pro** WiFi-based IR/RF devices for controlling set-top boxes, cable boxes, and other AV equipment that don't support MDC/TCP control.

### What You Can Do

- **Channel selection** with number pad (0-9, CH+, CH-, Last)
- **Menu navigation** with D-pad (↑ ↓ ← → OK)
- **Transport controls** for DVR (Play, Pause, Stop, Record, Rewind, Forward)
- **Guide/Info buttons** for EPG and program information
- **Combined control** of Samsung Flip display (via MDC) + STB (via Broadlink IR)

---

## Hardware Requirements

### Supported Broadlink Devices

| Device | Device Type Code | IR | RF | Notes |
|--------|------------------|----|----|-------|
| **RM4 Mini** | `0x61A2` | ✅ | ❌ | Infrared only, compact |
| **RM4 Pro** | `0x648D` | ✅ | ✅ | IR + 433MHz RF, temp sensor port |
| RM Mini 3 | `0x27D9` | ✅ | ❌ | Older model |
| RM Pro+ | `0x61A4` | ✅ | ✅ | Similar to RM4 Pro |

### Setup Location

- Place Broadlink device with **line-of-sight** to your set-top box
- IR range: ~8 meters (26 feet) typical
- Connect to same network as Flip Remote server
- Assign a **static IP** or DHCP reservation

---

## Installation

### 1. Install Python Dependencies

```bash
pip3 install broadlink
```

Or update from requirements:

```bash
pip3 install -r requirements.txt
```

### 2. Configure Broadlink Device

Use the official **Broadlink app** (iOS/Android) for initial setup:

1. Download "Broadlink" app from App Store or Google Play
2. Power on your Broadlink device (blue LED flashing)
3. Add device in app and connect to WiFi
4. Note the device's **IP address** and **MAC address**

---

## Quick Start

### Step 1: Discover Your Device

```bash
python3 broadlink_client.py --discover
```

**Example output:**

```
Found 1 device(s):
  Type: 61A2, Host: 192.168.1.150, MAC: 24DFA7F94D84
```

### Step 2: Learn IR Codes

Point your STB remote at the Broadlink and run:

```bash
python3 broadlink_client.py --learn \
  --host 192.168.1.150 \
  --mac 24DFA7F94D84 \
  --type 0x61A2
```

Press a button on your STB remote (e.g., channel "1"). The captured code will display:

```
Captured code:
260050000001269213371337133713381...
```

**Copy this hex string** – you'll add it to your configuration.

### Step 3: Test the Code

Send the learned code back to verify it works:

```bash
python3 broadlink_client.py --send "260050000001269213371337133713381..." \
  --host 192.168.1.150 \
  --mac 24DFA7F94D84
```

Your set-top box should respond (e.g., switch to channel 1).

### Step 4: Configure in displays.yaml

Add Broadlink configuration to your room:

```yaml
displays:
  living_room:
    title: Living Room
    model: WM55B
    ip: 192.168.1.100      # Samsung Flip display
    port: 1515
    device_id: 0
    
    # Add Broadlink for STB control
    broadlink:
      host: 192.168.1.150
      port: 80
      mac: "24:DF:A7:F9:4D:84"
      device_type: 0x61A2
    
    # Add learned IR codes
    ir_codes:
      num_1: "260050000001269213371337133713381..."
      num_2: "260056000001289415391539153915481..."
      ch_up: "26005A000001309617401740174017501..."
      # ... (learn and add all buttons you need)
    
    # Enable channel pad in layout
    layout:
      section_order:
        - master
        - sources
        - channels      # ← Number pad section
        - navigation
        - transport     # ← DVR controls
```

See [`BROADLINK_CONFIG_EXAMPLE.yaml`](./BROADLINK_CONFIG_EXAMPLE.yaml) for complete example.

### Step 5: Restart Server

```bash
python3 server.py 8080
```

Your remote will now show channel selection and transport controls!

---

## Learning All Buttons

**Recommended workflow:**

1. Create a checklist of buttons to learn:
   - Numbers: 0-9
   - Channels: CH+, CH-, Last/Prev
   - Navigation: Up, Down, Left, Right, OK
   - Menu: Menu, Guide, Info, Exit, Back
   - Transport: Play, Pause, Stop, Record, FF, Rewind
   - Power: Power toggle (if separate from display)

2. Run learning mode for each button:

   ```bash
   # Terminal 1: Start learning session
   python3 broadlink_client.py --learn --host 192.168.1.150 --mac 24DFA7F94D84
   ```

3. Press STB remote button → copy hex code → add to `displays.yaml`

4. Test each code before moving to next button

5. Optionally, save codes to external file:

   ```yaml
   # displays.yaml
   ir_codes_file: "ir_codes/living_room_stb.yaml"
   ```

   ```yaml
   # ir_codes/living_room_stb.yaml
   ir_codes:
     num_0: "2600..."
     num_1: "2600..."
     # etc.
   ```

---

## Layout Configuration

### Available Button Sections

| Section | Purpose | Example Buttons |
|---------|---------|----------------|
| `channels` | Number pad + channel nav | 0-9, CH+, CH-, Last, Guide |
| `navigation` | D-pad menu navigation | ↑ ↓ ← → OK, Menu, Back, Exit |
| `transport` | DVR playback controls | Play, Pause, Stop, Record, FF, Rewind |

### Example Layout

```yaml
layout:
  button_size: lg
  columns: 2
  section_order:
    - master        # Power, Mute, Vol+/-
    - sources       # HDMI inputs
    - channels      # 📱 Number pad
    - navigation    # 🎮 D-pad
    - transport     # ⏯️ DVR controls
    - volume
    - picture
  
  button_order:
    channels:
      - num_1
      - num_2
      - num_3
      - num_4
      - num_5
      - num_6
      - num_7
      - num_8
      - num_9
      - last        # Last/Previous channel
      - num_0
      - guide       # Program guide
      - ch_up       # CH+ button
      - ch_down     # CH- button
    
    navigation:
      - up
      - left
      - ok
      - right
      - down
      - menu
      - back
      - exit
      - info
    
    transport:
      - rewind
      - play
      - pause
      - forward
      - stop
      - record
```

---

## Troubleshooting

### Device Not Discovered

**Problem:** `python3 broadlink_client.py --discover` returns no devices.

**Solutions:**

1. **Same network:** Ensure Broadlink and server are on same subnet
2. **Firewall:** Allow UDP port 80 inbound
   ```bash
   sudo iptables -A INPUT -p udp --sport 80 -j ACCEPT
   ```
3. **Locked device:** If device was locked in Broadlink app, discovery fails. Use unicast:
   ```bash
   python3 broadlink_client.py --learn --host 192.168.1.150
   ```

### Learning Mode Timeout

**Problem:** "Timeout: No IR code captured" after 10 seconds.

**Solutions:**

- **Point remote directly** at Broadlink (within 1 meter during learning)
- **Press and hold** button for 1-2 seconds
- **Try different remote battery** (weak batteries = weak IR signal)
- **Increase timeout** in code or press button multiple times rapidly

### IR Code Doesn't Work

**Problem:** Code sends successfully but STB doesn't respond.

**Solutions:**

1. **Wrong code learned:** Re-learn the button
2. **STB not in IR mode:** Some STBs have RF remotes – use IR mode
3. **Obstructed IR:** Ensure Broadlink has line-of-sight to STB
4. **Multiple IR codes:** Some buttons send 2-3 codes in sequence – capture full sequence:
   ```bash
   # Press and hold button during learning to capture repeat codes
   ```

### Temperature Always Returns 0.0 (RM4 Pro only)

The RM4 Pro requires the **HTS2 sensor cable** for temperature/humidity. Without it, `check_temperature()` returns 0. The Broadlink app may show temperature from your phone's sensors, not the device.

---

## Advanced: External IR Code Files

For multi-room setups, store IR codes in separate files:

```yaml
# displays.yaml
displays:
  bedroom:
    broadlink:
      host: 192.168.1.151
    ir_codes_file: "ir_codes/bedroom_stb.yaml"
  
  living_room:
    broadlink:
      host: 192.168.1.150
    ir_codes_file: "ir_codes/living_room_stb.yaml"
```

```yaml
# ir_codes/bedroom_stb.yaml
ir_codes:
  num_0: "2600..."
  num_1: "2600..."
  # ... etc
```

---

## API Endpoints

### Send IR Command

```http
POST /api/displays/:id/send
Content-Type: application/json

{
  "command": "num_1"
}
```

**Response:**

```json
{
  "ok": true,
  "display_id": "living_room",
  "command": "num_1",
  "method": "broadlink_ir",
  "device": "192.168.1.150"
}
```

### Learn IR Code (Future)

*(Not yet exposed in API – use CLI for now)*

---

## Security Notes

- **Network isolation:** Place Broadlink devices on isolated VLAN if untrusted
- **Static IPs:** Prevent DHCP reassignment breaking configuration
- **MAC filtering:** Optional, for extra security
- **Firmware updates:** Keep Broadlink firmware updated via official app

---

## FAQ

**Q: Can I control multiple STBs with one Broadlink?**  
A: Yes, if they're all in IR range. Configure separate rooms in `displays.yaml` pointing to the same Broadlink host, each with its own `ir_codes`.

**Q: What about RF remotes (433MHz)?**  
A: RM4 Pro and RM Pro+ support 433MHz RF. Learning RF works the same as IR – just point and press.

**Q: Can I use this with other IR devices (soundbars, projectors)?**  
A: Absolutely! Any IR-controlled device works. Just learn the codes and add them to your configuration.

**Q: Does this work with the Lovable frontend?**  
A: Yes! The React frontend automatically displays channel/transport sections when configured in the layout.

---

## Support

- **GitHub Issues:** [Report bugs or request features](https://github.com/vivekbb1/MediaControl/issues)
- **Broadlink Library:** [mjg59/python-broadlink](https://github.com/mjg59/python-broadlink)
- **CLI Reference:** Run `python3 broadlink_client.py --help`

---

## Related Documentation

- [`BROADLINK_CONFIG_EXAMPLE.yaml`](./BROADLINK_CONFIG_EXAMPLE.yaml) – Complete configuration example
- [`broadlink_client.py`](./broadlink_client.py) – CLI tool for discovery and learning
- [`displays.yaml`](./displays.yaml) – Main configuration file
- [`layout_templates.yaml`](./layout_templates.yaml) – Button layout definitions
