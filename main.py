# main.py
import sys
from pathlib import Path
import argparse
import os

sys.path.append(str(Path(__file__).parent / "src"))

from botc.core import GameManager
from time import sleep

def main():
    game = GameManager()
    game.mgr_discord.run_bot()
    while input() != "z":
        sleep(10)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--testing",action="store_true")
    parser.add_argument("--disable_voting",action="store_true")
    parser.add_argument("--immortal",action="store_true",help="no players can die")
    parser.add_argument("--assignment_map",type=str,default="")
    
    args=parser.parse_args()
    if args.testing:
        os.environ["TESTING"] = "1"
    else:
        os.environ["TESTING"]="0"
    
    if args.disable_voting:
        os.environ["VOTING"]="0"
    else:
        os.environ["VOTING"]="1"
    
    if args.immortal:
        os.environ["IMMORTAL"]="1"
    else:
        os.environ["IMMORTAL"]="0"
        
    if len(args.assignment_map)>0:
        os.environ["ASSIGN"]=args.assignment_map
    main()
