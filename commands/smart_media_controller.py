"""
Smart Media Controller - Handles media detection and control
"""

import time
import ctypes
import pyautogui
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Windows API constants
SW_RESTORE = 9


class SmartMediaController:
    """Precise media control with browser tab detection"""

    def __init__(self):
        self.user32 = ctypes.windll.user32

    def _find_window(self, app_name: str) -> Optional[int]:
        """Find application window handle"""
        try:
            window_hwnd = []

            def enum_windows_proc(hwnd, lParam):
                if self.user32.IsWindowVisible(hwnd):
                    length = self.user32.GetWindowTextLengthW(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    self.user32.GetWindowTextW(hwnd, buff, length + 1)

                    if app_name.lower() in buff.value.lower():
                        window_hwnd.append(hwnd)
                return True

            callback = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
            self.user32.EnumWindows(callback(enum_windows_proc), 0)

            return window_hwnd[0] if window_hwnd else None

        except Exception as e:
            logger.error(f"Window finding error: {e}")
            return None

    def _activate_window(self, hwnd: int) -> bool:
        """Activate and bring window to foreground"""
        try:
            if self.user32.IsIconic(hwnd):
                self.user32.ShowWindow(hwnd, SW_RESTORE)
            self.user32.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Window activation error: {e}")
            return False

    def _get_last_used_media(self) -> Optional[Dict[str, Any]]:
        """Find the media source user was last using"""
        media_sources = []

        # Check Stremio
        stremio_hwnd = self._find_window("stremio")
        if stremio_hwnd:
            media_sources.append({'type': 'stremio', 'hwnd': stremio_hwnd, 'name': 'Stremio'})

        # Check browsers
        browsers = ['chrome', 'firefox', 'edge', 'opera']
        music_sites = ['youtube music', 'music.youtube', 'spotify', 'soundcloud']
        video_sites = ['youtube', 'netflix', 'twitch', 'prime video']

        for browser in browsers:
            hwnd = self._find_window(browser)
            if hwnd:
                try:
                    length = self.user32.GetWindowTextLengthW(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    self.user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.lower()

                    print(f"[DEBUG] Found {browser} window: '{title}'")

                    # Check for media sites
                    is_music = any(site in title for site in music_sites)
                    is_video = any(site in title for site in video_sites) and not is_music

                    if is_music or is_video:
                        media_sources.append({
                            'type': 'browser_music' if is_music else 'browser_video',
                            'hwnd': hwnd,
                            'name': title,
                            'browser': browser
                        })
                        print(f"[DEBUG] Added media source: {title}")

                except Exception as e:
                    logger.error(f"Browser check error: {e}")

        if not media_sources:
            return None

        # Get currently focused window
        try:
            focused_hwnd = self.user32.GetForegroundWindow()

            # Check if user is currently on a media window
            for source in media_sources:
                if source['hwnd'] == focused_hwnd:
                    print(f"[DEBUG] User is currently on: {source['name']}")
                    return source

            # Return first media source found
            print(f"[DEBUG] Using first media source: {media_sources[0]['name']}")
            return media_sources[0]

        except Exception as e:
            logger.error(f"Focus detection error: {e}")
            return media_sources[0] if media_sources else None

    def control_stremio(self) -> bool:
        """Control Stremio"""
        stremio_hwnd = self._find_window("stremio")
        if not stremio_hwnd:
            return False

        if not self._activate_window(stremio_hwnd):
            return False

        try:
            time.sleep(0.2)
            pyautogui.press('space')
            return True
        except Exception as e:
            logger.error(f"Stremio control error: {e}")
            return False

    def control_browser_media(self, media_source: Dict[str, Any]) -> bool:
        """Control browser media"""
        try:
            if media_source['type'] == 'browser_music':
                pyautogui.press('playpause')
                print(f"[DEBUG] Used media key for: {media_source['name']}")
                return True
            elif media_source['type'] == 'browser_video':
                if self._activate_window(media_source['hwnd']):
                    time.sleep(0.2)
                    pyautogui.press('space')
                    print(f"[DEBUG] Used spacebar for: {media_source['name']}")
                    return True
        except Exception as e:
            logger.error(f"Browser control error: {e}")
        return False

    def smart_play_pause(self, params: Dict[str, Any] = None) -> bool:
        """Play/pause the media source user was last using"""

        # Find what user was last using
        user_media = self._get_last_used_media()

        if user_media:
            print(f"[DEBUG] Targeting: {user_media['name']} (type: {user_media['type']})")

            if user_media['type'] == 'stremio':
                return self.control_stremio()
            elif user_media['type'] in ['browser_music', 'browser_video']:
                return self.control_browser_media(user_media)

        # Fallback
        print("[DEBUG] No media detected, using media key fallback")
        try:
            pyautogui.press('playpause')
            return True
        except:
            return False