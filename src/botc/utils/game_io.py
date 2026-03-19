from typing import List
from pathlib import Path
import json
from botc.player import Player
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
class GameIO:
    def get_user_choice(self, choices: List[str], prompt_pre: str="", prompt_post: str=""):
        display_prompt = prompt_pre
        valid_choices = []
        for index, option in enumerate(choices):
            selection = index+1
            display_prompt += str(selection) + option + "\n"
            valid_choices.append(selection)
        display_prompt = prompt_post
        while True:
            # 1. Display the menu
            print(display_prompt)
            # 2. Get input and strip any accidental extra spaces
            choice = input(f"Please select an option ({valid_choices[0]} - {valid_choices[-1]}): ").strip()
            # 3. Validate the input
            if choice in valid_choices:
                return choice  # Exit the loop and return the valid choice
            else:
                # Error message, and the loop repeats automatically
                print(f"\n❌'{choice}' is not valid. ({valid_choices[0]} - {valid_choices[-1]}): ")
    def write_to_file(self, filename: str, log_content: str):
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        # Create the full file path and write to it
        filepath = OUTPUTS_DIR / filename
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(log_content + '\n')

    def export_players_to_json(self, players: List[Player], filename: str):
        """Takes a list of Player objects and saves them to a structured JSON file."""
        
        # 1. Build the dictionary mapping player names to their data
        game_state = {}
        for player in players:
            game_state[player.player_name] = player._to_dict()
            
        filepath = OUTPUTS_DIR / filename
        # 2. Write the dictionary to a JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            # indent=4 makes the JSON easily readable for humans
            json.dump(game_state, f, indent=4)
