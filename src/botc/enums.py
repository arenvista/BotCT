# src/botc/enums.py
from enum import Enum
from typing import List, Optional

class StatusItem:
    def __init__(self, state: Optional[bool]):
        self.state = state
    def __invert__(self):
        """Allows using ~Status.POISONED to toggle the boolean inline."""
        self.state = not self.state
        return self
    def __repr__(self):
        # Makes it print out nicely like your original tuples
        return f"{self.state}"

class Status:
    # We replace the immutable tuples with our mutable StatusItem objects
    def __init__(self, poisoned: StatusItem, drunk: StatusItem, protected: StatusItem, alive: StatusItem):
        self.poisoned = StatusItem(False)
        self.drunk = StatusItem(False)
        self.protected = StatusItem(False)
        self.alive = StatusItem(True)

    def is_reliable(self) -> bool:
        return self.poisoned.state == False and self.drunk.state == False

    def is_protected(self) -> bool:
        return self.poisoned.state == False and self.protected.state == False

    def __eq__(self, other) -> bool:
        # Optional but highly recommended: ensure we are comparing to another Status (or similar) object
        if not isinstance(other, Status):
            return False

        # Loop via all members_vars in self
        for attr_name, my_status_item in vars(self).items():
            # Match var in other
            other_status_item = getattr(other, attr_name, None)
            # If other is not None
            if other_status_item is not None:
                # Comparte them
                if my_status_item.state != other_status_item.state:
                    return False 
        return True

    @classmethod
    def toggle_state(cls, status_name: str):
        """Allows toggling by passing the string name of the status."""
        # Fetch the attribute by string name, converting to uppercase just in case
        status_obj = getattr(cls, status_name.upper(), None)
        
        if isinstance(status_obj, StatusItem):
            # Toggle the inner state
            status_obj.state = not status_obj.state
            print(f"{status_name.upper()} toggled to {status_obj.state}")
        else:
            raise ValueError(f"Status '{status_name}' does not exist.")


class Alignment(Enum):
    GOOD = 1
    EVIL = 2
    def __str__(self):
        return self.name.title()

class RoleClass(Enum):
    GAMEMASTER = 0
    DEMONS = 1
    MINIONS = 2
    OUTSIDERS = 3
    TOWNSFOLK = 4

    @property
    def display_name(self) -> str: 
        return self.name.replace('_', ' ').title()
    def __str__(self): 
        return self.display_name

class RoleName(Enum):
    role_class: RoleClass

    def __new__(cls, value: int, role_class: RoleClass):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.role_class = role_class
        return obj

    # GameMaster/Storyteller
    GAMEMASTER = (0, RoleClass.GAMEMASTER)

    # Minions
    POISONER = (1, RoleClass.MINIONS)
    SPY = (2, RoleClass.MINIONS)
    BARON = (3, RoleClass.MINIONS)
    SCARLET_WOMAN = (4, RoleClass.MINIONS)

    # Outsiders
    BUTLER = (5, RoleClass.OUTSIDERS)
    DRUNK = (6, RoleClass.OUTSIDERS)
    RECLUSE = (7, RoleClass.OUTSIDERS)
    SAINT = (8, RoleClass.OUTSIDERS)

    # Townsfolk
    WASHERWOMAN = (9, RoleClass.TOWNSFOLK)
    LIBRARIAN = (10, RoleClass.TOWNSFOLK)
    INVESTIGATOR = (11, RoleClass.TOWNSFOLK)
    CHEF = (12, RoleClass.TOWNSFOLK)
    EMPATH = (13, RoleClass.TOWNSFOLK)
    FORTUNE_TELLER = (14, RoleClass.TOWNSFOLK)
    UNDERTAKER = (15, RoleClass.TOWNSFOLK)
    MONK = (16, RoleClass.TOWNSFOLK)
    RAVENKEEPER = (17, RoleClass.TOWNSFOLK)
    VIRGIN = (18, RoleClass.TOWNSFOLK)
    SLAYER = (19, RoleClass.TOWNSFOLK)
    SOLDIER = (20, RoleClass.TOWNSFOLK)
    MAYOR = (21, RoleClass.TOWNSFOLK)

    # Demons
    IMP = (22, RoleClass.DEMONS)

    @property
    def display_name(self) -> str: 
        return self.name.replace('_', ' ').title()

    def __str__(self): 
        return self.display_name

    @classmethod
    def get_by_class(cls, target_class: RoleClass) -> List['RoleName']:
        return [role for role in cls if role.role_class == target_class]
