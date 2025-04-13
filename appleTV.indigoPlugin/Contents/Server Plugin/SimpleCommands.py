from enum import Enum
from typing import Dict


class SimpleCommands(str, Enum):
    """Additional simple commands of the Apple TV not covered by media-player features."""

    def __new__(cls, value, description):
        # Create the enum member instance.
        obj = str.__new__(cls, value)
        obj._value_ = value
        # Store the description in a custom attribute.
        obj.description = description
        return obj

    TOP_MENU = ("TOP_MENU", "Go to home screen.")
    APP_SWITCHER = ("APP_SWITCHER", "Show running applications.")
    SCREENSAVER = ("SCREENSAVER", "Run screensaver.")
    SKIP_FORWARD = ("SKIP_FORWARD", "Skip forward a time interval.")
    SKIP_BACKWARD = ("SKIP_BACKWARD", "Skip backward a time interval.")
    SWIPE_LEFT = ("SWIPE_LEFT", "Swipe left using Companion protocol.")
    SWIPE_RIGHT = ("SWIPE_RIGHT", "Swipe right using Companion protocol.")
    SWIPE_UP = ("SWIPE_UP", "Swipe up using Companion protocol.")
    SWIPE_DOWN = ("SWIPE_DOWN", "Swipe down using Companion protocol.")
    CHANNEL_UP = ("CHANNEL_UP", "Channel up using Companion protocol.")
    CHANNEL_DOWN = ("CHANNEL_DOWN", "Channel down using Companion protocol.")

def enum_to_dict() -> Dict[str, str]:
    """
    Convert the SimpleCommands enum into a dictionary where each key is the command name
    and the value is the command's description.

    Returns:
        Dict[str, str]: A dictionary mapping each command to its description.
    """
    return {command.name: command.description for command in SimpleCommands}