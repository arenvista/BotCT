# tests/test_game.py
import pytest
from botc.game import RoleDistributor, GameManager
from botc.enums import RoleName, Alignment

def test_role_distribution_math():
    """Test that the math for role distributions is correct."""
    # 5 players: 1 Demon, 0 Outsiders, 3 Townsfolk, 1 Minion
    dist_5 = RoleDistributor(["P1", "P2", "P3", "P4", "P5"])
    assert dist_5.num_demons == 1
    assert dist_5.num_outsiders == 0
    assert dist_5.num_townsfolk == 3
    assert dist_5.num_minions == 1

    # 15 players: 1 Demon, 2 Outsiders, 9 Townsfolk, 3 Minions
    dist_15 = RoleDistributor([f"P{i}" for i in range(15)])
    assert dist_15.num_demons == 1
    assert dist_15.num_outsiders == 2
    assert dist_15.num_townsfolk == 9
    assert dist_15.num_minions == 3

def test_game_initialization():
    """Test that the game initializes with the correct number of players and default states."""
    players = ["Alice", "Bob", "Charlie", "David", "Eve"]
    game = GameManager(players)
    
    assert len(game.players) == 5
    assert game.turn_counter == 0
    
    # Check that alignment defaults worked
    evil_count = sum(1 for p in game.players if p.registered_alignment == Alignment.EVIL)
    assert evil_count == 2 # 1 Demon + 1 Minion in a 5 player game

def test_get_alive_neighbors():
    """Test the neighbor logic, especially skipping dead players."""
    game = GameManager(["P1", "P2", "P3", "P4", "P5"])
    
    # Kill P2 and P4
    game.players[1].alive = False
    game.players[3].alive = False
    
    # The neighbors of P3 should now be P1 and P5 (skipping the dead ones)
    left, right = game.get_alive_neighbors(game.players[2])
    
    assert left.player_name == "P1"
    assert right.player_name == "P5"
