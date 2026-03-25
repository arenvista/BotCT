'''
simple events- for testing so far
'''

from .base import Event,register_event,EVENT_MAP

NULL_EVENT_ENUM="null_event"
NULL_EVENT_CHILD_ENUM="null_event_child"
NULL_EVENT_ANTI_CHILD_ENUM="null_event_anti_child"
ONESHOT_EVENT_ENUM="oneshot_event"

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