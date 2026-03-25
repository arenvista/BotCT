from typing import List

class RoleDistributor:
    DISTRIBUTION_TABLE = {
        5:  (1, 0, 3, 1), 6:  (1, 1, 3, 1), 7:  (1, 0, 5, 1), 8:  (1, 1, 5, 1),
        9:  (1, 2, 5, 1), 10: (1, 0, 7, 2), 11: (1, 1, 7, 2), 12: (1, 2, 7, 2),
        13: (1, 0, 9, 3), 14: (1, 1, 9, 3), 15: (1, 2, 9, 3),
    }

    def __init__(self, player_names: List[str]):
        self.player_names = player_names
        self.num_demons, self.num_outsiders, self.num_townsfolk, self.num_minions = self._calculate_role_counts()

    def _calculate_role_counts(self):
        num_players = min(len(self.player_names), 15)
        
        # Auto-fill for testing if under 5 players
        # if num_players < 5: 
        #     for i in range(len(self.player_names) + 1, 6):
        #         self.player_names.append(f"Player {i}")
        #     num_players = 5
            
        if num_players == 1:
            num_players = 5
        return self.DISTRIBUTION_TABLE[num_players]
