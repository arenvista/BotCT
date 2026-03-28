from __future__ import annotations
from typing import List, Optional
from typing import TYPE_CHECKING
import discord

if TYPE_CHECKING:
    from botc.core.game import GameManager

class ExecutionDropdown(discord.ui.Select):
    def __init__(self, alive_players):
        options = []
        # Add all alive players as options
        for player in alive_players:
            options.append(discord.SelectOption(
                label=player.username, 
                description="Vote to execute this player", 
                emoji="🖊️"
            ))
        # Add the skip option
        options.append(discord.SelectOption(
            label="Skip Vote", 
            description="Abstain from voting today", 
            emoji="🕊️"
        ))
        
        super().__init__(placeholder="Select a player to execute...", min_values=1, max_values=1, options=options)
        
        # This dictionary will store {username: chosen_option}
        self.votes = {} 

    async def callback(self, interaction: discord.Interaction):
        # When a user selects an option, record it
        user_name = interaction.user.name
        chosen_target = self.values[0]
        
        self.votes[user_name] = chosen_target
        
        # Send an ephemeral confirmation that only they can see
        await interaction.response.send_message(
            f"🖊️ Your vote for **{chosen_target}** has been recorded. You can change your selection until the poll closes.", 
            ephemeral=True
        )

class ExecutionView(discord.ui.View):
    def __init__(self, alive_players):
        super().__init__(timeout=None)
        self.dropdown = ExecutionDropdown(alive_players)
        self.add_item(self.dropdown)

class JoinLobbyView(discord.ui.View):
    def __init__(self, game: GameManager) -> None:
        super().__init__(timeout=None)
        self.game: GameManager = game

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green, custom_id="join_game_btn", emoji="✋")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        user_name: str = str(interaction.user.name)
        
        if user_name not in self.game.mgr_player.player_names:
            self.game.mgr_player.player_names.append(user_name)
            await interaction.response.send_message(
                f"✅ You've joined the game! We now have {len(self.game.mgr_player.player_names)} players.", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(f"Players: " + ",".join(self.game.mgr_player.player_names), ephemeral=True)
            await interaction.response.send_message("⚠️ You are already in the game!", ephemeral=True)

class DropdownView(discord.ui.View):
    def __init__(self, options: List[str], max_selection: int, timeout: float = 3600.0):
        # Set the timeout (default 1 hour)
        super().__init__(timeout=timeout)
        self.selected_values: Optional[List[str]] = None

        # Discord Dropdowns support up to 25 options (better than Polls' 10!)
        select_options = [discord.SelectOption(label=opt) for opt in options[:25]]
        
        # Create the Select menu component
        self.select = discord.ui.Select(
            placeholder=f"Select up to {max_selection}...",
            min_values=1,
            max_values=max_selection,
            options=select_options
        )
        
        # Bind the callback function
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        # 1. Grab the values the user clicked
        self.selected_values = self.select.values
        
        # 2. Disable the menu so they can't change their mind later
        self.select.disabled = True
        
        # 3. Acknowledge the interaction and update the message visually
        await interaction.response.edit_message(content="✅ **Selection locked in!**", view=self)
        
        # 4. Stop the view, which tells the `await view.wait()` in your cog to continue
        self.stop()
