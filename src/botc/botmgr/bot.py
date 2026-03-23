from __future__ import annotations      
from typing import TYPE_CHECKING         
if TYPE_CHECKING:                        
    from botc.player import Player
    from botc.game import GameManager
import discord
from discord.ext import commands
from discord import app_commands  # Added to support slash commands in Cogs
import logging
import datetime  # Added for poll duration
from dotenv import load_dotenv
import os 

# --- 1. The Cog (Where your commands live) ---
class TeamManagement(commands.Cog):
    def __init__(self, bot, game: GameManager):
        self.bot = bot
        self.game = game

    @commands.command(name="create_private")
    @commands.has_permissions(manage_roles=True)
    async def create_private_channel(self, ctx, category: discord.CategoryChannel, channel_name: str, members: commands.Greedy[discord.Member]):
        """
        Creates a private text channel under a specific category.
        Usage: !create_private "Category Name" "channel-name" @user1 @user2
        """
        # Base Permissions
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.guild.me: discord.PermissionOverwrite(view_channel=True)
        }
        if not members:
            await ctx.send("⚠️ You need to mention at least one member!")
            return
        
        for member in members:
            overwrites[member] = discord.PermissionOverwrite(view_channel=True)
            
        try:
            new_channel = await ctx.guild.create_text_channel(
                name=channel_name,
                category=category,  
                overwrites=overwrites,
                reason=f"Private channel created by {ctx.author}"
            )
            member_names = ", ".join([m.display_name for m in members])
            await ctx.send(f"✅ Created {new_channel.mention} under the **{category.name}** category for: **{member_names}**")
        except discord.Forbidden:
            await ctx.send("❌ I don't have the required permissions to do this.")
        except discord.HTTPException:
            await ctx.send("❌ Something went wrong communicating with Discord.")

    @create_private_channel.error
    async def create_private_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ You need the `Manage Roles` permission to use this command.")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("❌ I couldn't find a category with that name. Check your spelling and try again!")

    @commands.command(name="assign")
    @commands.has_permissions(manage_roles=True)
    async def assign(self, ctx, team_number: int, members: commands.Greedy[discord.Member]):
        """
        Assigns members to a team. Creates the role if it doesn't exist.
        Usage: !assign 1 @user1 @user2
        """
        if team_number not in [1, 2]:
            return await ctx.send("❌ Please choose team **1** or **2**.")

        if not members:
            return await ctx.send("❓ Mention at least one user to assign!")

        role_name = f"Team {team_number}"
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role is None:
            try:
                team_color = discord.Color.blue() if team_number == 1 else discord.Color.red()
                role = await ctx.guild.create_role(
                    name=role_name, 
                    color=team_color, 
                    reason="Auto-created by Team Assign command"
                )
                await ctx.send(f"🔨 Created new role: **{role_name}**")
            except discord.Forbidden:
                return await ctx.send("❌ I don't have permission to **create** roles!")

        added = []
        for member in members:
            try:
                await member.add_roles(role)
                added.append(member.display_name)
            except discord.Forbidden:
                continue 

        if added:
            await ctx.send(f"✅ Added to **{role_name}**: {', '.join(added)}")
        else:
            await ctx.send("⚠️ No members were updated. Check my role position in Server Settings!")

    @commands.command(name="print_grim")
    @commands.has_permissions(manage_roles=True)
    async def print_grim(self, ctx):
        """
        Usage: !print_grim 1
        """
        await ctx.send(self.game.print_board())

    @commands.command(name="create_poll", description="Creates a native Discord poll")
    @commands.has_permissions(manage_roles=True)
    async def create_poll(self, interaction: discord.Interaction): # FIX: Added 'self'
        print("Creating Poll!")
        # 1. Initialize the Poll object
        poll = discord.Poll(
            question="What is the best programming language?",
            duration=datetime.timedelta(hours=24), # Polls can last up to 32 days
            multiple=False # Set to True to allow users to select multiple options
        )

        # 2. Add options (You can add up to 10 answers)
        poll.add_answer(text="Python", emoji="🐍")
        poll.add_answer(text="JavaScript", emoji="🌐")
        poll.add_answer(text="Rust", emoji="🦀")

        # 3. Send the poll using the 'poll' keyword argument
        await interaction.response.send_message(poll=poll)
        
        # Optional: Grab the message ID so you can check results later
        message = await interaction.original_response()
        await interaction.followup.send(f"Poll sent! To check results later, use message ID: `{message.id}`", ephemeral=True)


# --- 2. The Bot Manager (Where your bot is configured) ---
class BotMgr(commands.Bot):
    def __init__(self, game: GameManager):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.game = game
        
        # Initialize the underlying commands.Bot class
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This is the modern discord.py way to load classes/cogs on startup
        await self.add_cog(TeamManagement(self, self.game))
        await self.tree.sync()
        print("Hooking in custom commands and syncing slash commands.")

    async def on_ready(self):
        print(f"We are ready to go in, {self.user.name}")
