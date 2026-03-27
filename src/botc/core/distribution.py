from typing import List
from botc import RoleName, RoleClass, Alignment, Player
import random

class RoleDistributor:
    DISTRIBUTION_TABLE = {
        5:  (1, 0, 3, 1), 6:  (1, 1, 3, 1), 7:  (1, 0, 5, 1), 8:  (1, 1, 5, 1),
        9:  (1, 2, 5, 1), 10: (1, 0, 7, 2), 11: (1, 1, 7, 2), 12: (1, 2, 7, 2),
        13: (1, 0, 9, 3), 14: (1, 1, 9, 3), 15: (1, 2, 9, 3),
    }

    def __init__(self, player_names: List[str]=[]):
        self.player_names = player_names
        self.num_demons = -1
        self.num_outsiders = -1
        self.num_townsfolk = -1
        self.num_minions = -1

    def _calculate_role_counts(self):
        num_players = min(len(self.player_names), 15)
        return self.DISTRIBUTION_TABLE[num_players]

    def assign_roles(self) -> List[Player]:
        self.num_demons, self.num_outsiders, self.num_townsfolk, self.num_minions = self._calculate_role_counts()
        if self.player_names == []:
            print("Can NOT Assign Roles, Empty")
            exit()

        ROLES_DEMONS = RoleName.get_by_class(RoleClass.DEMONS)
        ROLES_MINIONS = RoleName.get_by_class(RoleClass.MINIONS)
        ROLES_OUTSIDERS = RoleName.get_by_class(RoleClass.OUTSIDERS)
        ROLES_TOWNSFOLK = RoleName.get_by_class(RoleClass.TOWNSFOLK)

        chosen_demons = random.sample(ROLES_DEMONS, self.num_demons)
        chosen_minions = random.sample(ROLES_MINIONS, self.num_minions)

        if RoleName.BARON in chosen_minions:
            BARON_OUTSIDER_OFFSET = 2 
            self.num_outsiders += BARON_OUTSIDER_OFFSET
            self.num_townsfolk -= BARON_OUTSIDER_OFFSET

        chosen_outsiders = random.sample(ROLES_OUTSIDERS, self.num_outsiders)
        chosen_townsfolk = random.sample(ROLES_TOWNSFOLK, self.num_townsfolk)
        selected_roles = chosen_demons + chosen_outsiders + chosen_townsfolk + chosen_minions

        drunk_fake_role = None
        if RoleName.DRUNK in chosen_outsiders:
            available_townsfolk = [r for r in ROLES_TOWNSFOLK if r not in chosen_townsfolk]
            drunk_fake_role = random.choice(available_townsfolk)

        spy_fake_role = None
        if RoleName.SPY in chosen_minions:
            available_good_roles = [
                r for r in (ROLES_TOWNSFOLK + ROLES_OUTSIDERS) 
                if r not in (chosen_townsfolk + chosen_outsiders) and r != drunk_fake_role
            ]
            if available_good_roles:
                spy_fake_role = random.choice(available_good_roles)


        random.shuffle(selected_roles)

        assigned_players: List[Player] = []
        for player_name, role_enum in zip(self.player_names, selected_roles):
            
            # The Drunk thinks they are a Townsfolk, otherwise everyone believes their actual role
            believed_role = drunk_fake_role if role_enum == RoleName.DRUNK else role_enum
            
            # The Spy registers falsely to abilities, otherwise everyone registers as their actual role
            registered_role = spy_fake_role if role_enum == RoleName.SPY else role_enum
            
            # Spy registers as Good, everyone else passes None so Player.__init__ sets their default
            registered_alignment = Alignment.GOOD if role_enum in ROLES_TOWNSFOLK+ROLES_OUTSIDERS else Alignment.EVIL

            assigned_players.append(
                Player(player_name, believed_role, registered_role, registered_alignment)
            )

        if RoleName.FORTUNE_TELLER in chosen_townsfolk:
            red_herring_index = random.randint(0,len(chosen_townsfolk)-1)
            assigned_players[red_herring_index].status.red_herring = True

        return assigned_players
