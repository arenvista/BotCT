from __future__ import annotations
from typing import TYPE_CHECKING

from botc.enums import Alignment, RoleClass, RoleName, Status
from botc.behaviors import BEHAVIOR_MAP
from botc.behaviors.base import PassiveBehavior

if TYPE_CHECKING:
    from botc.core.game import GameManager
    from botc.behaviors.base import RoleBehavior

class Player: 
    def __init__(self, username: str, believed_role: RoleName, registered_role: RoleName, registered_alignment: Alignment):
        self.username: str = username
        self.believed_role: RoleName = believed_role
        self.registered_role: RoleName = registered_role
        self.registered_alignment: Alignment = registered_alignment if registered_alignment else self._default_alignment()
        self.status: Status = Status()
        self.role_behavior: RoleBehavior = BEHAVIOR_MAP.get(self.believed_role, PassiveBehavior())

    def show_role(self):
        output = f"""Hi {self.username}, you are the {self.believed_role}\n> ### How To Play:\nhttps://wiki.bloodontheclocktower.com/{self.believed_role}"""
        return output

    def _default_alignment(self) -> Alignment:
        if self.registered_role.role_class in (RoleClass.DEMONS, RoleClass.MINIONS):
            return Alignment.EVIL
        return Alignment.GOOD

    async def take_action(self, game: GameManager):
        if not self.status.alive and self.believed_role != RoleName.RAVENKEEPER:
            return
        await self.role_behavior.act(self, game)

    def _to_dict(self) -> dict:
        return {
            "registered_role": self.registered_role.name, 
            "believed_role": self.believed_role.name,
            "registered_role": self.registered_role.name,
            "registered_alignment": self.registered_alignment.name,
            "alive": self.status.alive,
            "poisoned": self.status.poisoned,
            "protected": self.status.protected
        }
