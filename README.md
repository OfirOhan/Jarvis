# Local Smart Voice Assistant

A modular voice assistant that uses local AI models for intent classification and command execution without requiring API calls.

## Features

- **Local AI Processing**: Uses SentenceTransformers for intent classification
- **Modular Architecture**: Clean separation of concerns
- **Voice Commands**: Media control, system commands, app launching, text input
- **Safety Features**: Cooldown periods for dangerous commands
- **Extensible**: Easy to add custom commands

## Project Structure

```
voice_assistant/
├── __init__.py         # Package initialization
├── main.py             # Simple launch script
├── core.py             # Core assistant functionality
│   ├── Assistant       # Main coordinator class
│   ├── SpeechRecognizer # Microphone/listening
│   └── CommandProcessor # Execution pipeline
├── commands.py         # All command implementations
│   ├── MediaCommands   # Play, pause, volume
│   ├── SystemCommands  # Shutdown, restart
│   ├── AppCommands     # Stremio, calculator
│   └── TextCommands    # Typing, key presses
├── ai.py               # Intelligence components
│   ├── IntentClassifier # Sentence transformer model
│   └── COMMAND_TEMPLATES # Command definitions
└── utils.py            # Shared utilities
    ├── normalize_key_name # Key mapping
    └── SafetyChecker    # Dangerous command handling
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the assistant:
```bash
python -m voice_assistant.main
```

## Available Commands

### Media Commands
- "play", "pause", "play pause" - Toggle media playback
- "next song", "skip" - Next track
- "previous song", "go back" - Previous track
- "volume up", "louder" - Increase volume
- "volume down", "quieter" - Decrease volume
- "mute" - Toggle mute

### Stremio Commands
- "open stremio" - Launch Stremio
- "stremio play", "stremio pause" - Control Stremio playback
- "stremio fullscreen" - Toggle fullscreen

### System Commands
- "shutdown", "turn off computer" - Shutdown (with safety delay)
- "restart", "reboot" - Restart (with safety delay)
- "sleep" - Put computer to sleep
- "what time is it" - Show current time

### App Commands
- "open notepad" - Launch Notepad
- "open calculator" - Launch Calculator
- "search for [query]" - Web search

### Text Commands
- "write [text]" - Type text
- "press [key]" - Press keyboard keys (e.g., "press enter", "press alt f4")

## Safety Features

- **Dangerous Command Cooldown**: Shutdown/restart commands have a 10-second cooldown
- **High Confidence Thresholds**: Dangerous commands require higher confidence (0.85)
- **Safety Warnings**: Visual warnings for potentially harmful commands

## Adding Custom Commands

You can add custom commands at runtime:
```
> add_command test_cmd "test command,try this" "Testing command"
```

## Configuration

Edit `ai.py` to modify:
- Command templates and thresholds
- AI model selection
- Command examples

Edit `utils.py` to modify:
- Safety settings
- Key mappings

## Requirements

- Python 3.7+
- Microphone access
- Internet connection (for speech recognition)
- Windows OS (for system commands)