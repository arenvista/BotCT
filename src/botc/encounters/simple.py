'''
simple events- for testing so far
'''

from .base import Encounter,register_encounter,ENCOUNTER_MAP
from .enums import *

@register_encounter(NULL_EVENT_ENUM,[],[])
class NullEncounter(Encounter):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_encounter(NULL_EVENT_CHILD_ENUM,[NULL_EVENT_ENUM],[])
class NullEncounterChild(Encounter):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_encounter(NULL_EVENT_ANTI_CHILD_ENUM,[],[NULL_EVENT_ENUM])
class NullEncounterAntiChild(Encounter):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_encounter(ONESHOT_EVENT_ENUM,[],[ONESHOT_EVENT_ENUM])
class OneShotEncounter(Encounter):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_encounter(FLAVOR_TEXT_EVENT_ENUM,[],[])
class FlavorTextEncounter(Encounter):
    def __init__(self, name, dependency_names, anti_dependency_names):
        super().__init__(name, dependency_names, anti_dependency_names)
        self.flavor_text="A crazy ecnounter just happened wow!!!"
    async def resolve(self, *args, **kwargs):
        return self.flavor_text