# main.py
import sys
from pathlib import Path
import argparse
import os

# Tell Python to look in the 'src' directory for modules
sys.path.append(str(Path(__file__).parent / "src"))

from botc.core import GameManager
from time import sleep

def main():
    example = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry"]
    game = GameManager(example)
    game.bot.run(game.token)
    while input() != "z":
        sleep(10)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--testing",action="store_true")
    args=parser.parse_args()
    if args.testing:
        os.environ["TESTING"] = "1"
    else:
        os.environ["TESTING"]="0"
    main()
