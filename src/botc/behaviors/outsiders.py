# src/botc/behaviors/outsiders.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from botc.player import Player
    from botc.core.game import GameManager

import random

from botc.enums import RoleName

from . import register_role
from .base import RoleBehavior


@register_role(RoleName.BUTLER)
class ButlerBehavior(RoleBehavior):
    first_night_priority = 9
    other_night_priority = 10

    async def act(self, player: Player, game: GameManager):
        master = random.sample(game.get_players(), 1)[0]
        await game.send_message(
            player.username, f"Worship your lord, {master.username}"
        )
