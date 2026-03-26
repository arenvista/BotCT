from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import discord
import asyncio
import datetime
from datetime import timedelta
import random

from botc.discord_manager.views import ExecutionView

if TYPE_CHECKING:
    from botc.core.game import GameManager

class PollManager:
    def __init__(self, game: GameManager) -> None:
        self.game: GameManager = game

    async def run_gamemaster_poll(self, interaction: discord.Interaction) -> str:
        """
        Conducts a poll asking who wants to be GM. 
        Randomly selects one person who said 'Yes'.
        """
        # 1. Create the Poll
        # NOTE: Answers are passed as a list of PollAnswer objects or dicts
        poll = discord.Poll(
            question="Would you like to be the Game Master?",
            duration=datetime.timedelta(hours=1), # Discord prefers hour increments; 1 is the minimum for some versions
        )
        
        # Correct way to add answers in newer discord.py versions:
        poll.add_answer(text="Yes", emoji="✅")
        poll.add_answer(text="No", emoji="❌")

        try:
            # Use followup.send(poll=poll)
            poll_message = await interaction.followup.send(
                content="📊 **GM Selection:** Please vote 'Yes' if you are interested in being the Game Master.",
                poll=poll
            )
        except discord.HTTPException as e:
            print(f"Failed to send poll: {e.text}") # .text gives more detail on the 'Invalid Form Body'
            return ""

        # 2. Wait for the poll to finish 
        # For testing, we wait 120s, then manually end it because minimum duration is usually higher
        await asyncio.sleep(120)

        # 3. Finalize and fetch results
        try:
            # Refresh the message to get the latest poll state
            poll_message = await interaction.channel.fetch_message(poll_message.id)
            
            if not poll_message.poll.is_finalised:
                await poll_message.end_poll()
                # Re-fetch after ending to get final counts
                poll_message = await interaction.channel.fetch_message(poll_message.id)
        except discord.HTTPException:
            return ""

        # 4. Identify the "Yes" voters
        yes_voters = []
        
        # Find the specific answer for "Yes"
        yes_answer = discord.utils.get(poll_message.poll.answers, text="Yes")

        if yes_answer:
            # Fetch the users who voted for this specific answer
            async for user in yes_answer.voters():
                if not user.bot:
                    yes_voters.append(user.display_name)

        # 5. Random Selection
        if yes_voters:
            selected_gm = random.choice(yes_voters)
            await interaction.followup.send(f"👑 **{selected_gm}** has been randomly selected as the Game Master!")
            return selected_gm
        
        await interaction.followup.send("⚠️ No one volunteered to be the Game Master.")
        return ""

    async def run_execution_poll(self, interaction: discord.Interaction, allowed_player_ids: list[str]) -> Optional[discord.Message]:
        if not isinstance(interaction.channel, discord.TextChannel):
            error_msg = "This action requires a text channel."
            await interaction.followup.send(error_msg, ephemeral=True) if interaction.response.is_done() else await interaction.response.send_message(error_msg, ephemeral=True)
            return None

        await interaction.followup.send(f"Polling Day {self.game.day_counter}", ephemeral=True) if interaction.response.is_done() else await interaction.response.send_message(f"Polling Day {self.game.day_counter}", ephemeral=True)

        thread: discord.Thread = await interaction.channel.create_thread(
            name=f"Town Square Voting: (Day {self.game.day_counter})", type=discord.ChannelType.public_thread
        )

        # 1. Create the Dropdown View
        view = ExecutionView(self.game.players_alive)

        embed = discord.Embed(
            title=f"Day {self.game.day_counter}: Who should be executed?",
            description="Select a player from the dropdown menu below to cast your vote.\n*You may change your vote at any time before the timer runs out.*", 
            color=discord.Color.dark_red()
        )

        # 2. Send the message with the dropdown attached
        poll_message: discord.Message = await thread.send(embed=embed, view=view)

        duration_minutes: int = 4
        num_players: int = len(allowed_player_ids)
        elapsed_time: int = 0
        check_interval: int = 5

        # 3. Wait Loop
        while elapsed_time < (duration_minutes * 60):
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval
            
            # Check if all allowed players have voted
            # view.dropdown.votes tracks {username: chosen_target}
            voters = [u for u in view.dropdown.votes.keys() if u in allowed_player_ids]
            if len(voters) >= num_players:
                break

        # 4. Disable the dropdown so no more votes can be cast
        view.dropdown.disabled = True
        await poll_message.edit(view=view)

        # 5. Tally the Votes
        results = {"Skip Vote": 0}
        for player in self.game.players_alive:
            results[player.player_name] = 0
            
        total_valid_votes = 0
        
        for voter_name, chosen_target in view.dropdown.votes.items():
            # Rule: Only alive players count
            if voter_name in allowed_player_ids:
                if chosen_target in results:
                    results[chosen_target] += 1
                    total_valid_votes += 1

        # 6. Process the Results
        if total_valid_votes == 0:
            await thread.send("⚖️ No valid votes cast. No one executed.")
            return poll_message

        executed_target_name = None
        highest_vote_count = 0

        for target_name, votes in results.items():
            if votes > highest_vote_count:
                highest_vote_count = votes
            if votes > (total_valid_votes / 2.0):
                executed_target_name = target_name

        if executed_target_name is None:
            await thread.send(f"⚖️ No option received > 50% (Highest: {highest_vote_count}/{total_valid_votes}). No execution.")
        elif executed_target_name == "Skip Vote":
            await thread.send(f"⚖️ The majority ({results['Skip Vote']}/{total_valid_votes}) chose to skip. No execution.")
        else:
            await thread.send(f"🩸 The town has spoken with {results[executed_target_name]}/{total_valid_votes} votes! **{executed_target_name}** is executed.")
            
            # Update the Game State
            try:
                p = self.game.get_player_by_name(executed_target_name)
                p.status.alive = False
                self.game.executed_player = executed_target_name
            except ValueError as e:
                await thread.send(f"⚠️ Error: Could not find player.")

        print(self.game.get_board_str())
        return poll_message
