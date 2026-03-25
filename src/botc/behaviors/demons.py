# src/botc/behaviors/demons.py
from __future__ import annotations       # 1. Add this!
from typing import TYPE_CHECKING         # 2. Add this!
if TYPE_CHECKING:                        # 3. Add this block!
    from botc.player import Player
    from botc.core.game import GameManager

from botc.enums import RoleName
from .base import RoleBehavior
from . import register_role


@register_role(RoleName.IMP)
class ImpBehavior(RoleBehavior):
    other_night_priority = 5

    async def act(self, player: Player, game: GameManager) -> None:
        prompt = f"\nWake {player.believed_role} ({player.player_name}). Who do they kill?"
        print(prompt)
        target = game.get_player_by_name()
        if target and not target.protected:
            target.alive = False
            game.killed_tonight = target 
            print(f"{target.player_name} died.")
        elif target and target.protected:
            print(f"{target.player_name} was protected by the Monk and survives.")
        print(f"Put {player.believed_role} to sleep.")
