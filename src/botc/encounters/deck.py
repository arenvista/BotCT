from .base import Encounter,update_possibilities,ENCOUNTER_MAP
from typing import List
import random
import json
from importlib import resources
    
class EncounterCard: #multiple encounter cards can correspond to the same encounter; 
    #that way different encounters can happen with different rarities
    #technically we COULD just adjust probabilities but representing as cards feels more intuitive
    def __init__(self,specific_encounter:Encounter):
        self.specific_encounter=specific_encounter
        
class Deck: #each game will have one instance of the deck class
    
    @classmethod
    def from_json(cls,json_file_name):
        if not json_file_name.endswith(".json"):
            json_file_name+=".json"
        with resources.files("botc.decklists").joinpath(json_file_name).open("r") as f:
            json_object=json.load(f)
            count_list=json_object["count_list"]
            encounter_name_list=json_object["encounter_name_list"]
        return cls(
            [ENCOUNTER_MAP[n] for n in encounter_name_list],
            [c for c in count_list]
        )
            
        
    def __init__(self,encounter_list: List[Encounter],count_list:List[int]):
        
        self.unresolved_encounter_card_list:List[EncounterCard]=[]
        self.resolved_encounter_card_list:List[EncounterCard]=[]
        for encounter,count in zip(encounter_list,count_list):
            self.unresolved_encounter_card_list.extend([EncounterCard(encounter) for _ in range(count)])
        update_possibilities()
    
    
            
    
    def draw_card(self)-> EncounterCard:
        indices=[c for c,card in enumerate(self.unresolved_encounter_card_list) if (card.specific_encounter.parents_resolved and (card.specific_encounter.impossible==False))]
        index=random.choice(indices)
        card=self.unresolved_encounter_card_list.pop(index)
        card.specific_encounter.resolved=True
        self.resolved_encounter_card_list.append(card)
        update_possibilities()
        return card #actually resolving the card encounter will be done elsewhere
    
    def __str__(self):
        txt="Unresolved Card List: \n"
        unresolved_freq={}
        for card in self.unresolved_encounter_card_list:
            unresolved_freq[card.specific_encounter.name]=unresolved_freq.setdefault(card.specific_encounter.name,0)+1
        for k,v in unresolved_freq.items():
            txt+=f"{k}: {v}\n"
            
        txt+="Resolved Card List: \n"
        resolved_freq={}
        for card in self.resolved_encounter_card_list:
            resolved_freq[card.specific_encounter.name]=resolved_freq.setdefault(card.specific_encounter.name,0)+1
        for k,v in resolved_freq.items():
            txt+=f"{k}: {v}\n"
            
        return txt
    
    def __len__(self):
        return len(self.unresolved_encounter_card_list)+len(self.resolved_encounter_card_list)
    
    def __bool__(self):
        
        if len(self.unresolved_encounter_card_list)==0:
            return False
        
        for card in self.unresolved_encounter_card_list:
            if card.specific_encounter:
                return True
            
        return False