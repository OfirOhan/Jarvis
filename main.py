import speech_recognition as sr
import json
import os
import time
import subprocess
import pyautogui
from typing import Dict, Any, Optional
import threading
import queue
import re

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class LocalSmartVoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.command_queue = queue.Queue()

        # Load local sentence transformer model for intent matching
        print("Loading local AI model...")
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast model

        # Define command templates with examples
        self.command_templates = {
            "open_spotify": {
                "examples": [
                    "open spotify", "start spotify", "launch spotify", "play spotify",
                    "open music", "start music", "launch music app", "play music"
                ],
                "response": "Opening Spotify"
            },
            "play_pause": {
                "examples": [
                    "play", "pause", "play pause", "stop", "resume", "start playing",
                    "pause music", "resume music", "toggle play", "hit play"
                ],
                "response": "Playing/pausing media"
            },
            "volume_up": {
                "examples": [
                    "volume up", "turn up volume", "increase volume", "louder",
                    "make it louder", "turn it up", "raise volume", "boost volume"
                ],
                "response": "Turning up volume"
            },
            "volume_down": {
                "examples": [
                    "volume down", "turn down volume", "decrease volume", "quieter",
                    "make it quieter", "turn it down", "lower volume", "reduce volume"
                ],
                "response": "Turning down volume"
            },
            "open_chrome": {
                "examples": [
                    "open chrome", "open browser", "launch chrome", "start chrome",
                    "open google", "start browser", "launch browser", "open web"
                ],
                "response": "Opening Chrome"
            },
            "open_notepad": {
                "examples": [
                    "open notepad", "open text editor", "launch notepad", "start notepad",
                    "open editor", "new document", "create document", "open notes"
                ],
                "response": "Opening Notepad"
            },
            "web_search": {
                "examples": [
                    "search for", "google", "look up", "find information about",
                    "search the web for", "find", "look for", "search"
                ],
                "response": "Searching the web"
            },
            "get_time": {
                "examples": [
                    "what time is it", "current time", "tell me the time", "time",
                    "what's the time", "check time", "show time", "time please"
                ],
                "response": "Getting current time"
            },
            "shutdown": {
                "examples": [
                    "shutdown", "shut down", "turn off computer", "power off",
                    "shutdown computer", "turn off", "power down", "close computer"
                ],
                "response": "Shutting down computer"
            },
            "restart": {
                "examples": [
                    "restart", "reboot", "restart computer", "reboot computer",
                    "restart system", "reboot system", "refresh computer"
                ],
                "response": "Restarting computer"
            }
        }

        # Pre-compute embeddings for all command examples
        self.command_embeddings = {}
        self._compute_command_embeddings()

        # Adjust for ambient noise once at startup
        with self.microphone as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source)
            print("Ready! Local AI model loaded.")

    def _compute_command_embeddings(self):
        """Pre-compute embeddings for all command examples"""
        print("Computing command embeddings...")
        for command, data in self.command_templates.items():
            embeddings = self.sentence_model.encode(data["examples"])
            self.command_embeddings[command] = embeddings

    def classify_intent_local(self, text: str) -> Dict[str, Any]:
        """Use local AI to classify intent without API calls"""
        text = text.lower().strip()

        # Encode the input text
        input_embedding = self.sentence_model.encode([text])

        best_match = None
        best_score = 0.0
        best_command = "unknown"

        # Compare with all command embeddings
        for command, embeddings in self.command_embeddings.items():
            # Calculate similarity with all examples for this command
            similarities = cosine_similarity(input_embedding, embeddings)[0]
            max_similarity = np.max(similarities)

            if max_similarity > best_score:
                best_score = max_similarity
                best_command = command
                best_match = command

        # Extract parameters for certain commands
        parameters = {}
        if best_command == "web_search" and best_score > 0.6:
            # Extract search query
            search_triggers = ["search for", "google", "look up", "find"]
            for trigger in search_triggers:
                if trigger in text:
                    query = text.split(trigger, 1)[1].strip()
                    if query:
                        parameters["query"] = query
                        break

        return {
            "intent": best_command,
            "confidence": float(best_score),
            "parameters": parameters,
            "response": self.command_templates.get(best_command, {}).get("response", "Command not recognized")
        }

    def execute_command(self, intent_data: Dict[str, Any]) -> bool:
        """Execute the classified command"""
        intent = intent_data["intent"]
        params = intent_data.get("parameters", {})

        try:
            if intent == "open_spotify":
                # Try multiple possible Spotify paths
                spotify_paths = [
                    r'C:\Users\ofiri\AppData\Roaming\Spotify\Spotify.exe',
                    r'C:\Program Files\Spotify\Spotify.exe',
                    r'C:\Program Files (x86)\Spotify\Spotify.exe'
                ]

                for path in spotify_paths:
                    if os.path.exists(path):
                        subprocess.Popen([path])
                        time.sleep(3)
                        pyautogui.press('space')  # Auto-play
                        return True

                # If no Spotify found, try opening via start menu
                subprocess.run(["start", "spotify:"], shell=True)
                return True

            elif intent == "play_pause":
                pyautogui.press('playpause')
                return True

            elif intent == "volume_up":
                for _ in range(3):  # Increase by 3 steps
                    pyautogui.press('volumeup')
                return True

            elif intent == "volume_down":
                for _ in range(3):  # Decrease by 3 steps
                    pyautogui.press('volumedown')
                return True

            elif intent == "open_chrome":
                try:
                    subprocess.Popen(["chrome"])
                except:
                    subprocess.Popen(["start", "chrome"], shell=True)
                return True

            elif intent == "open_notepad":
                subprocess.Popen(["notepad"])
                return True

            elif intent == "web_search":
                query = params.get("query", "")
                if query:
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    subprocess.Popen(["start", search_url], shell=True)
                    return True
                else:
                    subprocess.Popen(["start", "https://www.google.com"], shell=True)
                    return True

            elif intent == "get_time":
                current_time = time.strftime("%I:%M %p")
                print(f"Current time: {current_time}")
                return True

            elif intent == "shutdown":
                print("Shutting down in 10 seconds...")
                subprocess.run(["shutdown", "/s", "/t", "10"])
                return True

            elif intent == "restart":
                print("Restarting in 10 seconds...")
                subprocess.run(["shutdown", "/r", "/t", "10"])
                return True

        except Exception as e:
            print(f"Command execution error: {e}")
            return False

        return False

    def listen_continuous(self):
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
                    self.command_queue.put(text)

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

    def process_commands(self):
        """Process commands from the queue"""
        while self.is_listening:
            try:
                # Get command from queue with timeout
                text = self.command_queue.get(timeout=1)

                print(f"Processing: {text}")

                # Use local AI to classify intent
                intent_data = self.classify_intent_local(text)
                print(f"Intent: {intent_data['intent']} (confidence: {intent_data['confidence']:.2f})")

                # Only execute if confidence is high enough
                if intent_data["confidence"] > 0.5:  # Lower threshold for local model
                    success = self.execute_command(intent_data)
                    if success:
                        print(f"✓ {intent_data['response']}")
                    else:
                        print(f"✗ Failed to execute command")
                else:
                    print(f"Low confidence ({intent_data['confidence']:.2f}): {intent_data['response']}")

                self.command_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Command processing error: {e}")

    def add_custom_command(self, command_name: str, examples: list, response: str):
        """Add a new custom command"""
        self.command_templates[command_name] = {
            "examples": examples,
            "response": response
        }
        # Recompute embeddings
        embeddings = self.sentence_model.encode(examples)
        self.command_embeddings[command_name] = embeddings
        print(f"Added custom command: {command_name}")

    def start(self):
        """Start the voice assistant"""
        self.is_listening = True

        # Start listening thread
        listen_thread = threading.Thread(target=self.listen_continuous, daemon=True)
        listen_thread.start()

        # Start command processing thread
        process_thread = threading.Thread(target=self.process_commands, daemon=True)
        process_thread.start()

        print("\n=== Local AI Voice Assistant Started ===")
        print("Available commands:")
        for cmd, data in self.command_templates.items():
            print(f"  {cmd}: {data['examples'][0]}")
        print("\nPress Enter to stop, or type 'status' for info")

        try:
            while True:
                command = input("> ").strip()
                if command == "":
                    break
                elif command == "status":
                    print(f"Queue size: {self.command_queue.qsize()}")
                elif command.startswith("add_command"):
                    # Example: add_command test_cmd "test command,try this" "Testing command"
                    parts = command.split('"')
                    if len(parts) >= 3:
                        cmd_name = parts[0].split()[1]
                        examples = [ex.strip() for ex in parts[1].split(',')]
                        response = parts[2]
                        self.add_custom_command(cmd_name, examples, response)
        except KeyboardInterrupt:
            pass

        print("Stopping voice assistant...")
        self.is_listening = False

        # Wait a bit for threads to finish
        time.sleep(2)


def main():
    assistant = LocalSmartVoiceAssistant()
    assistant.start()


if __name__ == "__main__":
    main()