import botc.encounters
from botc.encounters import simple,deck,ENCOUNTER_MAP,Deck
from botc.encounters.enums import *
from botc.encounters.base import reset_resolved
from botc.core.game import GameManager
from botc.behaviors.base import RoleBehavior
from botc.behaviors import BEHAVIOR_MAP
from botc.enums import Status,Alignment,RoleClass,RoleName
from types import SimpleNamespace
from unittest.mock import AsyncMock
from botc.discord_manager import PollManager
from botc.player import Player
from botc.discord_manager.cogs.game_commands import GameCommands
import discord
import os
import pytest



def test_encounter_map():
    assert len(ENCOUNTER_MAP) !=0
    values=[v for v in ENCOUNTER_MAP.values()]
    assert values[0]!=values[1]
    
def test_deck():
    n0=10
    n1=5
    my_deck=deck.Deck([ENCOUNTER_MAP[s] for s in [simple.NULL_EVENT_ENUM,simple.NULL_EVENT_CHILD_ENUM]],[n0,n1])
    
    assert len(my_deck)==n0+n1
    assert len(my_deck.unresolved_encounter_card_list)==n0+n1
    card=my_deck.draw_card()
    assert card.specific_encounter.name != simple.NULL_EVENT_CHILD_ENUM
    assert len(my_deck)==n0+n1
    assert len(my_deck.resolved_encounter_card_list)==1
    assert len(my_deck.unresolved_encounter_card_list)==n0+n1-1
    
    reset_resolved()
    my_deck=deck.Deck([ENCOUNTER_MAP[simple.NULL_EVENT_ENUM],ENCOUNTER_MAP[simple.NULL_EVENT_CHILD_ENUM]],[1,100])
    card=my_deck.draw_card()
    assert card.specific_encounter.name != simple.NULL_EVENT_CHILD_ENUM
    card=my_deck.draw_card()
    assert card.specific_encounter.name == simple.NULL_EVENT_CHILD_ENUM
    
    reset_resolved()
    ENCOUNTER_MAP[simple.NULL_EVENT_ENUM].resolved=True
    my_deck=deck.Deck([ENCOUNTER_MAP[simple.NULL_EVENT_ANTI_CHILD_ENUM]],[10])
    
    with pytest.raises(IndexError):
        card=my_deck.draw_card()
        
    reset_resolved()
    my_deck=deck.Deck([ENCOUNTER_MAP[simple.ONESHOT_EVENT_ENUM]],[10])
    card=my_deck.draw_card()
    with pytest.raises(IndexError):
        card=my_deck.draw_card()    
        
def test_deck_from_json():
    d=Deck.from_json("default.json")
    d.draw_card()
    
@pytest.fixture
def async_pair(monkeypatch):
    interaction=SimpleNamespace(
        response=SimpleNamespace(send_message=AsyncMock(),is_done=AsyncMock(True)),
        channel=SimpleNamespace(send=AsyncMock())
    )
    
    os.environ["ENCOUNTER"]="1"
    
    
    async def mock_nothing(*args,**kwargs):
        return
    
    for v in BEHAVIOR_MAP.values():
        monkeypatch.setattr(v,"act",mock_nothing) #act is an abstract method so we have to monkey patch each individual subclass
    monkeypatch.setattr(PollManager,"run_execution_poll",mock_nothing)
    
    #monkeypatch.setattr(GameCommands,"send_direct_message",mock_nothing)
    
    def get_mock_resolve_temporary_conditions(counter):
        def _mock_resolve_temporary_conditions(self): #mocking this to eventually end the game after n turns
            for player in self.players:
                player.status.protected=False
                player.status.poisoned=False
            if self.night_counter>=counter:
                self.game_over=True
        return _mock_resolve_temporary_conditions
    
    return interaction,get_mock_resolve_temporary_conditions

@pytest.mark.asyncio
async def test_wizard_happy(async_pair,monkeypatch):
    interaction,get_mock_resolve_temporary_conditions=async_pair
    
    monkeypatch.setattr(GameManager,"resolve_temporary_conditions",get_mock_resolve_temporary_conditions(2)) #how many nights we're doing this for
    
    players=[Player(f"p_{n}",RoleName.WASHERWOMAN,RoleName.WASHERWOMAN,Alignment.GOOD) for n in range(5)]
    players.append(Player("soldier",RoleName.SOLDIER,RoleName.SOLDIER,Alignment.GOOD))
    players.append(Player("demon",RoleName.IMP,RoleName.IMP,Alignment.EVIL))
    
    game=GameManager([p.player_name for p in players])
    monkeypatch.setattr(game, "assign_roles",lambda *args: players)
    
    game.event_deck=Deck([ENCOUNTER_MAP[WIZARD_COME],ENCOUNTER_MAP[HAPPY_WIZARD], ENCOUNTER_MAP[ANGRY_WIZARD]],[1,1,1])
    
    monkeypatch.setattr(game.command_cog,"dmdropdown",AsyncMock(side_effect=lambda *args: [WIZARD_YES]))
    
    message_queue=[]
    async def mock_direct_message(user_name: str, message: str):
        nonlocal message_queue
        message_queue.append([user_name,message])
        return True
    
    monkeypatch.setattr(game.command_cog,"send_direct_message",mock_direct_message)
    
    await game.start_game(interaction)
    
    last_message=message_queue[-1][-1]
    
    assert "demon" in last_message
    
@pytest.mark.asyncio
async def test_wizard_angry(async_pair,monkeypatch):
    interaction,get_mock_resolve_temporary_conditions=async_pair
    monkeypatch.setattr(GameManager,"resolve_temporary_conditions",get_mock_resolve_temporary_conditions(2)) #how many nights we're doing this for
    
    players=[Player(f"p_{n}",RoleName.WASHERWOMAN,RoleName.WASHERWOMAN,Alignment.GOOD) for n in range(5)]
    players.append(Player("soldier",RoleName.SOLDIER,RoleName.SOLDIER,Alignment.GOOD))
    players.append(Player("demon",RoleName.IMP,RoleName.IMP,Alignment.EVIL))
    
    game=GameManager([p.player_name for p in players])
    monkeypatch.setattr(game, "assign_roles",lambda *args: players)
    
    game.event_deck=Deck([ENCOUNTER_MAP[WIZARD_COME],ENCOUNTER_MAP[HAPPY_WIZARD], ENCOUNTER_MAP[ANGRY_WIZARD]],[1,1,1])
    
    monkeypatch.setattr(game.command_cog,"dmdropdown",AsyncMock(side_effect=lambda *args: [WIZARD_NO]))
    
    message_queue=[]
    async def mock_direct_message(user_name: str, message: str):
        nonlocal message_queue
        message_queue.append([user_name,message])
        return True
    
    monkeypatch.setattr(game.command_cog,"send_direct_message",mock_direct_message)
    
    await game.start_game(interaction)
    
    for [name,message] in message_queue[::-1]:
        if name =="demon":
            assert message.find("he wizard senses your malevolence")!=-1
            break
        
@pytest.mark.asyncio
async def test_chosen(async_pair,monkeypatch):
    interaction,get_mock_resolve_temporary_conditions=async_pair
    
    
    monkeypatch.setattr(GameManager,"resolve_temporary_conditions",get_mock_resolve_temporary_conditions(1)) #how many nights we're doing this for
    
    players=[Player(f"p_{n}",RoleName.WASHERWOMAN,RoleName.WASHERWOMAN,Alignment.GOOD) for n in range(5)]
    game=GameManager([p.player_name for p in players])
    monkeypatch.setattr(game, "assign_roles",lambda *args: players)
    monkeypatch.setattr(game.command_cog,"dmdropdown",AsyncMock(side_effect=lambda *args: ["p_0"]))
    
    message_queue=[]
    async def mock_direct_message(user_name: str, message: str):
        nonlocal message_queue
        message_queue.append([user_name,message])
        return True
    
    monkeypatch.setattr(game.command_cog,"send_direct_message",mock_direct_message)
    game.event_deck=Deck([ENCOUNTER_MAP[CHOSEN_ONE]],[10])
    
    await game.start_game(interaction)
    assert game.players[0].status.protected==True
    
@pytest.mark.asyncio
async def test_pacifism(async_pair,monkeypatch):
    interaction,get_mock_resolve_temporary_conditions=async_pair
    monkeypatch.setattr(GameManager,"resolve_temporary_conditions",get_mock_resolve_temporary_conditions(3)) #how many nights we're doing this for
    players=[Player(f"p_{n}",RoleName.WASHERWOMAN,RoleName.WASHERWOMAN,Alignment.GOOD) for n in range(5)]
    players.append(Player("soldier",RoleName.SOLDIER,RoleName.SOLDIER,Alignment.GOOD))
    monkeypatch.setattr(GameManager, "assign_roles",lambda *args: players)

    game=GameManager([p.player_name for p in players])

    
    message_queue=[]
    async def mock_direct_message(user_name: str, message: str):
        nonlocal message_queue
        message_queue.append([user_name,message])
        return True
    
    monkeypatch.setattr(game.command_cog,"send_direct_message",mock_direct_message)
    
    monkeypatch.setattr(game.command_cog,"dmdropdown",AsyncMock(side_effect=lambda *args: [RoleName.CHEF.name]))
    game.event_deck=Deck([ENCOUNTER_MAP[PACIFISM]],[10])
    await game.start_game(interaction)
    
    for player in game.players:
        assert player.registered_role.name!=RoleName.SOLDIER