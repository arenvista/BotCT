import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os 

# --- 1. The Cog (Where your commands live) ---
class TeamManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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


# --- 2. The Bot Manager (Where your bot is configured) ---
class BotMgr(commands.Bot):
    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        # Initialize the underlying commands.Bot class
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This is the modern discord.py way to load classes/cogs on startup
        await self.add_cog(TeamManagement(self))

    async def on_ready(self):
        print(f"We are ready to go in, {self.user.name}")


# --- 3. Execution Logic ---
if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    token = str(os.getenv("DISCORD_TOKEN"))
    
    # Setup logging
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

    # Instantiate and run the bot class
    bot = BotMgr()
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
