import botc.events
from botc.events import simple,deck,EVENT_MAP,Deck
from botc.events.base import reset_resolved
import pytest



def test_event_map():
    assert len(EVENT_MAP) !=0
    values=[v for v in EVENT_MAP.values()]
    assert values[0]!=values[1]
    
def test_deck():
    n0=10
    n1=5
    my_deck=deck.Deck([EVENT_MAP[s] for s in [simple.NULL_EVENT_ENUM,simple.NULL_EVENT_CHILD_ENUM]],[n0,n1])
    
    assert len(my_deck)==n0+n1
    assert len(my_deck.unresolved_event_card_list)==n0+n1
    card=my_deck.draw_card()
    assert card.specific_event.name != simple.NULL_EVENT_CHILD_ENUM
    assert len(my_deck)==n0+n1
    assert len(my_deck.resolved_event_card_list)==1
    assert len(my_deck.unresolved_event_card_list)==n0+n1-1
    
    reset_resolved()
    my_deck=deck.Deck([EVENT_MAP[simple.NULL_EVENT_ENUM],EVENT_MAP[simple.NULL_EVENT_CHILD_ENUM]],[1,100])
    card=my_deck.draw_card()
    assert card.specific_event.name != simple.NULL_EVENT_CHILD_ENUM
    card=my_deck.draw_card()
    assert card.specific_event.name == simple.NULL_EVENT_CHILD_ENUM
    
    reset_resolved()
    EVENT_MAP[simple.NULL_EVENT_ENUM].resolved=True
    my_deck=deck.Deck([EVENT_MAP[simple.NULL_EVENT_ANTI_CHILD_ENUM]],[10])
    
    with pytest.raises(IndexError):
        card=my_deck.draw_card()
        
    reset_resolved()
    my_deck=deck.Deck([EVENT_MAP[simple.ONESHOT_EVENT_ENUM]],[10])
    card=my_deck.draw_card()
    with pytest.raises(IndexError):
        card=my_deck.draw_card()    
        
def test_deck_from_json():
    d=Deck.from_json("default.json")
    d.draw_card()