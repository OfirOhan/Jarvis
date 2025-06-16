#!/usr/bin/env python3
"""
Simple launch script for the Local Smart Voice Assistant
"""

from core import Assistant


def main():
    """Launch the voice assistant"""
    assistant = Assistant()
    assistant.start()


if __name__ == "__main__":
    main()