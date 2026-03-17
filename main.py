import random
from typing import Dict, List, Optional, Tuple


class GameMaster: 
    def __init__(self, player_name: str):
        self.player_name = player_name
    def modify_info(self, input_information: str):
        return
class Role: 
    def __init__(self, name_player: str, name_role: str, believed_role: str|None = None, registered_role: str|None = None, registered_alignment: str|None = None):
        self.name_player: str  = name_player
        self.name_role: str  = name_role
        
        # What the player thinks they are (Drunk mechanics)
        self.believed_role: str = believed_role if believed_role else name_role
        
        # What the player shows up as to info roles (Spy mechanics)
        self.registered_role: str = registered_role if registered_role else name_role
        self.registered_alignment: str = registered_alignment if registered_alignment else self._default_alignment()
        
        self.alive: bool = True
        self.poisoned: bool = False
        self.protected: bool = False

    def _default_alignment(self) -> str:
        if self.name_role in ["Imp", "Poisoner", "Spy", "Baron", "Scarlet Woman"]:
            return "Evil"
        return "Good"

    def TakeAction(self, game: GameMgr):
        if not self.alive and self.believed_role not in ["Ravenkeeper"]:
            return

        match self.believed_role: 
            case "Poisoner": self.Act_Poisoner(game)
            case "Spy": self.Act_Spy(game)
            case "Baron": pass 
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
            case "Drunk" | "Recluse" | "Saint" | "Virgin" | "Slayer" | "Soldier" | "Mayor":
                pass 

    # --- ACTION IMPLEMENTATIONS ---
    def Act_Poisoner(self, game: GameMgr):
        target_name = input(f"\nWake {self.believed_role} ({self.name_player}). Who do they poison? ")
        target = game.get_player_by_name(target_name)
        if target: target.poisoned = True
        print(f"Put {self.believed_role} to sleep.")

    def Act_Monk(self, game: GameMgr):
        target_name = input(f"\nWake {self.believed_role} ({self.name_player}). Who do they protect? ")
        target = game.get_player_by_name(target_name)
        if target: target.protected = True
        print(f"Put {self.believed_role} to sleep.")

    def Act_Spy(self, game: GameMgr):
        print(f"\nWake {self.believed_role} ({self.name_player}). Show them the Grimoire. Put to sleep.")

    def Act_Scarlet_Woman(self, game: GameMgr):
        imp = game.get_player_by_role("Imp")
        alive_players = len([p for p in game.player_roles if p.alive])
        if imp and not imp.alive and alive_players >= 5:
            print(f"\n*** The Imp is dead. The {self.believed_role} ({self.name_player}) is now the Imp! ***")
            self.name_role = "Imp"
            self.believed_role = "Imp"
            self.registered_role = "Imp"
            self.registered_alignment = "Evil"

    def Act_Imp(self, game: GameMgr):
        target_name = input(f"\nWake {self.believed_role} ({self.name_player}). Who do they kill? ")
        target = game.get_player_by_name(target_name)
        if target and not target.protected:
            target.alive = False
            game.killed_tonight = target 
            print(f"{target.name_player} died.")
        elif target and target.protected:
            print(f"{target.name_player} was protected by the Monk and survives.")
        print(f"Put {self.believed_role} to sleep.")

    def Act_Butler(self, game: GameMgr):
        target = input(f"\nWake {self.believed_role} ({self.name_player}). Who is their Master? ")
        print(f"{self.believed_role} chose {target}. Put to sleep.")

    def Act_Ravenkeeper(self, game: GameMgr):
        if game.killed_tonight == self:
             print(f"\nWake {self.believed_role} ({self.name_player}). They died! Let them point to a player, show them the role. Put to sleep.")

    # --- AUTOMATED INFO ROLES ---
    def Act_Empath(self, game: GameMgr):
        left_neighbor, right_neighbor = game.get_alive_neighbors(self)
        
        evil_count = 0
        if left_neighbor and left_neighbor.registered_alignment == "Evil": evil_count += 1
        if right_neighbor and right_neighbor.registered_alignment == "Evil": evil_count += 1

        # Handle Drunk or Poisoned state (Random Info)
        if self.name_role == "Drunk" or self.poisoned:
            fake_count = random.choice([0, 1, 2])
            print(f"\nWake {self.believed_role} ({self.name_player}). Show them {fake_count} fingers [DRUNK/POISONED INFO]. Put to sleep.")
        else:
            print(f"\nWake {self.believed_role} ({self.name_player}). Show them {evil_count} fingers. (True Neighbors: {left_neighbor.name_player}, {right_neighbor.name_player}). Put to sleep.")

    def Act_Chef(self, game: GameMgr):
        # Just a placeholder for now, but you could automate this similar to the Empath!
        print(f"\nWake {self.believed_role} ({self.name_player}). Show them pairs of evil players. Put to sleep.")

    # Generic Info Roles 
    def Act_Washerwoman(self, game): print(f"\nWake {self.believed_role} ({self.name_player}). Show them 1 Townsfolk among 2 players. Put to sleep.")
    def Act_Librarian(self, game): print(f"\nWake {self.believed_role} ({self.name_player}). Show them 1 Outsider among 2 players. Put to sleep.")
    def Act_Investigator(self, game): print(f"\nWake {self.believed_role} ({self.name_player}). Show them 1 Minion among 2 players. Put to sleep.")
    def Act_Fortune_Teller(self, game): print(f"\nWake {self.believed_role} ({self.name_player}). Let them pick 2 players, nod if Demon. Put to sleep.")
    def Act_Undertaker(self, game): print(f"\nWake {self.believed_role} ({self.name_player}). Show them the role of today's executed player. Put to sleep.")


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
    LOG_GM: str = ""

    def __init__(self, players: List[str]):
        self.players = players
        self.num_players = len(players)
        self.roles_distribution = RoleDistributor(self.players)
        self.player_roles: List[Role] = self.assign_roles()
        self.turn_counter: int = 0
        self.killed_tonight: Optional[Role] = None
        self.game_master: GameMaster = GameMaster("GM")

    def assign_roles(self) -> List[Role]:
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
        if any(r["role"] == "Drunk" for r in chosen_outsiders):
            available_townsfolk = [r for r in self.ROLES_TOWNSFOLK if r not in chosen_townsfolk]
            drunk_fake_role = random.choice(available_townsfolk)["role"]

        spy_fake_role = None
        if any(r["role"] == "Spy" for r in chosen_minions):
            available_good_roles = [r for r in (self.ROLES_TOWNSFOLK + self.ROLES_OUTSIDERS) if r not in (chosen_townsfolk + chosen_outsiders) and r["role"] != drunk_fake_role]
            if available_good_roles:
                spy_fake_role = random.choice(available_good_roles)["role"]

        random.shuffle(selected_roles)
        
        assigned = []
        for player, role_data in zip(self.players, selected_roles):
            actual_role = role_data["role"]
            believed_role = None
            registered_role = None
            registered_alignment = None

            if actual_role == "Drunk":
                believed_role = drunk_fake_role
            elif actual_role == "Spy" and spy_fake_role:
                registered_role = spy_fake_role
                registered_alignment = "Good" 

            assigned.append(Role(player, actual_role, believed_role, registered_role, registered_alignment))
            
        return assigned

    # --- SEATING & NEIGHBOR HELPERS ---
    def get_alive_neighbors(self, target_player: Role) -> Tuple[Role, Role]:
        """Returns the closest alive neighbors (Left, Right) in the seating circle."""
        
        index = self.player_roles.index(target_player)
        num_players = len(self.player_roles)
        
        # Find Right Neighbor (+1 index direction)
        right_idx = (index + 1) % num_players
        while not self.player_roles[right_idx].alive:
            right_idx = (right_idx + 1) % num_players
            if right_idx == index: break # Prevents infinite loop if everyone is dead
        right_neighbor = self.player_roles[right_idx]

        # Find Left Neighbor (-1 index direction)
        left_idx = (index - 1) % num_players
        while not self.player_roles[left_idx].alive:
            left_idx = (left_idx - 1) % num_players
            if left_idx == index: break
        left_neighbor = self.player_roles[left_idx]

        return left_neighbor, right_neighbor

    # --- GENERAL HELPERS ---
    def get_player_by_role(self, role_name: str) -> Optional[Role]:
        for p in self.player_roles:
            if p.name_role == role_name: return p
        return None

    def get_player_by_name(self, player_name: str) -> Optional[Role]:
         for p in self.player_roles:
             if p.name_player == player_name: return p
         return None
         
    def wake_role(self, role_name: str):
        for p in self.player_roles:
            if p.believed_role == role_name: 
                p.TakeAction(self)

    # --- NIGHT PHASES ---
    def NightOne(self):
        print("\n=== NIGHT 1 ===")
        print("Everyone close your eyes. Put everyone to sleep.")

        imp = self.get_player_by_role("Imp")
        minions = [p for p in self.player_roles if p.name_role in [m["role"] for m in self.ROLES_MINIONS]]
        
        if imp and minions:
            print(f"\nWake Minions ({', '.join([m.name_player for m in minions])}). Show them Imp is {imp.name_player}. Sleep.")
            print(f"Wake Imp ({imp.name_player}). Show them Minions are {', '.join([m.name_player for m in minions])}.")
            
            in_play_bluffs = [p.believed_role for p in self.player_roles] + [p.registered_role for p in self.player_roles if p.name_role == "Spy"]
            all_good = [r["role"] for r in self.ROLES_TOWNSFOLK + self.ROLES_OUTSIDERS]
            bluffs = random.sample([r for r in all_good if r not in in_play_bluffs], 3)
            print(f"-> Show Imp these 3 bluffs: {', '.join(bluffs)}. Put to sleep.")

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
        self.killed_tonight = None
        for p in self.player_roles:
            p.poisoned = False
            p.protected = False

        self.wake_role("Poisoner")
        self.wake_role("Monk")
        self.wake_role("Spy")
        self.wake_role("Scarlet Woman")
        self.wake_role("Imp")           
        
        wake_order = ["Ravenkeeper", "Undertaker", "Empath", "Fortune Teller", "Butler"]
        for role in wake_order:
            self.wake_role(role)

        print("\n=== DAWN ===")
        self.turn_counter += 1

    def print_board(self):
        """Prints the current state of the board (The Grimoire) for the Storyteller."""
        print("\n" + "="*55)
        print(f"=== GRIMOIRE (STORYTELLER VIEW) - Turn {self.turn_counter} ===")
        print("="*55)
        
        for i, player in enumerate(self.player_roles):
            # 1. Check Alive/Dead
            status = "Alive" if player.alive else "DEAD"
            
            # 2. Check temporary statuses
            poison_str = " [POISONED]" if player.poisoned else ""
            protect_str = " [PROTECTED]" if player.protected else ""
            
            # 3. Format the role string to reveal Drunk/Spy mechanics
            if player.name_role == "Drunk":
                role_info = f"Drunk (Thinks: {player.believed_role})"
            elif player.name_role == "Spy":
                role_info = f"Spy (Registers: {player.registered_role}/{player.registered_alignment})"
            else:
                role_info = f"{player.name_role} ({player.registered_alignment})"

            # Print out the formatted row
            print(f"Seat {i+1:02d} | {player.name_player:<8} | {status:<5} | {role_info}{poison_str}{protect_str}")
        print("="*55 + "\n")


def main():
    example = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]
    game = GameMgr(example)
    
    print("--- SEATING & ROLES (STORYTELLER VIEW) ---")
    for i, player in enumerate(game.player_roles):
        prefix = f"Seat {i+1} - {player.name_player}"
        if player.name_role == "Drunk":
            print(f"{prefix}: {player.name_role} (Thinks they are {player.believed_role})")
        elif player.name_role == "Spy":
            print(f"{prefix}: {player.name_role} (Registers as {player.registered_alignment})")
        else:
            print(f"{prefix}: {player.name_role} (Alignment: {player.registered_alignment})")

    # Run a test loop
    game.NightOne()
    game.print_board()
    game.NightNext()
    game.print_board()

if __name__ == "__main__":
    main()
