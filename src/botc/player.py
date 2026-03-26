from __future__ import annotations
from typing import TYPE_CHECKING

from botc.enums import Alignment, RoleClass, RoleName, Status, StatusItem
from botc.behaviors import BEHAVIOR_MAP
from botc.behaviors.base import PassiveBehavior

if TYPE_CHECKING:
    from botc.core.game import GameManager
    from botc.behaviors.base import RoleBehavior

class Player: 
    def __init__(self, player_name: str, believed_role: RoleName, registered_role: RoleName, registered_alignment: Alignment):
        self.player_name: str = player_name
        self.believed_role: RoleName = believed_role
        self.registered_role: RoleName = registered_role
        self.registered_alignment: Alignment = registered_alignment if registered_alignment else self._default_alignment()
        self.status: Status = Status()
        self.role_behavior: RoleBehavior = BEHAVIOR_MAP.get(self.believed_role, PassiveBehavior())

    def show_role(self):
        output = f"""Hi {self.player_name}, you are the {self.believed_role}"""
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

    def propose_candidate(self, game: GameManager):
        potential_candidates = [player for player in game.players if player.status.alive == True]
        selection = ""
        if selection:
            game.vote_table[self.player_name][selection] += 1
