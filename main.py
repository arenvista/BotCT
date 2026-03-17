import random
from typing import List, Dict

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
    ROLES_DEMONS: List[Dict[str, str]] = [
        {"role": "Imp", "role_description": "Each night*, choose a player: they die. If you kill yourself this way, a Minion becomes the Imp."}
    ]
    
    ROLES_MINIONS: List[Dict[str, str]] = [ 
        {"role": "Poisoner", "role_description": "Each night, choose a player: they are poisoned tonight and tomorrow day."},
        {"role": "Spy", "role_description": "Each night, you see the Grimoire. You might register as good & as a Townsfolk or Outsider, even if dead."},
        {"role": "Baron", "role_description": "There are extra Outsiders in play. [+2 Outsiders]"},
        {"role": "Scarlet Woman", "role_description": "If there are 5 or more players alive & the Demon dies, you become the Demon. (Travellers don't count.)"},
    ]
    
    # FIXED: Renamed from ROLES_TOWNSFOLK to ROLES_OUTSIDERS
    ROLES_OUTSIDERS: List[Dict[str, str]] = [
        {"role": "Butler", "role_description": "Each night, choose a player (not yourself): tomorrow, you may only vote if they are voting too."},
        {"role": "Drunk", "role_description": "You do not know you are the Drunk. You think you are a Townsfolk character, but you are not."},
        {"role": "Recluse", "role_description": "You might register as evil & as a Minion or Demon, even if dead."},
        {"role": "Saint", "role_description": "If you die by execution, your team loses."},
    ]
    
    ROLES_TOWNSFOLK: List[Dict[str, str]] = [
        {"role": "Washerwoman", "role_description": "You start knowing that 1 of 2 players is a particular Townsfolk."},
        {"role": "Librarian", "role_description": "You start knowing that 1 of 2 players is a particular Outsider. (Or that zero are in play.)"},
        {"role": "Investigator", "role_description": "You start knowing that 1 of 2 players is a particular Minion."},
        {"role": "Chef", "role_description": "You start knowing how many pairs of evil players there are."},
        {"role": "Empath", "role_description": "Each night, you learn how many of your 2 alive neighbors are evil."},
        {"role": "Fortune Teller", "role_description": "Each night, choose 2 players: you learn if either is a Demon. There is a good player that registers as a Demon to you."},
        {"role": "Undertaker", "role_description": "Each night*, you learn which character died by execution today."},
        {"role": "Monk", "role_description": "Each night*, choose a player (not yourself): they are safe from the Demon tonight."},
        {"role": "Ravenkeeper", "role_description": "If you die at night, you are woken to choose a player: you learn their character."},
        {"role": "Virgin", "role_description": "The 1st time you are nominated, if the nominator is a Townsfolk, they are executed immediately."},
        {"role": "Slayer", "role_description": "Once per game, during the day, publicly choose a player: if they are the Demon, they die."},
        {"role": "Soldier", "role_description": "You are safe from the Demon."},
        {"role": "Mayor", "role_description": "If only 3 players live & no execution occurs, your team wins. If you die at night, another player might die instead."},
    ]

    def __init__(self, players: List[str]):
        self.players = players
        self.num_players = len(players)
        self.roles_distribution = RoleDistributor(self.players)
        self.player_roles: List[Role] = self.assign_roles()

    def assign_roles(self) -> List[Role]:
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

        # Pair up each player with a role from the shuffled bag
        assigned_roles = []
        for player, role_data in zip(self.players, all_selected_roles):
            # Extract just the string name for the role instantiation
            role_name = role_data["role"] 
            print(f"Assigning {player} -> {role_name}")
            
            # Assuming the Role class expects a player name and a role name string
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
