# src/botc/behaviors/demons.py
from __future__ import annotations       
from typing import TYPE_CHECKING         
if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.core.game import GameManager

from botc.enums import RoleName, RoleClass
from .base import RoleBehavior
from . import register_role

@register_role(RoleName.IMP)
class ImpBehavior(RoleBehavior):
    other_night_priority = 5

    async def act(self, player: Player, game: GameManager) -> None:
        if game.counter.night == 0 and len(game.get_players()) >= 7:
            list_of_minions = [p.username for p in game.get_players() if p.registered_role.role_class == RoleClass.MINIONS]  

            if len(game.get_players()) == 1:
                await game.send_message(player.username, f"Your Minion is {list_of_minions[0]}.")
            else:
                await game.send_message(player.username, f"Your Minions are, {" ".join(list_of_minions)}.")
            return
        else:
            prompt = f"Who do you want to kill? ⚔️"
            
            # FIXED: Replaced terminal input with discord dropdown
            target_list = [p.username for p in game.get_players() if p.status.alive and p != player]
            print("Imp usrname " + player.username)
            user_sel = await game.send_query(player.username, prompt, target_list, 1)
            
            if not user_sel:
                return # Player made no selection

            target = game.get_player(user_sel[0])
            
            if target and not target.status.is_protected:
                target.status.alive = False
                game.killed_tonight = target 
                message = f"{target.username} died. ⚰️"
                await game.mgr_discord.game_channel.channel.send(message)
            elif target and target.status.is_protected:
                message = f"{target.username} was protected by the Monk and survives. ⚰️"
                await game.mgr_discord.game_channel.channel.send(message)
            return

    async def death(self, player, game):
        pass