from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# 1. Load dotenv at the top level so environment variables are available immediately.
load_dotenv()

if TYPE_CHECKING:
    from botc.core.game import GameManager
    
from botc.discord_manager.cogs.game_commands import GameCommands

class BotManager(commands.Bot):
    def __init__(self, game: GameManager) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        self.game: GameManager = game
        
        # This now works perfectly because load_dotenv() already ran
        self.token = str(os.getenv("DISCORD_TOKEN"))
        
        super().__init__(command_prefix="!", intents=intents)
        
    async def setup_hook(self) -> None:
        # Load our command Cog
        await self.add_cog(GameCommands(self, self.game))
        
        # Fast syncing for testing server
        try:
            # os.getenv returns None if missing, so we need to handle that safely
            server_id_str = os.getenv("SERVER_ID")
            if server_id_str is None:
                raise ValueError("SERVER_ID not found in environment.")
            
            TEST_SERVER: discord.Object = discord.Object(id=int(server_id_str)) 
            
        except (ValueError, TypeError):
            # Fallback ID
            TEST_SERVER: discord.Object = discord.Object(id=1373836529390190602) 
            
        self.tree.copy_global_to(guild=TEST_SERVER)
        await self.tree.sync(guild=TEST_SERVER)
        print("Hooking in custom commands and syncing to test server.")

    async def on_ready(self) -> None:
        if self.user is None:
            raise ValueError("User is None")
        print(f"We are ready to go in, {self.user.name}")
