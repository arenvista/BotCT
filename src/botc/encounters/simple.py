'''
simple events- for testing so far
'''

from .base import Encounter,register_encounter,ENCOUNTER_MAP
from botc.enums import RoleClass,RoleName,Alignment
import discord
from .enums import *
import random

@register_encounter(NULL_EVENT_ENUM,[],[],'None','None')
class NullEncounter(Encounter):
    async def resolve(self,game,interaction: discord.Interaction):
        pass
    
@register_encounter(NULL_EVENT_CHILD_ENUM,[NULL_EVENT_ENUM],[],'None','None')
class NullEncounterChild(Encounter):
    async def resolve(self,game,interaction: discord.Interaction):
        pass
    
@register_encounter(NULL_EVENT_ANTI_CHILD_ENUM,[],[NULL_EVENT_ENUM],'None','None')
class NullEncounterAntiChild(Encounter):
    async def resolve(self,game,interaction: discord.Interaction):
        pass
    
@register_encounter(ONESHOT_EVENT_ENUM,[],[ONESHOT_EVENT_ENUM],'None','None')
class OneShotEncounter(Encounter):
    async def resolve(self,game,interaction: discord.Interaction):
        pass
    
@register_encounter(FLAVOR_TEXT_EVENT_ENUM,[],[],"Flavor","A crazy ecnounter just happened wow!!!")
class FlavorTextEncounter(Encounter):
    async def resolve(self, game,interaction: discord.Interaction):
        pass
    
@register_encounter(PACIFISM,[],[PACIFISM],"Pacifism",
                    "After too many years seeing the horrors of battle, the soldier has given up the way of the blade..."
                    )
class PacifismEncounter(Encounter):
        
    async def resolve(self,game,interaction: discord.Interaction):
        
        soldier=game.get_player_by_role(RoleName.SOLDIER)
        
        if soldier is not None:
            available_roles=RoleName.get_by_class(RoleClass.TOWNSFOLK)+RoleName.get_by_class(RoleClass.OUTSIDERS)

            for player in game.players:
                if player.registered_role in available_roles:
                    available_roles.remove(player.registered_role)

            if len(available_roles)>0:
                available_roles=available_roles[:3] #limit to 3 
                new_role_name=await game.command_cog.dmdropdown(soldier.player_name,"What shall this brave veteran's new occupation be?",[r.name for r in available_roles],1)
                new_role_name=new_role_name[0]
                #async def dmdropdown(self, user_name: str, message_text: str, dropdown_options: List[str], max_selection: int) -> Optional[List[str]]:
                for r in available_roles:
                    if r.name==new_role_name:
                        new_role=r
                        break
                
                soldier.registered_role=new_role
                soldier.believed_role=new_role
                
                await game.command_cog.send_direct_message(soldier.player_name,f"Your new job is {new_role.display_name}")
                
@register_encounter(PARTY,[],[],"Party Time!",
                    "The Townsfolk are throwing a party! Let's get totally sloshed!"
                    )
class PartyEncounter(Encounter):
    async def resolve(self,game,interaction: discord.Interaction):
        votes={
            
        }
        for player in game.players:
            chosen_player=await game.command_cog.dmdropdown(player.player_name,"Whos gonna get the most wasted?",[p.player_name for p in game.players])
            chosen_player=chosen_player[0]
            votes[chosen_player]=votes.get(chosen_player,0)+1
            
        most_popular_player=game.get_player_by_name(sorted([(v,k )for k,v in votes.items()],key=lambda x:x[0],reverse=True)[0][1])
        
        most_popular_player.status.poisoned =True
        
        drunk_player_list=random.sample(game.players,3)
        drunk_player_list.append(most_popular_player)
        
        for target in drunk_player_list:
            await game.command_cog.send_direct_message(target.player_name,f"You feel queasy and have a headache... hopefully you're not drunk")
            
        for player in game.players:
            if player not in drunk_player_list:
                await game.command_cog.send_direct_message(player.player_name,f"Someone got too drunk and poisoned themselves ")
            
            
@register_encounter(CHOSEN_ONE,[],[CHOSEN_ONE],
                    "The Gods have Chosen A Hero",
                    "Divine Might surges throughout the town... for a brief moment one brave soul is now protected from any infernal magic"
                    )
class ChosenEncounter(Encounter):
    async def resolve(self, game,interaction: discord.Interaction):
        votes={
            
        }
        for player in game.players:
            chosen_player=await game.command_cog.dmdropdown(player.player_name,"Who has curried the favor of the gods?",[p.player_name for p in game.players],1)
            chosen_player=chosen_player[0]
            votes[chosen_player]=votes.get(chosen_player,0)+1
            
        most_popular_player=game.get_player_by_name(sorted([(v,k )for k,v in votes.items()],key=lambda x:x[0],reverse=True)[0][1])
        most_popular_player.status.protected=True
        
        
        for player in game.players:
            if player ==most_popular_player:
                await game.command_cog.send_direct_message(player.player_name,f" Go forth, paladin of light, and vanquish evil! ")
            else:
                await game.command_cog.send_direct_message(player.player_name,f" The gods dont care for you. Stupid bitch. ")
                
@register_encounter(ANGRY_WIZARD,[WIZARD_COME],[HAPPY_WIZARD,ANGRY_WIZARD],"Angry Wizard",
                    "The old man is pissed at your hospitality! He unleashes his magical fury on the townsfolk, blasting fireballs left and right"
                    )
class AngryWizardEncounter(Encounter):
    async def resolve(self,game,interaction: discord.Interaction):
        for player in game.players:
            if player.registered_alignment==Alignment.GOOD:
                if random.random()<0.1 and not player.status.protected: #10% probability of getting murdered
                    player.alive=False
                    await game.command_cog.send_direct_message(player.player_name,f" Fireball straight to the torso. You burn alive and are now dead ")
                else:
                    await game.command_cog.send_direct_message(player.player_name,f" You narrowly escape immolation  ")
            else:
                await game.command_cog.send_direct_message(player.player_name,f" The wizard senses your malevolence, and spares you to enact further cruelty upon the town  ")
                    
        
@register_encounter(WIZARD_COME,[],[WIZARD_COME],
                    "A Mysterious Old Man Arrives",
                    "A strange, wizened old man has appeared ")
class WizardEncounter(Encounter):
    async def resolve(self,game,interaction: discord.Interaction):
        
        votes={
            WIZARD_YES:0,
            WIZARD_NO:0
        }
        for player in game.players:
            decision=await game.command_cog.dmdropdown(player.player_name,"Should we let in the wizard?",[WIZARD_YES,WIZARD_NO],1)
            decision=decision[0]
            votes[decision]+=1
            
        if votes[WIZARD_YES]>=votes[WIZARD_NO]:
            game.event_deck.remove_all_cards(ENCOUNTER_MAP[ANGRY_WIZARD])
            await interaction.channel.send("He reveals himself to be the Wizard Merlin, and is impressed by your friendliness")
        else:
            game.event_deck.remove_all_cards(ENCOUNTER_MAP[HAPPY_WIZARD])
            await interaction.channel.send("He reveals himself to be the Wizard Merlin, and is angered by your hostility")

        
@register_encounter(HAPPY_WIZARD,[WIZARD_COME],[HAPPY_WIZARD,ANGRY_WIZARD],
                    "The Wizard is Happy!",
                    "The Wizard appreciates your kindness, and he wants to warn you of danger in your midst"
                    )
class HappyWizardEncounter(Encounter):
    async def resolve(self,game,interaction: discord.Interaction):
        good_players=[gp for gp in game.players if gp.registered_alignment==Alignment.GOOD]
        evil_players=[ep for ep in game.players if ep.registered_alignment==Alignment.EVIL]
        
        pair=[random.choice(good_players),random.choice(evil_players)]
        if random.random()<0.5: #with 50% probability flip the order of good and evil
            pair=pair[::-1]
            
        target=random.choice(game.players)
        
        await game.command_cog.send_direct_message(target.player_name,f"The wizard warns you that he felt nefarious, infernal energy coming from on of {pair[0].player_name} or {pair[1].player_name}, but isnt sure which one")
            