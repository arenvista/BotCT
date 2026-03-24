from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord import app_commands

if TYPE_CHECKING:
    from botc.core.game import GameManager
    from botc.discord_manager.bot import BotManager

from botc.discord_manager.views import JoinLobbyView
from botc.discord_manager.polling import PollManager

class GameCommands(commands.Cog):
    def __init__(self, bot: BotManager, game: GameManager) -> None:
        self.bot: BotManager = bot
        self.game: GameManager = game

    async def send_direct_message(self, user_name: str, message: str) -> bool:
        """Searches for a user by username and sends them a DM."""
        clean_name: str = user_name.lstrip('@').lower()
        
        user: discord.User | None = discord.utils.find(
            lambda u: u.name.lower() == clean_name or (u.global_name and u.global_name.lower() == clean_name), 
            self.bot.users
        )
        
        if user is None:
            print(f"❌ Could not find '{user_name}' in cache.")
            return False
            
        try:
            await user.send(message)
            print(f"✅ Successfully sent DM to {user.name}")
            return True
        except discord.Forbidden:
            print(f"❌ Failed to DM {user.name}: DMs disabled.")
            return False
        except discord.HTTPException as e:
            print(f"❌ Failed to DM {user.name}: {e}")
            return False

    @commands.command(name="print_users")
    @commands.has_permissions(manage_roles=True)
    async def print_users(self, ctx: commands.Context) -> None:
        if ctx.guild is None:
            raise ValueError("Guild cannot be None")
            
        print(f"--- Member IDs for {ctx.guild.name} ---")
        for member in ctx.guild.members:
            print(member.id, member.name, member.global_name, member.roles)
        await ctx.send(f"Printed {len(ctx.guild.members)} member IDs to terminal!", ephemeral=True)

    @app_commands.command(name="open_lobby", description="[Admin] Open a lobby for players.")
    @app_commands.default_permissions(manage_roles=True)
    async def open_lobby(self, interaction: discord.Interaction) -> None:
        self.game.player_names = []
        view: JoinLobbyView = JoinLobbyView(self.game)
        
        embed: discord.Embed = discord.Embed(
            title="🩸 Blood on the Clocktower",
            description="A new game is forming! Click the button below to join the town.",
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="start_game", description="[Admin] Close the lobby and deal roles.")
    @app_commands.default_permissions(manage_roles=True)
    async def start_game(self, interaction: discord.Interaction) -> None:
        num_players: int = len(self.game.player_names)
        
        if num_players < 1: 
            await interaction.response.send_message(f"❌ You need at least 5 to play!", ephemeral=True)
            return
            
        await interaction.response.send_message("🚀 **The lobby is closed!** Starting GM Poll...")
        
        poll: PollManager = PollManager(self.game)
        await poll.run_gamemaster_poll(interaction, self.game.player_names)
        
        await self.game.start_game(interaction)
        
    @app_commands.command(name="display_players", description="Show the current players in the game!")
    async def display_players(self, interaction: discord.Interaction) -> None:
        if not self.game.player_names:
            await interaction.response.send_message("❌ No players have joined.", ephemeral=True)
            return
            
        player_list: str = "\n".join([f"✅ <@{player_id}>" for player_id in self.game.player_names])
        await interaction.response.send_message(f"**Current Players:**\n{player_list}")
