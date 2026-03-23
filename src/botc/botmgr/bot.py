from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from botc.player import Player
    from botc.game import GameManager

import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
import random
import datetime
from dotenv import load_dotenv
import os 

class JoinLobbyView(discord.ui.View):
    def __init__(self, game: GameManager) -> None:
        super().__init__(timeout=None) # The button won't expire on its own
        self.game: GameManager = game

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green, custom_id="join_game_btn", emoji="✋")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        user_name: str = str(interaction.user.name)
        
        # Check if they are already in the list
        if user_name not in self.game.player_names:
            print(f"Adding {user_name}")
            self.game.player_names.append(user_name)
            await interaction.response.send_message(
                f"✅ You've joined the game! We now have {len(self.game.player_names)} players.", 
                ephemeral=True # Only the user sees this confirmation
            )
        else:
            await interaction.response.send_message("⚠️ You are already in the game!", ephemeral=True)

# --- 1. The Cog (Where your commands live) ---
class TeamManagement(commands.Cog):
    def __init__(self, bot: BotMgr, game: GameManager) -> None:
        self.bot: BotMgr = bot
        self.game: GameManager = game

    async def send_message(self, user_name: str, message: str) -> bool:
        """
        Searches for a user by their username and sends them a Direct Message.
        Returns True if successful, False if it failed.
        """
        # 1. Clean up the input just in case someone typed "@username"
        clean_name: str = user_name.lstrip('@').lower()
        
        # 2. Search the bot's cache for a user with that exact name
        # Note: We use .lower() to make the search case-insensitive!
        user: discord.User | None = discord.utils.find(
            lambda u: u.name.lower() == clean_name or u.global_name and u.global_name.lower() == clean_name, 
            self.bot.users
        )
        
        # 3. Handle the case where the user isn't found
        if user is None:
            print(f"❌ Could not find anyone named '{user_name}' in the bot's cache.")
            return False
            
        # 4. Attempt to send the message
        try:
            await user.send(message)
            print(f"✅ Successfully sent DM to {user.name}")
            return True
            
        except discord.Forbidden:
            print(f"❌ Failed to DM {user.name}: They have DMs disabled for this server.")
            return False
        except discord.HTTPException as e:
            print(f"❌ Failed to DM {user.name} due to an API error: {e}")
            return False


    @commands.command(name="print_usrs")
    @commands.has_permissions(manage_roles=True)
    async def print_usrs(self, ctx: commands.Context) -> None:
        if ctx.guild == None:
            raise ValueError("Guild can not be None")
        print(f"--- Member IDs for {ctx.guild.name} ---")
        for member in ctx.guild.members:
            print(member.id, member.name, member.global_name, member.guild, member.nick, member.display_name, member.roles)
        await ctx.send(f"Printed {len(ctx.guild.members)} member IDs to the terminal!", ephemeral=True)

    @app_commands.command(name="open_lobby", description="[Admin] Open a lobby for players to join the game.")
    @app_commands.default_permissions(manage_roles=True) # Restricts to admins/GMs
    async def open_lobby(self, interaction: discord.Interaction) -> None:
        # Reset the player list for a fresh game
        self.game.player_names = []
        
        # Attach the button view we created above
        view: JoinLobbyView = JoinLobbyView(self.game)
        
        embed: discord.Embed = discord.Embed(
            title="🩸 Blood on the Clocktower",
            description="A new game is forming! Click the button below to join the town.",
            color=discord.Color.dark_red()
        )
        
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="start_game", description="[Admin] Close the lobby and deal roles.")
    @app_commands.default_permissions(manage_roles=True) # Restricts to admins/GMs
    async def start_game(self, interaction: discord.Interaction) -> None:
        num_players: int = len(self.game.player_names)
        
        # BotC requires at least 5 players. 
        if num_players < 1:
            await interaction.response.send_message(f"❌ You only have {num_players} players. You need at least 5 to play!", ephemeral=True)
            return
            
        await interaction.response.send_message("🚀 **The lobby is closed!** Distributing roles and waking up the town...")
        poll: PollManager = PollManager(self.game)
        print("Starting Poll for Game Master")
        res: Optional[discord.Message] = await poll.poll_gamemaster(interaction, self.game.player_names)
        await self.game._start_game()
        
    @app_commands.command(name="display_players", description="Show the current players in the game!")
    async def display_players(self, interaction: discord.Interaction) -> None:
        if not self.game.player_names:
            await interaction.response.send_message("❌ No players have joined the game yet.", ephemeral=True)
            return
            
        # Compile a single string of all players to send in one response
        player_list: str = "\n".join([f"✅ <@{player_id}>" for player_id in self.game.player_names])
        await interaction.response.send_message(f"**Current Players:**\n{player_list}")

class PollManager:
    def __init__(self, game: GameManager) -> None:
        self.game: GameManager = game

    async def poll_gamemaster(self, interaction: discord.Interaction, allowed_player_ids: list[str]) -> Optional[discord.Message]:
        print("From within Poll GameMaster")
        
        # 1. GUARDFIELD: Ensure we are actually in a TextChannel
        if not isinstance(interaction.channel, discord.TextChannel):
            error_msg: str = "This action can only be used in a standard text channel."
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)
            return None

        # 2. Acknowledge the interaction
        if not interaction.response.is_done():
            await interaction.response.send_message("Creating the public GM poll...", ephemeral=True)
        else:
            await interaction.followup.send("Creating the public GM poll...", ephemeral=True)

        # 3. Initialize the Poll object
        poll_minutes: int = 4
        poll: discord.Poll = discord.Poll(
            question="Do you want to be a GM?",
            duration=datetime.timedelta(hours=1), # Bypassing Discord's 1-hour minimum
            multiple=False
        )

        poll.add_answer(text="Yes", emoji="🙋")
        poll.add_answer(text="No / Skip Vote", emoji="⏭️")

        # 4. Create a Public Thread
        thread: discord.Thread = await interaction.channel.create_thread(
            name="Town Square Voting",
            type=discord.ChannelType.public_thread
        )

        # 5. Send the poll inside the public thread
        poll_message: discord.Message = await thread.send(poll=poll)
        
        # 6. Wait for the poll to finish OR until everyone votes
        num_players: int = len(allowed_player_ids)
        max_wait_time: int = poll_minutes * 60
        elapsed_time: int = 0
        check_interval: int = 5 # Wake up and check every 5 seconds

        while elapsed_time < max_wait_time:
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval

            # Fetch the latest version of the poll message to get updated vote counts
            poll_message = await thread.fetch_message(poll_message.id)
            
            if poll_message.poll:
                # Tally up all the votes across all options
                total_votes: int = sum(answer.vote_count for answer in poll_message.poll.answers)
                
                # If the total votes equal (or exceed) our player count, break the wait!
                if total_votes >= num_players:
                    break

        # 7. Forcefully end the poll early
        try:
            poll_message = await poll_message.end_poll()
        except Exception as e:
            print(f"Failed to end poll early: {e}")
            poll_message = await thread.fetch_message(poll_message.id)

        # 8. Process the results
        if poll_message.poll is None:
            raise ValueError("Poll Message is None")
            
        yes_answer: Optional[discord.PollAnswer] = discord.utils.get(poll_message.poll.answers, text="Yes")
        
        candidates: list[discord.User | discord.Member] = []
        if yes_answer:
            # Loop through everyone who voted "Yes"
            async for user in yes_answer.voters():
                # Validate that the voter is actually in your allowed list
                if str(user.id) in allowed_player_ids:
                    candidates.append(user)

        # 9. Randomly select and announce
        if candidates:
            selected_gm: discord.User | discord.Member = random.choice(candidates)
            self.game.game_master = selected_gm.name
            await thread.send(f"🎲 The votes are in! The randomly selected GM is {selected_gm.mention}!")
        else:
            await thread.send("Nobody volunteered to be the GM (or no valid players voted yes).")

        return poll_message

# --- 2. The Bot Manager (Where your bot is configured) ---
class BotMgr(commands.Bot):
    def __init__(self, game: GameManager) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.game: GameManager = game
        
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        await self.add_cog(TeamManagement(self, self.game))
        # --- FAST SYNCING FOR TESTING ---
        # Replace the numbers below with your actual Server ID
        TEST_SERVER: discord.Object = discord.Object(id=1373836529390190602) 
        # Copy the global commands to your specific test server
        self.tree.copy_global_to(guild=TEST_SERVER)
        # Sync the commands immediately to that specific server
        await self.tree.sync(guild=TEST_SERVER)
        print("Hooking in custom commands and syncing instantly to the test server.")

    async def on_ready(self) -> None:
        if self.user == None:
            raise ValueError("Usr is None")
        print(f"We are ready to go in, {self.user.name}")
