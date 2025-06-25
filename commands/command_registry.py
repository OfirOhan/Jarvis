"""
Command Registry - Central registry for all available commands
"""

import logging
from typing import Dict, Any

from .media_commands import MediaCommands
from .system_commands import SystemCommands
from .app_commands import AppCommands
from .text_commands import TextCommands

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CommandRegistry:
    """Registry for all available commands"""

    def __init__(self):
        # Initialize command handlers
        self.media = MediaCommands()
        self.system = SystemCommands()
        self.apps = AppCommands()
        self.text = TextCommands()

        # Map command names to their handlers
        self.command_map = {
            # Media commands
            "play_pause": self.media.play_pause,
            "youtube_music_play_pause": self.media.youtube_music_play_pause,
            "youtube_play_pause": self.media.youtube_play_pause,
            "music_play_pause": self.media.music_play_pause,
            "stremio_fullscreen": self.media.stremio_fullscreen,
            "next_song": self.media.next_song,
            "previous_song": self.media.previous_song,
            "volume_up": self.media.volume_up,
            "volume_down": self.media.volume_down,
            "mute": self.media.mute,

            # System commands
            "shutdown": self.system.shutdown,
            "restart": self.system.restart,
            "sleep": self.system.sleep,
            "get_time": self.system.get_time,

            # App commands
            "open_stremio": self.apps.open_stremio,
            "open_notepad": self.apps.open_notepad,
            "open_calculator": self.apps.open_calculator,
            "web_search": self.apps.web_search,

            # Text commands
            "write_text": self.text.write_text,
            "press_button": self.text.press_button,
        }

    def execute_command(self, intent: str, params: Dict[str, Any] = None, log_intent: bool = True) -> bool:
        """
        Execute a command or compound commands by name.
        Supports compound commands returned by the AI model.
        Cleans up dynamic parameters like 'content' before passing them to handlers.
        log_intent: If False, suppress logging the top-level intent to avoid duplicate logs.
        """
        # 1. Handle compound commands
        if intent == "compound_command":
            if params and isinstance(params.get("commands"), list):
                logger.info(f"Executing compound command sequence ({len(params['commands'])} commands)")
                all_success = True
                for sub_cmd in params["commands"]:
                    sub_intent = sub_cmd.get("intent")
                    sub_params = sub_cmd.get("parameters", {}) or {}
                    sub_confidence = sub_cmd.get("confidence")
                    sub_threshold = sub_cmd.get("threshold")

                    if isinstance(sub_params, dict) and "content" in sub_params:
                        sub_params["content"] = sub_params["content"].strip()

                    logger.info(
                        f"Executing sub-intent '{sub_intent}' (confidence={sub_confidence:.2f}, threshold={sub_threshold:.2f})"
                    )
                    success = self.execute_command(sub_intent, sub_params, log_intent=False)
                    all_success = all_success and success
                return all_success
            else:
                logger.warning("Compound command intent received, but no subcommands found!")
                return False

        # 2. Handle single commands
        if intent not in self.command_map:
            logger.error(f"Unknown command: {intent}")
            return False

        try:
            handler = self.command_map[intent]

            if params and isinstance(params, dict) and "content" in params:
                params["content"] = params["content"].strip()

            # Log the top-level intent execution only if log_intent is True
            if log_intent:
                logger.info(f"Executing intent '{intent}' with params={params}")

            return handler(params)
        except Exception as e:
            logger.exception(f"Command execution error for '{intent}': {e}")
            return False

    def get_available_commands(self) -> list:
        """Get list of all available commands"""
        return list(self.command_map.keys())