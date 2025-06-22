"""
Speech recognition module - handles microphone input and speech-to-text
"""

import speech_recognition as sr
import threading
import queue
import time


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
        listen_thread = threading.Thread(
            target=self.listen_continuous,
            args=(command_queue,),
            daemon=True
        )
        listen_thread.start()
        return listen_thread

    def stop_listening(self):
        """Stop the listening process"""
        self.is_listening = False