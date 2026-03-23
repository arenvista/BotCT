from __future__ import annotations      
from typing import TYPE_CHECKING         

if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.game import GameManager

import discord
from discord.ext import commands
from discord import app_commands
import logging
import datetime
from dotenv import load_dotenv
import os 

class JoinLobbyView(discord.ui.View):
    def __init__(self, game: 'GameManager'):
        super().__init__(timeout=None) # The button won't expire on its own
        self.game = game

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green, custom_id="join_game_btn", emoji="✋")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id_str = str(interaction.user.id)
        
        # Check if they are already in the list
        if user_id_str not in self.game.current_players:
            self.game.current_players.append(user_id_str)
            await interaction.response.send_message(
                f"✅ You've joined the game! We now have {len(self.game.current_players)} players.", 
                ephemeral=True # Only the user sees this confirmation
            )
        else:
            await interaction.response.send_message("⚠️ You are already in the game!", ephemeral=True)

# --- 1. The Cog (Where your commands live) ---
class TeamManagement(commands.Cog):
    def __init__(self, bot, game: 'GameManager'):
        self.bot = bot
        self.game = game

    @commands.command(name="print_usrs")
    @commands.has_permissions(manage_roles=True)
    async def print_usrs(self, ctx):
        print(f"--- Member IDs for {ctx.guild.name} ---")
        for member in ctx.guild.members:
            print(member.id, member.name, member.global_name, member.guild, member.nick, member.display_name, member.roles)
        await ctx.send(f"Printed {len(ctx.guild.members)} member IDs to the terminal!", ephemeral=True)

    @app_commands.command(name="open_lobby", description="[Admin] Open a lobby for players to join the game.")
    @app_commands.default_permissions(manage_roles=True) # Restricts to admins/GMs
    async def open_lobby(self, interaction: discord.Interaction):
        # Reset the player list for a fresh game
        self.game.current_players = []
        
        # Attach the button view we created above
        view = JoinLobbyView(self.game)
        
        embed = discord.Embed(
            title="🩸 Blood on the Clocktower",
            description="A new game is forming! Click the button below to join the town.",
            color=discord.Color.dark_red()
        )
        
        await interaction.response.send_message(embed=embed, view=view)


    @app_commands.command(name="start_game", description="[Admin] Close the lobby and deal roles.")
    @app_commands.default_permissions(manage_roles=True) # Restricts to admins/GMs
    async def start_game(self, interaction: discord.Interaction):
        num_players = len(self.game.current_players)
        
        # BotC requires at least 5 players. 
        if num_players < 5:
            await interaction.response.send_message(f"❌ You only have {num_players} players. You need at least 5 to play!", ephemeral=True)
            return
            
        await interaction.response.send_message("🚀 **The lobby is closed!** Distributing roles and waking up the town...")
        
        # Here is where you trigger the GameManager to actually start the game!
        self.game.start_new_game()

    @app_commands.command(name="display_players", description="Show the current players in the game!")
    async def display_players(self, interaction: discord.Interaction):
        if not self.game.current_players:
            await interaction.response.send_message("❌ No players have joined the game yet.", ephemeral=True)
            return
            
        # Compile a single string of all players to send in one response
        player_list = "\n".join([f"✅ <@{player_id}>" for player_id in self.game.current_players])
        await interaction.response.send_message(f"**Current Players:**\n{player_list}")

class PollManager:
    def __init__(self, bot):
        self.bot = bot

    async def create_restricted_poll(self, interaction: discord.Interaction, allowed_player_ids: list[str]):
        # 1. GUARDFIELD: Ensure we are actually in a TextChannel
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("This action can only be used in a standard text channel.", ephemeral=True)
            return

        # 2. Acknowledge the interaction so it doesn't timeout
        await interaction.response.send_message("Creating your restricted poll...", ephemeral=True)

        # 3. Initialize the Poll object
        poll = discord.Poll(
            question="Who do you vote to execute?",
            duration=datetime.timedelta(hours=24),
            multiple=False
        )

        poll.add_answer(text="Skip Vote", emoji="⏭️")
        # In the future, you can dynamically add players as answers here!

        # 4. Create a Private Thread to restrict who can see/vote
        thread = await interaction.channel.create_thread(
            name="Town Square Voting",
            type=discord.ChannelType.private_thread,
            invitable=False # Prevents users from inviting others
        )

        # 5. Add only the allowed players to the thread
        for player_id_str in allowed_player_ids:
            member = interaction.guild.get_member(int(player_id_str))
            if member:
                await thread.add_user(member)

        # 6. Send the poll inside the restricted thread
        poll_message = await thread.send(poll=poll)
        
        return poll_message

# --- 2. The Bot Manager (Where your bot is configured) ---
class BotMgr(commands.Bot):
    def __init__(self, game: 'GameManager'):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.game = game
        
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.add_cog(TeamManagement(self, self.game))
        # --- FAST SYNCING FOR TESTING ---
        # Replace the numbers below with your actual Server ID
        TEST_SERVER = discord.Object(id=1373836529390190602) 
        # Copy the global commands to your specific test server
        self.tree.copy_global_to(guild=TEST_SERVER)
        # Sync the commands immediately to that specific server
        await self.tree.sync(guild=TEST_SERVER)
        print("Hooking in custom commands and syncing instantly to the test server.")

    async def on_ready(self):
        print(f"We are ready to go in, {self.user.name}")
