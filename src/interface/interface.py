from botc import *
from botmgr import * 


class Interface:
    def __init__(self):
        return
    def test(self):
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
        # game.print_board()
        # game.night_next()
        # game.print_board()

if __name__ == "__main__":
    interface = Interface()
    interface.test()
