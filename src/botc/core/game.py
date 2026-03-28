import random
import os
from typing import List, Optional, Tuple, Dict
import discord
from dotenv import load_dotenv

from botc.enums import Alignment, RoleClass, RoleName, Status
from botc.player import Player
from botc.core.distribution import RoleDistributor
from botc.encounters import Deck

# Import Discord components
import discord
from botc.discord_manager.bot import BotManager
from botc.discord_manager.polling import PollManager
from botc.discord_manager.cogs.game_commands import GameCommands

from dataclasses import dataclass


# class EventManager:
#     def __init__(self):
#         self.event_interval = 1  # how frequently to do an event, hardcoded for now
#         self.event_deck = Deck.from_json("default")

#     async def CallEvent(self, game: 'GameManager', interaction: discord.interactions):
#         if self.event_deck:
#             card = self.event_deck.draw_card()
#             await interaction.channel.send(card.specific_encounter.flavor_text) 
#             await card.specific_encounter.resolve(self)

@dataclass
class Counters:
    turn: int = 0
    day: int = 0
    night: int = 0

class PlayerManager:
    def __init__(self, player_names: Optional[List[str]] = None):
        self.player_names = player_names or []
        self.player_list: List[Player] = []

    def assign_roles(self):
        self.player_list = RoleDistributor(self.player_names).assign_roles()

    def get_players(self, filter_status: Optional[Dict[str, bool|int]] = None, filter_role: Optional[List[RoleName]] = None, is_registered_role: bool = True) -> List[Player]:
        """
        Returns a list of players whose statuses match all conditions in the filters dict.
        Example: get_filtered_players({"poisoned": False, "alive": True})
        """
        if filter_status is None: filter_status = {}
        if filter_role is None: filter_role = []

        player_status_filtered = [
            p for p in self.player_list
            if all(getattr(p.status, attr_name) == required_state for attr_name, required_state in filter_status.items())
        ]

        if not filter_role: 
            return player_status_filtered
            
        if is_registered_role: 
            return [p for p in player_status_filtered if p.registered_role in filter_role]
        else: 
            return [p for p in player_status_filtered if p.believed_role in filter_role]

    def get_player(self, username) -> Optional[Player]:
        for p in self.player_list:
            if p.username == username: 
                return p
        return None


class DayManager:
    def __init__(self, game: 'GameManager'):
        self.game = game
        self.vote_table: dict[str, dict[str, int]] = {}
        self.executed_player: str = ""

    def reset_vote_table(self):
        # Pull names directly from game to avoid empty list bugs
        player_names = [p.username for p in self.game.get_players()]
        self.vote_table = {
            voter: {candidate: 0 for candidate in player_names}
            for voter in player_names
        }

    async def start_voting_phase(self, interaction: discord.Interaction):
        allowed_usernames = [player.username for player in self.game.get_players() if player.status.can_vote] 
        try:
            await self.game.mgr_discord.poll_manager.run_execution_poll(interaction, allowed_usernames)
        except Exception as e:
            print(f"⚠️ Error executing poll: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("System Error: Could not load the polling module.", ephemeral=True)


class NightManager:
    def __init__(self, game: 'GameManager'):
        self.game = game

    def get_wake_order(self, is_first_night: bool) -> List[Player]:
        waking_players = []
        # Fixed scope issue: changed 'game' to 'self.game'
        for player in self.game.get_players():
            priority = player.role_behavior.first_night_priority if is_first_night else player.role_behavior.other_night_priority
            if priority is not None: 
                waking_players.append((priority, player))
                
        waking_players.sort(key=lambda x: x[0])
        return [p for priority, p in waking_players]

class DiscordManager:
    def __init__(self, game: 'GameManager'):
        # Init bot components
        load_dotenv()
        self.token = str(os.getenv("DISCORD_TOKEN"))
        self.bot = BotManager(game)
        self.poll_manager = PollManager(game)
        self.command_cog = GameCommands(self.bot, game)

    async def send_message(self, username, content):
        await self.command_cog.send_direct_message(username, content)

    async def send_query(self, target: str, message: str, choices: List[str], max_input: int):
        return await self.command_cog.query_user(target, message, choices, max_input)

    def run_bot(self):
        self.bot.run(self.token)


class GameManager:
    def __init__(self):
        self.game_over: bool = False
        self.counter = Counters() # Added parentheses to instantiate
        self.game_master: str = ""
        self.mgr_player: PlayerManager = PlayerManager()
        self.mgr_night: NightManager = NightManager(self)
        self.mgr_day: DayManager = DayManager(self)
        self.killed_tonight: Player|None = None
        self.mgr_discord: DiscordManager = DiscordManager(self)

    def get_player(self, username) -> Player | None:
        return self.mgr_player.get_player(username)
        
    def get_players(self, filter_status: Optional[Dict[str, bool|int]] = None, filter_roles: Optional[List[RoleName]] = None) -> List[Player]:
        if filter_status is None: filter_status = {}
        if filter_roles is None: filter_roles = []
        # Passed filter_roles down to the player manager
        return self.mgr_player.get_players(filter_status, filter_roles)

    def resolve_temporary_conditions(self):
        for player in self.mgr_player.player_list: 
            player.status.resolve_temporary_conditions()

    async def send_query(self, username: str, message: str, choices: List[str], max_input: int):
        return await self.mgr_discord.send_query(username, message, choices, max_input)

    async def send_message(self, username, content):
        return await self.mgr_discord.send_message(username, content)

    async def message_roles_to_players(self):
        for player in self.get_players():
            await self.send_message(player.username, player.show_role())

    async def day_events(self, interaction: discord.Interaction):
        self.counter.day += 1
        self.resolve_temporary_conditions()
        await self.mgr_day.start_voting_phase(interaction)

    async def night_events(self):
        if self.counter.night == 0:
            #Start of 1st Night
            demon_players=[p.username for p in self.get_players() if p.registered_role.role_class == RoleClass.DEMONS]
            demon_str=" , ".join(demon_players)
            minion_players=[p.username for p in self.get_players() if p.registered_role.role_class == RoleClass.MINIONS]
            minion_str=" , ".join(minion_players)
            message=f"The demon players are {demon_str} and The minion players are {minion_str}"
            for player in demon_players+minion_players:
                await self.send_message(player, message)
            for player in self.mgr_night.get_wake_order(True):
                print("Calling " + player.registered_role.display_name)
                await player.take_action(self)
            taken_good_roles=[p.registered_role for p in self.get_players() if p.registered_alignment==Alignment.GOOD]
            all_good_roles=" , ".join([str(r) for r in RoleName.get_by_class(RoleClass.TOWNSFOLK) if r not in taken_good_roles][:3])
            
            for player in demon_players:
                await self.send_message(player, f"Three available good roles are {all_good_roles}")
        else:
            for player in self.mgr_night.get_wake_order(False):
                await player.take_action(self)
        self.counter.night += 1


    async def message_relevant_roles(self):
        player_spy = self.get_players(filter_roles=[RoleName.SPY])[0]
        spy_opts = []
        await self.send_query(self.game_master, "Pick a role to be assigned", spy_opts, 1)

        player_recluse = self.get_players(filter_roles=[RoleName.RECLUSE])[0]
        rec_opts = []
        await self.send_query(self.game_master, "", rec_opts, 1)

    async def assign_roles(self):
        self.mgr_player.assign_roles()
        if self.game_master != "":
            await self.message_relevant_roles()

    async def start_game(self, interaction: discord.Interaction):
        # await self.assign_roles()
        await self.message_roles_to_players()
        
        while self.game_over != True:
            await self.night_events()
            await self.day_events(interaction)


    def get_alive_neighbors(self, target_player: Player) -> Tuple[Player, Player]:
        index = self.get_players().index(target_player)
        num_players = len(self.get_players())
        player_list = self.get_players()

        right_idx = (index + 1) % num_players
        while not player_list[right_idx].status.alive:
            right_idx = (right_idx + 1) % num_players
            if right_idx == index: break
        right_neighbor = player_list[right_idx]

        left_idx = (index - 1) % num_players
        while not player_list[left_idx].status.alive:
            left_idx = (left_idx - 1) % num_players
            if left_idx == index: break
        left_neighbor = player_list[left_idx]

        return left_neighbor, right_neighbor

    def get_board_str(self) -> str:
        output_str = "The Grimoire 📔:\n" + "```\n" + "="*55 + "\n"
        for i, player in enumerate(self.get_players()):
            status = "Alive" if player.status.alive else "DEAD"
            poison_str = " [POISONED]" if player.status.poisoned else ""
            protect_str = " [PROTECTED]" if player.status.protected else ""

            if player.registered_role == RoleName.DRUNK:
                role_info = f"Drunk (Thinks: {player.believed_role})"
            elif player.registered_role == RoleName.SPY:
                role_info = f"Spy (Registers: {player.registered_role}/{player.registered_alignment})"
            else:
                role_info = f"{player.registered_role} ({player.registered_alignment})"

            output_str += f"Seat {i+1:02d} | {player.username:<8} | {status:<5} | {role_info}{poison_str}{protect_str}\n"
        output_str += "="*55 + "\n```"
        return output_str
