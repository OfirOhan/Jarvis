"""
System Commands - System control and utilities
"""

import time
import subprocess
from typing import Dict, Any
from utils import SafetyChecker


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