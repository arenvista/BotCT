# src/botc/behaviors/minions.py
from __future__ import annotations      
from typing import TYPE_CHECKING         
if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.core.game import GameManager

from botc.enums import RoleName, Alignment
from .base import RoleBehavior
from . import register_role, BEHAVIOR_MAP

@register_role(RoleName.POISONER)
class PoisonerBehavior(RoleBehavior):
    first_night_priority = 1
    other_night_priority = 1

    async def act(self, player: Player, game: GameManager) -> None:
        user_sel = await game.command_cog.dmpoll(player.player_name, "Who do you want to poision?", [player.player_name for player in game.players_alive], 1)
        if user_sel == None: raise ValueError("Selection Returned None")
        target_name: str = user_sel[0]
        target = game.get_player_by_name(target_name) 
        target.poisoned = True
        print(f"Put {player.believed_role} to sleep.")
        await game.command_cog.send_direct_message(player.player_name,game.get_board_str())

@register_role(RoleName.SPY)
class SpyBehavior(RoleBehavior):
    first_night_priority = 2
    other_night_priority = 3

    async def act(self, player: Player, game: GameManager) -> None:
        prompt = f"\nWake {player.believed_role} ({player.player_name}). Show them the Grimoire. Put to sleep."
        print(prompt)

@register_role(RoleName.SCARLET_WOMAN)
class ScarletWomanBehavior(RoleBehavior):
    other_night_priority = 4

    async def act(self, player: Player, game: GameManager) -> None:
        imp = game.get_player_by_role(RoleName.IMP)
        alive_players = sum(1 for p in game.players if p.alive)
        
        if imp and not imp.alive and alive_players >= 5:
            prompt = f"\n*** The Imp is dead. The {player.believed_role} ({player.player_name}) is now the Imp! ***"
            print(prompt)
            player.actual_role = RoleName.IMP
            player.believed_role = RoleName.IMP
            player.registered_role = RoleName.IMP
            player.registered_alignment = Alignment.EVIL
            player.role_behavior = BEHAVIOR_MAP[RoleName.IMP]
