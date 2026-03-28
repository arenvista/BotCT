# src/botc/behaviors/base.py
from __future__ import annotations
from functools import wraps
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

from botc.enums import RoleName
from . import register_role

if TYPE_CHECKING:
    from botc.core.game import GameManager
    from botc.player import Player

from functools import wraps # Highly recommended to preserve method names/docstrings


def message_self(func):
    @wraps(func)
    async def wrapper(self, player: Player, game: GameManager, *args, **kwargs):
        # Execute any specific logic the role might have upon dying first
        result: str = await func(self, player, game, *args, **kwargs)
        await game.send_message(player.username, result)
        return result
    return wrapper

def message_death(func):
    @wraps(func)
    async def wrapper(self, player: Player, game: GameManager, *args, **kwargs):
        # Execute any specific logic the role might have upon dying first
        result = await func(self, player, game, *args, **kwargs)
        
        # Broadcast the death and update state
        await game.send_message(player.username, "You have died!")
        player.status.alive = False
        
        return result
    return wrapper

class RoleBehavior(ABC):
    """The absolute root of all roles."""

    first_night_priority: Optional[int] = None
    other_night_priority: Optional[int] = None
    is_reliable: bool = True  # Base property, but actual reliability is dynamic

    async def check_gm_override(self, game: GameManager, player: Player) -> bool:
        """
        Asks the Game Master if they want to manually override the default
        night action for this player. Returns True if the GM wants to intervene.
        """
        if game.game_master == "":
            return False

        role_name: str = str(player.registered_role)

        # Dynamically build the prompt so the GM knows EXACTLY what state the player is in
        if player.status.is_reliable:
            prompt_text = f"Skip Manual Entry for {role_name} ({player.username})?"
        else:
            prompt_text = f"Skip Manual Entry for Drunk/Poisoned {role_name} ({player.username})?"

        gm_skip = await game.send_query(game.game_master, prompt_text, ["Yes", "No"], 1)

        # Return True if they clicked "No" (meaning, DO NOT skip manual entry)
        return gm_skip is not None and gm_skip[0] == "No"


    async def kill(self, target: Player, game: GameManager):
        await target.role_behavior.die(target,game)


    @abstractmethod
    async def act(self, player: Player, game: GameManager) -> Any:
        """Every role must do *something* at night."""
        pass


    @abstractmethod
    async def die(self, player: Player, game: GameManager) -> Any:
        pass

# --- THE ARCHETYPES ---


class InfoRoleBehavior(RoleBehavior):
    """
    Archetype for roles that receive information from the ST.
    (e.g., Washerwoman, Investigator, Empath, Librarian)
    """
    async def act(self, player: Player, game: GameManager) -> None:
        is_reliable: bool = player.status.is_reliable
        wants_manual = await self.check_gm_override(game, player)

        night_data: Dict[str, Any] = {}

        if is_reliable:
            night_data = await self.get_default_trusted(player, game)
            if wants_manual:
                night_data = await self.get_manual_trusted(player, game, night_data)
        else:
            night_data = await self.get_default_dishonest(player, game)
            if wants_manual:
                night_data = await self.get_manual_dishonest(player, game, night_data)

        if night_data:
            await self.send_result(player, game, night_data)

    @abstractmethod
    async def get_default_trusted( self, player: Player, game: GameManager) -> Dict[str, Any]: pass
    @abstractmethod
    async def get_manual_trusted( self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def get_default_dishonest( self, player: Player, game: GameManager) -> Dict[str, Any]: pass
    @abstractmethod
    async def get_manual_dishonest( self, player: Player, game: GameManager, default_data: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def send_result( self, player: Player, game: GameManager, night_data: Dict[str, Any]) -> None: pass
    async def die(self, player: Player, game: GameManager) -> Any: pass


class ActionRoleBehavior(RoleBehavior):
    """
    Archetype for roles that target players but don't get info back.
    (e.g., Monk, Imp, Poisoner)
    """
    async def act(self, player: Player, game: GameManager) -> None:
        wants_manual = await self.check_gm_override(game, player)
        if wants_manual: target = await self.get_manual_target(player, game)
        else: target = await self.get_default_target(player, game)
        if target: await self.execute_action(player, target, game)
    @abstractmethod
    async def get_default_target( self, player: Player, game: GameManager) -> Optional[Player]: pass
    @abstractmethod
    async def get_manual_target( self, player: Player, game: GameManager) -> Optional[Player]: pass
    @abstractmethod
    async def execute_action( self, player: Player, target: Player, game: GameManager) -> None: pass
    async def die(self, player: Player, game: GameManager) -> Any: pass


class PassiveBehavior(RoleBehavior):
    """
    Archetype for roles that do nothing during the night phase.
    (e.g., passive Outsiders, Day-acting roles)
    """
    async def act(self, player: Player, game: GameManager) -> None: pass
    async def die(self, player: Player, game: GameManager) -> Any: pass
