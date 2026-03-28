from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
import datetime
import asyncio
import re

import discord
from discord.ext import commands
from discord import app_commands

if TYPE_CHECKING:
    from botc.core.game import GameManager
    from botc.discord_manager.bot import BotManager

from botc import Player, Alignment
from botc.enums import RoleName, RoleClass
from botc.discord_manager.views import JoinLobbyView, DropdownView
from botc.discord_manager.polling import PollManager


class GameCommands(commands.Cog):
    def __init__(self, bot: BotManager, game: GameManager) -> None:
        self.bot: BotManager = bot
        self.game: GameManager = game

    @app_commands.command(name="set_seats", description="[Admin] Set seating order by pinging all players in clockwise order.")
    @app_commands.describe(mentions="Tag all players in order: @player1 @player2 @player3...")
    @app_commands.default_permissions(manage_roles=True)
    async def set_seats(self, interaction: discord.Interaction, mentions: str) -> None:
        if not self.game.get_players():
            await interaction.response.send_message("❌ The game hasn't started yet!", ephemeral=True)
            return

        user_ids = re.findall(r'<@!?(\d+)>', mentions)

        if len(user_ids) != len(self.game.get_players()):
            await interaction.response.send_message(
                f"❌ You mentioned {len(user_ids)} players, but there are {len(self.game.get_players())} players in the game. Please mention everyone.",
                ephemeral=True
            )
            return

        new_order_names = []
        for uid in user_ids:
            user = self.bot.get_user(int(uid))
            if not user:
                try:
                    user = await self.bot.fetch_user(int(uid))
                except discord.NotFound:
                    await interaction.response.send_message(f"❌ Could not resolve user with ID {uid}.", ephemeral=True)
                    return
            new_order_names.append(user.name)

        current_names = [p.username for p in self.game.get_players()]
        missing_players = [name for name in current_names if name.lstrip('@').lower() not in new_order_names]
        extra_players = [name for name in new_order_names if name.lstrip('@').lower() not in current_names]

        if missing_players or extra_players:
            err_msg = "❌ The players mentioned don't match the active game roster.\n"
            if missing_players: 
                err_msg += f"**Missing from your list:** {', '.join(missing_players)}\n"
            if extra_players: 
                err_msg += f"**Not in the game:** {', '.join(extra_players)}"
            
            await interaction.response.send_message(err_msg, ephemeral=True)
            return

        new_players_list = []
        for name in new_order_names:
            player_obj = next(p for p in self.game.get_players() if p.username == name)
            new_players_list.append(player_obj)

        self.game.mgr_player.player_list = new_players_list
        self.game.mgr_player.player_names = new_order_names

        await interaction.response.send_message(
            f"✅ **Seating order locked in!**\n\n**New Grimoire Order:**\n{self.game.get_board_str()}", 
            ephemeral=True
        )

    async def query_user_dropdown(self, user_name: str, message_text: str, options: List[str], max_selection: int) -> Optional[List[str]]:
        options = list(set(options))
        if len(options) > 25:
            print("Too Many Options!")
            raise ValueError("Dropdowns must have <= 25 options")
            
        clean_name: str = user_name.lstrip('@').lower()
        
        user: discord.User | None = discord.utils.find(
            lambda u: u.name.lower() == clean_name or (u.global_name and u.global_name.lower() == clean_name), 
            self.bot.users
        )
        
        if user is None:
            print(f"❌ Could not find user with name '{user_name}' in cache.")
            return None
            
        view = DropdownView(options=options, max_selection=max_selection)
        
        try:
            message: discord.Message = await user.send(content=message_text, view=view)
        except (discord.Forbidden, discord.HTTPException):
            return None
            
        is_timeout = await view.wait()
        
        if is_timeout:
            try:
                view.select.disabled = True
                await message.edit(content="**Time expired.**", view=view)
            except discord.HTTPException:
                pass
            return None
            
        return view.selected_values

    async def query_user(self, user_name: str, poll_message: str, poll_options: List[str], max_selection: int) -> Optional[List[str]]:
        poll_options = list(set(poll_options))
        if len(poll_options) > 10 or max_selection == 1:
            return await self.query_user_dropdown(user_name, poll_message, poll_options, max_selection)
        
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

        timeout = 3600
        poll_interval = 2.0
        elapsed = 0.0
        live_message = message

        while elapsed < timeout:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            try:
                live_message = await message.channel.fetch_message(message.id)
            except discord.HTTPException:
                continue
                
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

        if selected_count > max_selection:
            await live_message.end_poll() 
            await user.send(f"⚠️ **Oops!** You selected {selected_count} options, but the limit is {max_selection}. Let's try again.")
            return await self.query_user_dropdown(user_name, poll_message, poll_options, max_selection)
            
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
        self.game.mgr_player.player_names = []
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
        num_players: int = len(self.game.mgr_player.player_names)
        # if num_players < 5:  # Fixed from < 0
        #     await interaction.response.send_message(f"❌ You need at least 5 to play!", ephemeral=True)
        #     return
            
        await interaction.response.send_message("🔒 **The lobby is closed!** Starting GM Poll...")
        poll: PollManager = PollManager(self.game)
        self.game.game_master = await poll.run_gamemaster_poll(interaction)

        # # Testing End Start
        # ROLES_DEMONS = RoleName.get_by_class(RoleClass.DEMONS)
        # ROLES_MINIONS = RoleName.get_by_class(RoleClass.MINIONS)
        # ROLES_OUTSIDERS = RoleName.get_by_class(RoleClass.OUTSIDERS)
        # ROLES_TOWNSFOLK = RoleName.get_by_class(RoleClass.TOWNSFOLK)
        # targets = ROLES_DEMONS + ROLES_MINIONS + ROLES_OUTSIDERS + ROLES_TOWNSFOLK[:-10]
        
        # Fixed: Append directly to the actual state, not a filtered copy
        # for r in targets: 
        # r = RoleName.IMP
        # self.game.mgr_player.player_list.append(Player("iiiii5184", r, r, Alignment.GOOD))
        # r = RoleName.SLAYER
        # self.game.mgr_player.player_list.append(Player("microsina", r, r, Alignment.GOOD))
        r = RoleName.SOLDIER
        # self.game.mgr_player.player_list.append(Player("bakerthebread", r, r, Alignment.GOOD))
        # targets = ROLES_MINIONS + ROLES_OUTSIDERS + ROLES_TOWNSFOLK
        # counter = 0
        # for r in targets[0:3]:
        #     counter += 1
        #     self.game.mgr_player.player_list.append(Player(f"Test{counter}", r, r, Alignment.GOOD))
        # Testing End Start
        ROLES_DEMONS = RoleName.get_by_class(RoleClass.DEMONS)
        ROLES_MINIONS = RoleName.get_by_class(RoleClass.MINIONS)
        ROLES_OUTSIDERS = RoleName.get_by_class(RoleClass.OUTSIDERS)
        ROLES_TOWNSFOLK = RoleName.get_by_class(RoleClass.TOWNSFOLK)
        targets = ROLES_DEMONS + ROLES_MINIONS + ROLES_OUTSIDERS + ROLES_TOWNSFOLK[:-10]

        # for i, r in enumerate(targets):        
        # self.game.mgr_player.player_list.append(Player(f"temp1", RoleName.EMPATH, RoleName.EMPATH, Alignment.GOOD))
        self.game.mgr_player.player_list.append(Player(f"bakerthebread", RoleName.UNDERTAKER, RoleName.UNDERTAKER, Alignment.GOOD))
        self.game.mgr_player.player_list.append(Player("chudbotc1",RoleName.IMP, RoleName.IMP, Alignment.EVIL))
        self.game.mgr_player.player_list.append(Player(f"temp2", RoleName.IMP, RoleName.IMP, Alignment.EVIL))
        # self.game.mgr_player.player_list.append(Player(f"temp1", RoleName.IMP, RoleName.IMP, Alignment.EVIL))
        self.game.mgr_player.player_list.append(Player(f"temp3", RoleName.SCARLET_WOMAN, RoleName.SCARLET_WOMAN, Alignment.EVIL))
        self.game.mgr_player.player_list.append(Player(f"temp5", RoleName.VIRGIN, RoleName.VIRGIN, Alignment.GOOD))
        self.game.mgr_player.player_list.append(Player(f"temp6", RoleName.DRUNK, RoleName.DRUNK, Alignment.GOOD))
        self.game.mgr_player.player_list.append(Player(f"temp7", RoleName.SOLDIER, RoleName.SOLDIER, Alignment.GOOD))
        self.game.mgr_player.player_list.append(Player(f"temp8", RoleName.MAYOR, RoleName.MAYOR, Alignment.GOOD))
        




        # Fixed: Append directly to the actual state, not a filtered copy
        # for i, r in enumerate(targets): 
        #     self.game.mgr_player.player_list.append(Player(f"pain{i}", r, r, Alignment.GOOD))

        # targets = ROLES_MINIONS + ROLES_OUTSIDERS + ROLES_TOWNSFOLK
        
        # for i, r in enumerate(targets[0:3]):
        #     self.game.mgr_player.player_list.append(Player(f"suffering{i}", r, r, Alignment.GOOD))
        # Testing End

        await self.game.start_game(interaction)

    @app_commands.command(name="slay", description="Slay dem demons")
    @app_commands.describe(target="Slay dem demons")
    async def slay(self, interaction: discord.Interaction, target: discord.Member) -> None:
        await interaction.response.send_message(f"{interaction.user.name} draws his big, fat sword and attempts to slay {target.name}! ⚔️")
        
        target_player = self.game.get_player(target.name)
        myself = self.game.get_player(interaction.user.name)
        
        if target_player and target_player.registered_role == RoleName.IMP:
            if myself and myself.registered_role == RoleName.SLAYER:
                await interaction.followup.send(f"The Imp {target.name} has been slain!")
                return 
                
        await interaction.followup.send("This is a little awkward. Ineffective.")

    @app_commands.command(name="display_grimoire", description="Displays Game State")
    async def display_grimoire(self, interaction: discord.Interaction) -> None:
        # if interaction.user.name == self.game.game_master:
        await interaction.response.send_message(self.game.get_board_str(), ephemeral=True)

    @app_commands.command(name="display_players", description="Show the current players in the game!")
    async def display_players(self, interaction: discord.Interaction) -> None:
        print("Hiiiiiii")
        if len(self.game.mgr_player.player_names) == 0: # Fixed inverted logic
            await interaction.response.send_message("❌ No players have joined.", ephemeral=True)
            return
            
        player_list: str = "\n".join([f"🪪 {username}" for username in self.game.mgr_player.player_names])
        await interaction.response.send_message(f"**Current Players:**\n{player_list}")
