"""
Media Commands - High-level media control commands
"""

import pyautogui
from typing import Dict, Any
from .smart_media_controller import SmartMediaController


class MediaCommands:
    """Enhanced media commands with smart detection for specific apps"""

    def __init__(self):
        self.controller = SmartMediaController()

    def play_pause(self, params: Dict[str, Any] = None) -> bool:
        return self.controller.smart_play_pause(params)

    def youtube_music_play_pause(self, params: Dict[str, Any] = None) -> bool:
        return self.controller.control_media_key()

    def youtube_play_pause(self, params: Dict[str, Any] = None) -> bool:
        return self.controller.control_browser_media()

    def stremio_play_pause(self, params: Dict[str, Any] = None) -> bool:
        return self.controller.control_stremio()

    def music_play_pause(self, params: Dict[str, Any] = None) -> bool:
        return self.controller.control_media_key()

    @staticmethod
    def stremio_fullscreen(params: Dict[str, Any] = None) -> bool:
        try:
            pyautogui.press('f')
            return True
        except Exception as e:
            print(f"Stremio fullscreen error: {e}")
            return False

    @staticmethod
    def next_song(params: Dict[str, Any] = None) -> bool:
        try:
            pyautogui.press('nexttrack')
            return True
        except Exception as e:
            print(f"Next song error: {e}")
            return False

    @staticmethod
    def previous_song(params: Dict[str, Any] = None) -> bool:
        try:
            pyautogui.press('prevtrack')
            return True
        except Exception as e:
            print(f"Previous song error: {e}")
            return False

    @staticmethod
    def volume_up(params: Dict[str, Any] = None) -> bool:
        try:
            for _ in range(5):
                pyautogui.press('volumeup')
            return True
        except Exception as e:
            print(f"Volume up error: {e}")
            return False

    @staticmethod
    def volume_down(params: Dict[str, Any] = None) -> bool:
        try:
            for _ in range(5):
                pyautogui.press('volumedown')
            return True
        except Exception as e:
            print(f"Volume down error: {e}")
            return False

    @staticmethod
    def mute(params: Dict[str, Any] = None) -> bool:
        try:
            pyautogui.press('volumemute')
            return True
        except Exception as e:
            print(f"Mute error: {e}")
            return False