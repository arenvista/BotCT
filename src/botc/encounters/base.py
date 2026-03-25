from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from PIL import Image
import random

ENCOUNTER_MAP={}


def register_encounter(encounter_name,dependency_names,anti_dependency_names):
    #assigns name to encounter and adds it to encounter map dictionary
    def decorator(cls):
        encounter_object=cls(encounter_name,dependency_names,anti_dependency_names)
        ENCOUNTER_MAP[encounter_name] = encounter_object
        return cls
    return decorator

class Encounter(ABC):
    
    
    
    
    def __init__(self,name:str,dependency_names:List[str],anti_dependency_names:List[str]):
        super().__init__()
        self.dependency_names=dependency_names
        self.anti_dependency_names=anti_dependency_names
        self.name=name
        self.dependencies: List[Encounter]=[] #these encounters need to resolve to make this encounter possible
        self.anti_dependencies: List[Encounter]=[] #if any of these encounters resolve, then this encounter becomes impossible
        self.impossible:bool =False #an encounter becomes impossible if any of its anti depndencies resolve
        self.parents_resolved: bool =False #an encounter is marked possible if all of its dependencies have resolved
        #impossible always takes precedence over impossible
        self.resolved:bool=False #an encounter that has happened has resolved
        self.flavor_text:str=""
        self.image: Image.Image=None #image to render to depict encounter (low priority)
        
    
    @abstractmethod
    async def resolve(self,*args,**kwargs)->None: #async because we might want to use polling and shit
        pass
    
    def __str__(self):
        return f"{self.name} {self.parents_resolved} {self.impossible}"
    
    def __bool__(self):
        return self.parents_resolved and not self.impossible


def update_possibilities():
    for key,encounter in ENCOUNTER_MAP.items():
        impossible_flag=True
        for parent_encounter in  encounter.anti_dependencies:
            if not parent_encounter.resolved:
                impossible_flag=False
                break
        if len(encounter.anti_dependencies)==0:
            impossible_flag=False

        encounter.impossible=impossible_flag
        
        parents_resolved_flag=True
        for parent_encounter in encounter.dependencies:
            if not parent_encounter.resolved:
                parents_resolved_flag=False
                break

        encounter.parents_resolved=parents_resolved_flag
        
def reset_resolved():
    #probably only used for testing...
    for key,encounter in ENCOUNTER_MAP.items():
        encounter.impossible=False
        encounter.parents_resolved=False
        encounter.resolved=False