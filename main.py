import random
from typing import List, Dict, Optional

class Role: 
    def __init__(self, name_player: str, name_role: str):
        self.name_player: str  = name_player
        self.name_role: str  = name_role
        self.alive: bool = True
        self.poisoned: bool = False
        self.protected: bool = False
        self.class_role: str = "NULL"

    # We pass 'game' in so the role can see the board and interact with others
    def TakeAction(self, game: 'GameMgr'):
        # If they are dead (and not a role that acts on death), they do nothing
        if not self.alive and self.name_role not in ["Ravenkeeper"]:
            return

        match self.name_role: 
            case "Poisoner": self.Act_Poisoner(game)
            case "Spy": self.Act_Spy(game)
            case "Baron": pass # Passive setup role, no night action
            case "Scarlet Woman": self.Act_Scarlet_Woman(game)
            case "Butler": self.Act_Butler(game)
            case "Washerwoman": self.Act_Washerwoman(game)
            case "Librarian": self.Act_Librarian(game)
            case "Investigator": self.Act_Investigator(game)
            case "Chef": self.Act_Chef(game)
            case "Empath": self.Act_Empath(game)
            case "Fortune Teller": self.Act_Fortune_Teller(game)
            case "Undertaker": self.Act_Undertaker(game)
            case "Monk": self.Act_Monk(game)
            case "Ravenkeeper": self.Act_Ravenkeeper(game)
            case "Imp": self.Act_Imp(game)
            # Passive or Day roles - they don't wake up at night
            case "Drunk" | "Recluse" | "Saint" | "Virgin" | "Slayer" | "Soldier" | "Mayor":
                pass 

    # --- ACTION IMPLEMENTATIONS ---
    def Act_Poisoner(self, game: 'GameMgr'):
        target_name = input(f"\nWake Poisoner ({self.name_player}). Who do they poison? ")
        target = game.get_player_by_name(target_name)
        if target:
            target.poisoned = True
        print("Put Poisoner to sleep.")

    def Act_Monk(self, game: 'GameMgr'):
        target_name = input(f"\nWake Monk ({self.name_player}). Who do they protect? ")
        target = game.get_player_by_name(target_name)
        if target:
            target.protected = True
        print("Put Monk to sleep.")

    def Act_Spy(self, game: 'GameMgr'):
        print(f"\nWake Spy ({self.name_player}). Show them the Grimoire. Put to sleep.")

    def Act_Scarlet_Woman(self, game: 'GameMgr'):
        imp = game.get_player_by_role("Imp")
        alive_players = len([p for p in game.player_roles if p.alive])
        if imp and not imp.alive and alive_players >= 5:
            print(f"\n*** The Imp is dead. The Scarlet Woman ({self.name_player}) is now the Imp! ***")
            self.name_role = "Imp"

    def Act_Imp(self, game: 'GameMgr'):
        target_name = input(f"\nWake Imp ({self.name_player}). Who do they kill? ")
        target = game.get_player_by_name(target_name)
        if target and not target.protected:
            target.alive = False
            game.killed_tonight = target # Save for Ravenkeeper check
            print(f"{target.name_player} died.")
        elif target and target.protected:
            print(f"{target.name_player} was protected by the Monk and survives.")
        print("Put Imp to sleep.")

    def Act_Butler(self, game: 'GameMgr'):
        target = input(f"\nWake Butler ({self.name_player}). Who is their Master? ")
        print(f"Butler chose {target}. Put to sleep.")

    def Act_Ravenkeeper(self, game: 'GameMgr'):
        # Only wakes up if they were the specific person killed tonight
        if game.killed_tonight == self:
             print(f"\nWake Ravenkeeper ({self.name_player}). They died! Let them point to a player, show them the role. Put to sleep.")

    # Generic Info Roles (Storyteller handles the exact info)
    def Act_Washerwoman(self, game): print(f"\nWake Washerwoman ({self.name_player}). Show them 1 Townsfolk among 2 players. Put to sleep.")
    def Act_Librarian(self, game): print(f"\nWake Librarian ({self.name_player}). Show them 1 Outsider among 2 players. Put to sleep.")
    def Act_Investigator(self, game): print(f"\nWake Investigator ({self.name_player}). Show them 1 Minion among 2 players. Put to sleep.")
    def Act_Chef(self, game): print(f"\nWake Chef ({self.name_player}). Show them pairs of evil players. Put to sleep.")
    def Act_Empath(self, game): print(f"\nWake Empath ({self.name_player}). Show them evil neighbors count. Put to sleep.")
    def Act_Fortune_Teller(self, game): print(f"\nWake Fortune Teller ({self.name_player}). Let them pick 2 players, nod if Demon. Put to sleep.")
    def Act_Undertaker(self, game): print(f"\nWake Undertaker ({self.name_player}). Show them the role of today's executed player. Put to sleep.")


class RoleDistributor:
    DISTRIBUTION_TABLE = {
        5:  (1, 0, 3, 1), 6:  (1, 1, 3, 1), 7:  (1, 0, 5, 1), 8:  (1, 1, 5, 1),
        9:  (1, 2, 5, 1), 10: (1, 0, 7, 2), 11: (1, 1, 7, 2), 12: (1, 2, 7, 2),
        13: (1, 0, 9, 3), 14: (1, 1, 9, 3), 15: (1, 2, 9, 3),
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
    ROLES_DEMONS: List[Dict[str, str]] = [{"role": "Imp"}]
    ROLES_MINIONS: List[Dict[str, str]] = [{"role": "Poisoner"}, {"role": "Spy"}, {"role": "Baron"}, {"role": "Scarlet Woman"}]
    ROLES_OUTSIDERS: List[Dict[str, str]] = [{"role": "Butler"}, {"role": "Drunk"}, {"role": "Recluse"}, {"role": "Saint"}]
    ROLES_TOWNSFOLK: List[Dict[str, str]] = [
        {"role": "Washerwoman"}, {"role": "Librarian"}, {"role": "Investigator"}, 
        {"role": "Chef"}, {"role": "Empath"}, {"role": "Fortune Teller"}, 
        {"role": "Undertaker"}, {"role": "Monk"}, {"role": "Ravenkeeper"}, 
        {"role": "Virgin"}, {"role": "Slayer"}, {"role": "Soldier"}, {"role": "Mayor"}
    ]

    def __init__(self, players: List[str]):
        self.players = players
        self.num_players = len(players)
        self.roles_distribution = RoleDistributor(self.players)
        self.player_roles: List[Role] = self.assign_roles()
        self.turn_counter: int = 0
        self.killed_tonight: Optional[Role] = None

    def assign_roles(self) -> List[Role]:
        d_count, o_count, t_count, m_count = (
            self.roles_distribution.num_demons, self.roles_distribution.num_outsiders,
            self.roles_distribution.num_townsfolk, self.roles_distribution.num_minions
        )
        selected_roles = (
            random.sample(self.ROLES_DEMONS, d_count) + 
            random.sample(self.ROLES_OUTSIDERS, o_count) + 
            random.sample(self.ROLES_TOWNSFOLK, t_count) + 
            random.sample(self.ROLES_MINIONS, m_count)
        )
        random.shuffle(selected_roles)
        
        assigned = []
        for player, role_data in zip(self.players, selected_roles):
            assigned.append(Role(player, role_data["role"]))
        return assigned

    # --- HELPERS ---
    def get_player_by_role(self, role_name: str) -> Optional[Role]:
        for p in self.player_roles:
            if p.name_role == role_name: return p
        return None

    def get_player_by_name(self, player_name: str) -> Optional[Role]:
         for p in self.player_roles:
             if p.name_player == player_name: return p
         return None
         
    def wake_role(self, role_name: str):
        """Helper to wake a specific role and run its action."""
        player = self.get_player_by_role(role_name)
        if player: player.TakeAction(self)

    # --- NIGHT PHASES ---
    def NightOne(self):
        print("\n=== NIGHT 1 ===")
        print("Everyone close your eyes. Put everyone to sleep.")

        # 1 & 2. Demon/Minion Info
        imp = self.get_player_by_role("Imp")
        minions = [p for p in self.player_roles if p.name_role in [m["role"] for m in self.ROLES_MINIONS]]
        
        if imp and minions:
            print(f"\nWake Minions ({', '.join([m.name_player for m in minions])}). Show them Imp is {imp.name_player}. Sleep.")
            print(f"Wake Imp ({imp.name_player}). Show them Minions are {', '.join([m.name_player for m in minions])}.")
            
            in_play = [p.name_role for p in self.player_roles]
            all_good = [r["role"] for r in self.ROLES_TOWNSFOLK + self.ROLES_OUTSIDERS]
            bluffs = random.sample([r for r in all_good if r not in in_play], 3)
            print(f"-> Show Imp these 3 bluffs: {', '.join(bluffs)}. Put to sleep.")

        # 3 - 11. Iterate through the exact wake order using your Role actions
        wake_order = [
            "Poisoner", "Spy", "Washerwoman", "Librarian", "Investigator", 
            "Chef", "Empath", "Fortune Teller", "Butler"
        ]
        for role in wake_order:
            self.wake_role(role)

        print("\n=== DAWN ===")
        self.turn_counter += 1

    def NightNext(self):
        print(f"\n=== NIGHT {self.turn_counter + 1} ===")
        self.killed_tonight = None # Reset
        for p in self.player_roles:
            p.poisoned = False
            p.protected = False

        # 1 - 3
        self.wake_role("Poisoner")
        self.wake_role("Monk")
        self.wake_role("Spy")
        
        # 4 & 5
        self.wake_role("Scarlet Woman") # Checks condition internally
        self.wake_role("Imp")           # Does the kill
        
        # 6 - 10
        wake_order = ["Ravenkeeper", "Undertaker", "Empath", "Fortune Teller", "Butler"]
        for role in wake_order:
            self.wake_role(role)

        print("\n=== DAWN ===")
        self.turn_counter += 1


def main():
    example = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]
    game = GameMgr(example)
    
    print("--- ROLES ASSIGNED ---")
    for player in game.player_roles:
        print(f"{player.name_player}: {player.name_role}")

    # Run a test loop
    game.NightOne()
    game.NightNext()

if __name__ == "__main__":
    main()
