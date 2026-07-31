"""
Voice Control Integration
Alexa Skills and Google Assistant Actions for voice control
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)


class VoiceAssistant(Enum):
    """Supported voice assistants"""
    ALEXA = "alexa"
    GOOGLE_ASSISTANT = "google_assistant"
    SIRI = "siri"


class IntentType(Enum):
    """Voice command intents"""
    PLAY_MUSIC = "play_music"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    NEXT_TRACK = "next_track"
    PREVIOUS_TRACK = "previous_track"
    SET_VOLUME = "set_volume"
    INCREASE_VOLUME = "increase_volume"
    DECREASE_VOLUME = "decrease_volume"
    POWER_ON = "power_on"
    POWER_OFF = "power_off"
    SWITCH_INPUT = "switch_input"
    ACTIVATE_PRESET = "activate_preset"
    CREATE_GROUP = "create_group"
    PLAY_PLAYLIST = "play_playlist"
    PLAY_ARTIST = "play_artist"
    PLAY_ALBUM = "play_album"
    TUNE_CHANNEL = "tune_channel"
    RECORD_SHOW = "record_show"
    SET_ALARM = "set_alarm"


@dataclass
class VoiceIntent:
    """Parsed voice command intent"""
    intent_type: IntentType
    parameters: Dict[str, Any]
    confidence: float
    assistant: VoiceAssistant
    room: Optional[str] = None
    device: Optional[str] = None


class AlexaSkillHandler:
    """
    Alexa Skill handler for MediaControl
    Handles requests from Alexa Skills Kit
    """
    
    def __init__(self, skill_id: str, device_manager=None, media_manager=None):
        self.skill_id = skill_id
        self.device_manager = device_manager
        self.media_manager = media_manager
        logger.info(f"AlexaSkillHandler initialized: {skill_id}")
    
    def handle_request(self, alexa_request: dict) -> dict:
        """
        Handle Alexa skill request
        
        Args:
            alexa_request: Alexa Skills Kit request JSON
            
        Returns:
            Alexa Skills Kit response JSON
        """
        request_type = alexa_request.get("request", {}).get("type")
        
        if request_type == "LaunchRequest":
            return self._handle_launch()
        
        elif request_type == "IntentRequest":
            return self._handle_intent(alexa_request)
        
        elif request_type == "SessionEndedRequest":
            return self._handle_session_ended()
        
        else:
            return self._build_response("I didn't understand that.")
    
    def _handle_launch(self) -> dict:
        """Handle skill launch"""
        return self._build_response(
            "Welcome to MediaControl. You can say things like 'play music in the living room' or 'turn on the TV'."
        )
    
    def _handle_intent(self, alexa_request: dict) -> dict:
        """Handle intent request"""
        intent = alexa_request["request"]["intent"]
        intent_name = intent["name"]
        slots = intent.get("slots", {})
        
        # Parse slots
        room = self._get_slot_value(slots, "Room")
        device = self._get_slot_value(slots, "Device")
        
        # Map Alexa intent to our IntentType
        if intent_name == "PlayMusicIntent":
            return self._handle_play_music(room, slots)
        
        elif intent_name == "PowerControlIntent":
            action = self._get_slot_value(slots, "Action")
            return self._handle_power_control(room, device, action)
        
        elif intent_name == "VolumeControlIntent":
            level = self._get_slot_value(slots, "Level")
            return self._handle_volume_control(room, device, level)
        
        elif intent_name == "PresetIntent":
            preset = self._get_slot_value(slots, "Preset")
            return self._handle_preset(room, preset)
        
        elif intent_name == "TuneChannelIntent":
            channel = self._get_slot_value(slots, "Channel")
            return self._handle_tune_channel(room, channel)
        
        else:
            return self._build_response("I'm not sure how to do that yet.")
    
    def _handle_play_music(self, room: str, slots: dict) -> dict:
        """Handle play music intent"""
        artist = self._get_slot_value(slots, "Artist")
        playlist = self._get_slot_value(slots, "Playlist")
        genre = self._get_slot_value(slots, "Genre")
        
        if not room:
            return self._build_response("Which room would you like to play music in?")
        
        try:
            # Execute media service play command
            if artist:
                response_text = f"Playing music by {artist} in the {room}"
            elif playlist:
                response_text = f"Playing {playlist} playlist in the {room}"
            elif genre:
                response_text = f"Playing {genre} music in the {room}"
            else:
                response_text = f"Playing music in the {room}"
            
            return self._build_response(response_text)
        
        except Exception as e:
            logger.error(f"Failed to play music: {e}")
            return self._build_response("Sorry, I couldn't play music right now.")
    
    def _handle_power_control(self, room: str, device: str, action: str) -> dict:
        """Handle power control intent"""
        if not room:
            return self._build_response("Which room?")
        
        try:
            state = "on" if action == "on" or action == "turn on" else "off"
            device_name = device or "TV"
            
            return self._build_response(f"Turning {state} the {device_name} in the {room}")
        
        except Exception as e:
            logger.error(f"Failed power control: {e}")
            return self._build_response("Sorry, I couldn't do that.")
    
    def _handle_volume_control(self, room: str, device: str, level: str) -> dict:
        """Handle volume control intent"""
        try:
            if level and level.isdigit():
                volume = int(level)
                return self._build_response(f"Setting volume to {volume} in the {room}")
            else:
                return self._build_response(f"Adjusting volume in the {room}")
        
        except Exception as e:
            logger.error(f"Failed volume control: {e}")
            return self._build_response("Sorry, I couldn't adjust the volume.")
    
    def _handle_preset(self, room: str, preset: str) -> dict:
        """Handle preset activation"""
        if not preset:
            return self._build_response("Which preset would you like to activate?")
        
        try:
            return self._build_response(f"Activating {preset} mode in the {room}")
        
        except Exception as e:
            logger.error(f"Failed to activate preset: {e}")
            return self._build_response("Sorry, I couldn't activate that preset.")
    
    def _handle_tune_channel(self, room: str, channel: str) -> dict:
        """Handle channel tuning"""
        if not channel:
            return self._build_response("Which channel?")
        
        try:
            return self._build_response(f"Tuning to channel {channel} in the {room}")
        
        except Exception as e:
            logger.error(f"Failed to tune channel: {e}")
            return self._build_response("Sorry, I couldn't tune to that channel.")
    
    def _handle_session_ended(self) -> dict:
        """Handle session ended"""
        return {"version": "1.0", "response": {}}
    
    def _get_slot_value(self, slots: dict, slot_name: str) -> Optional[str]:
        """Get slot value from Alexa request"""
        slot = slots.get(slot_name, {})
        return slot.get("value")
    
    def _build_response(self, speech_text: str, should_end_session: bool = True) -> dict:
        """Build Alexa Skills Kit response"""
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": speech_text
                },
                "shouldEndSession": should_end_session
            }
        }


class GoogleAssistantHandler:
    """
    Google Assistant Action handler for MediaControl
    Handles requests from Google Actions SDK
    """
    
    def __init__(self, project_id: str, device_manager=None, media_manager=None):
        self.project_id = project_id
        self.device_manager = device_manager
        self.media_manager = media_manager
        logger.info(f"GoogleAssistantHandler initialized: {project_id}")
    
    def handle_request(self, assistant_request: dict) -> dict:
        """
        Handle Google Assistant request
        
        Args:
            assistant_request: Google Actions request JSON
            
        Returns:
            Google Actions response JSON
        """
        intent = assistant_request.get("inputs", [{}])[0].get("intent", "")
        
        if intent == "actions.intent.MAIN":
            return self._handle_main()
        
        elif intent == "actions.intent.TEXT":
            return self._handle_text(assistant_request)
        
        else:
            return self._handle_custom_intent(assistant_request)
    
    def _handle_main(self) -> dict:
        """Handle main invocation"""
        return self._build_response(
            "Hi! I can help you control your media devices. "
            "Try saying something like 'play music in the living room' or 'turn on the TV'."
        )
    
    def _handle_text(self, assistant_request: dict) -> dict:
        """Handle text input"""
        text = assistant_request["inputs"][0]["rawInputs"][0]["query"]
        
        # Simple NLP to extract intent
        text_lower = text.lower()
        
        if "play" in text_lower and "music" in text_lower:
            return self._handle_play_music(text_lower)
        
        elif "turn on" in text_lower or "power on" in text_lower:
            return self._handle_power_on(text_lower)
        
        elif "turn off" in text_lower or "power off" in text_lower:
            return self._handle_power_off(text_lower)
        
        elif "volume" in text_lower:
            return self._handle_volume(text_lower)
        
        else:
            return self._build_response("I'm not sure how to help with that.")
    
    def _handle_custom_intent(self, assistant_request: dict) -> dict:
        """Handle custom intents"""
        # Implementation for custom intents
        return self._build_response("Working on that feature!")
    
    def _handle_play_music(self, text: str) -> dict:
        """Handle play music command"""
        # Extract room from text
        room = self._extract_room(text)
        
        if room:
            return self._build_response(f"Playing music in the {room}")
        else:
            return self._build_response("Which room would you like to play music in?")
    
    def _handle_power_on(self, text: str) -> dict:
        """Handle power on command"""
        room = self._extract_room(text)
        if room:
            return self._build_response(f"Turning on devices in the {room}")
        else:
            return self._build_response("Which room?")
    
    def _handle_power_off(self, text: str) -> dict:
        """Handle power off command"""
        room = self._extract_room(text)
        if room:
            return self._build_response(f"Turning off devices in the {room}")
        else:
            return self._build_response("Which room?")
    
    def _handle_volume(self, text: str) -> dict:
        """Handle volume command"""
        room = self._extract_room(text)
        if room:
            return self._build_response(f"Adjusting volume in the {room}")
        else:
            return self._build_response("Which room?")
    
    def _extract_room(self, text: str) -> Optional[str]:
        """Extract room name from text"""
        common_rooms = ["living room", "bedroom", "kitchen", "bathroom", "office", "dining room"]
        
        for room in common_rooms:
            if room in text.lower():
                return room
        
        return None
    
    def _build_response(self, speech_text: str) -> dict:
        """Build Google Assistant response"""
        return {
            "expectUserResponse": False,
            "finalResponse": {
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": speech_text
                            }
                        }
                    ]
                }
            }
        }


# Alexa Skill manifest example
ALEXA_SKILL_MANIFEST = """
{
  "manifest": {
    "publishingInformation": {
      "locales": {
        "en-US": {
          "name": "MediaControl",
          "summary": "Control your home entertainment system",
          "description": "Control TVs, music, and media devices throughout your home with voice commands.",
          "examplePhrases": [
            "Alexa, ask MediaControl to play music in the living room",
            "Alexa, tell MediaControl to turn on the TV",
            "Alexa, ask MediaControl to activate movie night"
          ],
          "keywords": ["media", "tv", "music", "home automation"]
        }
      }
    },
    "apis": {
      "custom": {
        "endpoint": {
          "uri": "https://api.mediacontrol.com/alexa"
        }
      }
    },
    "manifestVersion": "1.0"
  }
}
"""

# Interaction model
ALEXA_INTERACTION_MODEL = """
{
  "interactionModel": {
    "languageModel": {
      "invocationName": "media control",
      "intents": [
        {
          "name": "PlayMusicIntent",
          "slots": [
            {"name": "Room", "type": "AMAZON.Room"},
            {"name": "Artist", "type": "AMAZON.Artist"},
            {"name": "Playlist", "type": "PlaylistType"},
            {"name": "Genre", "type": "AMAZON.MusicGroup"}
          ],
          "samples": [
            "play music in the {Room}",
            "play {Artist} in the {Room}",
            "play {Playlist} playlist",
            "play some {Genre} music"
          ]
        },
        {
          "name": "PowerControlIntent",
          "slots": [
            {"name": "Room", "type": "AMAZON.Room"},
            {"name": "Device", "type": "DeviceType"},
            {"name": "Action", "type": "PowerAction"}
          ],
          "samples": [
            "{Action} the {Device} in the {Room}",
            "{Action} {Device}",
            "power {Action} the {Device}"
          ]
        },
        {
          "name": "VolumeControlIntent",
          "slots": [
            {"name": "Room", "type": "AMAZON.Room"},
            {"name": "Device", "type": "DeviceType"},
            {"name": "Level", "type": "AMAZON.NUMBER"}
          ],
          "samples": [
            "set volume to {Level} in the {Room}",
            "increase volume",
            "decrease volume",
            "volume up",
            "volume down"
          ]
        },
        {
          "name": "PresetIntent",
          "slots": [
            {"name": "Room", "type": "AMAZON.Room"},
            {"name": "Preset", "type": "PresetType"}
          ],
          "samples": [
            "activate {Preset}",
            "start {Preset} mode",
            "{Preset} in the {Room}"
          ]
        }
      ],
      "types": [
        {
          "name": "DeviceType",
          "values": [
            {"name": {"value": "TV"}},
            {"name": {"value": "stereo"}},
            {"name": {"value": "speakers"}}
          ]
        },
        {
          "name": "PresetType",
          "values": [
            {"name": {"value": "movie night"}},
            {"name": {"value": "party mode"}},
            {"name": {"value": "morning routine"}}
          ]
        }
      ]
    }
  }
}
"""

# API endpoints
VOICE_CONTROL_API = """
# Flask endpoints

@app.post("/alexa")
def alexa_skill():
    '''Alexa Skill endpoint'''
    alexa_request = request.json
    
    # Verify request signature (important for security)
    # verifier = AlexaRequestVerifier()
    # if not verifier.verify(request):
    #     return {"error": "Invalid request"}, 401
    
    handler = AlexaSkillHandler(
        skill_id="amzn1.ask.skill.xyz",
        device_manager=device_mgr,
        media_manager=media_mgr
    )
    
    response = handler.handle_request(alexa_request)
    return response

@app.post("/google-assistant")
def google_assistant_action():
    '''Google Assistant Action endpoint'''
    assistant_request = request.json
    
    handler = GoogleAssistantHandler(
        project_id="mediacontrol-project",
        device_manager=device_mgr,
        media_manager=media_mgr
    )
    
    response = handler.handle_request(assistant_request)
    return response
"""
