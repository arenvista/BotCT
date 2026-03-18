# src/botc/game.py
import random
from typing import List, Optional, Tuple

from botc.enums import Alignment, RoleClass, RoleName
from botc.player import Player

class GameMaster: 
    def __init__(self, player_name: str):
        self.player_name = player_name

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
        chosen_minions = random.sample(self.ROLES_MINIONS, m_count)

        if RoleName.BARON in chosen_minions:
            BARON_OUTSIDER_OFFSET = 3
            o_count += BARON_OUTSIDER_OFFSET
            t_count -= BARON_OUTSIDER_OFFSET

        chosen_outsiders = random.sample(self.ROLES_OUTSIDERS, o_count)
        chosen_townsfolk = random.sample(self.ROLES_TOWNSFOLK, t_count)

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

    def get_alive_neighbors(self, target_player: Player) -> Tuple[Player, Player]:
        index = self.players.index(target_player)
        num_players = len(self.players)

        right_idx = (index + 1) % num_players
        while not self.players[right_idx].alive:
            right_idx = (right_idx + 1) % num_players
            if right_idx == index: break
        right_neighbor = self.players[right_idx]

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
        player_name = input("Select Target: ")
        for p in self.players:
            if p.player_name == player_name: return p
        raise ValueError(f"Player {player_name}")

    def get_wake_order(self, is_first_night: bool) -> List[Player]:
        waking_players = []
        for player in self.players:
            priority = player.role_behavior.first_night_priority if is_first_night else player.role_behavior.other_night_priority
            if priority is not None:
                waking_players.append((priority, player))
        
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
