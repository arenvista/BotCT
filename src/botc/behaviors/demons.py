# src/botc/behaviors/demons.py
from __future__ import annotations       
from typing import TYPE_CHECKING         
if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.core.game import GameManager

from botc.enums import RoleName
from .base import RoleBehavior, message_death, message_self
from . import register_role

@register_role(RoleName.IMP)
class ImpBehavior(RoleBehavior):
    other_night_priority = 5

    @message_self
    async def act(self, player: Player, game: GameManager) -> str:
        prompt = f"Who do you want to kill? ⚔️"
        
        # FIXED: Replaced terminal input with discord dropdown
        target_list = [p.username for p in game.get_players() if p.status.alive and p != player] + ["None"]
        print("Imp usrname " + player.username)
        user_sel = await game.send_query(player.username, prompt, target_list, 1)
        
        if not user_sel:
            return "No one dies tonight..." # Player made no selection

        target = game.get_player(user_sel[0])

        msg = ""
        if target and not target.status.is_protected:
            # target.status.alive = False
            await self.kill(target, game)
            game.killed_tonight = target 
            msg = f"{target.username} died. ⚰️"
        elif target and target.status.is_protected:
            msg = f"{target.username} was protected by the Monk and survives. ⚰️"
        return msg


    @message_death
    async def die(self, player: Player, game: GameManager):
        pass
