"""
FIXED CommandProcessor implementation with wake word and command execution
"""

import threading
import queue
import time
import pyttsx3
from typing import Dict, Any, Optional
from ai import IntentClassifier
from commands.command_registry import CommandRegistry


class CommandProcessor:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.command_registry = CommandRegistry()
        self.is_processing = False
        self._init_tts()

    def _init_tts(self):
        """Initialize text-to-speech engine"""
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        # Test TTS initialization
        try:
            # Use a different approach to test TTS
            voices = self.tts_engine.getProperty('voices')
            print(f"TTS initialized with {len(voices) if voices else 0} voices")
        except Exception as e:
            print(f"TTS Initialization Error: {e}")

    def _speak(self, text: str):
        """Handle voice responses - ONLY if text is provided"""
        if text and text.strip():  # Only speak if there's actual text
            print(f"ASSISTANT: {text}")
            try:
                # Stop any current speech first
                try:
                    self.tts_engine.stop()
                except:
                    pass

                # Run TTS in a separate thread to prevent blocking
                import threading
                def speak_async():
                    try:
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    except Exception as e:
                        print(f"TTS Error: {e}")

                tts_thread = threading.Thread(target=speak_async, daemon=True)
                tts_thread.start()

            except Exception as e:
                print(f"TTS Thread Error: {e}")

    def _execute_command(self, result: Dict[str, Any]):
        """Execute a validated command"""
        print(f"EXECUTING COMMAND: {result['intent']}")

        # Execute through registry
        success = self.command_registry.execute_command(
            result['intent'],
            result.get('parameters', {})
        )

        if success:
            print(f"Command '{result['intent']}' executed successfully")
            # Don't speak responses for commands - only for wake word
        else:
            print(f"Command '{result['intent']}' failed")
            # Don't speak error messages either to avoid interrupting media

    def process_commands(self, command_queue: queue.Queue):
        """Main processing loop - SIMPLIFIED"""
        print("DEBUG: Command processor thread started")
        while self.is_processing:
            try:
                text = command_queue.get(timeout=1)
                print(f"\n=== PROCESSING COMMAND ===")
                print(f"Heard: {text}")

                try:
                    # Process through wake word system
                    result = self.intent_classifier.process_audio_input(text)
                    print(f"Intent: {result['intent']} (Confidence: {result['confidence']:.2f})")

                    # Handle different intent types
                    if result['intent'] == 'ignored':
                        # No wake word detected - do nothing
                        print("DEBUG: No wake word - ignoring")

                    elif result['intent'] == 'wake_word_only':
                        # Just wake word, no command
                        print("DEBUG: Wake word only - responding")
                        # Only speak if it needs voice response (Hey Nico)
                        if result.get('needs_voice_response', False):
                            self._speak(result['response'])

                    elif result['confidence'] >= result['threshold']:
                        # Valid command with good confidence
                        print(f"DEBUG: Command meets threshold - executing: {result['intent']}")
                        print(f"DEBUG: Confidence: {result['confidence']:.3f} >= Threshold: {result['threshold']}")
                        self._execute_command(result)

                    else:
                        # Low confidence command - don't speak to avoid interrupting
                        print(f"DEBUG: Low confidence - {result['confidence']:.2f} < {result['threshold']}")

                except Exception as e:
                    print(f"ERROR in command processing: {e}")
                    import traceback
                    traceback.print_exc()

                print("DEBUG: Command processing complete")
                command_queue.task_done()

            except queue.Empty:
                # This is normal - just continue
                continue
            except Exception as e:
                print(f"CRITICAL ERROR in command loop: {e}")
                import traceback
                traceback.print_exc()
                try:
                    command_queue.task_done()
                except:
                    pass

    def start_processing(self, command_queue: queue.Queue):
        """Start the processing thread"""
        self.is_processing = True
        process_thread = threading.Thread(
            target=self.process_commands,
            args=(command_queue,),
            daemon=True
        )
        process_thread.start()
        return process_thread

    def stop_processing(self):
        """Stop command processing"""
        self.is_processing = False

    def print_commands(self):
        """Debug: Show registered commands"""
        print("\nRegistered Commands:")
        for cmd in self.command_registry.get_available_commands():
            print(f"- {cmd}")