# src/botc/enums.py
from enum import Enum
from typing import List

class Status(Enum):
    POISIONED = 1
    DRUNK = 2
    PROTECTED = 3
    def __str__(self):
        return self.name.title()

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
