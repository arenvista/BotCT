# Create a discord bot using python discord.py that lets me send members to a certain roles
import discord
from discord.ext import commands 
import logging
from dotenv import load_dotenv
import os 

load_dotenv()
token: str = str(os.getenv("DISCORD_TOKEN"))

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.command(name="create_private")
@commands.has_permissions(manage_roles=True)
async def create_private_channel(ctx, category: discord.CategoryChannel, channel_name: str, members: commands.Greedy[discord.Member]):
    """
    Creates a private text channel under a specific category.
    Usage: !create_private "Category Name" "channel-name" @user1 @user2
    """
    
    # 1. Base Permissions (Hide from everyone, keep bot access)
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.guild.me: discord.PermissionOverwrite(view_channel=True)
    }

    # 2. Add specific members to the permissions list
    if not members:
        await ctx.send("⚠️ You need to mention at least one member!")
        return

    for member in members:
        overwrites[member] = discord.PermissionOverwrite(view_channel=True)

    # 3. Create the channel IN THE SPECIFIC CATEGORY
    try:
        new_channel = await ctx.guild.create_text_channel(
            name=channel_name,
            category=category,  # <-- This tells Discord where to put the channel
            overwrites=overwrites,
            reason=f"Private channel created by {ctx.author}"
        )
        
        member_names = ", ".join([m.display_name for m in members])
        await ctx.send(f"✅ Created {new_channel.mention} under the **{category.name}** category for: **{member_names}**")

    except discord.Forbidden:
        await ctx.send("❌ I don't have the required permissions to do this.")
    except discord.HTTPException:
        await ctx.send("❌ Something went wrong communicating with Discord.")

# Error handling specifically if the bot can't find the category
@create_private_channel.error
async def create_private_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ You need the `Manage Roles` permission to use this command.")
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("❌ I couldn't find a category with that name. Check your spelling and try again!")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def assign(ctx, team_number: int, members: commands.Greedy[discord.Member]):
    """
    Assigns members to a team. Creates the role if it doesn't exist.
    Usage: !assign 1 @user1 @user2
    """
    if team_number not in [1, 2]:
        return await ctx.send("❌ Please choose team **1** or **2**.")

    if not members:
        return await ctx.send("❓ Mention at least one user to assign!")

    role_name = f"Team {team_number}"
    
    # 1. Try to find the role
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    # 2. If it doesn't exist, create it
    if role is None:
        try:
            # You can customize the colors here (e.g., Blue for Team 1, Red for Team 2)
            team_color = discord.Color.blue() if team_number == 1 else discord.Color.red()
            
            role = await ctx.guild.create_role(
                name=role_name, 
                color=team_color, 
                reason="Auto-created by Team Assign command"
            )
            await ctx.send(f"🔨 Created new role: **{role_name}**")
        except discord.Forbidden:
            return await ctx.send("❌ I don't have permission to **create** roles!")

    # 3. Assign the members
    added = []
    for member in members:
        try:
            await member.add_roles(role)
            added.append(member.display_name)
        except discord.Forbidden:
            continue # Skip users if the bot's hierarchy is too low

    if added:
        await ctx.send(f"✅ Added to **{role_name}**: {', '.join(added)}")
    else:
        await ctx.send("⚠️ No members were updated. Check my role position in Server Settings!")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
