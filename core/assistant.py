"""
Main assistant coordinator - orchestrates speech recognition and command processing
"""

import queue
import time

from .speech_recognizer import SpeechRecognizer
from .command_processor import CommandProcessor
from ai import COMMAND_TEMPLATES


class Assistant:
    """Main coordinator class for the voice assistant"""

    def __init__(self):
        self.speech_recognizer = SpeechRecognizer()
        self.command_processor = CommandProcessor()
        self.command_queue = queue.Queue()
        self.is_running = False

    def start(self):
        """Start the voice assistant"""
        print("=== Local AI Voice Assistant Starting ===")

        self.is_running = True

        # Start speech recognition
        listen_thread = self.speech_recognizer.start_listening(self.command_queue)

        # Start command processing
        process_thread = self.command_processor.start_processing(self.command_queue)

        # Display available commands
        self._show_available_commands()

        print("\nPress Enter to stop, or type commands:")
        print("  'status' - Show queue status")
        print("  'help' - Show all available commands")

        try:
            while self.is_running:
                command = input("> ").strip()

                if command == "":
                    break
                elif command == "status":
                    self._show_status()
                elif command == "help":
                    self._show_available_commands()
                else:
                    print("Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            pass

        print("Stopping voice assistant...")
        self._stop()

    def _stop(self):
        """Stop all components of the assistant"""
        self.is_running = False
        self.speech_recognizer.stop_listening()
        self.command_processor.stop_processing()

        # Wait a bit for threads to finish
        time.sleep(2)
        print("Voice assistant stopped.")

    def _show_status(self):
        """Show current status of the assistant"""
        print(f"Queue size: {self.command_queue.qsize()}")
        print(f"Listening: {self.speech_recognizer.is_listening}")
        print(f"Processing: {self.command_processor.is_processing}")

    def _show_available_commands(self):
        """Display all available voice commands"""
        print("\n=== Available Voice Commands ===")
        for cmd, data in COMMAND_TEMPLATES.items():
            examples = data['examples']
            print(f"  {cmd}: \"{examples[0]}\"")
            if len(examples) > 1:
                quote = '"'
                print(f"    (also: {', '.join([quote + ex + quote for ex in examples[1:3]])})")

    def stop(self):
        """Public method to stop the assistant"""
        self._stop()

