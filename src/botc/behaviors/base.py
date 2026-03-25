# src/botc/behaviors/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from botc.enums import RoleName
from . import register_role

if TYPE_CHECKING:
    from botc.player import Player
    from botc.core.game import GameManager


class RoleBehavior(ABC):
    first_night_priority: Optional[int] = None
    other_night_priority: Optional[int] = None
    is_reliable: bool = True # Determine reliablity of information if poisioned/drunk

    @abstractmethod
    async def act(self, player: Player, game: GameManager) -> None:
        pass

@register_role(
    RoleName.BARON, RoleName.DRUNK, RoleName.RECLUSE, RoleName.SAINT,
    RoleName.VIRGIN, RoleName.SLAYER, RoleName.SOLDIER, RoleName.MAYOR
)
class PassiveBehavior(RoleBehavior):
    async def act(self, player: Player, game: GameManager) -> None:
        pass
