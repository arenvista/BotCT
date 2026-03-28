from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from botc.player import Player
    from botc.core.game import GameManager

from botc.enums import Alignment, RoleName

from . import BEHAVIOR_MAP, register_role
from .base import RoleBehavior


@register_role(RoleName.POISONER)
class PoisonerBehavior(RoleBehavior):
    first_night_priority = 1
    other_night_priority = 1

    async def act(self, player: Player, game: GameManager) -> None:
        # 1. Get the list of alive Player objects
        alive_players = game.get_players({"alive": True})
        
        # 2. Extract just their usernames (strings)
        target_names = [p.username for p in alive_players]

        user_sel = await game.send_query(
            player.username,
            "Who do you want to poison?", 
            target_names,  # <--- MUST be the strings!
            1,
        )
        
        if user_sel is None:
            print(f"{player.username} (Poisoner) timed out or failed to make a selection.")
            return
            
        target_name: str = user_sel[0]
        target = game.get_player(target_name)
        if target: target.status.poisoned = True
        print(f"Put {player.believed_role} to sleep.")
        await game.send_message(player.username, game.get_board_str())

@register_role(RoleName.SPY)
class SpyBehavior(RoleBehavior):
    first_night_priority = 2
    other_night_priority = 3

    async def act(self, player: Player, game: GameManager) -> None:
        await game.send_message( player.username, game.get_board_str())


@register_role(RoleName.SCARLET_WOMAN)
class ScarletWomanBehavior(RoleBehavior):
    other_night_priority = 4

    async def act(self, player: Player, game: GameManager) -> None:
        imp = game.get_players(filter_roles=[RoleName.IMP])[0]
        alive_players = sum(1 for p in game.get_players({"alive":True}))

        if imp and not imp.status.alive and alive_players >= 5:
            prompt = f"\n*** The Imp is dead. The {player.believed_role} ({player.username}) is now the Imp! ***"
            player.registered_role = RoleName.IMP
            player.believed_role = RoleName.IMP
            player.registered_alignment = Alignment.EVIL
            player.role_behavior = BEHAVIOR_MAP[RoleName.IMP]
            await game.send_message(player.username, prompt)
