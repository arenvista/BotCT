# src/botc/behaviors/townsfolk.py
from __future__ import annotations      
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.core.game import GameManager

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
<<<<<<< HEAD
    
    async def act(self, player: Player, game: GameManager):
        # 1. FIXED: Added 'not' so Drunk/Poisoned = False
        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)
        
=======
    async def act(self, player: Player, game: GameManager):
        is_reliable: bool = player.actual_role == RoleName.DRUNK or player.poisoned
>>>>>>> 9e59c54 (poiser call on discord working)
        selected_players: List[str] = []
        role_to_reveal: str = ""
        
        if is_reliable: # --- REGULAR WASHERWOMAN ---
            # FIXED: Prompt text updated to reflect Regular Washerwoman
            gm_skip = await game.command_cog.dmdropdown(game.game_master, "Skip Manual Entry for Washerwoman?", ["Yes", "No"], 1)

            # Generate random fallback info first
            # FIXED: Washerwoman can no longer see themselves as the Townsfolk
            valid_townsfolk = [p for p in game.players if p.registered_role.role_class == RoleClass.TOWNSFOLK and p != player]
            townsfolk_to_reveal = random.choice(valid_townsfolk)
            
            valid_others = [p for p in game.players if p != townsfolk_to_reveal and p != player]
            other_player = random.choice(valid_others)
            
            selected_players = [townsfolk_to_reveal.player_name, other_player.player_name]
            role_to_reveal = townsfolk_to_reveal.registered_role.__str__()
            
            # If GM wants to manual override:
            if game.game_master != "" and gm_skip is not None and gm_skip[0] == "No":
                gm_sel_town = await game.modify_information("Select a Townsfolk to reveal", [p.player_name for p in valid_townsfolk], 1)
                
                # Ensure valid string returned, otherwise keep the random fallback
                actual_town_name = gm_sel_town[0] if gm_sel_town else townsfolk_to_reveal.player_name
                
                gm_sel_other = await game.modify_information("Select the 'wrong' player", [p.player_name for p in game.players if p.player_name != actual_town_name and p != player], 1)
                actual_other_name = gm_sel_other[0] if gm_sel_other else other_player.player_name
                
                # FIXED: Actually apply the GM's choices to the selected_players list
                selected_players = [actual_town_name, actual_other_name]
                
                # Update the role string to match the GM's new townsfolk target
                target_obj = game.get_player_by_name(actual_town_name)
                role_to_reveal = target_obj.registered_role.__str__()
                
        else: # --- DRUNK / POISONED WASHERWOMAN ---
            gm_skip = await game.command_cog.dmdropdown(game.game_master, "Skip Manual Entry for Drunk/Poisoned Washerwoman?", ["Yes", "No"], 1)
            
            # FIXED: Generate random fake info just in case the GM skips or times out
            random_two = random.sample([p for p in game.players if p != player], 2)
            selected_players = [p.player_name for p in random_two]
            
            # FIXED: Added GameManager. reference to ROLES_TOWNSFOLK
            role_to_reveal = random.choice(game.ROLES_TOWNSFOLK).__str__()

            if game.game_master != "" and gm_skip is not None and gm_skip[0] == "No":
                gm_sel_players = await game.modify_information("Select Two People to Reveal (Fake Info)", [p.player_name for p in game.players if p != player], 2)
                # FIXED: Failsafe gracefully instead of raising ValueError
                if gm_sel_players and len(gm_sel_players) == 2:
                    selected_players = gm_sel_players
                
                gm_sel_role = await game.modify_information("Select a Role to Reveal (Fake Info)", [r.__str__() for r in game.ROLES_TOWNSFOLK], 1)
                if gm_sel_role:
                    role_to_reveal = gm_sel_role[0]
                    
        # FIXED: Shuffle the array so the real Townsfolk isn't always listed first!
        random.shuffle(selected_players)
        
        # Build and send the final message
        message = f"One of {selected_players[0]} and {selected_players[1]} is the {role_to_reveal}."
        await game.command_cog.send_direct_message(player.player_name, message)

@register_role(RoleName.LIBRARIAN)
class LibrarianBehavior(RoleBehavior):
    first_night_priority = 4
    async def act(self, player: Player, game: GameManager):
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
        #TODO: log output 

@register_role(RoleName.INVESTIGATOR)
class InvestigatorBehavior(RoleBehavior):
    first_night_priority = 5
    async def act(self, player: Player, game: GameManager):
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
    async def act(self, player: Player, game: GameManager):
        print(f"\nWake {player.believed_role} ({player.player_name}). Show them pairs of evil players. Put to sleep.")
        # TODO: Implement Logic

        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)

        if is_reliable: # not drunk or poisoned
            # TODO: Needs testing. Have not tested [E, G, G, G, G, G, E] or [G, G, G, E, E, E, G, G,]
            
            # assuming that game.players (List) has people in order in which they're seated
            seated_order: List[Player] = game.players
            n: int = len(game.players)
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
            print(f'Tell {player.player_name} that there are {pairs} pairs')

        else: # either drunk or posioned so give random number from 0-2 depending on distribution of players
            num_evil = game.roles_distribution.num_demons + game.roles_distribution.num_minions
            if num_evil == 1:
                print(f'Tell {player.player_name} that there are 0 pairs')
            elif num_evil == 2:
                print(f'Tell {player.player_name} that there are {random.randint(0,1)} pairs') 
            else:
                print(f'Tell {player.player_name} that there are {random.randint(0,2)} pairs') 


@register_role(RoleName.EMPATH)
class EmpathBehavior(RoleBehavior):
    first_night_priority = 7
    other_night_priority = 8

    async def act(self, player: Player, game: GameManager) -> None:
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
    async def act(self, player: Player, game: GameManager):
        possible_selections: List[Player] = [p for p in game.players if p.alive == True and p != player]
        selected_player_names: List[str] = []
        selected_player_names.append(game.gameio.get_user_choice([p.player_name for p in possible_selections], "Select First Player to Divine"))
        selected_player_names.append(game.gameio.get_user_choice([p.player_name for p in possible_selections], "Select Second Player to Divine"))
        selected_players = [p for p in possible_selections if p.player_name in selected_player_names]
        for p in selected_players:
            if p.believed_role == RoleName.IMP:
                print("There is an Imp among us")
        print("All is good in the world, no Imps here.")
@register_role(RoleName.UNDERTAKER)
class UndertakerBehavior(RoleBehavior):
    other_night_priority = 7
    async def act(self, player: Player, game: GameManager):
        #print(f"\nWake {player.believed_role} ({player.player_name}). Show them the role of todays executed player. Put to sleep.")
        # TODO: Implement UndertakerBehavior
        # TODO: Print statements need to be updated. Display class than name in some cases.

        if not game.executed_player:
            print(f"No player has been executed, Undertaker does nothing")

        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned) # added not since we want is_reliable to be true when player is not Drunk OR is not Poisoned
        executed_player: Player = game.get_player_by_name(game.executed_player)

        if is_reliable: # not drunk or poisoned
            if executed_player.actual_role == RoleName.DRUNK:
                # TODO: English hard. Idk if this sentence makes sense. Should we assume players are playing in person or online. DIADJSAdaosdk
                print(f"Wake up {player.player_name} and tell them {executed_player.player_name} was a Drunk (or show them the Drunk Token).")
            else:
                print(f"Wake up {player.player_name} and tell them {executed_player.player_name} was a {executed_player.actual_role} (or show them the {executed_player.actual_role} Token).")
        else:

            # TODO: Check this out. Not sure how to give false information
            role = ""
            message = f"Wake up {player.believed_role}({player.player_name}) and tell them {executed_player.player_name} was a {role} (or show them the {role} Token)."

            # for the miss information, pick random role? 
            # can't pick role since information is dependent on game context. Giving a random role might fk over game
            # have the Game Manager pick role
            role = input(f"Give false information to {player.believed_role}({player.player_name}). What false role do you want to tell them?\n False Role: ")
            
            print(message)


@register_role(RoleName.MONK)
class MonkBehavior(RoleBehavior):
    other_night_priority = 2
    async def act(self, player: Player, game: GameManager) -> None:
        prompt = f"\nWake {player.believed_role} ({player.player_name}). Who do they protect?"
        print(prompt)
        target = game.get_player_by_name()
        if not player.poisoned: target.protected = True
        print(f"Put {player.believed_role} to sleep.")

@register_role(RoleName.RAVENKEEPER)
class RavenkeeperBehavior(RoleBehavior):
    other_night_priority = 6
    async def act(self, player: Player, game: GameManager) -> None:
            
        # drunk can be ravenkeeper but has fake info
        #if game.killed_tonight == player and player.registered_role == RoleName.RAVENKEEPER:
        #    print(f"\nWake {player.believed_role} ({player.player_name}). They died! Let them point to a player, show them the role. Put to sleep.")
            # TODO: Implement RavenkeeperBehavior

        # I FUCKING HATE THESE NEST IF STATEMENTS
        # but I want to deal with the case where a player is both drunk and poisoned. In this case, the Game Master needs to give information that really fucks the good side.

        random_float = random.random() # float from 0.0 - 1.0


        if player.actual_role == RoleName.DRUNK: 
            if player.poisoned: 
                print(f"\n{player.believed_role} ({player.player_name}) has died! {player.player_name} is a Drunk and is Poisoned.\n Let them point to a player and give them information that screws the Good team. \nPut them to sleep.")
            elif random_float <= 0.2: 
                print(f"\nWake {player.believed_role} ({player.player_name}). They died! Since {player.player_name} is a Drunk and got LUCKY, let them point to a player and show them the right role. Put them to sleep.")
            else: 
                print(f"\nWake {player.believed_role} ({player.player_name}). They died! Since {player.player_name} is a Drunk, let them point to a player and show them the wrong role. Put them to sleep.")

        
        if player.believed_role == RoleName.RAVENKEEPER: # Drunk case, player thinks their a Ravenkeeper
            print(f"\n{player.believed_role} ({player.player_name}) has died!")
            picked_player = input(f"Wake up {player.believed_role} ({player.player_name}) and have them point to another player. \n Who did they pick? ")



@register_role(RoleName.VIRGIN)
class VirginBehavior(RoleBehavior):
    async def act(self, player: Player, game: GameManager) -> None:
        # TODO: Implement Virgin
        # only need to check if not drunk or poisoned and if nominator is aa townfolk
        
        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)
        nominator: Player =  game.get_player_by_name(game.nominator)

        if is_reliable:
            if nominator.actual_role in ROLES_TOWNSFOLK:
                nominator.alive = False
                print(f"{nominator.believed_role}({nominator.player_name}) has died.") 

        # dont need to check drunk or poisoned since they will die either way during the vote (if majority voted to execute)

@register_role(RoleName.SLAYER)
class SlayerBehavior(RoleBehavior):
    async def act(self, player: Player, game: GameManager) -> None:
        # TODO: Implement Slayer

        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)

        if is_reliable:
            print(f"\nWake {player.believed_role}({player.player_name}) up.")
            target: Player = game.get_player_by_name()
            if target.actual_role == RoleName.IMP:
                target.alive = False
                print(f"\n {player.believed_role}({player.player_name}) has killed the Imp!")
            else: 
                print(f"{player.believed_role}({player.player_name}) has targeted someone who is not the Imp, nothing happens")

        # ignore drunk or poison case since nothing would happen either way.
        else:
            if player.actual_role == RoleName.DRUNK:
                print(f"\nSince {player.believed_role}({player.player_name}) is actually a Drunk, Nothing happens.")
            else:
                print(f"\nSince {player.believed_role}({player.player_name}) is poisoned, Nothing happens.")



@register_role(RoleName.SOLDIER)
class SoldierBehavior(RoleBehavior):
    first_night_priority = 100 # not sure what to set this as
    other_night_priority = 100 # not sure what to set this as
    async def act(self, player: Player, game: GameManager) -> None:
        # TODO: Implement Soldier
        
        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)

        if is_reliable:
            player.protected = True
        else: # if Drunk, they are not protected. If poisoned, they are not protected from Imp's Attack
            player.protected = False

@register_role(RoleName.MAYOR)
class MayorBehavior(RoleBehavior):
    async def act(self, player: Player, game: GameManager) -> None:
        # TODO: Implement Mayor
        
        if game.num_players_remaining != 3:
            return

        if game.executed_player:
            print("There has been an execution, Mayor's ability does not work.")
            return

        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)

        if is_reliable:
            game.game_over = True
            print(f"3 players are remaining and no Execution has occurred. Good Wins due to Mayor's ability")
        else:
            if player.actual_role == RoleName.DRUNK:
                print(f"3 players are remaining and no Execution has occurred. But Mayor is DRUNK! Nothing happens")
            if player.poisoned:
                print(f"3 players are remaining and no Execution has occurred. But Mayor is POISONED! Mayor's ability does not work!")
        


# NOTE
# how to deal with fake info????
# How do you figure out night priorities????????
# dont want to take power away from Game Master. Let them pick misinformation and have impact on game

# Need to clear game.executed_player at the beginning of next round
