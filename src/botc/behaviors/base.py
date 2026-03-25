# src/botc/behaviors/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from botc.enums import RoleName
from . import register_role

if TYPE_CHECKING:
    from botc.player import Player
    from botc.core.game import GameManager

class RoleBehavior(ABC):
    first_night_priority: Optional[int] = None
    other_night_priority: Optional[int] = None
    is_reliable: bool = True # Base property, but actual reliability is dynamic

    # --- NEW HELPER METHOD ---
    async def check_gm_override(self, game: GameManager, player: Player) -> bool:
        """
        Asks the Game Master if they want to manually override the default 
        night action for this player. Returns True if the GM wants to intervene.
        """
        if game.game_master == "":
            return False
            
        is_reliable: bool = not (player.actual_role == RoleName.DRUNK or player.poisoned)
        role_name: str = player.actual_role.__str__()
        
        # Dynamically build the prompt so the GM knows EXACTLY what state the player is in
        if is_reliable:
            prompt_text = f"Skip Manual Entry for {role_name} ({player.player_name})?"
        else:
            prompt_text = f"Skip Manual Entry for Drunk/Poisoned {role_name} ({player.player_name})?"
            
        gm_skip = await game.command_cog.dmdropdown(
            game.game_master, 
            prompt_text, 
            ["Yes", "No"], 
            1
        )
        
        # Return True if they clicked "No" (meaning, DO NOT skip manual entry)
        return (gm_skip is not None and gm_skip[0] == "No")

    @abstractmethod
    async def act(self, player: Player, game: GameManager) -> None:
        pass

class PassiveBehavior(RoleBehavior):
    async def act(self, player: Player, game: GameManager) -> None:
        pass
