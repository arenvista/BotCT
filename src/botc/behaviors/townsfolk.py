# src/botc/behaviors/townsfolk.py
from __future__ import annotations      
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.game import GameManager
    # from botc.selectors.selector import Selector

import random
from botc.enums import RoleName, Alignment, RoleClass
from .base import RoleBehavior
from . import register_role

ROLES_DEMONS = RoleName.get_by_class(RoleClass.DEMONS)
ROLES_MINIONS = RoleName.get_by_class(RoleClass.MINIONS)
ROLES_OUTSIDERS = RoleName.get_by_class(RoleClass.OUTSIDERS)
ROLES_TOWNSFOLK = RoleName.get_by_class(RoleClass.TOWNSFOLK)

@register_role(RoleName.WASHERWOMAN)
class WasherwomanBehavior(RoleBehavior):
    first_night_priority = 3

    def act(self, player: Player, game: GameManager):
        is_reliable: bool = player.actual_role == RoleName.DRUNK or player.poisoned
        selected_players: List[str] = []
        role_to_reveal: str = ""
        if is_reliable: # Regular
            selected_townsfolk = random.sample([p_other for p_other in game.players if p_other.registered_role.role_class == RoleClass.TOWNSFOLK],1)[0]
            selected_remainder = random.sample([p_other for p_other in game.players if p_other not in (selected_townsfolk, player)], 1)[0]
            selected_players = [selected_townsfolk.player_name, selected_remainder.player_name]
            random.shuffle(selected_players)
            role_to_reveal = selected_townsfolk.registered_role.role_class.display_name
        else: # If Drunk/Poisioned
            selected_players = random.sample([p_other.player_name for p_other in game.players if p_other != player], 2)
            role_to_reveal = random.sample(ROLES_TOWNSFOLK, 1)[0].display_name
        message = "One of " + ",".join(selected_players) + " is a " + role_to_reveal
        # TODO: log output message 

@register_role(RoleName.LIBRARIAN)
class LibrarianBehavior(RoleBehavior):
    first_night_priority = 4
    def act(self, player: Player, game: GameManager):
        is_reliable: bool = player.actual_role == RoleName.DRUNK or player.poisoned
        selected_players: List[str] = []
        role_to_reveal: str = ""
        if is_reliable: # Regular
            selected_townsfolk = random.sample([p_other for p_other in game.players if p_other.registered_role.role_class == RoleClass.OUTSIDERS],1)[0]
            selected_remainder = random.sample([p_other for p_other in game.players if p_other not in (selected_townsfolk, player)], 1)[0]
            selected_players = [selected_townsfolk.player_name, selected_remainder.player_name]
            random.shuffle(selected_players)
            role_to_reveal = selected_townsfolk.registered_role.role_class.display_name
        else: # If Drunk/Poisioned
            selected_players = random.sample([p_other.player_name for p_other in game.players if p_other != player], 2)
            role_to_reveal = random.sample(ROLES_OUTSIDERS, 1)[0].display_name
        message = "One of " + ",".join(selected_players) + " is a " + role_to_reveal

@register_role(RoleName.INVESTIGATOR)
class InvestigatorBehavior(RoleBehavior):
    first_night_priority = 5
    def act(self, player: Player, game: GameManager):
        is_reliable: bool = player.actual_role == RoleName.DRUNK or player.poisoned
        selected_players: List[str] = []
        role_to_reveal: str = ""
        if is_reliable: # Regular
            selected_townsfolk = random.sample([p_other for p_other in game.players if p_other.registered_role.role_class == RoleClass.MINIONS],1)[0]
            selected_remainder = random.sample([p_other for p_other in game.players if p_other not in (selected_townsfolk, player)], 1)[0]
            selected_players = [selected_townsfolk.player_name, selected_remainder.player_name]
            random.shuffle(selected_players)
            role_to_reveal = selected_townsfolk.registered_role.role_class.display_name
        else: # If Drunk/Poisioned
            selected_players = random.sample([p_other.player_name for p_other in game.players if p_other != player], 2)
        message = "One of " + ",".join(selected_players) + " is a Minion"

@register_role(RoleName.CHEF)
class ChefBehavior(RoleBehavior):
    first_night_priority = 6
    def act(self, player: Player, game: GameManager):
        print(f"\nWake {player.believed_role} ({player.player_name}). Show them pairs of evil players. Put to sleep.")
        # TODO: Implement Logic

@register_role(RoleName.EMPATH)
class EmpathBehavior(RoleBehavior):
    first_night_priority = 7
    other_night_priority = 8

    def act(self, player: Player, game: GameManager) -> None:
        is_reliable: bool = player.actual_role == RoleName.DRUNK or player.poisoned
        left_neighbor, right_neighbor = game.get_alive_neighbors(player)
        evil_count = 0
        if left_neighbor and left_neighbor.registered_alignment == Alignment.EVIL: evil_count += 1
        if right_neighbor and right_neighbor.registered_alignment == Alignment.EVIL: evil_count += 1
        if is_reliable: evil_count = random.choice([0, 1, 2])
        prompt = f"There are {evil_count}, evil players among you"
        # TODO: Implement logging

@register_role(RoleName.FORTUNE_TELLER)
class FortuneTellerBehavior(RoleBehavior):
    first_night_priority = 8
    other_night_priority = 9
    def act(self, player: Player, game: GameManager):
        print(f"\nWake {player.believed_role} ({player.player_name}). Let them pick 2 players, nod if Demon. Put to sleep.")
        # TODO: Implement FortuneTellerBehavior

@register_role(RoleName.MONK)
class MonkBehavior(RoleBehavior):
    other_night_priority = 2
    def act(self, player: Player, game: GameManager) -> None:
        prompt = f"\nWake {player.believed_role} ({player.player_name}). Who do they protect?"
        print(prompt)
        target = game.get_player_by_name()
        if not player.poisoned: target.protected = True
        print(f"Put {player.believed_role} to sleep.")

@register_role(RoleName.RAVENKEEPER)
class RavenkeeperBehavior(RoleBehavior):
    other_night_priority = 6
    def act(self, player: Player, game: GameManager) -> None:
        if game.killed_tonight == player:
            print(f"\nWake {player.believed_role} ({player.player_name}). They died! Let them point to a player, show them the role. Put to sleep.")
            # TODO: Implement RavenkeeperBehavior

@register_role(RoleName.UNDERTAKER)
class UndertakerBehavior(RoleBehavior):
    other_night_priority = 7
    def act(self, player: Player, game: GameManager):
        print(f"\nWake {player.believed_role} ({player.player_name}). Show them the role of todays executed player. Put to sleep.")
        # TODO: Implement UndertakerBehavior
