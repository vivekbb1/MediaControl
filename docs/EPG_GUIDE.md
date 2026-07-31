# EPG (Electronic Program Guide) Integration Guide

## Overview

The Flip Remote system now integrates with **global IPTV/EPG services** to provide a complete multimedia experience with:

- 📺 **Channel logos** from 10,000+ global TV stations
- 📅 **Program guides** with show names, descriptions, and air times
- 🌍 **Automatic timezone conversion** to your local time
- 🎬 **Rich metadata** including categories, ratings, episode numbers
- 🔄 **Auto-updating** EPG data every 6 hours
- 🎯 **One-click channel tuning** via Broadlink IR

This creates a **fully integrated multimedia setup** where you can:
1. See what's currently playing on each channel
2. Browse upcoming shows for the next 8 hours
3. Click a show to automatically tune your STB to that channel via IR
4. View high-quality channel logos
5. Get show descriptions, cast info, and episode details

---

## Data Sources

### 1. EPG Data: iptv-org/epg

**Repository:** https://github.com/iptv-org/epg  
**Stars:** 3,181+ | **Format:** XMLTV

The largest community-maintained EPG database with:
- 📡 **Thousands of channels** from 100+ countries
- 🔄 **Daily updates** via automated scripts
- 🗜️ **Compressed format** (gzip) for fast downloads
- 📋 **Rich metadata** including show descriptions, categories, cast
- 🆓 **Free and open source**

**Coverage by region:**
- **North America:** US, Canada, Mexico
- **Europe:** UK, Germany, France, Spain, Italy, Netherlands, +30 more
- **Asia:** India, Japan, South Korea, China, Singapore, Thailand, +20 more
- **Oceania:** Australia, New Zealand
- **Middle East:** UAE, Saudi Arabia, Qatar, Israel
- **Latin America:** Brazil, Argentina, Chile, Colombia
- **Africa:** South Africa, Kenya, Nigeria

### 2. Channel Logos: tv-logo/tv-logos

**Repository:** https://github.com/tv-logo/tv-logos  
**Stars:** 1,000+ | **Format:** PNG (transparent)

High-quality TV logos for dark backgrounds:
- 🎨 **10,000+ channel logos** worldwide
- 📐 **512px width** PNG with transparency
- 🌑 **Optimized for dark themes**
- 🏷️ **Organized by country**
- 🔄 **HD versions** available for major channels
- 📡 **Direct CDN links** via GitHub Pages

---

## Quick Start

### Step 1: Enable EPG in displays.yaml

```yaml
displays:
  living_room:
    title: Living Room
    ip: 192.168.1.100
    
    broadlink:
      host: 192.168.1.150
      mac: "24:DF:A7:F9:4D:84"
      device_type: 0x61A2
    
    # Add EPG configuration
    epg:
      enabled: true
      country_code: "us"
      timezone: "America/New_York"
      
      sources:
        - url: "https://iptv-org.github.io/epg/guides/us.xml.gz"
      
      channels:
        - name: "CNN"
          epg_id: "CNN.us"
          channel_number: 202
          ir_command: "num_2,num_0,num_2"
        
        - name: "ESPN"
          epg_id: "ESPN.us"
          channel_number: 206
          ir_command: "num_2,num_0,num_6"
```

### Step 2: Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 3: Test EPG Fetching

```bash
# Fetch and parse EPG
python3 epg_client.py https://iptv-org.github.io/epg/guides/us.xml.gz

# Test channel logo
python3 epg_client.py logo "CNN" us
```

### Step 4: Restart Server

```bash
python3 server.py 8080
```

### Step 5: Access EPG Guide

Open your remote and navigate to the **EPG Guide** section to see:
- Current show on each channel
- Upcoming programmes for next 8 hours
- Show descriptions and metadata
- One-click channel tuning

---

## Configuration

### Timezone Support

All show times are automatically converted to your local timezone:

```yaml
epg:
  timezone: "America/New_York"  # US Eastern
  # or
  timezone: "Europe/London"     # UK
  # or
  timezone: "Asia/Tokyo"        # Japan
```

**Common timezones:**

| Region | Timezone |
|--------|----------|
| US East Coast | `America/New_York` |
| US Central | `America/Chicago` |
| US Mountain | `America/Denver` |
| US West Coast | `America/Los_Angeles` |
| UK | `Europe/London` |
| Germany | `Europe/Berlin` |
| France | `Europe/Paris` |
| Australia Sydney | `Australia/Sydney` |
| Japan | `Asia/Tokyo` |
| India | `Asia/Kolkata` |
| Dubai | `Asia/Dubai` |
| Brazil | `America/Sao_Paulo` |

[Full list of timezones →](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

### Multi-Source EPG

Merge multiple EPG sources for better coverage:

```yaml
epg:
  sources:
    - url: "https://iptv-org.github.io/epg/guides/us.xml.gz"
      priority: 1
    
    - url: "https://iptv-org.github.io/epg/guides/ca.xml.gz"
      priority: 2
    
    # Custom source
    - url: "https://your-provider.com/epg.xml"
      priority: 3
```

### Channel Mapping

Link EPG channel IDs to your STB's IR commands:

```yaml
channels:
  # Single digit
  - name: "NBC"
    epg_id: "NBC.us"
    channel_number: 4
    ir_command: "num_4"
  
  # Multi-digit (comma-separated)
  - name: "CNN"
    epg_id: "CNN.us"
    channel_number: 202
    ir_command: "num_2,num_0,num_2"
  
  # With OK/Enter button
  - name: "HBO"
    epg_id: "HBO.us"
    channel_number: 300
    ir_command: "num_3,num_0,num_0,ok"
  
  # Custom logo
  - name: "Local News"
    epg_id: "KABC.us"
    channel_number: 7
    ir_command: "num_7"
    logo_override: "https://example.com/custom-logo.png"
```

### Update Schedule

```yaml
epg:
  update:
    interval_hours: 6      # Update every 6 hours
    auto_update: true      # Enable auto-updates
    retry_on_failure: true # Retry failed updates
```

### Cache Settings

```yaml
epg:
  cache:
    enabled: true
    max_age_hours: 12      # Use cache if < 12 hours old
    directory: "./epg_cache"
```

### Display Options

```yaml
epg:
  display:
    show_now_next: true          # Show current & next programme
    hours_ahead: 8               # Show next 8 hours
    show_descriptions: true      # Show programme descriptions
    show_categories: true        # Show genres
    show_episode_numbers: true   # Show S01E05 format
```

---

## Finding EPG Channel IDs

### Method 1: Browse the Database

Visit https://github.com/iptv-org/database and search for your channel.

### Method 2: Inspect XMLTV File

```bash
# Download EPG file
wget https://iptv-org.github.io/epg/guides/us.xml.gz
gunzip us.xml.gz

# List all channels
grep '<channel id=' us.xml | head -20

# Search for specific channel
grep -i 'cnn' us.xml
```

**Example output:**
```xml
<channel id="CNN.us">
  <display-name>CNN</display-name>
  <icon src="https://upload.wikimedia.org/..."/>
</channel>
```

Use `CNN.us` as your `epg_id`.

### Method 3: Use the CLI Tool

```bash
python3 epg_client.py https://iptv-org.github.io/epg/guides/us.xml.gz
```

This will list all available channels and their IDs.

---

## Available EPG Sources

### North America

```yaml
# United States
- url: "https://iptv-org.github.io/epg/guides/us.xml.gz"

# Canada
- url: "https://iptv-org.github.io/epg/guides/ca.xml.gz"

# Mexico
- url: "https://iptv-org.github.io/epg/guides/mx.xml.gz"
```

### Europe

```yaml
# United Kingdom
- url: "https://iptv-org.github.io/epg/guides/uk.xml.gz"

# Germany
- url: "https://iptv-org.github.io/epg/guides/de.xml.gz"

# France
- url: "https://iptv-org.github.io/epg/guides/fr.xml.gz"

# Spain
- url: "https://iptv-org.github.io/epg/guides/es.xml.gz"

# Italy
- url: "https://iptv-org.github.io/epg/guides/it.xml.gz"

# Netherlands
- url: "https://iptv-org.github.io/epg/guides/nl.xml.gz"
```

### Asia & Oceania

```yaml
# Australia
- url: "https://iptv-org.github.io/epg/guides/au.xml.gz"

# India
- url: "https://iptv-org.github.io/epg/guides/in.xml.gz"

# Japan
- url: "https://iptv-org.github.io/epg/guides/jp.xml.gz"

# South Korea
- url: "https://iptv-org.github.io/epg/guides/kr.xml.gz"

# Singapore
- url: "https://iptv-org.github.io/epg/guides/sg.xml.gz"
```

### Full List

Browse all available countries: https://github.com/iptv-org/epg/tree/master/sites

---

## Channel Logos

### Automatic Logo Fetching

Logos are automatically fetched from `tv-logo/tv-logos` based on channel name:

```python
# Example: CNN in US
https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cnn-us.png

# Example: BBC One in UK
https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-kingdom/bbc-one-hd-uk.png
```

### Logo Naming Convention

- **All lowercase**
- **Spaces → dashes**
- **Country code suffix**

Examples:
- `CNN` → `cnn-us.png`
- `BBC One` → `bbc-one-uk.png`
- `Discovery Channel` → `discovery-channel-us.png`
- `Sky Sports Main Event` → `sky-sports-main-event-uk.png`

### HD Logos

Some channels have HD versions in the `hd/` subfolder:

```
https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/hd/espn-us.png
```

### Custom Logos

Override the auto-fetched logo:

```yaml
channels:
  - name: "Local News"
    epg_id: "KABC.us"
    logo_override: "https://example.com/kabc-logo.png"
```

---

## Multi-Room Setup

Different EPG configurations per room:

```yaml
displays:
  living_room:
    epg:
      country_code: "us"
      timezone: "America/New_York"
      sources:
        - url: "https://iptv-org.github.io/epg/guides/us.xml.gz"
  
  bedroom:
    epg:
      country_code: "us"
      timezone: "America/Los_Angeles"  # Different timezone!
      sources:
        - url: "https://iptv-org.github.io/epg/guides/us.xml.gz"
  
  guest_room:
    epg:
      country_code: "uk"  # Different country!
      timezone: "Europe/London"
      sources:
        - url: "https://iptv-org.github.io/epg/guides/uk.xml.gz"
```

---

## API Endpoints

Once EPG is configured, these endpoints become available:

### Get All Channels

```http
GET /api/epg/channels
```

**Response:**
```json
{
  "ok": true,
  "channels": [
    {
      "id": "CNN.us",
      "name": "CNN",
      "number": 202,
      "logo": "https://raw.githubusercontent.com/.../cnn-us.png",
      "current_programme": {
        "title": "CNN Newsroom",
        "start": "2026-07-31T14:00:00-04:00",
        "stop": "2026-07-31T15:00:00-04:00",
        "description": "Breaking news and analysis..."
      }
    }
  ]
}
```

### Get Current Programme

```http
GET /api/epg/programme/CNN.us/now
```

### Get Programme Schedule

```http
GET /api/epg/programme/CNN.us/schedule?hours=8
```

### Tune to Channel

```http
POST /api/displays/:id/tune
{
  "channel_number": 202
}
```

This sends the IR command sequence to switch channels.

---

## Frontend Integration

The EPG guide is automatically available in the React frontend:

### EPG Guide Page

Access at: `/app/guide`

Shows:
- **Channel list** with logos
- **Current show** for each channel
- **Upcoming schedule** (next 8 hours)
- **Click to tune** functionality
- **Search and filter** by genre

### Now Playing Widget

On the remote page, see what's currently playing:

```
┌─────────────────────────────────┐
│ 📺 Now on CNN (202)            │
│ CNN Newsroom                    │
│ 14:00 - 15:00 (30 min left)    │
│ Breaking news and analysis...   │
│ [Tune Now]                      │
└─────────────────────────────────┘
```

---

## Troubleshooting

### EPG Not Loading

**Problem:** EPG data doesn't appear in UI.

**Solutions:**

1. **Check EPG source URL:**
   ```bash
   curl -I https://iptv-org.github.io/epg/guides/us.xml.gz
   # Should return 200 OK
   ```

2. **Test EPG fetching manually:**
   ```bash
   python3 epg_client.py https://iptv-org.github.io/epg/guides/us.xml.gz
   ```

3. **Check server logs** for EPG fetch errors

4. **Verify cache directory** is writable:
   ```bash
   ls -la ./epg_cache/
   ```

### Channel IDs Don't Match

**Problem:** EPG channel ID doesn't match your provider's ID.

**Solution:**

Check the XMLTV file for exact IDs:
```bash
wget https://iptv-org.github.io/epg/guides/us.xml.gz
gunzip us.xml.gz
grep -A 2 'CNN' us.xml
```

Look for the `<channel id="...">` value and use that exactly.

### Logos Not Displaying

**Problem:** Channel logos show broken image icon.

**Solutions:**

1. **Test logo URL directly:**
   ```bash
   python3 epg_client.py logo "CNN" us
   # Copy URL and test in browser
   ```

2. **Check naming convention** - tv-logos uses specific format:
   - All lowercase
   - Spaces become dashes
   - Must include country code

3. **Use custom logo** as workaround:
   ```yaml
   channels:
     - name: "Problem Channel"
       logo_override: "https://example.com/custom-logo.png"
   ```

### Timezone Issues

**Problem:** Show times are incorrect.

**Solution:**

1. **Verify timezone string**:
   ```bash
   python3 -c "from zoneinfo import ZoneInfo; print(ZoneInfo('America/New_York'))"
   ```

2. **Check system time**:
   ```bash
   date
   timedatectl  # On Linux
   ```

3. **Use correct IANA timezone** (not abbreviations):
   - ✅ `America/New_York`
   - ❌ `EST` or `EDT`

### Update Failures

**Problem:** EPG updates fail after initial setup.

**Solutions:**

1. **Check network connectivity**
2. **Verify cache directory permissions**
3. **Increase retry interval**:
   ```yaml
   epg:
     update:
       interval_hours: 12  # Try less frequent updates
   ```

---

## Advanced Configuration

### Favorites

Mark channels as favorites to show them first:

```yaml
epg:
  favorites:
    - "CNN.us"
    - "ESPN.us"
    - "HBO.us"
```

### Genre Filtering

Show/hide channels by genre:

```yaml
epg:
  genre_filter:
    show: ["News", "Sports", "Movies"]
    hide: ["Shopping", "Infomercials"]
```

### Custom EPG Source

Use your own EPG provider:

```yaml
epg:
  sources:
    - url: "https://your-provider.com/epg.xml.gz"
      headers:
        Authorization: "Bearer YOUR_TOKEN"
```

---

## Performance Tips

1. **Use compressed EPG** (`.xml.gz`) for faster downloads
2. **Enable caching** to reduce network requests
3. **Filter channels** to only parse what you need
4. **Increase update interval** if bandwidth is limited
5. **Use local EPG source** if running EPG server on LAN

---

## Resources

- **iptv-org/epg:** https://github.com/iptv-org/epg
- **tv-logo/tv-logos:** https://github.com/tv-logo/tv-logos
- **XMLTV Format Spec:** http://wiki.xmltv.org/index.php/XMLTVFormat
- **Timezone Database:** https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
- **EPG Config Example:** [`EPG_CONFIG_EXAMPLE.yaml`](../EPG_CONFIG_EXAMPLE.yaml)

---

## Summary

✅ **10,000+ channel logos** automatically fetched  
✅ **Global EPG data** from iptv-org community  
✅ **Automatic timezone conversion** to local time  
✅ **Rich metadata** including descriptions, categories, cast  
✅ **One-click tuning** via Broadlink IR  
✅ **Auto-updating** every 6 hours  
✅ **Multi-room support** with different timezones  
✅ **Fully integrated** with existing remote UI  

Your multimedia setup is now complete!
