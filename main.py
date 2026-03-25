# main.py
import sys
from pathlib import Path

# Tell Python to look in the 'src' directory for modules
sys.path.append(str(Path(__file__).parent / "src"))

from botc.core import GameManager
from time import sleep

def main():
    example = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry"]
    game = GameManager(example)
    game.bot.run(game.token)
    print("done")
    while input() != "z":
        sleep(10)


if __name__ == "__main__":
    main()
