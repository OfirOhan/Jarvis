"""
Command implementations organized by category
"""

import time
import subprocess
import pyautogui
from typing import Dict, Any
from utils import normalize_key_name, SafetyChecker


class MediaCommands:
    """Media playback and volume control commands"""

    @staticmethod
    def play_pause(params: Dict[str, Any] = None) -> bool:
        """Toggle play/pause for media"""
        try:
            pyautogui.press('playpause')
            return True
        except Exception as e:
            print(f"Media play/pause error: {e}")
            return False

    @staticmethod
    def stremio_play_pause(params: Dict[str, Any] = None) -> bool:
        """Toggle play/pause specifically for Stremio"""
        try:
            # Focus Stremio window first, then send spacebar
            pyautogui.press('alt')
            pyautogui.press('tab')
            time.sleep(0.1)
            pyautogui.press('space')
            return True
        except Exception as e:
            print(f"Stremio play/pause error: {e}")
            return False

    @staticmethod
    def stremio_fullscreen(params: Dict[str, Any] = None) -> bool:
        """Toggle fullscreen in Stremio"""
        try:
            pyautogui.press('f')  # F key for fullscreen in most video players
            return True
        except Exception as e:
            print(f"Stremio fullscreen error: {e}")
            return False

    @staticmethod
    def next_song(params: Dict[str, Any] = None) -> bool:
        """Skip to next track"""
        try:
            pyautogui.press('nexttrack')
            return True
        except Exception as e:
            print(f"Next song error: {e}")
            return False

    @staticmethod
    def previous_song(params: Dict[str, Any] = None) -> bool:
        """Go to previous track"""
        try:
            pyautogui.press('prevtrack')
            return True
        except Exception as e:
            print(f"Previous song error: {e}")
            return False

    @staticmethod
    def volume_up(params: Dict[str, Any] = None) -> bool:
        """Increase system volume"""
        try:
            for _ in range(3):  # Increase by 3 steps
                pyautogui.press('volumeup')
            return True
        except Exception as e:
            print(f"Volume up error: {e}")
            return False

    @staticmethod
    def volume_down(params: Dict[str, Any] = None) -> bool:
        """Decrease system volume"""
        try:
            for _ in range(3):  # Decrease by 3 steps
                pyautogui.press('volumedown')
            return True
        except Exception as e:
            print(f"Volume down error: {e}")
            return False

    @staticmethod
    def mute(params: Dict[str, Any] = None) -> bool:
        """Toggle system mute"""
        try:
            pyautogui.press('volumemute')
            return True
        except Exception as e:
            print(f"Mute error: {e}")
            return False


class SystemCommands:
    """System control commands (shutdown, restart, sleep)"""

    def __init__(self):
        self.safety_checker = SafetyChecker()

    def shutdown(self, params: Dict[str, Any] = None) -> bool:
        """Shutdown the computer"""
        if not self.safety_checker.check_dangerous_command_safety("shutdown"):
            return False

        try:
            print("⚠️  Shutting down in 10 seconds...")
            subprocess.run(["shutdown", "/s", "/t", "10"])
            return True
        except Exception as e:
            print(f"Shutdown error: {e}")
            return False

    def restart(self, params: Dict[str, Any] = None) -> bool:
        """Restart the computer"""
        if not self.safety_checker.check_dangerous_command_safety("restart"):
            return False

        try:
            print("⚠️  Restarting in 10 seconds...")
            subprocess.run(["shutdown", "/r", "/t", "10"])
            return True
        except Exception as e:
            print(f"Restart error: {e}")
            return False

    @staticmethod
    def sleep(params: Dict[str, Any] = None) -> bool:
        """Put computer to sleep"""
        try:
            print("💤 Putting computer to sleep...")
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            return True
        except Exception as e:
            print(f"Sleep error: {e}")
            return False

    @staticmethod
    def get_time(params: Dict[str, Any] = None) -> bool:
        """Display current time"""
        try:
            current_time = time.strftime("%I:%M %p")
            print(f"Current time: {current_time}")
            return True
        except Exception as e:
            print(f"Get time error: {e}")
            return False


class AppCommands:
    """Application launching commands"""

    @staticmethod
    def open_stremio(params: Dict[str, Any] = None) -> bool:
        """Launch Stremio application"""
        try:
            subprocess.run(["start", "stremio://"], shell=True)
            return True
        except Exception as e:
            print(f"Open Stremio error: {e}")
            return False

    @staticmethod
    def open_notepad(params: Dict[str, Any] = None) -> bool:
        """Launch Notepad"""
        try:
            subprocess.Popen(["notepad"])
            return True
        except Exception as e:
            print(f"Open Notepad error: {e}")
            return False

    @staticmethod
    def open_calculator(params: Dict[str, Any] = None) -> bool:
        """Launch Calculator"""
        try:
            subprocess.Popen(["calc"])
            return True
        except Exception as e:
            print(f"Open Calculator error: {e}")
            return False

    @staticmethod
    def web_search(params: Dict[str, Any] = None) -> bool:
        """Search the web using default browser"""
        if not params or not params.get('content'):
            print("No search query provided")
            return False

        try:
            query = params['content']
            subprocess.Popen(
                f"start chrome https://www.google.com/search?q={query.replace(' ', '+')}",
                shell=True
            )
            return True
        except Exception as e:
            print(f"Web search error: {e}")
            return False


class TextCommands:
    """Text input and keyboard commands"""

    @staticmethod
    def write_text(params: Dict[str, Any] = None) -> bool:
        """Type text at current cursor position"""
        if not params or not params.get('content'):
            print("No text provided to write")
            return False

        try:
            text_to_write = params['content'].strip()
            pyautogui.write(text_to_write)
            print(f"Wrote: {text_to_write}")
            return True
        except Exception as e:
            print(f"Write text error: {e}")
            return False

    @staticmethod
    def press_button(params: Dict[str, Any] = None) -> bool:
        """Press keyboard keys or key combinations"""
        if not params or not params.get('content'):
            print("No key specified to press")
            return False

        try:
            key_to_press = params['content'].strip()
            # Normalize the key name
            normalized_key = normalize_key_name(key_to_press)

            # Handle key combinations (e.g., "ctrl+c", "alt+f4")
            if "+" in normalized_key:
                keys = normalized_key.split("+")
                pyautogui.hotkey(*keys)
                print(f"Pressed key combination: {normalized_key}")
            else:
                pyautogui.press(normalized_key)
                print(f"Pressed key: {normalized_key}")
            return True
        except Exception as e:
            print(f"Press button error '{params.get('content', '')}': {e}")
            return False


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
            "stremio_play_pause": self.media.stremio_play_pause,
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