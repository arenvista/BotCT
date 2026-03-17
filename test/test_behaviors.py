# tests/test_behaviors.py
import pytest
from botc.game import GameManager
from botc.enums import RoleName, Alignment

@pytest.fixture
def custom_game():
    """A pytest fixture that creates a blank 5-player game we can manipulate."""
    return GameManager(["Alice", "Bob", "Charlie", "David", "Eve"])

def test_empath_behavior(custom_game, capsys):
    """Test that the Empath reads the correct number of evil neighbors."""
    # Force the roles to create a specific scenario:
    # Alice (Evil) - Bob (Good Empath) - Charlie (Evil) - David (Good) - Eve (Good)
    
    custom_game.players[0].registered_alignment = Alignment.EVIL   # Alice (Left)
    custom_game.players[1].actual_role = RoleName.EMPATH           # Bob (Empath)
    custom_game.players[1].believed_role = RoleName.EMPATH
    custom_game.players[1].registered_alignment = Alignment.GOOD
    custom_game.players[2].registered_alignment = Alignment.EVIL   # Charlie (Right)
    
    # Trigger the empath's action
    empath_player = custom_game.players[1]
    empath_player.role_behavior.act(empath_player, custom_game)
    
    # Capture the print output using pytest's built-in capsys fixture
    captured = capsys.readouterr()
    
    # The empath should see 2 evil neighbors
    assert "Show them 2 fingers" in captured.out
    assert "Alice, Charlie" in captured.out

def test_monk_protection(custom_game, monkeypatch):
    """Test that the Monk successfully protects a player."""
    monk = custom_game.players[0]
    monk.actual_role = RoleName.MONK
    monk.believed_role = RoleName.MONK
    
    target = custom_game.players[1]
    target.player_name = "Bob"
    
    # Mock the Python input() function so it automatically types "Bob" when prompted
    monkeypatch.setattr('builtins.input', lambda _: "Bob")
    
    assert target.protected is False
    monk.role_behavior.act(monk, custom_game)
    assert target.protected is True
