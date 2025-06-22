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

    def execute_command(self, intent: str, params: Dict[str, Any] = None) -> bool:
        """Execute a command by name"""
        if intent not in self.command_map:
            print(f"Unknown command: {intent}")
            return False

        try:
            handler = self.command_map[intent]
            return handler(params)
        except Exception as e:
            print(f"Command execution error for '{intent}': {e}")
            return False

    def get_available_commands(self) -> list:
        """Get list of all available commands"""
        return list(self.command_map.keys())