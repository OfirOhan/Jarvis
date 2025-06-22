"""
AI components for intent classification and command template management
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any

# Command templates with examples and thresholds
COMMAND_TEMPLATES = {
    # ========= STATIC COMMANDS (type 0) =========
    "open_stremio": {
        "type": 0,
        "confidence_threshold": 0.6,
        "examples": [
            "open stremio", "start stremio", "launch stremio", "play stremio",
            "open streaming", "start streaming", "launch streaming app"
        ],
        "response": "Opening Stremio"
    },
    "play_pause": {
        "type": 0,
        "confidence_threshold": 0.6,
        "examples": [
            "play", "pause", "play pause", "resume", "stop"
        ],
        "response": "Controlling media playback"
    },
    "youtube_music_play_pause": {
        "type": 0,
        "confidence_threshold": 0.7,
        "examples": [
            "play music", "pause music", "play youtube music", "pause youtube music",
            "resume music", "stop music", "music play", "music pause", "stop youtube music"
        ],
        "response": "Controlling YouTube Music"
    },

    "youtube_play_pause": {
        "type": 0,
        "confidence_threshold": 0.7,
        "examples": [
            "play youtube", "pause youtube", "play video", "pause video",
            "resume youtube", "stop youtube", "youtube play", "youtube pause"
        ],
        "response": "Controlling YouTube"
    },

    "stremio_play_pause": {
        "type": 0,
        "confidence_threshold": 0.7,
        "examples": [
            "play stremio", "pause stremio", "resume stremio", "stop stremio",
            "stremio play", "stremio pause"
        ],
        "response": "Controlling Stremio"
    },

    "music_play_pause": {
        "type": 0,
        "confidence_threshold": 0.7,
        "examples": [
            "play spotify", "pause spotify", "spotify play", "spotify pause",
            "play song", "pause song", "next song", "previous song"
        ],
        "response": "Controlling music player"
    },
    "stremio_fullscreen": {
        "type": 0,
        "confidence_threshold": 0.6,
        "examples": [
            "stremio fullscreen", "fullscreen", "full screen", "make fullscreen",
            "expand video", "maximize video", "big screen"
        ],
        "response": "Toggling Stremio fullscreen"
    },
    "volume_up": {
        "type": 0,
        "confidence_threshold": 0.6,  # Medium - safe
        "examples": [
            "volume up", "turn up volume", "increase volume", "louder",
            "make it louder", "turn it up", "raise volume", "boost volume"
        ],
        "response": "Turning up volume"
    },
    "volume_down": {
        "type": 0,
        "confidence_threshold": 0.6,  # Medium - safe
        "examples": [
            "volume down", "turn down volume", "decrease volume", "quieter",
            "make it quieter", "turn it down", "lower volume", "reduce volume"
        ],
        "response": "Turning down volume"
    },
    "open_notepad": {
        "type": 0,
        "confidence_threshold": 0.7,  # Higher - but still safe
        "examples": [
            "open notepad", "open text editor", "launch notepad", "start notepad",
            "open editor", "new document", "create document", "open notes"
        ],
        "response": "Opening Notepad"
    },
    "get_time": {
        "type": 0,
        "confidence_threshold": 0.6,  # Medium - safe
        "examples": [
            "what time is it", "current time", "tell me the time", "time",
            "what's the time", "check time", "show time", "time please"
        ],
        "response": "Getting current time"
    },
    "next_song": {
        "type": 0,
        "confidence_threshold": 0.6,  # Medium - safe
        "examples": [
            "next song", "skip song", "next track", "skip track", "next",
            "skip", "play next", "next music", "skip this song", "change song"
        ],
        "response": "Playing next song"
    },
    "previous_song": {
        "type": 0,
        "confidence_threshold": 0.6,  # Medium - safe
        "examples": [
            "previous song", "last song", "previous track", "last track", "previous",
            "go back", "back song", "previous music", "play previous", "last music"
        ],
        "response": "Playing previous song"
    },
    "mute": {
        "type": 0,
        "confidence_threshold": 0.6,
        "examples": [
            "mute", "silence", "turn off sound", "mute volume", "no sound",
            "quiet", "mute audio", "turn off audio"
        ],
        "response": "Muting audio"
    },
    "open_calculator": {
        "type": 0,
        "confidence_threshold": 0.7,
        "examples": [
            "open calculator", "launch calculator", "start calculator", "calc",
            "calculator", "open calc", "math calculator"
        ],
        "response": "Opening Calculator"
    },
    # ========= DANGEROUS COMMANDS - HIGH THRESHOLD =========
    "shutdown": {
        "type": 0,
        "confidence_threshold": 0.85,  # VERY HIGH - dangerous!
        "examples": [
            "shutdown", "shut down", "turn off computer", "power off",
            "shutdown computer", "turn off", "power down", "close computer"
        ],
        "response": "Shutting down computer"
    },
    "restart": {
        "type": 0,
        "confidence_threshold": 0.85,  # VERY HIGH - dangerous!
        "examples": [
            "restart", "reboot", "restart computer", "reboot computer",
            "restart system", "reboot system", "refresh computer"
        ],
        "response": "Restarting computer"
    },
    "sleep": {
        "type": 0,
        "confidence_threshold": 0.85,
        "examples": [
            "sleep", "sleep computer", "put computer to sleep", "hibernate",
            "sleep mode", "standby"
        ],
        "response": "Putting computer to sleep"
    },
    # ========= DYNAMIC COMMANDS (type 1) =========
    "web_search": {
        "type": 1,
        "confidence_threshold": 0.7,  # Medium-high for dynamic
        "examples": [
            "search for", "google", "look up", "find information about",
            "search the web for", "find", "look for", "search"
        ],
        "response": "Searching the web"
    },
    "write_text": {
        "type": 1,
        "confidence_threshold": 0.7,  # Medium-high - could be disruptive
        "examples": [
            "write", "type", "write text", "type text", "write down",
            "type this", "write this", "input text", "enter text"
        ],
        "response": "Writing text"
    },
    "press_button": {
        "type": 1,
        "confidence_threshold": 0.6,  # Medium - safe but specific
        "examples": [
            "press", "hit", "push", "click", "press key", "hit key",
            "push button", "click button", "press the", "hit the"
        ],
        "response": "Pressing button"
    }
}


class IntentClassifier:
    """Handles intent classification using local AI models"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        print("Loading local AI model...")
        self.sentence_model = SentenceTransformer(model_name)
        self.command_templates = COMMAND_TEMPLATES
        self.command_embeddings = {}
        self._compute_command_embeddings()
        print("Local AI model loaded.")

    def _compute_command_embeddings(self):
        """Pre-compute embeddings for all command examples"""
        print("Computing command embeddings...")
        for command, data in self.command_templates.items():
            embeddings = self.sentence_model.encode(data["examples"])
            self.command_embeddings[command] = embeddings

    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Use local AI to classify intent without API calls"""
        text = text.lower().strip()

        # First, check for dynamic commands (type 1) using simple keyword matching
        for command, data in self.command_templates.items():
            if data.get("type") == 1:  # Dynamic command
                for trigger in data["examples"]:
                    if trigger in text:
                        # Found a dynamic command trigger - extract everything after it
                        extracted_text = text.split(trigger, 1)[1].strip()

                        # Generic parameter extraction - use "content" as universal parameter name
                        parameters = {"content": extracted_text} if extracted_text else {}

                        return {
                            "intent": command,
                            "confidence": 0.9,
                            "parameters": parameters,
                            "response": data["response"],
                            "threshold": data.get("confidence_threshold", 0.7)
                        }

        # If no dynamic command found, use embeddings for static commands (type 0)
        input_embedding = self.sentence_model.encode([text])

        best_match = None
        best_score = 0.0
        best_command = "unknown"

        # Only check static commands (type 0)
        for command, data in self.command_templates.items():
            if data.get("type", 0) == 0:  # Static command
                embeddings = self.command_embeddings[command]
                similarities = cosine_similarity(input_embedding, embeddings)[0]
                max_similarity = np.max(similarities)

                if max_similarity > best_score:
                    best_score = max_similarity
                    best_command = command
                    best_match = command

        return {
            "intent": best_command,
            "confidence": float(best_score),
            "parameters": {},
            "response": self.command_templates.get(best_command, {}).get("response", "Command not recognized"),
            "threshold": self.command_templates.get(best_command, {}).get("confidence_threshold", 0.5)
        }
