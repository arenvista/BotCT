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
        Ends automatically when 3 unique users vote, or after 120 seconds.
        Randomly selects one person who said 'Yes'.
        """
        # 1. Create the Poll
        poll = discord.Poll(
            question="Would you like to be the Game Master?",
            duration=datetime.timedelta(hours=1), # Minimum native duration
        )
        
        poll.add_answer(text="Yes", emoji="✅")
        poll.add_answer(text="No", emoji="❌")

        try:
            poll_message = await interaction.followup.send(
                content="👑 **GM Selection:** Please vote 'Yes' if you are interested in being the Game Master.",
                poll=poll
            )
        except discord.HTTPException as e:
            print(f"Failed to send poll: {e.text}")
            return ""

        # 2. Wait for 3 unique users to vote, or timeout
        voted_users = set()

        def check(payload):
            # Ensure we are only tracking votes on THIS specific poll message
            if payload.message_id == poll_message.id:
                voted_users.add(payload.user_id)
            
            # Return True to break the 'wait_for' loop when we hit our max
            return len(voted_users) >= len(self.game.mgr_player.player_names)

        try:
            # interaction.client safely accesses your bot's event loop
            await interaction.client.wait_for('raw_poll_vote_add', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            # If 120s pass and we don't hit 3 voters, we just move on and finalize anyway
            pass

        # 3. Finalize and fetch results
        try:
            # Refresh to get the latest state
            poll_message = await interaction.channel.fetch_message(poll_message.id)
            
            if not poll_message.poll.is_finalised:
                # OPTIMIZATION: end_poll() actually returns the updated Message object,
                # saving you from needing an extra fetch_message call afterward!
                poll_message = await poll_message.end_poll()
                
        except discord.HTTPException:
            return ""

        # 4. Identify the "Yes" voters
        yes_voters = []
        
        yes_answer = discord.utils.get(poll_message.poll.answers, text="Yes")

        if yes_answer:
            async for user in yes_answer.voters():
                if not user.bot:
                    yes_voters.append(user.display_name)

        # 5. Random Selection
        if yes_voters:
            selected_gm = random.choice(yes_voters)
            await interaction.followup.send(f"👑 **{selected_gm}** has been randomly selected as the Game Master!")
            return selected_gm
        
        await interaction.followup.send("🪹 No one volunteered to be the Game Master.")
        return ""

    # Assuming this is inside your class
    async def run_execution_poll(self, interaction: discord.Interaction, allowed_player_ids: list[str]) -> Optional[discord.Message]:
        # 1. Validate Channel
        print("Enter")
        if not isinstance(interaction.channel, discord.TextChannel):
            error_msg = "This action requires a text channel."
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)
            return None

        # 2. Acknowledge the Command
        day_msg = f"Polling Day {self.game.counter.day}"
        print("Acknowledgeing")
        if interaction.response.is_done():
            await interaction.followup.send(day_msg, ephemeral=True)
        else:
            await interaction.response.send_message(day_msg, ephemeral=True)

        # 3. Setup the Thread and View
        print("Setting up thread")
        thread: discord.Thread = await interaction.channel.create_thread(
            name=f"Town Square Voting: (Day {self.game.counter.day}) 🏛️", 
            type=discord.ChannelType.public_thread
        )

        alive_players = self.game.get_players(filter_status={"alive": True})
        print("Got players", alive_players)
        view = ExecutionView(alive_players)
        print("Made view")

        embed = discord.Embed(
            title=f"Who should be executed? 🪢",
            description="Select a player from the dropdown menu below to cast your vote.\n*You may change your vote at any time before the timer runs out.*", 
            color=discord.Color.dark_red()
        )

        print("Sending Thred")
        poll_message: discord.Message = await thread.send(embed=embed, view=view)
        print("Send Poll A")

        # 4. Wait Loop (Polling approach)
        duration_minutes: int = 5
        num_players: int = len(allowed_player_ids)
        print("Wating A")
        
        # We convert duration to seconds. Range with step 5 acts as our check_interval.
        for _ in range(0, duration_minutes * 5, 5):
            # view.dropdown.votes tracks {user_identifier: chosen_target}
            voters = [u for u in view.dropdown.votes.keys() if u in allowed_player_ids]
            print("Inner A")
            if len(voters) >= num_players:
                print("Inner B")
                break
            await asyncio.sleep(5)

        print("Locking")
        # 5. Lock the Poll
        view.dropdown.disabled = True
        await poll_message.edit(view=view)

        # 6. Tally the Votes
        results = {"Skip Vote": 0}
        for player in alive_players:
            results[player.username] = 0
            
        total_valid_votes = 0
        
        for voter_id, chosen_target in view.dropdown.votes.items():
            if voter_id in allowed_player_ids and chosen_target in results:
                results[chosen_target] += 1
                total_valid_votes += 1

        # 7. Process the Results
        if total_valid_votes == 0:
            await thread.send("⚖️ No valid votes cast. No one executed.")
            return poll_message

        executed_target_name = None
        highest_vote_count = 0
        majority_threshold = total_valid_votes / 2.0

        for target_name, votes in results.items():
            if votes > highest_vote_count:
                highest_vote_count = votes
            # Strict majority check
            if votes > majority_threshold:
                executed_target_name = target_name

        # 8. Announce and Apply State Changes
        if executed_target_name is None:
            await thread.send(f"⚖️ No option received a majority (>50%). Highest was {highest_vote_count}/{total_valid_votes}. No execution.")
        elif executed_target_name == "Skip Vote":
            await thread.send(f"⚖️ The majority ({results['Skip Vote']}/{total_valid_votes}) chose to skip. No execution.")
        else:
            await thread.send(f"🩸 The town has spoken with {results[executed_target_name]}/{total_valid_votes} votes! **{executed_target_name}** is executed.")
            
            # Update the Game State
            try:
                p = self.game.get_player(executed_target_name)
                if p: 
                    p.status.alive = False
                self.game.mgr_day.executed_player = executed_target_name
            except ValueError:
                await thread.send("⚠️ Error: Could not find player data to update status.")

        print(self.game.get_board_str())
        return poll_message
