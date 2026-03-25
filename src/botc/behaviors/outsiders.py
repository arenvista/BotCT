# src/botc/behaviors/outsiders.py
from __future__ import annotations      
from typing import TYPE_CHECKING         
if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.core.game import GameManager
    from botc.core.game import GameManager


from botc.enums import RoleName
from .base import RoleBehavior
from . import register_role
import random

@register_role(RoleName.BUTLER)
class ButlerBehavior(RoleBehavior):
    first_night_priority = 9
    other_night_priority = 10
    
    async def act(self, player: Player, game: GameManager):
        master = random.sample(game.players,1)[0]
        await game.command_cog.send_direct_message(player.player_name, f"Worship your lord, {master.player_name}")
