# src/botc/__init__.py
"""
Blood on the Clocktower (botc) core engine package.
"""

# Expose the primary classes and enums at the package level 
# so they can be imported directly from 'botc'.
from .enums import Alignment, RoleClass, RoleName
from .player import Player
from .game import GameManager, GameMaster
from .utils import GameIO

# __all__ restricts what gets imported if someone uses `from botc import *`
__all__ = [
    "Alignment",
    "RoleClass",
    "RoleName",
    "Player",
    "GameManager",
    "GameMaster",
]
