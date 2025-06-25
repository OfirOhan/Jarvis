"""
Speech recognition module - handles microphone input and speech-to-text
"""

import speech_recognition as sr
import queue


class SpeechRecognizer:
    """Handles microphone input and speech recognition"""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.stop_listening_func = None

        with self.microphone as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            print("Microphone ready!")

    def start_listening(self, command_queue: queue.Queue):
        """Start listening continuously in the background"""

        def callback(recognizer, audio):
            """Called when speech is recognized"""
            try:
                text = recognizer.recognize_google(audio, language='en-US')
                if text:
                    print(f"Heard: {text}")
                    command_queue.put(text)
            except sr.UnknownValueError:
                pass  # ignore if speech wasn't clear
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")

        # 🟡 CHANGED — background listener provided by SpeechRecognition
        self.stop_listening_func = self.recognizer.listen_in_background(
            self.microphone,
            callback
        )
        print("Listening in background...")

    def stop_listening(self):
        """Stop the background listening process"""  # 🟡 CHANGED — stops background listener
        if self.stop_listening_func:
            self.stop_listening_func(wait_for_stop=False)
            self.stop_listening_func = None
            print("Stopped listening")
