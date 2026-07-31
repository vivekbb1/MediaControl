# Access Flip Remote on iPhone

## Quick Start

1. **Connect iPhone to same WiFi** as your development computer

2. **Start the backend** (Terminal 1):
   ```bash
   python3 server.py 8080
   ```

3. **Start the frontend** (Terminal 2):
   ```bash
   cd frontend
   npm install  # first time only
   npm run dev
   ```

4. **Open Safari on iPhone** and navigate to:
   ```
   http://YOUR_COMPUTER_IP:5173/app/
   ```

   Replace `YOUR_COMPUTER_IP` with your computer's local network IP address.

## Finding Your Computer's IP Address

### On macOS:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1
```

### On Linux:
```bash
hostname -I | awk '{print $1}'
```

### On Windows:
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually starts with 192.168.x.x or 10.x.x.x)

## Current Environment

- **Backend Server**: `http://127.0.0.1:8080`
- **Frontend Dev Server**: `http://0.0.0.0:5173` (accessible on network)
- **iPhone Access URL**: `http://YOUR_IP:5173/app/`

## Touch-Optimized Features

The UI is designed for mobile with:
- **Touch targets ≥ 44px** on remote controls
- **Portrait mode support** for phone usage
- **Dark theme** optimized for AV environments
- **Icon-first navigation** for quick access

## Testing Checklist

- [ ] Login page loads on iPhone Safari
- [ ] Authentication works (session cookies)
- [ ] Room list displays correctly
- [ ] Remote control responds to touches
- [ ] Source switching buttons work
- [ ] Volume/power controls are accessible
- [ ] Orientation changes don't break layout

## Troubleshooting

**Can't connect from iPhone?**
- Verify both devices are on same WiFi network
- Check firewall isn't blocking port 5173
- Try accessing `http://YOUR_IP:5173/app/` in Safari (not Chrome)
- Ensure Vite shows "Network: http://YOUR_IP:5173" when starting

**Backend connection issues?**
- Backend must also allow network access
- Check `server.py` runs with `0.0.0.0` binding (not just localhost)

**Session/auth not working?**
- Safari blocks third-party cookies by default
- Ensure accessing via IP, not mixing localhost + IP
- Backend and frontend must use same hostname/IP for cookies to work
