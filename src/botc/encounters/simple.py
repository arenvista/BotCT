'''
simple events- for testing so far
'''

from .base import Encounter,register_encounter,ENCOUNTER_MAP
from botc.enums import RoleClass,RoleName,Alignment
from .enums import *
import random

@register_encounter(NULL_EVENT_ENUM,[],[],'None','None')
class NullEncounter(Encounter):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_encounter(NULL_EVENT_CHILD_ENUM,[NULL_EVENT_ENUM],[],'None','None')
class NullEncounterChild(Encounter):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_encounter(NULL_EVENT_ANTI_CHILD_ENUM,[],[NULL_EVENT_ENUM],'None','None')
class NullEncounterAntiChild(Encounter):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_encounter(ONESHOT_EVENT_ENUM,[],[ONESHOT_EVENT_ENUM],'None','None')
class OneShotEncounter(Encounter):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_encounter(FLAVOR_TEXT_EVENT_ENUM,[],[],"Flavor","A crazy ecnounter just happened wow!!!")
class FlavorTextEncounter(Encounter):
    async def resolve(self, *args, **kwargs):
        pass
    
@register_encounter(PACIFISM,[],[PACIFISM],"Pacifism",
                    "After too many years seeing the horrors of battle, the soldier has given up the way of the blade..."
                    )
class PacifismEncounter(Encounter):
        
    async def resolve(self,game, *args, **kwargs):
        
        soldier=game.get_player_by_role(RoleName.SOLDIER)
        
        if soldier is not None:
            available_roles=RoleName.get_by_class(RoleClass.OUTSIDERS)+RoleName.get_by_class(RoleClass.TOWNSFOLK)[:3] #limit to length 3
            for player in game.players:
                if player.actual_role in available_roles:
                    available_roles.remove(player.actual_role)
            if len(available_roles)>0:
                
                new_role_name=await game.command_cog.dmdropdown(soldier.player_name,"What shall this brave veteran's new occupation be?",[r.name for r in available_roles],1)
                #async def dmdropdown(self, user_name: str, message_text: str, dropdown_options: List[str], max_selection: int) -> Optional[List[str]]:
                for r in available_roles:
                    if r.name==new_role_name:
                        new_role=r
                        break
                
                soldier.actual_role=new_role
                soldier.registered_role=new_role
                soldier.believed_role=new_role
                
                game.command_cog.send_direct_message(soldier.player_name,f"Your new job is {new_role.display_name}")
                
@register_encounter(PARTY,[],[],"Party Time!",
                    "The Townsfolk are throwing a party! Let's get totally sloshed!"
                    )
class PartyEncounter(Encounter):
    async def resolve(self,game, *args, **kwargs):
        votes={
            
        }
        for player in game.players:
            chosen_player=await game.command_cog.dmdropdown(player.player_name,"Whos gonna get the most wasted?",[p.player_name for p in game.players])
            votes[chosen_player.player_name]=votes.get(chosen_player,0)+1
            
        most_popular_player=game.get_player_by_name(sorted([(v,k )for k,v in votes.items()],key=lambda x:x[0],reverse=True)[0][1])
        
        most_popular_player.poisoned =True
        
        drunk_player_list=random.sample(game.players,3)
        drunk_player_list.append(most_popular_player)
        
        for target in drunk_player_list:
            game.command_cog.send_direct_message(target.player_name,f"You feel queasy and have a headache... hopefully you're not drunk")
            
        for player in game.players:
            if player not in drunk_player_list:
                game.command_cog.send_direct_message(player.player_name,f"Someone got too drunk and poisoned themselves ")
            
            
@register_encounter(CHOSEN_ONE,[],[CHOSEN_ONE],
                    "The Gods have Chosen A Hero",
                    "Divine Might surges throughout the town... for a brief moment one brave soul is now protected from any infernal magic"
                    )
class ChosenEncounter(Encounter):
    async def resolve(self, game,*args, **kwargs):
        votes={
            
        }
        for player in game.players:
            chosen_player=await game.command_cog.dmdropdown(player.player_name,"Who has curried the favor of the gods?",[p.player_name for p in game.players])
            votes[chosen_player.player_name]=votes.get(chosen_player,0)+1
            
        most_popular_player=game.get_player_by_name(sorted([(v,k )for k,v in votes.items()],key=lambda x:x[0],reverse=True)[0][1])
        most_popular_player.protected=True
        
        for player in game.players:
            if player ==most_popular_player:
                game.command_cog.send_direct_message(player.player_name,f" Go forth, paladin of light, and vanquish evil! ")
            else:
                game.command_cog.send_direct_message(player.player_name,f" The gods dont care for you. Stupid bitch. ")
                
@register_encounter(ANGRY_WIZARD,[ANGRY_WIZARD,WIZARD_COME],[HAPPY_WIZARD],"Angry Wizard",
                    "The old man is pissed at your hospitality! He unleashes his magical fury on the townsfolk, blasting fireballs left and right"
                    )
class AngryWizardEncounter(Encounter):
    async def resolve(game,*args, **kwargs):
        for player in game.players:
            if player.registered_alignment==Alignment.GOOD:
                if random.random()<0.1 and not player.protected: #10% probability of getting murdered
                    player.alive=False
                    game.command_cog.send_direct_message(player.player_name,f" Fireball straight to the torso. You burn alive and are now dead ")
                else:
                    game.command_cog.send_direct_message(player.player_name,f" You narrowly escape immolation  ")
            else:
                game.command_cog.send_direct_message(player.player_name,f" The wizard senses your malevolence, and spares you to enact further cruelty upon the town  ")
                    
        
@register_encounter(WIZARD_COME,[],[WIZARD_COME],
                    "A Mysterious Old Man Arrives",
                    "A strange, wizened old man has appeared ")