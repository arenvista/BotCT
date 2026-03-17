# src/botc/behaviors/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from botc.enums import RoleName
from . import register_role

if TYPE_CHECKING:
    from botc.player import Player
    from botc.game import GameManager


class RoleBehavior(ABC):
    first_night_priority: Optional[int] = None
    other_night_priority: Optional[int] = None

    @abstractmethod
    def act(self, player: Player, game: GameManager) -> None:
        pass

@register_role(
    RoleName.BARON, RoleName.DRUNK, RoleName.RECLUSE, RoleName.SAINT,
    RoleName.VIRGIN, RoleName.SLAYER, RoleName.SOLDIER, RoleName.MAYOR
)
class PassiveBehavior(RoleBehavior):
    def act(self, player: Player, game: GameManager) -> None:
        pass
