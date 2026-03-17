import random
from typing import List

class Role: 
    def __init__(self, name_player: str, name_role: str):
        self.name_player: str  = name_player
        self.name_role: str  = name_role
        self.alive: bool = True
        self.poisoned: bool = False

class RoleDistributor:
    # A class-level dictionary serves as a clean, readable lookup table
    # Format: { num_players: (demons, outsiders, townsfolk, minions) }
    DISTRIBUTION_TABLE = {
        5:  (1, 0, 3, 1),
        6:  (1, 1, 3, 1),
        7:  (1, 0, 5, 1),
        8:  (1, 1, 5, 1),
        9:  (1, 2, 5, 1),
        10: (1, 0, 7, 2),
        11: (1, 1, 7, 2),
        12: (1, 2, 7, 2),
        13: (1, 0, 9, 3),
        14: (1, 1, 9, 3),
        15: (1, 2, 9, 3),
    }

    def __init__(self, players: List[str]):
        self.players = players
        self.num_demons, self.num_outsiders, self.num_townsfolk, self.num_minions = self.split_players()

    def split_players(self):
        num_players = min(len(self.players), 15)
        
        if num_players < 5: 
            raise ValueError("Sorry, numbers less than 5 are not allowed.")
            
        return self.DISTRIBUTION_TABLE[num_players]


class GameMgr:
    ROLES_DEMONS = ["Imp"]
    ROLES_TOWNSFOLK = [
        "Washerwoman", 
        "Librarian",
        "Investigtor",
        "Chef",
        "Empath",
        "Fortune Teller",
        "Undertaker",
        "Monk",
        "Ravenkeeper",
        "Virgin",
        "Slayer",
        "Soldier",
        "Mayor"
    ]
    ROLES_OUTSIDERS = [
        "Butler",
        "Drunk",
        "Recluse",
        "Saint"
    ]
    ROLES_MINIONS = [
        "Poisoner",
        "Spy", 
        "Baron", 
        "Scarlet Woman"
    ]

    def __init__(self, players: List[str]):
        self.players: List[str] = players
        self.num_players = len(players)
        self.roles_distribution = RoleDistributor(self.players)
        self.player_roles: List[Role] = self.AssignRoles()

    def AssignRoles(self) -> List[Role]:
        # Get the target counts from our distributor
        d_count = self.roles_distribution.num_demons
        o_count = self.roles_distribution.num_outsiders
        t_count = self.roles_distribution.num_townsfolk
        m_count = self.roles_distribution.num_minions

        # random.sample guarantees we don't pick the same role twice
        selected_demons = random.sample(self.ROLES_DEMONS, d_count)
        selected_outsiders = random.sample(self.ROLES_OUTSIDERS, o_count)
        selected_townsfolk = random.sample(self.ROLES_TOWNSFOLK, t_count)
        selected_minions = random.sample(self.ROLES_MINIONS, m_count)

        # Combine them into one "bag" of roles
        all_selected_roles = (
            selected_demons + 
            selected_outsiders + 
            selected_townsfolk + 
            selected_minions
        )

        # Shuffle the bag so player assignment is completely random
        random.shuffle(all_selected_roles)

        #  Pair up each player with a role from the shuffled bag
        assigned_roles = []
        for player, role_name in zip(self.players, all_selected_roles):
            print(player, role_name)
            assigned_roles.append(Role(player, role_name))

        return assigned_roles


def main():
    example = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
    ]
    game = GameMgr(example)


if __name__ == "__main__":
    main()
