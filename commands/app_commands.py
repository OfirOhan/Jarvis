"""
Application Commands - Launch and control applications
"""

import subprocess
from typing import Dict, Any


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