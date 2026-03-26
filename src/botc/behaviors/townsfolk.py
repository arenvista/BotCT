# src/botc/behaviors/townsfolk.py
from __future__ import annotations      
from typing import TYPE_CHECKING, List, Optional, Set, Dict, Any
import random

if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.core.game import GameManager

from botc.enums import RoleName, Alignment, RoleClass
from .base import RoleBehavior, InfoRoleBehavior, ActionRoleBehavior, PassiveBehavior
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
    
    player_list: List[Player] = game.players
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
        valid_townsfolk = [p for p in game.players if p.registered_role.role_class == RoleClass.TOWNSFOLK and p != player]
        if not valid_townsfolk: return {}
        actual = random.choice(valid_townsfolk)
        decoy = random.choice([p for p in game.players if p != actual and p != player])
        return {"players": [actual.player_name, decoy.player_name], "role": str(actual.registered_role)}

    async def get_manual_trusted(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        valid_townsfolk = [p for p in game.players if p.registered_role.role_class == RoleClass.TOWNSFOLK and p != player]
        gm_town = await game.modify_information("Select a Townsfolk", [p.player_name for p in valid_townsfolk], 1)
        if not gm_town: return default_data
        
        gm_decoy = await game.modify_information("Select a Decoy", [p.player_name for p in game.players if p.player_name != gm_town[0] and p != player], 1)
        actual_other = gm_decoy[0] if gm_decoy else default_data["players"][1]
        
        return {"players": [gm_town[0], actual_other], "role": str(game.get_player_by_name(gm_town[0]).registered_role)}

    async def get_default_dishonest(self, player: Player, game: GameManager) -> Dict[str, Any]:
        fake_targets = random.sample([p for p in game.players if p != player], 2)
        return {"players": [p.player_name for p in fake_targets], "role": str(random.choice(ROLES_TOWNSFOLK))}

    async def get_manual_dishonest(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        gm_players = await game.modify_information("Select 2 Fake Targets", [p.player_name for p in game.players if p != player], 2)
        if gm_players and len(gm_players) == 2: default_data["players"] = gm_players
        gm_role = await game.modify_information("Select Fake Role", [str(r) for r in ROLES_TOWNSFOLK], 1)
        if gm_role: default_data["role"] = gm_role[0]
        return default_data

    async def send_result(self, player: Player, game: GameManager, night_data: Dict[str, Any]) -> None:
        players = night_data.get("players", [])
        if len(players) == 2:
            random.shuffle(players)
            msg = f"One of {players[0]} and {players[1]} is the {night_data.get('role')}."
            await game.command_cog.send_direct_message(player.player_name, msg)


@register_role(RoleName.LIBRARIAN)
class LibrarianBehavior(InfoRoleBehavior):
    first_night_priority = 4
    # (Implementation mirrors Washerwoman, checking ROLES_OUTSIDERS instead of TOWNSFOLK)
    async def get_default_trusted(self, player: Player, game: GameManager) -> Dict[str, Any]:
        valid_outsiders = [p for p in game.players if p.registered_role.role_class == RoleClass.OUTSIDERS and p != player]
        if not valid_outsiders: return {"players": ["No Outsiders"], "role": "in play"} # BotC specific rule (0 Outsiders ping)
        actual = random.choice(valid_outsiders)
        decoy = random.choice([p for p in game.players if p != actual and p != player])
        return {"players": [actual.player_name, decoy.player_name], "role": str(actual.registered_role)}

    async def get_manual_trusted(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        return default_data # Add GM overrides similar to Washerwoman if desired

    async def get_default_dishonest(self, player: Player, game: GameManager) -> Dict[str, Any]:
        fake_targets = random.sample([p for p in game.players if p != player], 2)
        return {"players": [p.player_name for p in fake_targets], "role": str(random.choice(ROLES_OUTSIDERS))}

    async def get_manual_dishonest(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        return default_data

    async def send_result(self, player: Player, game: GameManager, night_data: Dict[str, Any]) -> None:
        players = night_data.get("players", [])
        if len(players) == 1:
            await game.command_cog.send_direct_message(player.player_name, "There are no Outsiders in play.")
        else:
            random.shuffle(players)
            await game.command_cog.send_direct_message(player.player_name, f"One of {players[0]} and {players[1]} is the {night_data.get('role')}.")


@register_role(RoleName.CHEF)
class ChefBehavior(InfoRoleBehavior):
    first_night_priority = 6

    async def get_default_trusted(self, player: Player, game: GameManager) -> Dict[str, Any]:
        pairs = 0
        n = len(game.players)
        for i in range(n):
            if game.players[i].registered_alignment == Alignment.EVIL:
                next_index = (i + 1) % n
                if game.players[next_index].registered_alignment == Alignment.EVIL:
                    pairs += 1
        return {"pairs": pairs}

    async def get_manual_trusted(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        return default_data # Usually GM doesn't override true math, but you can add it

    async def get_default_dishonest(self, player: Player, game: GameManager) -> Dict[str, Any]:
        # Give random number from 0-2 depending on distribution of players
        num_evil = sum(1 for p in game.players if p.registered_alignment == Alignment.EVIL)
        max_guess = min(num_evil, 2)
        return {"pairs": random.randint(0, max_guess)}

    async def get_manual_dishonest(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        gm_val = await game.modify_information("Enter False Pair Count (0-3)", ["0", "1", "2", "3"], 1)
        if gm_val: default_data["pairs"] = int(gm_val[0])
        return default_data

    async def send_result(self, player: Player, game: GameManager, night_data: Dict[str, Any]) -> None:
        await game.command_cog.send_direct_message(player.player_name, f"There are {night_data.get('pairs')} pairs of evil players.")


@register_role(RoleName.UNDERTAKER)
class UndertakerBehavior(InfoRoleBehavior):
    other_night_priority = 7

    async def get_default_trusted(self, player: Player, game: GameManager) -> Dict[str, Any]:
        if not game.executed_player: return {}
        executed = game.get_player_by_name(game.executed_player)
        return {"role": str(executed.registered_role)}

    async def get_manual_trusted(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        return default_data

    async def get_default_dishonest(self, player: Player, game: GameManager) -> Dict[str, Any]:
        if not game.executed_player: return {}
        # Pick a completely random role that isn't what they actually are
        executed = game.get_player_by_name(game.executed_player)
        fake_roles = [r for r in RoleName if r != executed.registered_role]
        return {"role": str(random.choice(fake_roles))}

    async def get_manual_dishonest(self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]:
        if not game.executed_player: return {}
        gm_val = await game.modify_information("Provide false role for executed player", [str(r) for r in RoleName], 1)
        if gm_val: default_data["role"] = gm_val[0]
        return default_data

    async def send_result(self, player: Player, game: GameManager, night_data: Dict[str, Any]) -> None:
        if "role" in night_data:
            msg = f"The player executed today was the {night_data['role']}."
            await game.command_cog.send_direct_message(player.player_name, msg)


# ==========================================
# ACTION ROLES (Targeting Pipeline)
# ==========================================

@register_role(RoleName.MONK)
class MonkBehavior(ActionRoleBehavior):
    other_night_priority = 2

    async def get_default_target(self, player: Player, game: GameManager) -> Optional[Player]:
        # Prompt the PLAYER for their target
        target_list = get_filtered_players(game, excluded_players={player}, is_alive=True)
        user_sel = await game.command_cog.dmdropdown(player.player_name, "Who do you protect?", [p.player_name for p in target_list], 1)
        if user_sel:
            return game.get_player_by_name(user_sel[0])
        return None

    async def get_manual_target(self, player: Player, game: GameManager) -> Optional[Player]:
        # If the GM wants to force a target for the Monk
        target_list = get_filtered_players(game, excluded_players={player}, is_alive=True)
        gm_sel = await game.command_cog.dmdropdown(game.game_master, f"Force target for Monk ({player.player_name})", [p.player_name for p in target_list], 1)
        if gm_sel:
            return game.get_player_by_name(gm_sel[0])
        return None

    async def execute_action(self, player: Player, target: Player, game: GameManager) -> None:
        target.status.protected = True
        print(f"{target.player_name} protected by Monk.")


# ==========================================
# CUSTOM/HYBRID ROLES (Bypasses Pipelines)
# ==========================================

@register_role(RoleName.FORTUNE_TELLER)
class FortuneTellerBehavior(RoleBehavior):
    first_night_priority = 8
    other_night_priority = 9
    
    async def act(self, player: Player, game: GameManager) -> None:
        # Custom logic because FT actively queries multiple targets during the night
        possible_selections = [p for p in game.players if p.status.alive and p != player]
        
        sel_1 = await game.command_cog.dmdropdown(player.player_name, "Select First Player to Divine", [p.player_name for p in possible_selections], 1)
        sel_2 = await game.command_cog.dmdropdown(player.player_name, "Select Second Player to Divine", [p.player_name for p in possible_selections], 1)
        
        if not sel_1 or not sel_2: return
        
        target_1 = game.get_player_by_name(sel_1[0])
        target_2 = game.get_player_by_name(sel_2[0])
        
        is_reliable = player.status.is_reliable
        has_demon = False

        if is_reliable:
            # Check for Demon OR Red Herring
            if target_1.registered_role in ROLES_DEMONS or target_2.registered_role in ROLES_DEMONS: has_demon = True
            if target_1.status.red_herring or target_2.status.red_herring: has_demon = True
        else:
            # Drunk/Poisoned: Random yes/no
            has_demon = random.choice([True, False])

        msg = "YES" if has_demon else "NO"
        await game.command_cog.send_direct_message(player.player_name, f"Demon presence: {msg}")


@register_role(RoleName.RAVENKEEPER)
class RavenkeeperBehavior(RoleBehavior):
    other_night_priority = 6
    async def act(self, player: Player, game: GameManager) -> None:
        if game.killed_tonight == player.player_name:
            target_list = get_filtered_players(game, excluded_players={player})
            sel = await game.command_cog.dmdropdown(player.player_name, "You died! Select a player to view their role:", [p.player_name for p in target_list], 1)
            
            if sel:
                target = game.get_player_by_name(sel[0])
                if player.status.is_reliable:
                    await game.command_cog.send_direct_message(player.player_name, f"{target.player_name} is the {target.registered_role}.")
                else:
                    fake_role = random.choice([r for r in RoleName if r != target.registered_role])
                    await game.command_cog.send_direct_message(player.player_name, f"{target.player_name} is the {fake_role}.")


# ==========================================
# PASSIVE / DAY ROLES (Do nothing at night)
# ==========================================

@register_role(RoleName.VIRGIN)
class VirginBehavior(PassiveBehavior):
    pass # Triggered during nominations in the Day Phase

@register_role(RoleName.SLAYER)
class SlayerBehavior(PassiveBehavior):
    pass # Triggered via bot command during the Day Phase

@register_role(RoleName.SOLDIER)
class SoldierBehavior(PassiveBehavior):
    pass # Status handled by Imp's kill check

@register_role(RoleName.MAYOR)
class MayorBehavior(PassiveBehavior):
    pass # Triggered at the end of the execution phase
