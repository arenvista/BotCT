from __future__ import annotations
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
                label=player.player_name, 
                description="Vote to execute this player", 
                emoji="💀"
            ))
        # Add the skip option
        options.append(discord.SelectOption(
            label="Skip Vote", 
            description="Abstain from voting today", 
            emoji="⏭️"
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
            f"✅ Your vote for **{chosen_target}** has been recorded. You can change your selection until the poll closes.", 
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
        
        if user_name not in self.game.player_names:
            self.game.player_names.append(user_name)
            await interaction.response.send_message(
                f"✅ You've joined the game! We now have {len(self.game.player_names)} players.", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(f"Players: " + ",".join(self.game.player_names), ephemeral=True)
            await interaction.response.send_message("⚠️ You are already in the game!", ephemeral=True)
