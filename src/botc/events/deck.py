from .base import Event,update_possibilities
from typing import List
import random
    
class EventCard: #multiple event cards can correspond to the same event; 
    #that way different events can happen with different rarities
    #technically we COULD just adjust probabilities but representing as cards feels more intuitive
    def __init__(self,specific_event:Event):
        self.specific_event=specific_event
        
class Deck: #each game will have one instance of the deck class
    def __init__(self,event_list: List[Event],count_list:List[int]):
        
        self.unresolved_event_card_list=[]
        self.resolved_event_card_list=[]
        for event,count in zip(event_list,count_list):
            self.unresolved_event_card_list.extend([EventCard(event) for _ in range(count)])
        update_possibilities()
    
    
            
    
    def draw_card(self)-> EventCard:
        indices=[c for c,card in enumerate(self.unresolved_event_card_list) if (card.specific_event.parents_resolved and (card.specific_event.impossible==False))]
        index=random.choice(indices)
        card=self.unresolved_event_card_list.pop(index)
        card.specific_event.resolved=True
        self.resolved_event_card_list.append(card)
        update_possibilities()
        return card #actually resolving the card event will be done elsewhere
    
    def __str__(self):
        txt="Unresolved Card List: \n"
        unresolved_freq={}
        for card in self.unresolved_event_card_list:
            unresolved_freq[card.specific_event.name]=unresolved_freq.setdefault(card.specific_event.name,0)+1
        for k,v in unresolved_freq.items():
            txt+=f"{k}: {v}\n"
            
        txt+="Resolved Card List: \n"
        resolved_freq={}
        for card in self.resolved_event_card_list:
            resolved_freq[card.specific_event.name]=resolved_freq.setdefault(card.specific_event.name,0)+1
        for k,v in resolved_freq.items():
            txt+=f"{k}: {v}\n"
            
        return txt
    
    def __len__(self):
        return len(self.unresolved_event_card_list)+len(self.resolved_event_card_list)