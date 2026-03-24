from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from PIL import Image
import random

EVENT_MAP={}


def register_event(event_name,dependency_names,anti_dependency_names):
    #assigns name to event and adds it to event map dictionary
    def decorator(cls):
        event_object=cls(event_name,dependency_names,anti_dependency_names)
        EVENT_MAP[event_name] = event_object
        return cls
    return decorator

class Event(ABC):
    
    
    
    
    def __init__(self,name:str,dependency_names:List[str],anti_dependency_names:List[str]):
        super().__init__()
        self.dependency_names=dependency_names
        self.anti_dependency_names=anti_dependency_names
        self.name=name
        self.dependencies: List[Event]=[] #these events need to resolve to make this event possible
        self.anti_dependencies: List[Event]=[] #if any of these events resolve, then this event becomes impossible
        self.impossible:bool =False #an event becomes impossible if any of its anti depndencies resolve
        self.parents_resolved: bool =False #an event is marked possible if all of its dependencies have resolved
        #impossible always takes precedence over impossible
        self.resolved:bool=False #an event that has happened has resolved
        self.flavor_text:str=""
        self.image: Image.Image=None #image to render to depict event (low priority)
        
    
    @abstractmethod
    async def resolve(self,*args,**kwargs)->None: #async because we might want to use polling and shit
        pass
    
    def __str__(self):
        return f"{self.name} {self.parents_resolved} {self.impossible}"

def update_possibilities():
    for key,event in EVENT_MAP.items():
        impossible_flag=True
        for parent_event in  event.anti_dependencies:
            if not parent_event.resolved:
                impossible_flag=False
                break
        if len(event.anti_dependencies)==0:
            impossible_flag=False

        event.impossible=impossible_flag
        
        parents_resolved_flag=True
        for parent_event in event.dependencies:
            if not parent_event.resolved:
                parents_resolved_flag=False
                break

        event.parents_resolved=parents_resolved_flag
        
def reset_resolved():
    #probably only used for testing...
    for key,event in EVENT_MAP.items():
        event.impossible=False
        event.parents_resolved=False
        event.resolved=False