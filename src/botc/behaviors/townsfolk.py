# src/botc/behaviors/townsfolk.py
from __future__ import annotations      
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.game import GameManager
    from botc.utils.game_io import GameIO

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
    def act(self, player: Player, game: GameManager) -> str:
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
    def act(self, player: Player, game: GameManager) -> str:
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
        
        return "One of " + ",".join(selected_players) + " is a " + role_to_reveal

@register_role(RoleName.INVESTIGATOR)
class InvestigatorBehavior(RoleBehavior):
    first_night_priority = 5
    def act(self, player: Player, game: GameManager) -> str:
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
        
        return "One of " + ",".join(selected_players) + " is a Minion"

@register_role(RoleName.CHEF)
class ChefBehavior(RoleBehavior):
    first_night_priority = 6
    def act(self, player: Player, game: GameManager) -> str:
        print(f"\nWake {player.believed_role} ({player.player_name}). Show them pairs of evil players. Put to sleep.")
        # TODO: Implement Logic

        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)

        if is_reliable: # not drunk or poisoned
            # TODO: Needs testing. Have not tested [E, G, G, G, G, G, E] or [G, G, G, E, E, E, G, G,]
            
            # assuming that game.players (List) has people in order in which they're seated
            seated_order: List[Player] = game.players
            n: int = len(game.players_alive)
            pairs: int = 0

            for i in range(n):
                #check if player is evil
                if seated_order[i].registered_alignment == Alignment.EVIL:
                    # check if person to right is evil
                    if i < n - 1:
                        if seated_order[i + 1].registered_alignment == Alignment.EVIL:
                            pairs += 1

                    # manually check last person in array
                    elif i == n - 1:
                        # check to see if person at index 0 is GOOD or EVIl
                        if seated_order[0].registered_alignment == Alignment.EVIL:
                            pairs += 1
            return f'Tell {player.player_name} that there are {pairs} pairs'

        else: # either drunk or posioned so give random number from 0-2 depending on distribution of players
            num_evil = game.roles_distribution.num_demons + game.roles_distribution.num_minions
            if num_evil == 1:
                return f'Tell {player.player_name} that there are 0 pairs'
            elif num_evil == 2:
                return f'Tell {player.player_name} that there are {random.randint(0,1)} pairs'
            else:
                return f'Tell {player.player_name} that there are {random.randint(0,2)} pairs' 


@register_role(RoleName.EMPATH)
class EmpathBehavior(RoleBehavior):
    first_night_priority = 7
    other_night_priority = 8

    def act(self, player: Player, game: GameManager) -> str:
        is_reliable: bool = player.actual_role == RoleName.DRUNK or player.poisoned
        left_neighbor, right_neighbor = game.get_alive_neighbors(player)
        evil_count = 0
        if left_neighbor and left_neighbor.registered_alignment == Alignment.EVIL: evil_count += 1
        if right_neighbor and right_neighbor.registered_alignment == Alignment.EVIL: evil_count += 1
        if is_reliable: evil_count = random.choice([0, 1, 2])
        return f"There are {evil_count}, evil players among you"

@register_role(RoleName.FORTUNE_TELLER)
class FortuneTellerBehavior(RoleBehavior):
    first_night_priority = 8
    other_night_priority = 9
    def act(self, player: Player, game: GameManager) -> str:
        possible_selections: List[Player] = [p for p in game.players if p.alive == True and p != player]
        selected_player_names: List[str] = []
        selected_player_names.append(game.gameio.get_user_choice([p.player_name for p in possible_selections], "Select First Player to Divine"))
        selected_player_names.append(game.gameio.get_user_choice([p.player_name for p in possible_selections], "Select Second Player to Divine"))
        selected_players = [p for p in possible_selections if p.player_name in selected_player_names]
        for p in selected_players:
            if p.believed_role == RoleName.IMP:
                return "There is an Imp among us"
        return "All is good in the world, no Imps here."
@register_role(RoleName.UNDERTAKER)
class UndertakerBehavior(RoleBehavior):
    other_night_priority = 7
    def act(self, player: Player, game: GameManager) -> str:
        #print(f"\nWake {player.believed_role} ({player.player_name}). Show them the role of todays executed player. Put to sleep.")
        # TODO: Implement UndertakerBehavior
        # TODO: Print statements need to be updated. Display class than name in some cases.

        if not game.executed_player:
            return f"No player has been executed, Undertaker does nothing"

        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned) # added not since we want is_reliable to be true when player is not Drunk OR is not Poisoned
        executed_player: Player = game.get_player_by_name(game.executed_player)

        if is_reliable: # not drunk or poisoned
            if executed_player.actual_role == RoleName.DRUNK:
                # TODO: English hard. Idk if this sentence makes sense. Should we assume players are playing in person or online. DIADJSAdaosdk
                    return f"Wake up {player.player_name} and tell them {executed_player.player_name} was a Drunk."
            else:
                return f"Wake up {player.player_name} and tell them {executed_player.player_name} was a {executed_player.actual_role}."
        else:

            # TODO: Check this out. Not sure how to give false information
            role = ""
            message = f"Wake up {player.believed_role}({player.player_name}) and tell them {executed_player.player_name} was a {role} (or show them the {role} Token)."

            # for the miss information, pick random role? 
            # can't pick role since information is dependent on game context. Giving a random role might fk over game
            # have the Game Manager pick role
            role = input(f"Give false information to {player.believed_role}({player.player_name}). What false role do you want to tell them?\n False Role: ")
            
            return message


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
    def act(self, player: Player, game: GameManager) -> str:
            
        # drunk can be ravenkeeper but has fake info
        #if game.killed_tonight == player and player.registered_role == RoleName.RAVENKEEPER:
        #    print(f"\nWake {player.believed_role} ({player.player_name}). They died! Let them point to a player, show them the role. Put to sleep.")
            # TODO: Implement RavenkeeperBehavior


        if player.alive: # if RavenKeeper is Alive, do nothing
            return ""

        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)

        print(f"\n{player.believed_role} ({player.player_name}) has died!")
        print(f"Wake up {player.believed_role} ({player.player_name}) and have them point to another player. \n Who did they pick? ")
        target = game.get_player_by_name()

        if is_reliable: # not drunk and not poisoned
            return f"{player.believed_role} ({player.player_name}) has picked {target.player_name}. There role is {target.actual_role}"
        else:   
            # TODO: call function to get fake info from Game Master
            return f"Give {player.believed_role}({player.player_name}) fake information on who they picked"


@register_role(RoleName.VIRGIN)
class VirginBehavior(RoleBehavior):
    def act(self, player: Player, game: GameManager) -> str:
        # TODO: Implement Virgin
        # only need to check if not drunk or poisoned and if nominator is aa townfolk
        
        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)
        nominator: Player =  game.get_player_by_name(next(iter(game.vote_table)))

        if is_reliable:
            if nominator.actual_role in ROLES_TOWNSFOLK:
                nominator.alive = False
                return f"{nominator.believed_role}({nominator.player_name}) has died."
        
        # dont need to check drunk or poisoned since they will die either way during the vote (if majority voted to execute)
        return ""

@register_role(RoleName.SLAYER)
class SlayerBehavior(RoleBehavior):
    def act(self, player: Player, game: GameManager) -> str:
        # TODO: Implement Slayer

        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)

        if is_reliable:
            print(f"\nWake {player.believed_role}({player.player_name}) up.")
            target: Player = game.get_player_by_name()
            if target.actual_role == RoleName.IMP:
                target.alive = False
                return f"\n {player.believed_role}({player.player_name}) has killed the Imp!"
            else: 
                return f"{player.believed_role}({player.player_name}) has targeted someone who is not the Imp, nothing happens"

        # ignore drunk or poison case since nothing would happen either way.
        else:
            if player.actual_role == RoleName.DRUNK:
                return f"\nSince {player.believed_role}({player.player_name}) is actually a Drunk, Nothing happens."
            else:
                return f"\nSince {player.believed_role}({player.player_name}) is poisoned, Nothing happens."



@register_role(RoleName.SOLDIER)
class SoldierBehavior(RoleBehavior):
    def act(self, player: Player, game: GameManager) -> None:
        # TODO: Implement Soldier
        
        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)

        if is_reliable:
            player.protected = True
        else: # if Drunk, they are not protected. If poisoned, they are not protected from Imp's Attack
            player.protected = False

@register_role(RoleName.MAYOR)
class MayorBehavior(RoleBehavior):
    def act(self, player: Player, game: GameManager) -> str:
        # TODO: Implement Mayor
        

        if len(game.players_alive) != 3:
            return ""

        if game.executed_player:
            print("There has been an execution, Mayor's ability does not work.")
            return ""

        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)

        if is_reliable:
            game.game_over = True
            return f"3 players are remaining and no Execution has occurred. Good Wins due to Mayor's ability"
        else:
            if player.actual_role == RoleName.DRUNK:
                return f"3 players are remaining and no Execution has occurred. But Mayor is DRUNK! Nothing happens"
            if player.poisoned:
                return f"3 players are remaining and no Execution has occurred. But Mayor is POISONED! Mayor's ability does not work!"
        


# NOTE
# how to deal with fake info????
# How do you figure out night priorities????????
# dont want to take power away from Game Master. Let them pick misinformation and have impact on game

# Need to clear game.executed_player at the beginning of next round