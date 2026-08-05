# LEGAL COMPLIANCE & LICENSING

**IMPORTANT LEGAL NOTICE**

---

## Disclaimer

MediaControl is a **device control and automation system**. It is NOT:
- ❌ A content distribution platform
- ❌ A media streaming service
- ❌ A tool for bypassing content protection
- ❌ A mechanism for unauthorized access to copyrighted content

---

## User Responsibility

### Content Licensing

**Users are solely responsible for:**

1. **Obtaining proper licenses** for all content they access through integrated services
2. **Maintaining valid subscriptions** to streaming services (Spotify, Netflix, etc.)
3. **Complying with copyright laws** in their jurisdiction
4. **Respecting content usage rights** and terms of service
5. **Ensuring legal ownership** of physical media and devices they control

### Service Requirements

All media service integrations **require valid, paid subscriptions**:

```yaml
✅ LEGAL USE:
- User has active Spotify Premium subscription
- MediaControl controls playback on user's authorized devices
- Content accessed through official Spotify API with user's credentials

❌ ILLEGAL USE:
- Attempting to access content without subscription
- Bypassing authentication or payment systems
- Sharing credentials with unauthorized users
- Recording/redistributing copyrighted content
```

---

## What MediaControl Does

### Legitimate Functions

MediaControl provides **control interfaces** for legally owned/licensed content:

1. **Device Control**
   - Power on/off TVs, ACs, fans, lights
   - Change inputs, volume, channels
   - Automation and scheduling

2. **Media Service Integration**
   - Play/pause/skip on user's **authorized** streaming services
   - Control playback on user's **registered** devices
   - Require user's **valid credentials** and **active subscriptions**

3. **EPG Display**
   - Show TV guide information from **public EPG sources**
   - For channels user has **legal access** to via their STB subscription

4. **Screen Recording** (Optional)
   - For personal, non-commercial use only
   - Subject to local laws and content terms of service
   - NOT for redistribution of copyrighted content

---

## What MediaControl Does NOT Do

### Prohibited Functions

MediaControl does **NOT**:

- ❌ Provide access to pirated or unauthorized content
- ❌ Bypass DRM, encryption, or content protection
- ❌ Enable sharing of copyrighted material
- ❌ Provide "free" access to paid streaming services
- ❌ Facilitate credential sharing or account hijacking
- ❌ Decode, decrypt, or redistribute protected streams
- ❌ Provide IPTV streams of copyrighted content
- ❌ Include pre-configured piracy sources or tools

---

## Terms of Service Requirements

### For End Users

By using MediaControl, users agree to:

1. **Legal Content Access**
   - Only control content they have legal right to access
   - Maintain valid subscriptions to all streaming services
   - Comply with each service's terms of service

2. **No Piracy**
   - Not use MediaControl to access unauthorized content
   - Not use screen recording for illegal redistribution
   - Not bypass authentication or payment systems

3. **Personal Use**
   - Use for personal, non-commercial purposes only
   - Not resell, redistribute, or share access credentials
   - Comply with all applicable copyright and licensing laws

4. **Compliance**
   - Follow all local, state, and federal laws
   - Respect intellectual property rights
   - Report any misuse or security concerns

### For Integrators/Resellers

Integrators deploying MediaControl **must**:

1. **Client Education**
   - Inform clients about licensing requirements
   - Ensure clients have valid subscriptions
   - Provide guidance on legal compliance

2. **No Pre-Configuration**
   - Not pre-configure unauthorized content sources
   - Not provide "free" access to paid services
   - Not include piracy tools or links

3. **Compliance Monitoring**
   - Monitor for misuse in commercial deployments
   - Remove access for users violating terms
   - Cooperate with copyright enforcement

---

## Media Service Integration Compliance

### Required User Actions

For each streaming service, users **must**:

#### Spotify
- ✅ Have active Spotify Premium subscription ($9.99/month)
- ✅ Authenticate with their personal Spotify credentials
- ✅ Only control devices registered to their account
- ❌ Cannot access content without valid subscription

#### Apple Music
- ✅ Have active Apple Music subscription ($10.99/month)
- ✅ Authenticate with their Apple ID
- ✅ Comply with Apple's terms of service
- ❌ Cannot bypass iCloud authentication

#### Netflix, Disney+, Prime Video, etc.
- ✅ Have valid subscription for each service
- ✅ Only launch apps on their authorized devices
- ✅ Not redistribute, record, or share content
- ❌ MediaControl does NOT provide content access

### How Integration Works (Legal)

```python
# LEGAL: User has Spotify Premium, authenticates with their credentials
spotify_service = SpotifyService(credentials={
    "client_id": user.spotify_client_id,      # User's own credentials
    "client_secret": user.spotify_secret,
    "redirect_uri": "https://app.mediacontrol.com/callback"
})

# User must complete OAuth flow with Spotify
await spotify_service.authenticate()  # Redirects to Spotify login

# Only after successful auth can user control their content
await spotify_service.play(track_uri, device_id=user_device)
```

**MediaControl does NOT:**
- Store or provide Spotify credentials
- Bypass Spotify's authentication
- Provide "free" access to Premium features
- Enable multiple users to share one account

---

## EPG (Electronic Program Guide) Compliance

### Legitimate EPG Sources

MediaControl uses **public, legal EPG sources**:

1. **Official Broadcaster APIs**
   - BBC, PBS, etc. provide free public EPG data
   - No content access, only schedule information

2. **Open-Source EPG Projects**
   - iptv-org/epg (open-source, community-maintained)
   - Contains schedule data for legal, public channels

3. **User's STB Provider**
   - EPG data from user's existing cable/satellite subscription
   - User must have valid STB subscription

### EPG Data ≠ Content Access

**Important:** EPG data shows TV schedules, but:
- ❌ Does NOT provide access to streams
- ❌ Does NOT bypass subscription requirements
- ❌ Does NOT include pirated IPTV links
- ✅ Only shows what's available through user's **legal** STB/cable subscription

---

## Screen Recording Compliance

### Legal Use Only

MediaControl's screen recording feature is for:

✅ **Permitted Uses:**
- Personal time-shifting (recording shows to watch later)
- Archiving personal media collections
- Accessibility purposes (captions, transcription)
- Educational fair use (in compliance with local laws)

❌ **Prohibited Uses:**
- Commercial redistribution of copyrighted content
- Sharing recordings on public platforms
- Circumventing DRM or content protection
- Recording for piracy or resale

### Disclaimer

**Recording functionality requires:**
- User compliance with local copyright laws
- Adherence to content provider terms of service
- Understanding of fair use limitations
- Personal, non-commercial use only

**Note:** Some content may be technically protected from recording (HDCP, DRM). MediaControl does NOT bypass these protections.

---

## Developer Responsibilities

### For MediaControl Developers

The development team commits to:

1. **No Piracy Tools**
   - Not implement DRM circumvention
   - Not provide unauthorized content sources
   - Not enable credential sharing or account hijacking

2. **Proper Integration**
   - Use official APIs only (Spotify API, Apple MusicKit, etc.)
   - Require user authentication for all services
   - Respect rate limits and usage policies

3. **Compliance Updates**
   - Monitor API terms of service changes
   - Update integrations to maintain compliance
   - Remove features if they become non-compliant

4. **User Education**
   - Provide clear documentation on legal use
   - Display licensing requirements prominently
   - Include compliance notices in UI

---

## Terms of Service (Template)

### Acceptable Use Policy

**You MAY:**
- ✅ Control your own legally owned/subscribed devices and content
- ✅ Automate playback of content you have rights to access
- ✅ Use for personal, non-commercial purposes
- ✅ Control devices in your home or authorized locations

**You MAY NOT:**
- ❌ Access content without proper licenses or subscriptions
- ❌ Bypass authentication, DRM, or payment systems
- ❌ Share, redistribute, or resell copyrighted content
- ❌ Use for commercial piracy or copyright infringement
- ❌ Violate any service provider's terms of service
- ❌ Enable unauthorized access for other users

### Enforcement

MediaControl reserves the right to:
- Suspend accounts engaging in piracy or unauthorized use
- Report illegal activity to appropriate authorities
- Cooperate with copyright enforcement requests
- Terminate service for terms of service violations

---

## Content Provider Partnerships (Recommended)

### Official Partnerships

For commercial deployment, consider:

1. **Spotify for Developers** - Official partner program
2. **Apple MusicKit** - Licensed Apple Music integration
3. **YouTube API** - Official Google partnership
4. **Netflix Partner Program** - For hospitality deployments

These partnerships provide:
- ✅ Legal protection and licensing
- ✅ Enhanced API access and features
- ✅ Support and compliance guidance
- ✅ White-label or co-branding opportunities

---

## Liability Disclaimer

### Limitation of Liability

**MEDIACONTROL IS A CONTROL SYSTEM, NOT A CONTENT PROVIDER.**

- MediaControl provides device control and automation software
- Users are solely responsible for content licensing and compliance
- MediaControl assumes no liability for user copyright violations
- Integration with streaming services requires users' valid credentials and subscriptions
- Screen recording is provided for legal, personal use only

**By using MediaControl, you agree:**
- To obtain proper licenses for all content you access
- To maintain valid subscriptions to integrated services
- To comply with all applicable copyright and licensing laws
- That MediaControl is not responsible for your content usage
- To indemnify MediaControl against claims arising from your misuse

---

## Compliance Checklist

### For Developers

- [ ] All streaming integrations use official APIs
- [ ] User authentication required for all services
- [ ] No hardcoded credentials or subscription bypass
- [ ] No pre-configured piracy sources
- [ ] Legal disclaimers in UI and documentation
- [ ] Terms of service clearly displayed
- [ ] Privacy policy for user data handling

### For Users

- [ ] Valid subscriptions to all streaming services used
- [ ] Legal access to all content controlled/recorded
- [ ] Compliance with local copyright laws
- [ ] Understanding of fair use limitations
- [ ] Personal, non-commercial use only

### For Integrators

- [ ] Client education on licensing requirements
- [ ] No unauthorized content pre-configuration
- [ ] Monitoring for misuse in deployments
- [ ] Compliance with hospitality/commercial licensing
- [ ] Proper contractual protections

---

## Contact & Reporting

### Report Piracy or Abuse

If you discover MediaControl being used for piracy or copyright infringement:

**Email:** legal@mediacontrol.com  
**Subject:** Copyright Infringement Report

Include:
- Description of infringement
- Evidence (screenshots, URLs, etc.)
- Your contact information
- Rights holder information (if applicable)

We will investigate and take appropriate action, including:
- Account suspension/termination
- Reporting to authorities
- Cooperation with copyright holders

---

## Summary

**MediaControl is a legitimate automation tool for legally owned content and devices.**

✅ **We Provide:** Device control, automation, and convenience  
❌ **We Do NOT Provide:** Pirated content, DRM bypass, or unauthorized access  

**Users are responsible for:**
- Obtaining proper licenses and subscriptions
- Complying with copyright laws
- Respecting content provider terms of service

**Legal use only. No piracy. No exceptions.**

---

*This document should be reviewed by legal counsel before commercial deployment.*
