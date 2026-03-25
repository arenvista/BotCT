'''
simple events- for testing so far
'''

from .base import Event,register_event,EVENT_MAP
from .enums import *

@register_event(NULL_EVENT_ENUM,[],[])
class NullEvent(Event):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_event(NULL_EVENT_CHILD_ENUM,[NULL_EVENT_ENUM],[])
class NullEventChild(Event):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_event(NULL_EVENT_ANTI_CHILD_ENUM,[],[NULL_EVENT_ENUM])
class NullEventAntiChild(Event):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_event(ONESHOT_EVENT_ENUM,[],[ONESHOT_EVENT_ENUM])
class OneShotEvent(Event):
    async def resolve(self,*args,**kwargs):
        pass
    
@register_event(FLAVOR_TEXT_EVENT_ENUM,[],[])
class FlavorTextEvent(Event):
    def __init__(self, name, dependency_names, anti_dependency_names):
        super().__init__(name, dependency_names, anti_dependency_names)
        self.flavor_text="A crazy event just happened wow!!!"
    async def resolve(self, *args, **kwargs):
        return self.flavor_text