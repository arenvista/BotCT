# main.py
import sys
from pathlib import Path

# Tell Python to look in the 'src' directory for modules
sys.path.append(str(Path(__file__).parent / "src"))

from botc import GameManager, RoleName
from botc.interface import Interface
from botc.botmgr import BotMgr

from time import sleep
import logging
from dotenv import load_dotenv
import os 

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
    # Instantiate and run the bot class
    load_dotenv()
    token = str(os.getenv("DISCORD_TOKEN"))
    # Setup logging
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    # Instantiate and run the bot class
    bot = BotMgr(game)
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
    game.night_one()
    while input != "z":
        sleep(10)
    # game.print_board()
    # game.night_next()
    # game.print_board()

if __name__ == "__main__":
    main()
