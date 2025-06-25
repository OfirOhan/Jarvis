"""
AI components for intent classification and command template management with wake word system
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any, List, Optional
import re
import time
from datetime import datetime, timedelta

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
        "confidence_threshold": 0.6,
        "examples": [
            "volume up", "turn up volume", "increase volume", "louder",
            "make it louder", "turn it up", "raise volume", "boost volume"
        ],
        "response": "Turning up volume"
    },
    "volume_down": {
        "type": 0,
        "confidence_threshold": 0.6,
        "examples": [
            "volume down", "turn down volume", "decrease volume", "quieter",
            "make it quieter", "turn it down", "lower volume", "reduce volume"
        ],
        "response": "Turning down volume"
    },
    "open_notepad": {
        "type": 0,
        "confidence_threshold": 0.7,
        "examples": [
            "open notepad", "open text editor", "launch notepad", "start notepad",
            "open editor", "new document", "create document", "open notes"
        ],
        "response": "Opening Notepad"
    },
    "get_time": {
        "type": 0,
        "confidence_threshold": 0.6,
        "examples": [
            "what time is it", "current time", "tell me the time", "time",
            "what's the time", "check time", "show time", "time please"
        ],
        "response": "Getting current time"
    },
    "next_song": {
        "type": 0,
        "confidence_threshold": 0.6,
        "examples": [
            "next song", "skip song", "next track", "skip track", "next",
            "skip", "play next", "next music", "skip this song", "change song"
        ],
        "response": "Playing next song"
    },
    "previous_song": {
        "type": 0,
        "confidence_threshold": 0.6,
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
        "confidence_threshold": 0.85,
        "examples": [
            "shutdown", "shut down", "turn off computer", "power off",
            "shutdown computer", "turn off", "power down", "close computer"
        ],
        "response": "Shutting down computer"
    },
    "restart": {
        "type": 0,
        "confidence_threshold": 0.85,
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
        "confidence_threshold": 0.7,
        "examples": [
            "search for", "google", "look up", "find information about",
            "search the web for", "find", "look for", "search"
        ],
        "response": "Searching the web"
    },
    "write_text": {
        "type": 1,
        "confidence_threshold": 0.7,
        "examples": [
            "write", "type", "write text", "type text", "write down",
            "type this", "write this", "input text", "enter text"
        ],
        "response": "Writing text"
    },
    "press_button": {
        "type": 1,
        "confidence_threshold": 0.6,
        "examples": [
            "press", "hit", "push", "click", "press key", "hit key",
            "push button", "click button", "press the", "hit the"
        ],
        "response": "Pressing button"
    }
}

# Wake word configurations with examples like command templates
WAKE_WORD_CONFIG = {
    "wake_words": {
        "examples": [
            "nico", "niko", "nicole", "nicko", "neeko", "neco", "nik", "nick"
        ],
        "threshold": 0.75  # Slightly lower than activation phrases for flexibility
    },
    "activation_phrases": {
        "examples": [
            "hey nico", "hey niko", "hey nicole", "yo nico", "yo niko",
            "hello nico", "hello niko", "hi nico", "hi niko", "nico listen",
            "niko listen", "nico wake up", "niko wake up", "nico activate",
            "niko activate", "hey there nico", "hey there niko"
        ],
        "threshold": 0.8,  # Higher threshold for activation
        "response": "Hey sir"
    },
    "sleep_phrases": {
        "examples": [
            "go to sleep", "sleep mode", "deactivate", "stop listening",
            "nico sleep", "niko sleep", "nico stop", "niko stop", "shut up",
            "be quiet", "sleep now", "go away", "stop responding", "turn off",
            "nico off", "niko off", "disable", "quiet mode", "silent mode"
        ],
        "threshold": 0.8  # High threshold to avoid accidental deactivation
    },
    "activation_duration": 120,  # 2 minutes in seconds
}

# Stop words to ignore during processing
STOP_WORDS = {
    "please", "can", "you", "could", "would", "will", "should", "may", "might",
    "i", "want", "to", "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "for", "me", "my", "mine", "your",
    "yours", "his", "her", "hers", "its", "our", "ours", "their", "theirs",
    "this", "that", "these", "those", "of", "in", "on", "at", "by", "with",
    "from", "up", "about", "into", "through", "during", "before", "after",
    "above", "below", "to", "from", "over", "under", "again", "further", "then", "once", "now", "go", "get",
    "make", "let", "help", "assist", "try", "attempt"
}

# Compound command separators
COMPOUND_SEPARATORS = ["and", "then", "also", "plus", "after that", "next", "followed by"]


class IntentClassifier:
    """Simplified wake word system - just checks for 'Nico' or 'Hey Nico' at start"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        print("Loading local AI model...")
        self.sentence_model = SentenceTransformer(model_name)
        self.command_templates = COMMAND_TEMPLATES
        self.command_embeddings = {}
        self.stop_words = STOP_WORDS
        self.compound_separators = COMPOUND_SEPARATORS

        # Wake words - more variations for better recognition
        self.wake_words = [
            'hey nico', 'hey niko', 'hey nicole', 'hey nikko',
            'nico', 'niko', 'nicole', 'nikko', 'neko', 'nika'
        ]

        # Simple activation state
        self.is_active = False
        self.activation_end_time = None
        self.activation_duration = 120  # 2 minutes instead of 10 seconds

        self._compute_command_embeddings()
        print("Local AI model loaded.")

    def _compute_command_embeddings(self):
        """Pre-compute embeddings for all command examples"""
        print("Computing command embeddings...")
        for command, data in self.command_templates.items():
            embeddings = self.sentence_model.encode(data["examples"])
            self.command_embeddings[command] = embeddings

    def _has_wake_word(self, text: str) -> tuple[bool, str, bool, bool]:
        """Check if text starts with wake word and return remaining text + activation type"""
        text_lower = text.lower().strip()
        needs_voice_response = False
        needs_activation = False

        for wake_word in self.wake_words:
            if text_lower.startswith(wake_word):
                # "Hey Nico" variants trigger voice response + 2min activation
                if wake_word.startswith('hey'):
                    needs_voice_response = True
                    needs_activation = True
                # Plain "Nico" variants just execute command without activation
                else:
                    needs_voice_response = False
                    needs_activation = False

                # Remove wake word and return remaining text
                remaining = text[len(wake_word):].strip()
                return True, remaining, needs_voice_response, needs_activation

        return False, text, False, False

    def _remove_stop_words(self, text: str) -> str:
        """Remove stop words from text while preserving command structure"""
        words = text.split()
        filtered_words = [word for word in words if word not in self.stop_words]
        return " ".join(filtered_words)

    def _classify_single_intent(self, text: str) -> Dict[str, Any]:
        """Classify a single command"""
        print(f"DEBUG: Classifying: '{text}'")

        if not text.strip():
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "parameters": {},
                "response": "How can I help you?",
                "threshold": 0.5
            }

        cleaned_text = self._remove_stop_words(text)
        if not cleaned_text:
            cleaned_text = text

        # Check for dynamic commands (type 1)
        for command, data in self.command_templates.items():
            if data.get("type") == 1:
                for trigger in data["examples"]:
                    if trigger in text.lower():
                        extracted_text = text.lower().split(trigger, 1)[1].strip()
                        if extracted_text:
                            extracted_text = self._remove_stop_words(extracted_text)

                        parameters = {"content": extracted_text} if extracted_text else {}
                        return {
                            "intent": command,
                            "confidence": 0.9,
                            "parameters": parameters,
                            "response": data["response"],
                            "threshold": data.get("confidence_threshold", 0.7)
                        }

        # Use embeddings for static commands (type 0)
        input_embedding = self.sentence_model.encode([cleaned_text])

        best_score = 0.0
        best_command = "unknown"

        for command, data in self.command_templates.items():
            if data.get("type", 0) == 0:
                embeddings = self.command_embeddings[command]
                similarities = cosine_similarity(input_embedding, embeddings)[0]
                max_similarity = np.max(similarities)

                if max_similarity > best_score:
                    best_score = max_similarity
                    best_command = command

        return {
            "intent": best_command,
            "confidence": float(best_score),
            "parameters": {},
            "response": self.command_templates.get(best_command, {}).get("response", "Command not recognized"),
            "threshold": self.command_templates.get(best_command, {}).get("confidence_threshold", 0.5)
        }

    def _is_active(self) -> bool:
        """Check if assistant is currently active"""
        if not self.is_active or not self.activation_end_time:
            return False

        from datetime import datetime
        if datetime.now() >= self.activation_end_time:
            self.is_active = False
            self.activation_end_time = None
            print("DEBUG: Activation expired")
            return False

        return True

    def _activate(self):
        """Activate assistant for a short time"""
        from datetime import datetime, timedelta
        self.is_active = True
        self.activation_end_time = datetime.now() + timedelta(seconds=self.activation_duration)
        print(f"DEBUG: Assistant activated for {self.activation_duration} seconds")

    def process_audio_input(self, text: str) -> Dict[str, Any]:
        """Main method - simplified wake word processing with activation"""
        text = text.strip()
        print(f"DEBUG: Processing: '{text}' (Active: {self._is_active()})")

        # Check for wake word first
        has_wake, remaining_text, needs_voice_response, needs_activation = self._has_wake_word(text)

        if has_wake:
            print(f"DEBUG: Wake word detected, command: '{remaining_text}'")

            if needs_activation:
                self._activate()  # Only activate for "Hey Nico"

            if remaining_text:
                # Process the command immediately
                return self._classify_single_intent(remaining_text)
            else:
                # Just wake word, no command
                if needs_activation:
                    # "Hey Nico" - activate and respond
                    return {
                        "intent": "wake_word_only",
                        "confidence": 1.0,
                        "parameters": {},
                        "response": "Hello sir",
                        "threshold": 0.5,
                        "needs_voice_response": needs_voice_response
                    }
                else:
                    # Plain "Nico" with no command - do nothing
                    return {
                        "intent": "ignored",
                        "confidence": 0.0,
                        "parameters": {},
                        "response": "",
                        "threshold": 0.0
                    }

        # If no wake word but assistant is active, process command anyway
        elif self._is_active():
            print("DEBUG: No wake word but assistant is active - processing command")
            return self._classify_single_intent(text)

        else:
            # No wake word and not active - ignore
            return {
                "intent": "ignored",
                "confidence": 0.0,
                "parameters": {},
                "response": "",
                "threshold": 0.0
            }

    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Direct classification without wake word check"""
        return self._classify_single_intent(text)