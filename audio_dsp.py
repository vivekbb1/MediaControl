"""
Advanced Audio DSP (Digital Signal Processing)
EQ, crossfade, ducking, and other audio effects
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class EQPreset(Enum):
    """Equalizer presets"""
    FLAT = "flat"
    BASS_BOOST = "bass_boost"
    TREBLE_BOOST = "treble_boost"
    VOCAL = "vocal"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    POP = "pop"
    HIP_HOP = "hip_hop"
    CUSTOM = "custom"


@dataclass
class EQBand:
    """Equalizer band configuration"""
    frequency: int  # Hz
    gain: float     # dB (-12 to +12)
    q_factor: float = 1.0  # Quality factor (bandwidth)


@dataclass
class EqualizerConfig:
    """Complete equalizer configuration"""
    preset: EQPreset = EQPreset.FLAT
    bands: List[EQBand] = field(default_factory=list)
    enabled: bool = True
    
    def __post_init__(self):
        if not self.bands and self.preset != EQPreset.CUSTOM:
            self.bands = self._get_preset_bands(self.preset)
    
    def _get_preset_bands(self, preset: EQPreset) -> List[EQBand]:
        """Get EQ bands for preset"""
        # Standard 10-band EQ frequencies
        frequencies = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        
        presets = {
            EQPreset.FLAT: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            EQPreset.BASS_BOOST: [8, 6, 4, 2, 0, 0, 0, 0, 0, 0],
            EQPreset.TREBLE_BOOST: [0, 0, 0, 0, 0, 0, 2, 4, 6, 8],
            EQPreset.VOCAL: [-2, -2, 0, 2, 4, 4, 3, 1, 0, -1],
            EQPreset.ROCK: [5, 3, 1, -1, -2, -1, 1, 3, 4, 4],
            EQPreset.JAZZ: [4, 3, 1, 0, -1, -1, 0, 1, 3, 4],
            EQPreset.CLASSICAL: [5, 4, 2, 0, -1, -1, 0, 2, 4, 5],
            EQPreset.ELECTRONIC: [6, 4, 1, 0, -2, 2, 1, 2, 5, 6],
            EQPreset.POP: [-1, -1, 0, 2, 4, 4, 3, 1, 0, -1],
            EQPreset.HIP_HOP: [6, 5, 2, 1, -1, -1, 1, 2, 3, 4]
        }
        
        gains = presets.get(preset, [0] * 10)
        
        return [
            EQBand(frequency=freq, gain=gain)
            for freq, gain in zip(frequencies, gains)
        ]


@dataclass
class CrossfadeConfig:
    """Crossfade configuration"""
    enabled: bool = True
    duration_ms: int = 3000  # Crossfade duration in milliseconds
    curve: str = "linear"    # linear, exponential, logarithmic
    overlap_threshold: float = 0.8  # Start crossfade when track is 80% complete


@dataclass
class DuckingConfig:
    """Audio ducking configuration (lower music volume during voice/notifications)"""
    enabled: bool = True
    duck_level: float = 0.3    # Duck to 30% of original volume
    fade_in_ms: int = 500      # Fade in duration
    fade_out_ms: int = 500     # Fade out duration
    hold_ms: int = 1000        # Hold ducked volume for this duration after trigger ends


@dataclass
class CompressorConfig:
    """Dynamic range compressor"""
    enabled: bool = False
    threshold: float = -20.0   # dB
    ratio: float = 4.0         # Compression ratio (4:1)
    attack: float = 5.0        # ms
    release: float = 100.0     # ms
    makeup_gain: float = 0.0   # dB


@dataclass
class LimiterConfig:
    """Audio limiter (prevent clipping)"""
    enabled: bool = True
    threshold: float = -1.0    # dB
    release: float = 50.0      # ms


@dataclass
class AudioDSPConfig:
    """Complete audio DSP configuration"""
    equalizer: EqualizerConfig = field(default_factory=EqualizerConfig)
    crossfade: CrossfadeConfig = field(default_factory=CrossfadeConfig)
    ducking: DuckingConfig = field(default_factory=DuckingConfig)
    compressor: CompressorConfig = field(default_factory=CompressorConfig)
    limiter: LimiterConfig = field(default_factory=LimiterConfig)
    master_volume: float = 1.0  # 0.0 to 1.0


class AudioDSPProcessor:
    """
    Audio DSP processor for real-time audio effects
    Uses FFmpeg audio filters and/or direct audio processing
    """
    
    def __init__(self):
        self.device_configs: Dict[str, AudioDSPConfig] = {}
        logger.info("AudioDSPProcessor initialized")
    
    def set_device_config(self, device_id: str, config: AudioDSPConfig):
        """Set DSP configuration for a device"""
        self.device_configs[device_id] = config
        logger.info(f"Set DSP config for device {device_id}")
    
    def get_device_config(self, device_id: str) -> Optional[AudioDSPConfig]:
        """Get DSP configuration for a device"""
        return self.device_configs.get(device_id)
    
    def set_eq_preset(self, device_id: str, preset: EQPreset):
        """Set equalizer preset for a device"""
        config = self.device_configs.get(device_id, AudioDSPConfig())
        config.equalizer.preset = preset
        config.equalizer.bands = config.equalizer._get_preset_bands(preset)
        self.device_configs[device_id] = config
        
        logger.info(f"Set EQ preset {preset.value} for device {device_id}")
        return config.equalizer
    
    def set_custom_eq(self, device_id: str, bands: List[EQBand]):
        """Set custom EQ bands for a device"""
        config = self.device_configs.get(device_id, AudioDSPConfig())
        config.equalizer.preset = EQPreset.CUSTOM
        config.equalizer.bands = bands
        self.device_configs[device_id] = config
        
        logger.info(f"Set custom EQ for device {device_id}: {len(bands)} bands")
    
    def enable_crossfade(self, device_id: str, duration_ms: int = 3000):
        """Enable crossfade for a device"""
        config = self.device_configs.get(device_id, AudioDSPConfig())
        config.crossfade.enabled = True
        config.crossfade.duration_ms = duration_ms
        self.device_configs[device_id] = config
        
        logger.info(f"Enabled crossfade ({duration_ms}ms) for device {device_id}")
    
    def enable_ducking(
        self,
        device_id: str,
        duck_level: float = 0.3,
        fade_in_ms: int = 500
    ):
        """Enable audio ducking for a device"""
        config = self.device_configs.get(device_id, AudioDSPConfig())
        config.ducking.enabled = True
        config.ducking.duck_level = duck_level
        config.ducking.fade_in_ms = fade_in_ms
        self.device_configs[device_id] = config
        
        logger.info(f"Enabled ducking (level={duck_level}) for device {device_id}")
    
    def build_ffmpeg_filter(self, config: AudioDSPConfig) -> str:
        """
        Build FFmpeg audio filter chain from DSP config
        
        Returns:
            FFmpeg audio filter string
        """
        filters = []
        
        # Equalizer
        if config.equalizer.enabled and config.equalizer.bands:
            eq_filters = []
            for band in config.equalizer.bands:
                eq_filters.append(
                    f"equalizer=f={band.frequency}:width_type=q:width={band.q_factor}:g={band.gain}"
                )
            filters.extend(eq_filters)
        
        # Compressor
        if config.compressor.enabled:
            filters.append(
                f"acompressor=threshold={config.compressor.threshold}dB:"
                f"ratio={config.compressor.ratio}:"
                f"attack={config.compressor.attack}:"
                f"release={config.compressor.release}:"
                f"makeup={config.compressor.makeup_gain}"
            )
        
        # Limiter
        if config.limiter.enabled:
            filters.append(
                f"alimiter=limit={config.limiter.threshold}dB:"
                f"release={config.limiter.release}"
            )
        
        # Master volume
        if config.master_volume != 1.0:
            filters.append(f"volume={config.master_volume}")
        
        # Join filters
        filter_chain = ",".join(filters) if filters else "anull"
        
        return filter_chain
    
    def apply_ducking(self, device_id: str, trigger: bool):
        """
        Apply or remove ducking effect
        
        Args:
            device_id: Device to duck
            trigger: True to duck, False to restore
        """
        config = self.device_configs.get(device_id)
        if not config or not config.ducking.enabled:
            return
        
        if trigger:
            # Duck down
            target_volume = config.master_volume * config.ducking.duck_level
            fade_duration = config.ducking.fade_out_ms
        else:
            # Restore
            target_volume = config.master_volume
            fade_duration = config.ducking.fade_in_ms
        
        logger.info(
            f"{'Ducking' if trigger else 'Restoring'} audio on {device_id} "
            f"to {target_volume} over {fade_duration}ms"
        )
        
        # Implementation would fade volume via audio device API
        # e.g., sonos.set_volume(target_volume, fade_duration)


class AudioEnhancer:
    """
    Additional audio enhancement features
    """
    
    @staticmethod
    def normalize_volume(
        devices: List[str],
        target_loudness: float = -14.0  # LUFS
    ):
        """
        Normalize volume across multiple devices
        Uses loudness normalization (EBU R128 standard)
        """
        logger.info(f"Normalizing volume for {len(devices)} devices to {target_loudness} LUFS")
        
        # Would analyze audio levels and adjust volume accordingly
        # Implementation depends on audio device capabilities
    
    @staticmethod
    def sync_audio_delay(devices: List[str], reference_device: str):
        """
        Synchronize audio across devices (compensate for delays)
        Useful for multi-room audio groups
        """
        logger.info(f"Synchronizing audio delay for {len(devices)} devices")
        
        # Would measure and compensate for audio delays
        # Implementation depends on device capabilities
    
    @staticmethod
    def apply_room_correction(
        device_id: str,
        room_profile: Dict[str, float]
    ):
        """
        Apply room acoustic correction
        Compensates for room acoustics using measured room profile
        """
        logger.info(f"Applying room correction for device {device_id}")
        
        # Would apply EQ based on room acoustics
        # Similar to Sonos TruePlay or Apple HomePod spatial audio


# Integration examples
DSP_USAGE_EXAMPLES = """
# Basic usage

from audio_dsp import AudioDSPProcessor, EQPreset, AudioDSPConfig

dsp = AudioDSPProcessor()

# Set EQ preset
dsp.set_eq_preset("living_room_sonos", EQPreset.BASS_BOOST)

# Custom EQ
custom_bands = [
    EQBand(frequency=60, gain=6.0),
    EQBand(frequency=230, gain=3.0),
    EQBand(frequency=1000, gain=-2.0),
    EQBand(frequency=4000, gain=4.0)
]
dsp.set_custom_eq("living_room_sonos", custom_bands)

# Enable crossfade
dsp.enable_crossfade("living_room_sonos", duration_ms=5000)

# Enable ducking for notifications
dsp.enable_ducking("living_room_sonos", duck_level=0.2, fade_in_ms=300)

# Trigger ducking (e.g., during notification)
dsp.apply_ducking("living_room_sonos", trigger=True)  # Duck
# ... notification plays ...
dsp.apply_ducking("living_room_sonos", trigger=False)  # Restore

# Get FFmpeg filter for streaming
config = dsp.get_device_config("living_room_sonos")
filter_chain = dsp.build_ffmpeg_filter(config)
print(filter_chain)
# Output: equalizer=f=60:width_type=q:width=1.0:g=6.0,equalizer=f=230:...,alimiter=...
"""

# API endpoints
AUDIO_DSP_API = """
# Flask endpoints

@app.post("/api/v1/audio/{device_id}/eq")
def set_equalizer(device_id: str, request: EQRequest):
    '''Set equalizer for device'''
    dsp = AudioDSPProcessor()
    
    if request.preset:
        eq = dsp.set_eq_preset(device_id, request.preset)
    else:
        dsp.set_custom_eq(device_id, request.bands)
        eq = dsp.get_device_config(device_id).equalizer
    
    return {
        "device_id": device_id,
        "preset": eq.preset.value,
        "bands": [
            {"frequency": b.frequency, "gain": b.gain}
            for b in eq.bands
        ]
    }

@app.post("/api/v1/audio/{device_id}/crossfade")
def enable_crossfade(device_id: str, request: CrossfadeRequest):
    '''Enable crossfade'''
    dsp = AudioDSPProcessor()
    dsp.enable_crossfade(device_id, request.duration_ms)
    
    return {"device_id": device_id, "crossfade_enabled": True}

@app.post("/api/v1/audio/{device_id}/ducking")
def enable_ducking(device_id: str, request: DuckingRequest):
    '''Enable audio ducking'''
    dsp = AudioDSPProcessor()
    dsp.enable_ducking(device_id, request.duck_level, request.fade_in_ms)
    
    return {"device_id": device_id, "ducking_enabled": True}

@app.get("/api/v1/audio/{device_id}/dsp-config")
def get_dsp_config(device_id: str):
    '''Get complete DSP configuration'''
    dsp = AudioDSPProcessor()
    config = dsp.get_device_config(device_id)
    
    if not config:
        return {"error": "No config found"}, 404
    
    return {
        "device_id": device_id,
        "equalizer": {
            "preset": config.equalizer.preset.value,
            "bands": [
                {"frequency": b.frequency, "gain": b.gain}
                for b in config.equalizer.bands
            ]
        },
        "crossfade": {
            "enabled": config.crossfade.enabled,
            "duration_ms": config.crossfade.duration_ms
        },
        "ducking": {
            "enabled": config.ducking.enabled,
            "duck_level": config.ducking.duck_level
        }
    }
"""

# Room preset with DSP
PRESET_WITH_DSP = """
presets:
  hifi_listening:
    name: "Hi-Fi Listening Mode"
    actions:
      - type: audio_dsp
        device: living_room_system
        equalizer:
          preset: classical
        compressor:
          enabled: true
          threshold: -20
          ratio: 2.5
        limiter:
          enabled: true
      
      - type: media_service
        service: tidal
        action: play_playlist
        playlist: "Classical Masters"
        quality: "HiFi"  # Lossless
  
  party_mode:
    name: "Party Mode"
    actions:
      - type: audio_dsp
        device: all_speakers
        equalizer:
          preset: bass_boost
        crossfade:
          enabled: true
          duration_ms: 5000
        ducking:
          enabled: false  # No ducking during party
      
      - type: media_service
        service: spotify
        action: play_playlist
        playlist: "Party Hits"
"""
