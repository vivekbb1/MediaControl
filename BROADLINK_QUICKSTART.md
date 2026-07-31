# Broadlink STB Control - Quick Start Guide

## ✅ What's Been Implemented

Your Flip Remote system now has **full Broadlink RM4 Mini/Pro support** for controlling set-top boxes and other IR/RF devices!

### New Features

✅ **Channel Selection**
- Number pad buttons (0-9)
- Channel Up/Down (CH+, CH-)
- Last/Previous channel
- Program Guide button

✅ **Menu Navigation**
- D-pad (Up, Down, Left, Right, OK)
- Menu, Back, Exit, Info buttons
- Perfect for STB EPG navigation

✅ **DVR Controls**
- Play, Pause, Stop
- Fast Forward, Rewind
- Record button

✅ **Hybrid Control**
- Samsung Flip (via MDC/TCP) + Set-Top Box (via Broadlink IR) in one remote
- Or use Broadlink-only for any IR/RF device

---

## 🚀 Quick Setup (5 Steps)

### 1. Install Broadlink Library

```bash
pip3 install -r requirements.txt
```

### 2. Find Your Broadlink Device

```bash
python3 broadlink_client.py --discover
```

**Example output:**
```
Found 1 device(s):
  Type: 61A2, Host: 192.168.1.150, MAC: 24DFA7F94D84
```

### 3. Learn IR Codes from Your STB Remote

```bash
# Start learning mode
python3 broadlink_client.py --learn \
  --host 192.168.1.150 \
  --mac 24DFA7F94D84

# Point your STB remote at the Broadlink and press "1"
# You'll see: Captured code: 260050000001269213371337...
```

### 4. Add to displays.yaml

```yaml
displays:
  living_room:
    title: Living Room
    model: WM55B
    ip: 192.168.1.100
    
    # Add Broadlink config
    broadlink:
      host: 192.168.1.150
      mac: "24:DF:A7:F9:4D:84"
      device_type: 0x61A2  # RM4 Mini
    
    # Add learned IR codes
    ir_codes:
      num_1: "260050000001269213371337..."  # Paste captured code
      num_2: "260056000001289415391539..."
      # ... learn all buttons you need
    
    # Enable channel pad in layout
    layout:
      section_order:
        - master
        - sources
        - channels      # ← Number pad
        - navigation
        - transport     # ← DVR controls
```

### 5. Restart & Test

```bash
python3 server.py 8080
```

Open remote → see channel pad and transport controls!

---

## 📱 iPhone Testing

The remote works on iPhone too! See [`IPHONE_ACCESS.md`](./IPHONE_ACCESS.md).

```bash
# Start frontend
cd frontend
npm install
npm run dev
```

Access from iPhone at: `http://YOUR_IP:5173/app/`

---

## 📚 Full Documentation

- **[docs/BROADLINK_SETUP.md](./docs/BROADLINK_SETUP.md)** – Complete setup guide with troubleshooting
- **[BROADLINK_CONFIG_EXAMPLE.yaml](./BROADLINK_CONFIG_EXAMPLE.yaml)** – Full configuration examples
- **[broadlink_client.py](./broadlink_client.py)** – CLI tool (run with `--help`)

---

## 🎮 Supported Buttons

### Channel Section (3x5 grid)
```
1  2  3
4  5  6
7  8  9
Last  0  Guide
CH+  CH-
```

### Navigation Section (D-pad + actions)
```
    ↑
  ← OK →
    ↓
    
Menu  Back  Exit  Info
```

### Transport Section (DVR controls)
```
⏪  ▶️  ⏸️  ⏩  ⏹️  ⏺️
(Rewind, Play, Pause, FF, Stop, Record)
```

---

## 🔧 CLI Tools

### Discover Devices
```bash
python3 broadlink_client.py --discover
```

### Learn IR Code
```bash
python3 broadlink_client.py --learn --host 192.168.1.150 --mac 24DFA7F94D84
```

### Test Learned Code
```bash
python3 broadlink_client.py --send "260050..." --host 192.168.1.150
```

---

## 💡 Tips

1. **Static IPs:** Assign static IPs to Broadlink devices in your router
2. **Line of sight:** Place Broadlink within ~8 meters of your STB
3. **Battery check:** Weak remote batteries = weak IR signal during learning
4. **Test each code:** After learning, test with `--send` before adding to config
5. **External files:** For multiple rooms, store IR codes in separate YAML files

---

## 🐛 Troubleshooting

**Discovery fails?**
- Check same network/subnet
- Allow UDP port 80: `sudo iptables -A INPUT -p udp --sport 80 -j ACCEPT`
- Try unicast if device is locked: `--host 192.168.1.150` (no discover)

**Learning times out?**
- Point remote **directly** at Broadlink (< 1 meter)
- Press and **hold** button for 1-2 seconds
- Check remote battery

**Code doesn't work?**
- Re-learn the button
- Ensure line-of-sight to STB
- Some buttons send multiple codes – press and hold during learning

See [docs/BROADLINK_SETUP.md](./docs/BROADLINK_SETUP.md) for full troubleshooting.

---

## 🎯 Next Steps

1. **Learn all buttons** you need (see checklist in docs)
2. **Configure layout** to show/hide sections as needed
3. **Create external IR code files** for multi-room setups
4. **Test on mobile** devices for touch-friendly experience

---

## 📦 What Was Added

### New Files
- `broadlink_client.py` – Broadlink controller library + CLI
- `docs/BROADLINK_SETUP.md` – Complete setup guide
- `BROADLINK_CONFIG_EXAMPLE.yaml` – Configuration examples

### Updated Files
- `button_svgs.py` – 24 new icons (numbers, arrows, transport)
- `button_svgs.js` – Regenerated with new icons
- `layout_templates.yaml` – New "channels" and "transport" sections
- `display_manager.py` – Broadlink integration alongside MDC
- `requirements.txt` – Added broadlink library
- `frontend/vite.config.ts` – iPhone network access

### Backend Features
- Automatic device type detection (RM4 Mini/Pro)
- Inline IR codes or external YAML files
- Hybrid MDC + IR control in single room
- CLI for discovery and learning

### Frontend Features
- Data-driven rendering (automatically shows new sections)
- Touch-friendly button grids
- iPhone/mobile responsive
- Status polling and feedback

---

## 🌟 Example Use Cases

### Cable/Satellite Box Control
```yaml
ir_codes:
  num_0: "..."
  num_1: "..."
  # ... all numbers
  ch_up: "..."
  guide: "..."
  last: "..."
```

### Home Theater STB + Flip Display
```yaml
# Samsung display via MDC
ip: 192.168.1.100
port: 1515

# STB via Broadlink
broadlink:
  host: 192.168.1.150
```

### Multi-Room with Shared Codes
```yaml
# Room 1
ir_codes_file: "ir_codes/living_room_stb.yaml"

# Room 2
ir_codes_file: "ir_codes/bedroom_stb.yaml"
```

---

## 🎉 You're All Set!

The system is ready to use. Just:
1. Learn your IR codes
2. Add them to config
3. Restart server
4. Enjoy unified control!

**Questions?** Check [docs/BROADLINK_SETUP.md](./docs/BROADLINK_SETUP.md) or file an issue.
