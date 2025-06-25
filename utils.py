"""
Shared utilities for the voice assistant
"""

import time
from typing import Set


def normalize_key_name(key_text: str) -> str:
    """Normalize spoken key names to pyautogui key names"""
    key_text = key_text.lower().strip()

    # Only map the few cases where spoken name differs from pyautogui name
    key_mappings = {
        "return": "enter",
        "spacebar": "space",
        "escape": "esc",
        "del": "delete",
        "control": "ctrl",
        "windows": "win",
        "page up": "pageup",
        "page down": "pagedown",
        "caps lock": "capslock",
        "num lock": "numlock",
        "scroll lock": "scrolllock",
        "print screen": "printscreen",
        "break": "pause",
        # Arrow key variations
        "up arrow": "up",
        "down arrow": "down",
        "left arrow": "left",
        "right arrow": "right",
        "arrow up": "up",
        "arrow down": "down",
        "arrow left": "left",
        "arrow right": "right",
        # Number words
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
    }

    # Handle combinations like "alt f4", "ctrl c", etc.
    words = key_text.split()
    if len(words) > 1:
        mapped_keys = []
        for word in words:
            mapped_keys.append(key_mappings.get(word, word))
        return "+".join(mapped_keys)

    # Single key - return mapped version or original
    return key_mappings.get(key_text, key_text)


class SafetyChecker:
    """Handles dangerous command safety checks"""

    def __init__(self, dangerous_commands: Set[str] = None, cooldown_seconds: int = 20):
        self.dangerous_commands = dangerous_commands or {"shutdown", "restart"}
        self.cooldown_seconds = cooldown_seconds
        self.last_dangerous_command_time = 0

    def check_dangerous_command_safety(self, command: str) -> bool:
        """Check if a dangerous command can be executed safely"""
        if command not in self.dangerous_commands:
            return True

        current_time = time.time()
        if current_time - self.last_dangerous_command_time < self.cooldown_seconds:
            remaining = self.cooldown_seconds - (current_time - self.last_dangerous_command_time)
            print(f"⚠️  Dangerous command on cooldown. Wait {remaining:.1f} more seconds.")
            return False

        self.last_dangerous_command_time = current_time
        return True