from __future__ import annotations
import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Tuple


# --- ENUMS ---
class Alignment(Enum):
    GOOD = 1
    EVIL = 2

    def __str__(self):
        return self.name.title()

class RoleClass(Enum):
    DEMONS = 1
    MINIONS = 2
    OUTSIDERS = 3
    TOWNSFOLK = 4

    @property
    def display_name(self) -> str: 
        return self.name.replace('_', ' ').title()
    def __str__(self): 
        return self.display_name

class RoleName(Enum):
    role_class: RoleClass

    def __new__(cls, value: int, role_class: RoleClass):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.role_class = role_class
        return obj

    # Minions
    POISONER = (1, RoleClass.MINIONS)
    SPY = (2, RoleClass.MINIONS)
    BARON = (3, RoleClass.MINIONS)
    SCARLET_WOMAN = (4, RoleClass.MINIONS)

    # Outsiders
    BUTLER = (5, RoleClass.OUTSIDERS)
    DRUNK = (6, RoleClass.OUTSIDERS)
    RECLUSE = (7, RoleClass.OUTSIDERS)
    SAINT = (8, RoleClass.OUTSIDERS)

    # Townsfolk
    WASHERWOMAN = (9, RoleClass.TOWNSFOLK)
    LIBRARIAN = (10, RoleClass.TOWNSFOLK)
    INVESTIGATOR = (11, RoleClass.TOWNSFOLK)
    CHEF = (12, RoleClass.TOWNSFOLK)
    EMPATH = (13, RoleClass.TOWNSFOLK)
    FORTUNE_TELLER = (14, RoleClass.TOWNSFOLK)
    UNDERTAKER = (15, RoleClass.TOWNSFOLK)
    MONK = (16, RoleClass.TOWNSFOLK)
    RAVENKEEPER = (17, RoleClass.TOWNSFOLK)
    VIRGIN = (18, RoleClass.TOWNSFOLK)
    SLAYER = (19, RoleClass.TOWNSFOLK)
    SOLDIER = (20, RoleClass.TOWNSFOLK)
    MAYOR = (21, RoleClass.TOWNSFOLK)

    # Demons
    IMP = (22, RoleClass.DEMONS)

    @property
    def display_name(self) -> str: 
        return self.name.replace('_', ' ').title()

    def __str__(self): 
        return self.display_name

    @classmethod
    def get_by_class(cls, target_class: RoleClass) -> List['RoleName']:
        """Helper method to easily grab all roles of a specific class."""
        return [role for role in cls if role.role_class == target_class]


# --- BEHAVIOR ARCHITECTURE (STRATEGY PATTERN) ---

# The central registry for mapping RoleNames to their behavior instances
BEHAVIOR_MAP = {}

def register_role(*role_names: RoleName):
    """Decorator to automatically register a behavior to one or more roles."""
    def decorator(cls):
        behavior_instance = cls()
        for role in role_names:
            BEHAVIOR_MAP[role] = behavior_instance
        return cls
    return decorator

class RoleBehavior(ABC):
    """
    Base class for all role logic. 
    Priorities determine wake order (lower numbers wake up first).
    If priority is None, the role does not wake that night.
    """
    first_night_priority: Optional[int] = None
    other_night_priority: Optional[int] = None

    @abstractmethod
    def act(self, player: 'Player', game: 'GameManager') -> None:
        """The action this role takes during the night."""
        pass

@register_role(
    RoleName.BARON, RoleName.DRUNK, RoleName.RECLUSE, RoleName.SAINT,
    RoleName.VIRGIN, RoleName.SLAYER, RoleName.SOLDIER, RoleName.MAYOR
)
class PassiveBehavior(RoleBehavior):
    """For roles that don't wake up in the night to take actions."""
    def act(self, player: 'Player', game: 'GameManager') -> None:
        pass

# -- Minion Behaviors --
@register_role(RoleName.POISONER)
class PoisonerBehavior(RoleBehavior):
    first_night_priority = 1
    other_night_priority = 1

    def act(self, player: 'Player', game: 'GameManager') -> None:
        prompt = f"\nWake {player.believed_role} ({player.player_name}). Who do they poison?"
        print(prompt)
        # Note: In a real app, replace this with actual input/selection logic
        target = game.get_player_by_name() 
        target.poisoned = True
        print(f"Put {player.believed_role} to sleep.")

@register_role(RoleName.SPY)
class SpyBehavior(RoleBehavior):
    first_night_priority = 2
    other_night_priority = 3

    def act(self, player: 'Player', game: 'GameManager') -> None:
        prompt = f"\nWake {player.believed_role} ({player.player_name}). Show them the Grimoire. Put to sleep."
        print(prompt)

@register_role(RoleName.SCARLET_WOMAN)
class ScarletWomanBehavior(RoleBehavior):
    other_night_priority = 4

    def act(self, player: 'Player', game: 'GameManager') -> None:
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

# -- Demon Behaviors --
@register_role(RoleName.IMP)
class ImpBehavior(RoleBehavior):
    other_night_priority = 5

    def act(self, player: 'Player', game: 'GameManager') -> None:
        prompt = f"\nWake {player.believed_role} ({player.player_name}). Who do they kill?"
        print(prompt)
        target = game.get_player_by_name()
        if target and not target.protected:
            target.alive = False
            game.killed_tonight = target 
            print(f"{target.player_name} died.")
        elif target and target.protected:
            print(f"{target.player_name} was protected by the Monk and survives.")
        print(f"Put {player.believed_role} to sleep.")

# -- Townsfolk/Outsider Behaviors --
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

@register_role(RoleName.BUTLER)
class ButlerBehavior(RoleBehavior):
    first_night_priority = 9
    other_night_priority = 10
    def act(self, player: 'Player', game: 'GameManager'):
        print(f"\nWake {player.believed_role} ({player.player_name}). Who is their Master? Put to sleep.")

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

# --- CORE GAME CLASSES ---
class GameMaster: 
    def __init__(self, player_name: str):
        self.player_name = player_name

class Player: 
    def __init__(self, player_name: str, actual_role: RoleName, believed_role: RoleName | None = None, registered_role: RoleName | None = None, registered_alignment: Alignment | None = None):
        self.player_name: str = player_name
        self.actual_role: RoleName = actual_role

        # What the player thinks they are (Drunk mechanics)
        self.believed_role: RoleName = believed_role if believed_role else actual_role

        # What the player shows up as to info roles (Spy mechanics)
        self.registered_role: RoleName = registered_role if registered_role else actual_role
        self.registered_alignment: Alignment = registered_alignment if registered_alignment else self._default_alignment()

        self.alive: bool = True
        self.poisoned: bool = False
        self.protected: bool = False

        # Assign behavior based on what they *think* they are
        self.role_behavior: RoleBehavior = BEHAVIOR_MAP.get(self.believed_role, PassiveBehavior())

    def _default_alignment(self) -> Alignment:
        if self.actual_role.role_class in (RoleClass.DEMONS, RoleClass.MINIONS):
            return Alignment.EVIL
        return Alignment.GOOD

    def take_action(self, game: GameManager):
        # Dead players usually don't act, but the Ravenkeeper acts immediately after dying
        if not self.alive and self.believed_role != RoleName.RAVENKEEPER:
            return
        
        # Delegate logic to the specific behavior class
        self.role_behavior.act(self, game)


class RoleDistributor:
    DISTRIBUTION_TABLE = {
        5:  (1, 0, 3, 1), 6:  (1, 1, 3, 1), 7:  (1, 0, 5, 1), 8:  (1, 1, 5, 1),
        9:  (1, 2, 5, 1), 10: (1, 0, 7, 2), 11: (1, 1, 7, 2), 12: (1, 2, 7, 2),
        13: (1, 0, 9, 3), 14: (1, 1, 9, 3), 15: (1, 2, 9, 3),
    }

    def __init__(self, player_names: List[str]):
        self.player_names = player_names
        self.num_demons, self.num_outsiders, self.num_townsfolk, self.num_minions = self.split_players()

    def split_players(self):
        num_players = min(len(self.player_names), 15)
        if num_players < 5: 
            raise ValueError("Sorry, numbers less than 5 are not allowed.")
        return self.DISTRIBUTION_TABLE[num_players]


class GameManager:
    ROLES_DEMONS = RoleName.get_by_class(RoleClass.DEMONS)
    ROLES_MINIONS = RoleName.get_by_class(RoleClass.MINIONS)
    ROLES_OUTSIDERS = RoleName.get_by_class(RoleClass.OUTSIDERS)
    ROLES_TOWNSFOLK = RoleName.get_by_class(RoleClass.TOWNSFOLK)

    def __init__(self, player_names: List[str]):
        self.player_names = player_names
        self.num_players = len(player_names)
        self.roles_distribution = RoleDistributor(self.player_names)
        self.players: List[Player] = self.assign_roles()
        self.turn_counter: int = 0
        self.killed_tonight: Optional[Player] = None
        self.game_master: GameMaster = GameMaster("GM")

    def assign_roles(self) -> List[Player]:
        d_count, o_count, t_count, m_count = (
            self.roles_distribution.num_demons, self.roles_distribution.num_outsiders,
            self.roles_distribution.num_townsfolk, self.roles_distribution.num_minions
        )

        chosen_demons = random.sample(self.ROLES_DEMONS, d_count)
        chosen_outsiders = random.sample(self.ROLES_OUTSIDERS, o_count)
        chosen_townsfolk = random.sample(self.ROLES_TOWNSFOLK, t_count)
        chosen_minions = random.sample(self.ROLES_MINIONS, m_count)

        selected_roles = chosen_demons + chosen_outsiders + chosen_townsfolk + chosen_minions

        drunk_fake_role = None
        if RoleName.DRUNK in chosen_outsiders:
            available_townsfolk = [r for r in self.ROLES_TOWNSFOLK if r not in chosen_townsfolk]
            drunk_fake_role = random.choice(available_townsfolk)

        spy_fake_role = None
        if RoleName.SPY in chosen_minions:
            available_good_roles = [r for r in (self.ROLES_TOWNSFOLK + self.ROLES_OUTSIDERS) if r not in (chosen_townsfolk + chosen_outsiders) and r != drunk_fake_role]
            if available_good_roles:
                spy_fake_role = random.choice(available_good_roles)

        random.shuffle(selected_roles)

        assigned = []
        for player_name, role_enum in zip(self.player_names, selected_roles):
            believed_role = None
            registered_role = None
            registered_alignment = None

            if role_enum == RoleName.DRUNK:
                believed_role = drunk_fake_role
            elif role_enum == RoleName.SPY and spy_fake_role:
                registered_role = spy_fake_role
                registered_alignment = Alignment.GOOD 

            assigned.append(Player(player_name, role_enum, believed_role, registered_role, registered_alignment))

        return assigned

    # --- SEATING & NEIGHBOR HELPERS ---
    def get_alive_neighbors(self, target_player: Player) -> Tuple[Player, Player]:
        index = self.players.index(target_player)
        num_players = len(self.players)

        # Right Neighbor
        right_idx = (index + 1) % num_players
        while not self.players[right_idx].alive:
            right_idx = (right_idx + 1) % num_players
            if right_idx == index: break
        right_neighbor = self.players[right_idx]

        # Left Neighbor
        left_idx = (index - 1) % num_players
        while not self.players[left_idx].alive:
            left_idx = (left_idx - 1) % num_players
            if left_idx == index: break
        left_neighbor = self.players[left_idx]

        return left_neighbor, right_neighbor

    def get_player_by_role(self, target_role: RoleName) -> Optional[Player]:
        for p in self.players:
            if p.actual_role == target_role: return p
        return None

    def get_player_by_name(self) -> Player:
        # Stub for CLI input
        player_name = input("Select Target: ")
        for p in self.players:
            if p.player_name == player_name: return p
        raise ValueError(f"Player {player_name}")

    # --- DYNAMIC NIGHT PHASES ---
    def get_wake_order(self, is_first_night: bool) -> List[Player]:
        """Dynamically sorts players by their behavior's priority for the current night."""
        waking_players = []
        for player in self.players:
            priority = player.role_behavior.first_night_priority if is_first_night else player.role_behavior.other_night_priority
            if priority is not None:
                waking_players.append((priority, player))
        
        # Sort by priority ascending, then return just the player objects
        waking_players.sort(key=lambda x: x[0])
        return [p for priority, p in waking_players]

    def night_one(self):
        print("\n=== NIGHT 1 ===")
        print("Everyone close your eyes. Put everyone to sleep.")

        imp = self.get_player_by_role(RoleName.IMP)
        minions = [p for p in self.players if p.actual_role.role_class == RoleClass.MINIONS]

        if imp and minions:
            print(f"\nWake Minions ({', '.join([m.player_name for m in minions])}). Show them Imp is {imp.player_name}. Sleep.")
            print(f"Wake Imp ({imp.player_name}). Show them Minions are {', '.join([m.player_name for m in minions])}.")

            in_play_bluffs = [p.believed_role for p in self.players] + [p.registered_role for p in self.players if p.actual_role == RoleName.SPY]
            all_good = self.ROLES_TOWNSFOLK + self.ROLES_OUTSIDERS
            bluffs = random.sample([r for r in all_good if r not in in_play_bluffs], 3)
            print(f"-> Show Imp these 3 bluffs: {', '.join(str(b) for b in bluffs)}. Put to sleep.")

        # Let the dynamic order take over
        for player in self.get_wake_order(is_first_night=True):
            player.take_action(self)

        print("\n=== DAWN ===")
        self.turn_counter += 1

    def night_next(self) -> None:
        print(f"\n=== NIGHT {self.turn_counter + 1} ===")
        self.killed_tonight = None
        for p in self.players:
            p.poisoned = False
            p.protected = False

        # Let the dynamic order take over
        for player in self.get_wake_order(is_first_night=False):
            player.take_action(self)

        print("\n=== DAWN ===")
        self.turn_counter += 1

    def print_board(self) -> None:
        print("\n" + "="*55)
        print(f"=== GRIMOIRE (STORYTELLER VIEW) - Turn {self.turn_counter} ===")
        print("="*55)

        for i, player in enumerate(self.players):
            status = "Alive" if player.alive else "DEAD"
            poison_str = " [POISONED]" if player.poisoned else ""
            protect_str = " [PROTECTED]" if player.protected else ""

            if player.actual_role == RoleName.DRUNK:
                role_info = f"Drunk (Thinks: {player.believed_role})"
            elif player.actual_role == RoleName.SPY:
                role_info = f"Spy (Registers: {player.registered_role}/{player.registered_alignment})"
            else:
                role_info = f"{player.actual_role} ({player.registered_alignment})"

            print(f"Seat {i+1:02d} | {player.player_name:<8} | {status:<5} | {role_info}{poison_str}{protect_str}")
        print("="*55 + "\n")


def main():
    example = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry"]
    game = GameManager(example)
    print("--- SEATING & ROLES (STORYTELLER VIEW) ---")
    for i, player in enumerate(game.players):
        prefix = f"Seat {i+1} - {player.player_name}"
        if player.actual_role == RoleName.DRUNK:
            print(f"{prefix}: {player.actual_role} (Thinks they are {player.believed_role})")
        elif player.actual_role == RoleName.SPY:
            print(f"{prefix}: {player.actual_role} (Registers as {player.registered_role}/{player.registered_alignment})")
        else:
            print(f"{prefix}: {player.actual_role} (Alignment: {player.registered_alignment})")
            
    game.night_one()
    game.print_board()
    game.night_next()
    game.print_board()

if __name__ == "__main__":
    main()
