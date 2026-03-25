from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

import discord
from discord.ext import commands
from discord import app_commands
import datetime
import asyncio

if TYPE_CHECKING:
    from botc.core.game import GameManager
    from botc.discord_manager.bot import BotManager

from botc.discord_manager.views import JoinLobbyView, DropdownView
from botc.discord_manager.polling import PollManager

class GameCommands(commands.Cog):
    def __init__(self, bot: BotManager, game: GameManager) -> None:
        self.bot: BotManager = bot
        self.game: GameManager = game

    async def dmdropdown(self, user_name: str, message_text: str, dropdown_options: List[str], max_selection: int) -> Optional[List[str]]:
        if len(dropdown_options) > 25:
            raise ValueError("Dropdowns must have <= 25 options")
            
        clean_name: str = user_name.lstrip('@').lower()
        
        # 1. Fetch user safely using their string username
        user: discord.User | None = discord.utils.find(
            lambda u: u.name.lower() == clean_name or (u.global_name and u.global_name.lower() == clean_name), 
            self.bot.users
        )
        
        if user is None:
            print(f"❌ Could not find user with name '{user_name}' in cache.")
            return None
            
        # 2. Instantiate the View we created above
        view = DropdownView(options=dropdown_options, max_selection=max_selection)
        
        # 3. Send the DM
        try:
            message: discord.Message = await user.send(content=message_text, view=view)
        except (discord.Forbidden, discord.HTTPException):
            return None
            
        # 4. Wait politely until the user clicks something or the 1-hour timeout hits.
        # This replaces your while-loop entirely!
        is_timeout = await view.wait()
        
        # 5. Handle the results
        if is_timeout:
            # User ignored the DM for an hour. Disable the menu so it locks.
            try:
                view.select.disabled = True
                await message.edit(content="⏳ **Time expired.**", view=view)
            except discord.HTTPException:
                pass
            return None
            
        return view.selected_values

    async def dmpoll(self, user_name: str, poll_message: str, poll_options: List[str], max_selection: int) -> Optional[List[str]]:
        if len(poll_options) > 10 or max_selection == 1:
            return await self.dmdropdown(user_name, poll_message, poll_options, max_selection)
        
        # 1. Fetch user safely using their string username
        clean_name: str = user_name.lstrip('@').lower()
        
        user: discord.User | None = discord.utils.find(
            lambda u: u.name.lower() == clean_name or (u.global_name and u.global_name.lower() == clean_name), 
            self.bot.users
        )
        
        if user is None:
            print(f"❌ Could not find user with name '{user_name}' in cache.")
            return None

        allow_multiple = max_selection > 1

        poll = discord.Poll(
            question=f"{poll_message} (Select up to {max_selection})",
            duration=datetime.timedelta(hours=1),
            multiple=allow_multiple 
        )

        for option in poll_options[:10]:
            poll.add_answer(text=option)

        try:
            message: discord.Message = await user.send(poll=poll)
        except (discord.Forbidden, discord.HTTPException):
            return None

        # --- Safe Polling Loop ---
        timeout = 3600  # Give up after 1 hour if they never vote
        poll_interval = 2.0  # Check for votes every 2 seconds
        elapsed = 0.0
        live_message = message

        while elapsed < timeout:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            try:
                live_message = await message.channel.fetch_message(message.id)
            except discord.HTTPException:
                continue # If Discord hiccups, try again next loop
                
            if live_message.poll is None:
                raise ValueError("Poll Returned Message.Poll == None")
                
            selected_count = sum(1 for answer in live_message.poll.answers if answer.vote_count > 0)
            
            if selected_count > 0:
                if allow_multiple:
                    await asyncio.sleep(3) 
                    live_message = await message.channel.fetch_message(message.id)
                    if live_message.poll is None: continue
                    selected_count = sum(1 for answer in live_message.poll.answers if answer.vote_count > 0)
                break 
        else:
            return None

        # --- Validation & Recursion ---
        if selected_count > max_selection:
            await live_message.end_poll() 
            await user.send(f"⚠️ **Oops!** You selected {selected_count} options, but the limit is {max_selection}. Let's try again.")
            # Note: Updated recursion call to use user_name
            return await self.dmpoll(user_name, poll_message, poll_options, max_selection)
            
        # --- Close the poll upon valid selection ---
        try:
            await live_message.end_poll()
        except discord.HTTPException:
            pass 
            
        selected_choices: List[str] = []
        
        if live_message.poll: 
            for answer in live_message.poll.answers:
                if answer.vote_count > 0:
                    selected_choices.append(answer.text)
                
        return selected_choices

    async def send_direct_message(self, user_name: str, message: str) -> bool:
        """Finds a user by username and sends them a DM."""
        clean_name: str = user_name.lstrip('@').lower()
        
        user: discord.User | None = discord.utils.find(
            lambda u: u.name.lower() == clean_name or (u.global_name and u.global_name.lower() == clean_name), 
            self.bot.users
        )
        
        if user is None:
            print(f"❌ Could not find user with name '{user_name}' in cache.")
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
        
        # CHANGED: Fixed the typo from < -1 to < 5
        if num_players < 0: 
            await interaction.response.send_message(f"❌ You need at least 5 to play!", ephemeral=True)
            return
            
        await interaction.response.send_message("🚀 **The lobby is closed!** Starting GM Poll...")
        
        # CAUTION: Ensure the functions below use `interaction.followup.send()` if they send messages!
        poll: PollManager = PollManager(self.game)
        await poll.run_gamemaster_poll(interaction, self.game.player_names)
        
        await self.game.start_game(interaction)
        
    @app_commands.command(name="display_players", description="Show the current players in the game!")
    async def display_players(self, interaction: discord.Interaction) -> None:
        if not self.game.player_names:
            await interaction.response.send_message("❌ No players have joined.", ephemeral=True)
            return
            
        # CHANGED: Removed the Discord ID ping format (<@id>) since we are using string usernames.
        player_list: str = "\n".join([f"✅ {player_name}" for player_name in self.game.player_names])
        await interaction.response.send_message(f"**Current Players:**\n{player_list}")
