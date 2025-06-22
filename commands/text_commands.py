"""
Text Commands - Text input and keyboard control
"""

import pyautogui
from typing import Dict, Any
from utils import normalize_key_name


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