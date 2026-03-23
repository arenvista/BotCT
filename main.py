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
    game.bot.run(game.token)
    while input() != "z":
        sleep(10)


if __name__ == "__main__":
    main()
