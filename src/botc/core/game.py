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

class GameManager:
    ROLES_DEMONS = RoleName.get_by_class(RoleClass.DEMONS)
    ROLES_MINIONS = RoleName.get_by_class(RoleClass.MINIONS)
    ROLES_OUTSIDERS = RoleName.get_by_class(RoleClass.OUTSIDERS)
    ROLES_TOWNSFOLK = RoleName.get_by_class(RoleClass.TOWNSFOLK)

    def __init__(self, player_names: List[str] = []):
        self.player_names = player_names
        self.event_interval=1 #how frequently to do an event, hardcoded for now
        self.event_deck=Deck.from_json("default")
        
        if self.player_names:
            self.roles_distribution = RoleDistributor(self.player_names)
            self.players: List[Player] = self.assign_roles()
            self.players_alive: List[Player] = self.players
        else:
            self.players = []
            self.players_alive = []
            
        self.turn_counter: int = 0
        self.day_counter: int = 0
        self.night_counter: int = 0
        self.game_over: bool = False
        
        self.game_master: str = ""
        self.killed_tonight: Optional[Player] = None
        self.executed_player: str = ""
        self.nominator: str = ""
        
        self.vote_table: dict[str, dict[str, int]] = {}
        self.reset_vote_table()

        # Init bot components
        load_dotenv()
        self.token = str(os.getenv("DISCORD_TOKEN"))
        self.bot = BotManager(self)
        self.poll_manager = PollManager(self)
        self.command_cog = GameCommands(self.bot, self)

    async def modify_information(self, message: str, choices: List[str], max_input: int):
        return await self.command_cog.dmpoll(self.game_master, message, choices, max_input)

    def reset_vote_table(self):
        self.vote_table = {
            voter: {candidate: 0 for candidate in self.player_names}
            for voter in self.player_names
        }

    def assign_roles(self) -> List[Player]:
        demon_count = self.roles_distribution.num_demons
        outsider_count = self.roles_distribution.num_outsiders
        townsfolk_count = self.roles_distribution.num_townsfolk
        minion_count = self.roles_distribution.num_minions

        chosen_demons = random.sample(self.ROLES_DEMONS, demon_count)
        chosen_minions = random.sample(self.ROLES_MINIONS, minion_count)

        if RoleName.BARON in chosen_minions:
            # Note: In standard Blood on the Clocktower, Baron adds 2 Outsiders, not 3!
            # Change this to 2 if you want to follow standard Trouble Brewing rules.
            BARON_OUTSIDER_OFFSET = 2 
            outsider_count += BARON_OUTSIDER_OFFSET
            townsfolk_count -= BARON_OUTSIDER_OFFSET

        chosen_outsiders = random.sample(self.ROLES_OUTSIDERS, outsider_count)
        chosen_townsfolk = random.sample(self.ROLES_TOWNSFOLK, townsfolk_count)
        selected_roles = chosen_demons + chosen_outsiders + chosen_townsfolk + chosen_minions

        drunk_fake_role = None
        if RoleName.DRUNK in chosen_outsiders:
            available_townsfolk = [r for r in self.ROLES_TOWNSFOLK if r not in chosen_townsfolk]
            drunk_fake_role = random.choice(available_townsfolk)

        spy_fake_role = None
        if RoleName.SPY in chosen_minions:
            available_good_roles = [
                r for r in (self.ROLES_TOWNSFOLK + self.ROLES_OUTSIDERS) 
                if r not in (chosen_townsfolk + chosen_outsiders) and r != drunk_fake_role
            ]
            if available_good_roles:
                spy_fake_role = random.choice(available_good_roles)

        random.shuffle(selected_roles)

        assigned_players: List[Player] = []
        for player_name, role_enum in zip(self.player_names, selected_roles):
            
            # The Drunk thinks they are a Townsfolk, otherwise everyone believes their actual role
            believed_role = drunk_fake_role if role_enum == RoleName.DRUNK else role_enum
            
            # The Spy registers falsely to abilities, otherwise everyone registers as their actual role
            registered_role = spy_fake_role if role_enum == RoleName.SPY else role_enum
            
            # Spy registers as Good, everyone else passes None so Player.__init__ sets their default
            registered_alignment = Alignment.GOOD if role_enum in self.ROLES_TOWNSFOLK+self.ROLES_OUTSIDERS else Alignment.EVIL

            assigned_players.append(
                Player(player_name, believed_role, registered_role, registered_alignment)
            )

        return assigned_players
    
    def resolve_temporary_conditions(self):
        for player in self.players:
            player.status.protected=False
            player.status.poisoned=False

    async def start_game(self, interaction: discord.Interaction):
        # self.roles_distribution = RoleDistributor(self.player_names)
        # self.players = self.assign_roles()

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
