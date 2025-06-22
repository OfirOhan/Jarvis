"""
Command processing module - handles intent classification and command execution
"""

import threading
import queue
import time

from ai import IntentClassifier
from commands.commnad_registry import CommandRegistry


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
        process_thread = threading.Thread(
            target=self.process_commands,
            args=(command_queue,),
            daemon=True
        )
        process_thread.start()
        return process_thread

    def stop_processing(self):
        """Stop the command processing"""
        self.is_processing = False
