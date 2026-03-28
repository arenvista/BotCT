# src/botc/behaviors/townsfolk.py
from __future__ import annotations      
from typing import TYPE_CHECKING, List, Optional, Set, Dict, Any
import random

if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.core.game import GameManager

from botc.enums import RoleName, Alignment, RoleClass
from .base import RoleBehavior, InfoRoleBehavior, ActionRoleBehavior, PassiveBehavior, message_death
from . import register_role

ROLES_DEMONS = RoleName.get_by_class(RoleClass.DEMONS)
ROLES_MINIONS = RoleName.get_by_class(RoleClass.MINIONS)
ROLES_OUTSIDERS = RoleName.get_by_class(RoleClass.OUTSIDERS)
ROLES_TOWNSFOLK = RoleName.get_by_class(RoleClass.TOWNSFOLK)

def get_filtered_players(
    game: GameManager, 
    role_names_registered: Optional[set[RoleName]] = None, 
    role_names_believed: Optional[set[RoleName]] = None, 
    alignment: Optional[Alignment] = None, 
    is_poisoned: Optional[bool] = None,
    is_drunk: Optional[bool] = None,
    is_alive: Optional[bool] = None,
    is_protected: Optional[bool] = None,
    excluded_players: Optional[Set[Player]] = None 
) -> List[Player]:
    
    player_list: List[Player] = game.get_players()
    if alignment is not None: player_list = [p for p in player_list if p.registered_alignment == alignment]
    if is_poisoned is not None: player_list = [p for p in player_list if p.status.poisoned == is_poisoned]
    if is_drunk is not None: player_list = [p for p in player_list if p.status.drunk == is_drunk]
    if is_alive is not None: player_list = [p for p in player_list if p.status.alive == is_alive]
    if is_protected is not None: player_list = [p for p in player_list if p.status.protected == is_protected]
    if role_names_registered is not None: player_list = [p for p in player_list if p.registered_role in role_names_registered]
    if role_names_believed is not None: player_list = [p for p in player_list if p.registered_role in role_names_believed]
    if excluded_players is not None: player_list = list(set(player_list) - excluded_players)

    return player_list

# ==========================================
# INFO ROLES (Uses the 4-step Data Pipeline)
# ==========================================

@register_role(RoleName.WASHERWOMAN)
class WasherwomanBehavior(InfoRoleBehavior):
    first_night_priority = 3

    async def get_default_trusted(self, player: Player, game: GameManager) -> Dict[str, Any]:
        valid_townsfolk = [p for p in game.get_players() if p.registered_role.role_class == RoleClass.TOWNSFOLK and p != player]
        if not valid_townsfolk: return {}
        actual = random.choice(valid_townsfolk)
        decoy = random.choice([p for p in game.get_players() if p != actual and p != player])
        return {"players": [actual.username, decoy.username], "role": str(actual.registered_role)}

    async def get_manual_trusted(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        valid_townsfolk = [p for p in game.get_players() if p.registered_role.role_class == RoleClass.TOWNSFOLK and p != player]
        gm_town = await game.send_query(game.game_master, "Select a Townsfolk", [p.username for p in valid_townsfolk], 1)
        if not gm_town: return default_data
        
        gm_decoy = await game.send_query(game.game_master, "Select a Decoy", [p.username for p in game.get_players() if p.username != gm_town[0] and p != player], 1)
        actual_other = gm_decoy[0] if gm_decoy else default_data["players"][1]
        
        return {"players": [gm_town[0], actual_other], "role": str(game.get_player(gm_town[0]).registered_role)}

    async def get_default_dishonest(self, player: Player, game: GameManager) -> Dict[str, Any]:
        fake_targets = random.sample([p for p in game.get_players() if p != player], 2)
        return {"players": [p.username for p in fake_targets], "role": str(random.choice(ROLES_TOWNSFOLK))}

    async def get_manual_dishonest(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        gm_players = await game.send_query(game.game_master, "Select 2 Fake Targets", [p.username for p in game.get_players() if p != player], 2)
        if gm_players and len(gm_players) == 2: default_data["players"] = gm_players
        gm_role = await game.send_query(game.game_master, "Select Fake Role", [str(r) for r in ROLES_TOWNSFOLK], 1)
        if gm_role: default_data["role"] = gm_role[0]
        return default_data

    async def send_result(self, player: Player, game: GameManager, night_data: Dict[str, Any]) -> None:
        players = night_data.get("players", [])
        if len(players) == 2:
            random.shuffle(players)
            msg = f"One of {players[0]} and {players[1]} is the {night_data.get('role')}."
            await game.send_message(player.username, msg)

    @message_death
    async def die(self, player: Player, game: GameManager):
        pass

@register_role(RoleName.LIBRARIAN)
class LibrarianBehavior(InfoRoleBehavior):
    first_night_priority = 4
    # (Implementation mirrors Washerwoman, checking ROLES_OUTSIDERS instead of TOWNSFOLK)
    async def get_default_trusted(self, player: Player, game: GameManager) -> Dict[str, Any]:
        valid_outsiders = [p for p in game.get_players() if p.registered_role.role_class == RoleClass.OUTSIDERS and p != player]
        if not valid_outsiders: return {"players": ["No Outsiders"], "role": "in play"} # BotC specific rule (0 Outsiders ping)
        actual = random.choice(valid_outsiders)
        decoy = random.choice([p for p in game.get_players() if p != actual and p != player])
        return {"players": [actual.username, decoy.username], "role": str(actual.registered_role)}

    async def get_manual_trusted(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        valid_outsiders = get_filtered_players(game, role_names_registered=ROLES_OUTSIDERS, excluded_players=set([player]))
        if not valid_outsiders: return {"players": ["No Outsiders"], "role": "in play"} # BotC specific rule (0 Outsiders ping)
        
        actual = await game.send_query(game.game_master, "Select Outsider", [p.username for p in valid_outsiders], 1)
        if not actual: return default_data
        decoy = await game.send_query(game.game_master, "Select Player", [p.username for p in game.get_players() if p.username != actual[0] and p != player], 1)
        actual_other = decoy[0] if decoy else default_data["players"][1]

        return {"players": [actual[0], actual_other], "role": str(game.get_player(actual[0]).registered_role)}


    async def get_default_dishonest(self, player: Player, game: GameManager) -> Dict[str, Any]:
        fake_targets = random.sample([p for p in game.get_players() if p != player], 2)
        return {"players": [p.username for p in fake_targets], "role": str(random.choice(ROLES_OUTSIDERS))}

    async def get_manual_dishonest(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        return default_data

    async def send_result(self, player: Player, game: GameManager, night_data: Dict[str, Any]) -> None:
        players = night_data.get("players", [])
        if len(players) == 1:
            await game.send_message(player.username, "There are no Outsiders in play.")
        else:
            random.shuffle(players)
            await game.send_message(player.username, f"One of {players[0]} and {players[1]} is the {night_data.get('role')}.")
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass

@register_role(RoleName.INVESTIGATOR)
class InvestigatorBehavior(InfoRoleBehavior):
    first_night_priority = 5
    async def get_default_trusted(self, player, game):
        minions = get_filtered_players(game, role_names_believed=ROLES_MINIONS)  
        others = get_filtered_players(game, excluded_players=set(minions + [player]))

        rand_minion = random.choice(minions)
        rand_other = random.choice(others)

        return {"player_one": rand_minion.username, "player_two": rand_other.username, "role_to_reveal": rand_minion.believed_role}

    async def get_manual_trusted(self, player, game, default_data):
        minions = get_filtered_players(game, role_names_believed=ROLES_MINIONS)  
        others = get_filtered_players(game, excluded_players=set(minions + [player]))    


        gm_minion = await game.send_query(game.game_master, "Select a Minion for Investigator", [p.username for p in minions], 1)
        if not gm_minion: return default_data
        gm_other = await game.send_query(game.game_master, "Select Non-Minion Player for Investigator", [p.username for p in others], 1)
        if not gm_other: return default_data

        gm_minion_player = game.get_player(gm_minion[0])
        gm_other_player = game.get_player(gm_other[0])

        return {"player_one": gm_minion_player.username, "player_two": gm_other_player.username, "role_to_reveal": gm_minion_player.believed_role}
    
    async def get_default_dishonest(self, player, game):
        evil_players = get_filtered_players(game, alignment=Alignment.EVIL)
        others = random.sample(get_filtered_players(game, excluded_players=set(evil_players + [player])), k=2)
        rand_other_one = others[0]
        rand_other_two = others[1]

        return {"player_one": rand_other_one.username, "player_two": rand_other_two.username, "role_to_reveal": random.choice(ROLES_MINIONS).__str__()}

    async def get_manual_dishonest(self, player, game, default_data):
        evil_players = get_filtered_players(game, alignment=Alignment.EVIL)
        others = random.sample(get_filtered_players(game, excluded_players=set(evil_players + [player])), k=2)
        rand_other_one = await game.send_query(game.game_master, "Select Non-Evil Player", [p.username for p in others], 1)
        if not rand_other_one: return default_data

        rand_other_player_one = game.get_player(rand_other_one[0])
        others.remove(rand_other_player_one)

        rand_other_two = await game.send_query(game.game_master, "Select Non-Evil Player", [p.username for p in others], 1)
        if not rand_other_two: return default_data
        rand_other_player_two = game.get_player(rand_other_two[0])

        random_evil_role = await game.send_query(game.game_master, "Select Evil Role", [str(r) for r in ROLES_MINIONS], 1)
        if not random_evil_role: return default_data

        return {"player_one": rand_other_player_one.username, "player_two": rand_other_player_two.username, "role_to_reveal": random_evil_role[0]}

    async def send_result(self, player, game, night_data):

        rand_int = random.randint(0, 1)
        
        if rand_int == 0:
            await game.send_message(player.username, f"Either {night_data["player_one"]} or {night_data["player_two"]} is a {night_data["role_to_reveal"]} ", )
        else:
            await game.send_message(player.username, f"Either {night_data["player_two"]} or {night_data["player_one"]} is a {night_data["role_to_reveal"]} ", )

@register_role(RoleName.EMPATH)
class EmpathBehavior(InfoRoleBehavior):
    first_night_priority = 7
    other_night_priority = 8

    async def get_default_trusted(self, player, game):
        left, right = game.get_alive_neighbors(player)
        evil_count = sum(1 for p in [left, right] if p.registered_alignment == Alignment.EVIL)
        return {"neighbor_one": left.username, "neighbor_two": right.username, "evil_count": evil_count}

    async def get_manual_trusted(self, player, game, default_data):
        gm_val = await game.send_query(game.game_master, "Override Empath Evil Count (0-2)", ["0", "1", "2"], 1)
        if gm_val:
            default_data["evil_count"] = int(gm_val[0])
        return default_data

    async def get_default_dishonest(self, player, game):
        left, right = game.get_alive_neighbors(player)
        return {"neighbor_one": left.username, "neighbor_two": right.username, "evil_count": random.randint(0, 2)}

    async def get_manual_dishonest(self, player, game, default_data):
        gm_val = await game.send_query(game.game_master, "Select False Evil Count for Empath", ["0", "1", "2"], 1)
        if gm_val:
            default_data["evil_count"] = int(gm_val[0])
        return default_data

    async def send_result(self, player, game, night_data):
        await game.send_message(player.username, f"{night_data['evil_count']} of your neighbors ({night_data['neighbor_one']} and {night_data['neighbor_two']}) are evil.")


@register_role(RoleName.CHEF)
class ChefBehavior(InfoRoleBehavior):
    first_night_priority = 6

    async def get_default_trusted(self, player: Player, game: GameManager) -> Dict[str, Any]:
        pairs = 0
        n = len(game.get_players())
        for i in range(n):
            if game.get_players()[i].registered_alignment == Alignment.EVIL:
                next_index = (i + 1) % n
                if game.get_players()[next_index].registered_alignment == Alignment.EVIL:
                    pairs += 1
        return {"pairs": pairs}

    async def get_manual_trusted(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        gm_val = await game.send_query(game.game_master, "Enter Pair Count (0-2)", ['0', '1', '2'], 1)
        return {"pairs": int(gm_val[0])}

    async def get_default_dishonest(self, player: Player, game: GameManager) -> Dict[str, Any]:
        # Give random number from 0-2 depending on distribution of players
        num_evil = sum(1 for p in game.get_players() if p.registered_alignment == Alignment.EVIL)
        max_guess = min(num_evil, 2)
        return {"pairs": random.randint(0, max_guess)}

    async def get_manual_dishonest(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        gm_val = await game.send_query(game.game_master, "Enter False Pair Count (0-2)", ["0", "1", "2"], 1)
        if gm_val: default_data["pairs"] = int(gm_val[0])
        return default_data

    async def send_result(self, player: Player, game: GameManager, night_data: Dict[str, Any]) -> None:
        await game.send_message(player.username, f"There are {night_data.get('pairs')} pairs of evil players.")
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass


@register_role(RoleName.UNDERTAKER)
class UndertakerBehavior(InfoRoleBehavior):
    other_night_priority = 7

    async def get_default_trusted(self, player: Player, game: GameManager) -> Dict[str, Any]:
        if not game: return {}
        executed = game.get_player(game.mgr_day.executed_player)
        if not executed: return {}

        if executed.registered_role == RoleName.RECLUSE:
            return {"role": str(executed.believed_role)}
        return {"role": str(executed.registered_role)}

    # Kinda useless logic here but whatever, if GM wants overright, their wish is my command
    async def get_manual_trusted(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        if not game.mgr_day.executed_player: return {}
        
        gm_val = await game.send_query(game.game_master, "Provide the role of the executed player", [p.registered_role.__str__() if p.registered_role != RoleName.RECLUSE else p.believed_role for p in game.mgr_player.player_list], 1)
        if not gm_val: return default_data
        return {"role": str(game.get_player(gm_val[0]).registered_role)}


    async def get_default_dishonest(self, player: Player, game: GameManager) -> Dict[str, Any]:
        if not game.mgr_day.executed_player: return {}
        # Pick a completely random role that isn't what they actually are
        executed = game.get_player(game.mgr_day.executed_player)
        if executed: fake_roles = [r for r in RoleName if r != executed.registered_role]
        else: fake_roles = [""]
        return {"role": str(random.choice(fake_roles))}

    async def get_manual_dishonest(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        if not game.mgr_day.executed_player: return {}
        gm_val = await game.send_query(game.game_master, "Provide false role for executed player", [str(r) for r in RoleName], 1)
        if gm_val: default_data["role"] = gm_val[0]
        return default_data

    async def send_result(self, player: Player, game: GameManager, night_data: Dict[str, Any]) -> None:
        if "role" in night_data:
            msg = f"The player executed today was the {night_data['role']}."
            await game.send_message(player.username, msg)
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass


# ==========================================
# ACTION ROLES (Targeting Pipeline)
# ==========================================

@register_role(RoleName.MONK)
class MonkBehavior(ActionRoleBehavior):
    other_night_priority = 2

    async def get_default_target(self, player: Player, game: GameManager) -> Optional[Player]:
        # Prompt the PLAYER for their target
        target_list = get_filtered_players(game, excluded_players={player}, is_alive=True)
        user_sel = await game.send_query(player.username, "Who do you protect?", [p.username for p in target_list], 1)
        if user_sel:
            return game.get_player(user_sel[0])
        return None

    async def get_manual_target(self, player: Player, game: GameManager) -> Optional[Player]:
        # If the GM wants to force a target for the Monk
        target_list = get_filtered_players(game, excluded_players={player}, is_alive=True)
        gm_sel = await game.send_query(game.game_master, f"Force target for Monk ({player.username})", [p.username for p in target_list], 1)
        if gm_sel:
            return game.get_player(gm_sel[0])
        return None

    async def execute_action(self, player: Player, target: Player, game: GameManager) -> None:
        target.status.protected = True
        print(f"{target.username} protected by Monk.")
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass


# ==========================================
# CUSTOM/HYBRID ROLES (Bypasses Pipelines)
# ==========================================

@register_role(RoleName.FORTUNE_TELLER)
class FortuneTellerBehavior(RoleBehavior):
    first_night_priority = 8
    other_night_priority = 9
    
    async def act(self, player: Player, game: GameManager) -> None:
        # Custom logic because FT actively queries multiple targets during the night
        possible_selections = [p for p in game.get_players() if p.status.alive and p != player]
        
        sel_1 = await game.send_query(player.username, "Select First Player to Divine", [p.username for p in possible_selections], 1)
        sel_2 = await game.send_query(player.username, "Select Second Player to Divine", [p.username for p in possible_selections], 1)
        
        if not sel_1 or not sel_2: return
        
        target_1 = game.get_player(sel_1[0])
        target_2 = game.get_player(sel_2[0])
        
        is_reliable = player.status.is_reliable
        has_demon = False

        if is_reliable:
            # Check for Demon OR Red Herring
            if target_1 is not None and target_2 is not None:
                if target_1.registered_role in ROLES_DEMONS or target_2.registered_role in ROLES_DEMONS: has_demon = True
                if target_1.status.red_herring or target_2.status.red_herring: has_demon = True
        else:
            # Drunk/Poisoned: Random yes/no
            has_demon = random.choice([True, False])

        msg = "YES" if has_demon else "NO"
        await game.send_message(player.username, f"Demon presence: {msg}")
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass

#TODO: TEST
@register_role(RoleName.RAVENKEEPER)
class RavenkeeperBehavior(RoleBehavior):
    other_night_priority = 6
    async def act(self, player: Player, game: GameManager) -> None:
        if game.killed_tonight.username == player.username:
            target_list = get_filtered_players(game, excluded_players={player})
            sel = await game.send_query(player.username, "You died! Select a player to view their role:", [p.username for p in target_list], 1)
            
            if sel:
                target = game.get_player(sel[0])
                if target is None: return 
                if player.status.is_reliable:
                    await game.send_message(player.username, f"{target.username} is the {target.registered_role}.")
                else:
                    fake_role = random.choice([r for r in RoleName if r != target.registered_role])
                    await game.send_message(player.username, f"{target.username} is the {fake_role}.")
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass


# ==========================================
# PASSIVE / DAY ROLES (Do nothing at night)
# ==========================================

@register_role(RoleName.VIRGIN)
class VirginBehavior(PassiveBehavior):
    pass # Triggered during nominations in the Day Phase
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass

@register_role(RoleName.SLAYER)
class SlayerBehavior(PassiveBehavior):
    pass # Triggered via bot command during the Day Phase
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass

@register_role(RoleName.SOLDIER)
class SoldierBehavior(PassiveBehavior):
    pass # Status handled by Imp's kill check
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass

@register_role(RoleName.MAYOR)
class MayorBehavior(PassiveBehavior):
    pass # Triggered at the end of the execution phase
    @message_death
    async def die(self, player: Player, game: GameManager):
        pass
