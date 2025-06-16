"""
Local Smart Voice Assistant Package

A modular voice assistant that uses local AI models for intent classification
and command execution without requiring API calls.
"""

from core import Assistant
from ai import IntentClassifier
from commands import CommandRegistry

__version__ = "1.0.0"
__author__ = "Ofir Ohana"

__all__ = ["Assistant", "IntentClassifier", "CommandRegistry"]