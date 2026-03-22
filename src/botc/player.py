from __future__ import annotations
from typing import TYPE_CHECKING

from botc.enums import Alignment, RoleClass, RoleName
from botc.behaviors import BEHAVIOR_MAP
from botc.behaviors.base import PassiveBehavior

if TYPE_CHECKING:
    from botc.game import GameManager
    from botc.behaviors.base import RoleBehavior

class Player: 
    def __init__(self, player_name: str, actual_role: RoleName, believed_role: RoleName | None = None, registered_role: RoleName | None = None, registered_alignment: Alignment | None = None):
        self.player_name: str = player_name
        self.actual_role: RoleName = actual_role
        self.believed_role: RoleName = believed_role if believed_role else actual_role
        self.registered_role: RoleName = registered_role if registered_role else actual_role
        self.registered_alignment: Alignment = registered_alignment if registered_alignment else self._default_alignment()
        self.alive: bool = True
        self.poisoned: bool = False
        self.protected: bool = False
        self.role_behavior: RoleBehavior = BEHAVIOR_MAP.get(self.believed_role, PassiveBehavior())

    def _default_alignment(self) -> Alignment:
        if self.actual_role.role_class in (RoleClass.DEMONS, RoleClass.MINIONS):
            return Alignment.EVIL
        return Alignment.GOOD

    def take_action(self, game: GameManager):
        if not self.alive and self.believed_role != RoleName.RAVENKEEPER:
            return
        self.role_behavior.act(self, game)

    def _to_dict(self) -> dict:
        return {
            "actual_role": self.actual_role.name, 
            "believed_role": self.believed_role.name,
            "registered_role": self.registered_role.name,
            "registered_alignment": self.registered_alignment.name,
            "alive": self.alive,
            "poisoned": self.poisoned,
            "protected": self.protected
        }

    def propose_candidate(self, game: GameManager):
        potential_candidates = [player for player in game.players if player.alive == True]
        selection = ""
        if selection:
            game.vote_table[self.player_name][selection] += 1
