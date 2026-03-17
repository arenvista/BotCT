# src/botc/behaviors/__init__.py
BEHAVIOR_MAP = {}

def register_role(*role_names):
    """Decorator to automatically register a behavior to one or more roles."""
    def decorator(cls):
        behavior_instance = cls()
        for role in role_names:
            BEHAVIOR_MAP[role] = behavior_instance
        return cls
    return decorator

# Import modules to trigger the decorators
from . import base, demons, minions, outsiders, townsfolk
