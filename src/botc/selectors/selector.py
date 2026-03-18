from typing import List


class Selector:
    def __init__(self):
        return

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
