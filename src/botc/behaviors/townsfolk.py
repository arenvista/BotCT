# src/botc/behaviors/townsfolk.py
from __future__ import annotations      
from typing import TYPE_CHECKING         
if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.game import GameManager

import random
from botc.enums import RoleName, Alignment
from .base import RoleBehavior
from . import register_role

@register_role(RoleName.WASHERWOMAN)
class WasherwomanBehavior(RoleBehavior):
    first_night_priority = 3
    def act(self, player: 'Player', game: 'GameManager'):
        print(f"\nWake {player.believed_role} ({player.player_name}). Show them 1 Townsfolk among 2 players. Put to sleep.")

@register_role(RoleName.LIBRARIAN)
class LibrarianBehavior(RoleBehavior):
    first_night_priority = 4
    def act(self, player: 'Player', game: 'GameManager'):
        print(f"\nWake {player.believed_role} ({player.player_name}). Show them 1 Outsider among 2 players. Put to sleep.")

@register_role(RoleName.INVESTIGATOR)
class InvestigatorBehavior(RoleBehavior):
    first_night_priority = 5
    def act(self, player: 'Player', game: 'GameManager'):
        print(f"\nWake {player.believed_role} ({player.player_name}). Show them 1 Minion among 2 players. Put to sleep.")

@register_role(RoleName.CHEF)
class ChefBehavior(RoleBehavior):
    first_night_priority = 6
    def act(self, player: 'Player', game: 'GameManager'):
        print(f"\nWake {player.believed_role} ({player.player_name}). Show them pairs of evil players. Put to sleep.")

@register_role(RoleName.EMPATH)
class EmpathBehavior(RoleBehavior):
    first_night_priority = 7
    other_night_priority = 8

    def act(self, player: 'Player', game: 'GameManager') -> None:
        left_neighbor, right_neighbor = game.get_alive_neighbors(player)
        evil_count = 0
        if left_neighbor and left_neighbor.registered_alignment == Alignment.EVIL: evil_count += 1
        if right_neighbor and right_neighbor.registered_alignment == Alignment.EVIL: evil_count += 1

        if player.actual_role == RoleName.DRUNK or player.poisoned:
            fake_count = random.choice([0, 1, 2])
            prompt = f"\nWake {player.believed_role} ({player.player_name}). Show them {fake_count} fingers [DRUNK/POISONED INFO]. Put to sleep."
        else:
            prompt = f"\nWake {player.believed_role} ({player.player_name}). Show them {evil_count} fingers. (Neighbors: {left_neighbor.player_name}, {right_neighbor.player_name}). Put to sleep."
        print(prompt)

@register_role(RoleName.FORTUNE_TELLER)
class FortuneTellerBehavior(RoleBehavior):
    first_night_priority = 8
    other_night_priority = 9
    def act(self, player: 'Player', game: 'GameManager'):
        print(f"\nWake {player.believed_role} ({player.player_name}). Let them pick 2 players, nod if Demon. Put to sleep.")

@register_role(RoleName.MONK)
class MonkBehavior(RoleBehavior):
    other_night_priority = 2
    def act(self, player: 'Player', game: 'GameManager') -> None:
        prompt = f"\nWake {player.believed_role} ({player.player_name}). Who do they protect?"
        print(prompt)
        target = game.get_player_by_name()
        if not player.poisoned: target.protected = True
        print(f"Put {player.believed_role} to sleep.")

@register_role(RoleName.RAVENKEEPER)
class RavenkeeperBehavior(RoleBehavior):
    other_night_priority = 6
    def act(self, player: 'Player', game: 'GameManager') -> None:
        if game.killed_tonight == player:
            print(f"\nWake {player.believed_role} ({player.player_name}). They died! Let them point to a player, show them the role. Put to sleep.")

@register_role(RoleName.UNDERTAKER)
class UndertakerBehavior(RoleBehavior):
    other_night_priority = 7
    def act(self, player: 'Player', game: 'GameManager'):
        print(f"\nWake {player.believed_role} ({player.player_name}). Show them the role of today's executed player. Put to sleep.")
