"""
Core assistant functionality - main coordinator classes
"""

import speech_recognition as sr
import threading
import queue
import time
from typing import Dict, Any

from ai import IntentClassifier, COMMAND_TEMPLATES
from commands import CommandRegistry


class SpeechRecognizer:
    """Handles microphone input and speech recognition"""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False

        # Adjust for ambient noise once at startup
        with self.microphone as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source)
            print("Microphone ready!")

    def listen_continuous(self, command_queue: queue.Queue):
        """Continuous listening with proper resource management"""
        print("Starting continuous listening...")

        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)

                try:
                    # Recognize speech
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    print(f"Heard: {text}")

                    # Add to command queue for processing
                    command_queue.put(text)

                except sr.UnknownValueError:
                    pass  # Didn't understand audio
                except sr.RequestError as e:
                    print(f"Speech recognition error: {e}")
                    time.sleep(1)

            except sr.WaitTimeoutError:
                pass  # No audio within timeout, continue listening
            except Exception as e:
                print(f"Listening error: {e}")
                time.sleep(1)

    def start_listening(self, command_queue: queue.Queue):
        """Start listening in a separate thread"""
        self.is_listening = True
        listen_thread = threading.Thread(target=self.listen_continuous, args=(command_queue,), daemon=True)
        listen_thread.start()
        return listen_thread

    def stop_listening(self):
        """Stop the listening process"""
        self.is_listening = False


class CommandProcessor:
    """Handles command processing and execution pipeline"""

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.command_registry = CommandRegistry()
        self.is_processing = False

    def process_commands(self, command_queue: queue.Queue):
        """Process commands from the queue"""
        while self.is_processing:
            try:
                text = command_queue.get(timeout=1)
                print(f"Processing: {text}")

                # Classify intent using local AI
                intent_data = self.intent_classifier.classify_intent(text)
                command = intent_data['intent']
                confidence = intent_data['confidence']
                threshold = intent_data['threshold']
                params = intent_data.get('parameters', {})

                print(f"Intent: {command} (confidence: {confidence:.2f}, threshold: {threshold:.2f})")

                # Execute if confidence meets threshold
                if confidence >= threshold:
                    # Safety warning for dangerous commands
                    dangerous_commands = {"shutdown", "restart", "sleep"}
                    if command in dangerous_commands:
                        print(f"⚠️  Dangerous command detected: {command}")

                    success = self.command_registry.execute_command(command, params)
                    if success:
                        print(f"✓ {intent_data['response']}")
                    else:
                        print(f"✗ Failed to execute command")
                else:
                    print(f"Low confidence ({confidence:.2f} < {threshold:.2f}): Command ignored")

                command_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Command processing error: {e}")

    def start_processing(self, command_queue: queue.Queue):
        """Start command processing in a separate thread"""
        self.is_processing = True
        process_thread = threading.Thread(target=self.process_commands, args=(command_queue,), daemon=True)
        process_thread.start()
        return process_thread

    def stop_processing(self):
        """Stop the command processing"""
        self.is_processing = False

    def add_custom_command(self, command_name: str, examples: list, response: str):
        """Add a custom command to the system"""
        self.intent_classifier.add_custom_command(command_name, examples, response)


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
        print("  'add_command <name> \"<examples>\" \"<response>\"' - Add custom command")

        try:
            while self.is_running:
                command = input("> ").strip()

                if command == "":
                    break
                elif command == "status":
                    self._show_status()
                elif command.startswith("add_command"):
                    self._handle_add_command(command)
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

    def _handle_add_command(self, command: str):
        """Handle adding a custom command"""
        try:
            # Parse command: add_command test_cmd "test command,try this" "Testing command"
            parts = command.split('"')
            if len(parts) >= 3:
                cmd_name = parts[0].split()[1]
                examples = [ex.strip() for ex in parts[1].split(',')]
                response = parts[2] if len(parts) > 2 else f"Executing {cmd_name}"

                self.command_processor.add_custom_command(cmd_name, examples, response)
                print(f"✓ Added custom command: {cmd_name}")
            else:
                print("✗ Invalid format. Use: add_command <name> \"<examples>\" \"<response>\"")
        except Exception as e:
            print(f"✗ Error adding command: {e}")

    def stop(self):
        """Public method to stop the assistant"""
        self._stop()