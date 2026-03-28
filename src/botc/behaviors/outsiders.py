# src/botc/behaviors/outsiders.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from botc.player import Player
    from botc.core.game import GameManager

import random

from botc.enums import RoleName, Alignment

from . import register_role
from .base import RoleBehavior, message_death


# @register_role(RoleName.BUTLER)
# class ButlerBehavior(RoleBehavior):
#     first_night_priority = 9
#     other_night_priority = 10
#
#     async def act(self, player: Player, game: GameManager):
#         master = random.sample(game.get_players(), 1)[0]
#         await game.send_message(
#             player.username, f"Worship your lord, {master.username}"
#         )

@register_role(RoleName.SWEETHEART)
class Sweetheart(RoleBehavior):
    async def act(self, player: Player, game: GameManager):
        pass

    @message_death
    async def die(self, player: Player, game: GameManager):
        new_drunk = random.sample(game.get_players({"alive":True}),1)[0]
        new_drunk.status.drunk = True
        return

@register_role(RoleName.MOONCHILD)
class Moonchild(RoleBehavior):
    async def act(self, player: Player, game: GameManager):
        pass

    @message_death
    async def die(self, player: Player, game: GameManager):
        selections = [p.username for p in game.get_players({"alive":True})]
        target = await game.send_query(player.username, "Curse someone to die.",selections,1)
        try:
            target = target[0]
            target = game.get_player(target)
            if target: await target.role_behavior.die(target, game)
        except:
            return 
@register_role(RoleName.KLUTZ)
class Klutz(RoleBehavior):
    async def act(self, player: Player, game: GameManager):
        pass

    @message_death
    async def die(self, player: Player, game: GameManager):
        selections = [p.username for p in game.get_players({"alive":True})]
        target = await game.send_query(player.username, "Choose 1 alive player: if they are evil, your team loses",selections,1)
        try:
            target = target[0]
            target = game.get_player(target)
            for p in game.get_players():
                await game.send_message(p.username, f"The Klutz {player.username}, chooses {target.username}")
            if target.registered_alignment == Alignment.EVIL:
                for p in game.get_players():
                    await game.send_message(p.username, f"Evil Triumphs")
            else:
                for p in game.get_players():
                    await game.send_message(p.username, f"The Game Continues...")
        except:
            return 
