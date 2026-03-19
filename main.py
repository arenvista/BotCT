# main.py
import sys
from pathlib import Path

# Tell Python to look in the 'src' directory for modules
sys.path.append(str(Path(__file__).parent / "src"))

from botc import GameManager, RoleName

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
    game.export_players_to_json()

if __name__ == "__main__":
    main()
