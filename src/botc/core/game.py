import random
import os
from typing import List, Optional, Tuple
import discord
from dotenv import load_dotenv

from botc.enums import Alignment, RoleClass, RoleName
from botc.player import Player
from botc.core.distribution import RoleDistributor
from botc.encounters import Deck

# Import Discord components
from botc.discord_manager.bot import BotManager
from botc.discord_manager.polling import PollManager
from botc.discord_manager.cogs.game_commands import GameCommands

from dataclasses import dataclass

@dataclass
class Counters:
    turn: int = 0
    day: int = 0
    night: int = 0

class PlayerManager():
    def __init__(self, player_names: List[str] = []):
        self.player_names = player_names
        self.roles_distribution = RoleDistributor(self.player_names)
        self.player_list: List[Player] = self.roles_distribution.assign_roles()

    @property 
    def players_alive(self) -> List[Player]:
        return [player for player in self.player_list if player.status.alive]



class EventManager():
    def __init__(self):
        self.event_interval=1 #how frequently to do an event, hardcoded for now
        self.event_deck=Deck.from_json("default")


@dataclass
class VoteTable():
    vote_table: dict[str, dict[str, int]] = {}

class ExecuteManager():
    def __init__(self):
        self.killed_tonight: Optional[Player] = None
        self.executed_player: str = ""
        self.player_names: List[str] = []
    def reset_vote_table(self):
        self.vote_table = {
            voter: {candidate: 0 for candidate in self.player_names}
            for voter in self.player_names
        }

class DiscordManager():
    def __init__(self, game: 'GameManager'):
        # Init bot components
        load_dotenv()
        self.token = str(os.getenv("DISCORD_TOKEN"))
        self.bot = BotManager(game)
        self.poll_manager = PollManager(game)
        self.command_cog = GameCommands(self.bot, game)

    async def modify_information(self, target: str, message: str, choices: List[str], max_input: int):
        return await self.command_cog.dmpoll(target, message, choices, max_input)

class GameManager:
    def __init__(self):
        self.game_over: bool = False
        self.counter = Counters
        self.game_master: str = ""
        self.mgr_player: PlayerManager = PlayerManager()
        
    def resolve_temporary_conditions(self):
        for player in self.players:
            player.status.protected=False
            player.status.poisoned=False

    async def start_game(self, interaction: discord.Interaction):
        self.players_alive = self.players
        await self.message_roles_to_players()

        for player in self.get_wake_order(is_first_night=True):
            print("Calling " + player.registered_role.role_class.__str__())
            await player.take_action(self)

        while(self.game_over != True):
            self.night_counter+=1
            self.resolve_temporary_conditions()
            await self.start_voting_phase(interaction)
            self.day_counter+=1
            
            # if self.event_deck:
            #     card=self.event_deck.draw_card()
            #     await interaction.channel.send(card.specific_encounter.flavor_text) 
            #     await card.specific_encounter.resolve(self)
            
            for player in self.get_wake_order(is_first_night=False):
                await player.take_action(self)

    async def message_roles_to_players(self):
        for player in self.players:
            await self.command_cog.send_direct_message(player.player_name, player.show_role())

    async def start_voting_phase(self, interaction: discord.Interaction):
        if not self.players_alive:
            if not interaction.response.is_done():
                await interaction.response.send_message("There are no alive players to vote!", ephemeral=True)
            return

        allowed_player_ids = [player.player_name for player in self.players_alive] 

        try:
            await self.poll_manager.run_execution_poll(interaction, allowed_player_ids)
        except Exception as e:
            print(f"⚠️ Error executing poll: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("System Error: Could not load the polling module.", ephemeral=True)

    def get_alive_neighbors(self, target_player: Player) -> Tuple[Player, Player]:
        index = self.players.index(target_player)
        num_players = len(self.players)

        right_idx = (index + 1) % num_players
        while not self.players[right_idx].status.alive:
            right_idx = (right_idx + 1) % num_players
            if right_idx == index: break
        right_neighbor = self.players[right_idx]

        left_idx = (index - 1) % num_players
        while not self.players[left_idx].status.alive:
            left_idx = (left_idx - 1) % num_players
            if left_idx == index: break
        left_neighbor = self.players[left_idx]

        return left_neighbor, right_neighbor

    def get_player_by_role(self, target_role: RoleName) -> Optional[Player]:
        for p in self.players:
            if p.registered_role == target_role: return p
        return None

    def get_player_by_name(self, player_name="") -> Player:
        if player_name == "":
            player_name = input("Select Target: ")
        for p in self.players:
            if p.player_name == player_name: return p
        raise ValueError(f"Player '{player_name}' not found.")

    def get_wake_order(self, is_first_night: bool) -> List[Player]:
        waking_players = []
        for player in self.players:
            priority = player.role_behavior.first_night_priority if is_first_night else player.role_behavior.other_night_priority
            if priority is not None:
                waking_players.append((priority, player))
        
        waking_players.sort(key=lambda x: x[0])
        return [p for priority, p in waking_players]

    def get_board_str(self) -> str:
        output_str = "```\n" + "="*55 + "\n"
        for i, player in enumerate(self.players):
            status = "Alive" if player.status.alive else "DEAD"
            poison_str = " [POISONED]" if player.status.poisoned else ""
            protect_str = " [PROTECTED]" if player.status.protected else ""

            if player.registered_role == RoleName.DRUNK:
                role_info = f"Drunk (Thinks: {player.believed_role})"
            elif player.registered_role == RoleName.SPY:
                role_info = f"Spy (Registers: {player.registered_role}/{player.registered_alignment})"
            else:
                role_info = f"{player.registered_role} ({player.registered_alignment})"

            output_str += f"Seat {i+1:02d} | {player.player_name:<8} | {status:<5} | {role_info}{poison_str}{protect_str}\n"
        output_str += "="*55 + "\n```"
        return output_str
