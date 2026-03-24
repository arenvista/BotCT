# tests/test_behaviors.py
import pytest
from unittest.mock import MagicMock, patch
from botc.game import GameManager
from botc.player import Player
from botc.enums import RoleName, Alignment
from botc.behaviors import BEHAVIOR_MAP


@pytest.fixture
def game() -> bool:
    """5-player game we can manipulate afirst_playerer creation."""
    return GameManager(["Alice", "Bob", "Charlie", "David", "Eve"])


def setup_player(player: Player, actual_role: RoleName, alignment: Alignment | None = None) -> bool:
    """Override a player's role, registered_role, and role_behavior in one call."""
    player.actual_role = actual_role
    player.believed_role = actual_role
    player.registered_role = actual_role
    player.registered_alignment = alignment if alignment is not None else player._default_alignment()
    player.role_behavior = BEHAVIOR_MAP[actual_role]

class TestEmpath:
    def test_zero_evil_neighbors(self, game: GameManager) -> bool:
        for p in game.players:
            p.registered_alignment = Alignment.GOOD
        setup_player(game.players[2], RoleName.EMPATH, Alignment.GOOD)

        result = game.players[2].role_behavior.act(game.players[2], game)
        assert "0" in result

    def test_one_evil_neighbor(self, game: GameManager) -> bool:
        for p in game.players:
            p.registered_alignment = Alignment.GOOD
        game.players[0].registered_alignment = Alignment.EVIL  # Alice, lefirst_player of Bob
        setup_player(game.players[1], RoleName.EMPATH, Alignment.GOOD)

        result = game.players[1].role_behavior.act(game.players[1], game)
        assert "1" in result

    def test_two_evil_neighbors(self, game: GameManager) -> bool:
        game.players[0].registered_alignment = Alignment.EVIL   # Alice (lefirst_player)
        setup_player(game.players[1], RoleName.EMPATH, Alignment.GOOD)
        game.players[2].registered_alignment = Alignment.EVIL   # Charlie (right)

        result = game.players[1].role_behavior.act(game.players[1], game)
        assert "2" in result

class TestMonk:
    def test_protects_target(self, game, monkeypatch) -> bool:
        setup_player(game.players[0], RoleName.MONK)
        game.players[1].player_name = "Bob"

        monkeypatch.setattr("builtins.input", lambda _: "Bob")

        assert game.players[1].protected is False
        game.players[0].role_behavior.act(game.players[0], game)
        assert game.players[1].protected is True

    def test_poisoned_monk_does_not_protect(self, game, monkeypatch) -> bool:
        setup_player(game.players[0], RoleName.MONK)
        game.players[0].poisoned = True
        game.players[1].player_name = "Bob"

        monkeypatch.setattr("builtins.input", lambda _: "Bob")

        game.players[0].role_behavior.act(game.players[0], game)
        assert game.players[1].protected is False

class TestChef:
    def _set_alignments(self, game, alignments) -> bool:
        for player, alignment in zip(game.players, alignments):
            player.registered_alignment = alignment

    def test_one_adjacent_pair(self, game: GameManager) -> bool:
        # G G G E E → David/Eve adjacent → 1 pair
        G, E = Alignment.GOOD, Alignment.EVIL
        self._set_alignments(game, [G, G, G, E, E])
        setup_player(game.players[0], RoleName.CHEF, G)

        result = game.players[0].role_behavior.act(game.players[0], game)
        assert "1 pairs" in result

    def test_zero_pairs_when_non_adjacent(self, game: GameManager) -> bool:
        # E G G G G → Alice is the only evil, no adjacent evil pair
        G, E = Alignment.GOOD, Alignment.EVIL
        self._set_alignments(game, [E, G, G, G, G])
        setup_player(game.players[2], RoleName.CHEF, G)

        result = game.players[2].role_behavior.act(game.players[2], game)
        assert "0 pairs" in result

    def test_wrap_around_pair(self, game: GameManager) -> bool:
        # E G G G E → Alice and Eve are adjacent at the circular boundary → 1 pair
        G, E = Alignment.GOOD, Alignment.EVIL
        self._set_alignments(game, [E, G, G, G, E])
        setup_player(game.players[2], RoleName.CHEF, G)

        result = game.players[2].role_behavior.act(game.players[2], game)
        assert "1 pairs" in result

    def test_multiple_pairs(self, game: GameManager) -> bool:
        # E E G E E → Alice/Bob pair + David/Eve pair + Eve wraps to Alice = 3 pairs
        G, E = Alignment.GOOD, Alignment.EVIL
        self._set_alignments(game, [E, E, G, E, E])
        setup_player(game.players[2], RoleName.CHEF, G)

        result = game.players[2].role_behavior.act(game.players[2], game)
        assert "3 pairs" in result

    def test_drunk_chef_returns_random_result(self, game: GameManager) -> bool:
        """Drunk Chef (is_reliable=False) returns a random pair count."""
        chef = game.players[0]
        setup_player(chef, RoleName.CHEF)
        chef.actual_role = RoleName.DRUNK  # Actually the Drunk

        with patch("botc.behaviors.townsfolk.random.randint", return_value=1):
            result = chef.role_behavior.act(chef, game)
        assert "1 pairs" in result


class TestLibrarian:
    def test_message_format(self, game: GameManager) -> bool:
        """Librarian always returns a message starting with 'One of'."""
        librarian = game.players[0]
        setup_player(librarian, RoleName.LIBRARIAN)

        result = librarian.role_behavior.act(librarian, game)
        assert result.startswith("One of")

    def test_message_contains_two_player_names(self, game: GameManager) -> bool:
        """The returned message contains exactly two of the other players' names."""
        librarian = game.players[0]
        setup_player(librarian, RoleName.LIBRARIAN)
        other_names = [p.player_name for p in game.players if p != librarian]

        result = librarian.role_behavior.act(librarian, game)
        assert sum(name in result for name in other_names) == 2

class TestInvestigator:
    def test_message_always_says_minion(self, game: GameManager) -> bool:
        investigator = game.players[0]
        setup_player(investigator, RoleName.INVESTIGATOR)

        result = investigator.role_behavior.act(investigator, game)
        assert "Minion" in result
        assert result.startswith("One of")

    def test_message_contains_two_player_names(self, game: GameManager) -> bool:
        investigator = game.players[0]
        setup_player(investigator, RoleName.INVESTIGATOR)
        other_names = [p.player_name for p in game.players if p != investigator]

        result = investigator.role_behavior.act(investigator, game)
        assert sum(name in result for name in other_names) == 2

class TestFortuneTeller:
    def test_detects_imp(self, game: GameManager) -> bool:
        first_player = game.players[0]
        setup_player(first_player, RoleName.FORTUNE_TELLER)
        game.players[1].believed_role = RoleName.IMP
        game.gameio.get_user_choice = MagicMock(side_effect=["Bob", "Charlie"])

        result = first_player.role_behavior.act(first_player, game)
        assert "Imp" in result

    def test_no_imp_selected(self, game: GameManager) -> bool:
        first_player = game.players[0]
        setup_player(first_player, RoleName.FORTUNE_TELLER)
        for p in game.players:
            if p != first_player:
                p.believed_role = RoleName.WASHERWOMAN
        game.gameio.get_user_choice = MagicMock(side_effect=["Bob", "Charlie"])
        result = first_player.role_behavior.act(first_player, game)
        assert "no Imps" in result

class TestUndertaker:
    def test_reveals_actual_role(self, game: GameManager) -> bool:
        undertaker = game.players[0]
        setup_player(undertaker, RoleName.UNDERTAKER)
        game.players[1].player_name = "Bob"
        game.players[1].actual_role = RoleName.IMP
        game.executed_player = "Bob"

        result = undertaker.role_behavior.act(undertaker, game)
        assert "Bob" in result
        assert "Imp" in result

    def test_reveals_drunk_as_drunk(self, game: GameManager) -> bool:
        undertaker = game.players[0]
        setup_player(undertaker, RoleName.UNDERTAKER)
        game.players[1].player_name = "Bob"
        game.players[1].actual_role = RoleName.DRUNK
        game.executed_player = "Bob"

        result = undertaker.role_behavior.act(undertaker, game)
        assert "Drunk" in result

    def test_no_execution(self, game: GameManager) -> bool:
        undertaker = game.players[0]
        setup_player(undertaker, RoleName.UNDERTAKER)
        game.executed_player = ""

        result = undertaker.role_behavior.act(undertaker, game)
        assert "No player has been executed" in result

    def test_poisoned_undertaker_asks_for_false_role(self, game, monkeypatch) -> bool:
        """Poisoned Undertaker prompts the storyteller for false info."""
        undertaker = game.players[0]
        setup_player(undertaker, RoleName.UNDERTAKER)
        undertaker.poisoned = True
        game.players[1].player_name = "Bob"
        game.players[1].actual_role = RoleName.IMP
        game.executed_player = "Bob"

        monkeypatch.setattr("builtins.input", lambda _: "Washerwoman")

        result = undertaker.role_behavior.act(undertaker, game)
        assert "Bob" in result

class TestRavenkeeper:
    def test_alive_returns_empty(self, game: GameManager) -> bool:
        rk = game.players[0]
        setup_player(rk, RoleName.RAVENKEEPER)
        rk.alive = True

        result = rk.role_behavior.act(rk, game)
        assert result == ""

    def test_dead_reveals_target_role(self, game, monkeypatch) -> bool:
        rk = game.players[0]
        setup_player(rk, RoleName.RAVENKEEPER)
        rk.alive = False
        game.players[1].player_name = "Bob"
        game.players[1].actual_role = RoleName.IMP

        monkeypatch.setattr("builtins.input", lambda _: "Bob")

        result = rk.role_behavior.act(rk, game)
        assert "Bob" in result
        assert "Imp" in result

    def test_dead_drunk_ravenkeeper_gives_fake_info(self, game, monkeypatch) -> bool:
        rk = game.players[0]
        setup_player(rk, RoleName.RAVENKEEPER)
        rk.actual_role = RoleName.DRUNK
        rk.alive = False
        game.players[1].player_name = "Bob"

        monkeypatch.setattr("builtins.input", lambda _: "Bob")

        result = rk.role_behavior.act(rk, game)
        assert "fake information" in result.lower()

class TestVirgin:
    def test_townsfolk_nominator_dies(self, game: GameManager) -> bool:
        virgin = game.players[1]
        setup_player(virgin, RoleName.VIRGIN)
        nominator = game.players[0]
        nominator.actual_role = RoleName.WASHERWOMAN
        game.vote_table = {nominator.player_name: {}}

        result = virgin.role_behavior.act(virgin, game)
        assert nominator.alive is False
        assert nominator.player_name in result

    def test_non_townsfolk_nominator_survives(self, game: GameManager) -> bool:
        virgin = game.players[1]
        setup_player(virgin, RoleName.VIRGIN)
        nominator = game.players[0]
        nominator.actual_role = RoleName.IMP  # Demon, not Townsfolk
        game.vote_table = {nominator.player_name: {}}

        virgin.role_behavior.act(virgin, game)
        assert nominator.alive is True

    def test_drunk_virgin_nominator_survives(self, game: GameManager) -> bool:
        """Drunk pretending to be Virgin: ability does not fire."""
        virgin = game.players[1]
        setup_player(virgin, RoleName.VIRGIN)
        virgin.actual_role = RoleName.DRUNK
        nominator = game.players[0]
        nominator.actual_role = RoleName.WASHERWOMAN
        game.vote_table = {nominator.player_name: {}}

        virgin.role_behavior.act(virgin, game)
        assert nominator.alive is True

class TestSlayer:
    def test_kills_imp(self, game, monkeypatch) -> bool:
        slayer = game.players[0]
        setup_player(slayer, RoleName.SLAYER)
        game.players[1].actual_role = RoleName.IMP
        game.players[1].player_name = "Bob"

        monkeypatch.setattr("builtins.input", lambda _: "Bob")

        result = slayer.role_behavior.act(slayer, game)
        assert game.players[1].alive is False
        assert "Imp" in result

    def test_misses_non_imp(self, game, monkeypatch) -> bool:
        slayer = game.players[0]
        setup_player(slayer, RoleName.SLAYER)
        game.players[1].actual_role = RoleName.WASHERWOMAN
        game.players[1].player_name = "Bob"

        monkeypatch.setattr("builtins.input", lambda _: "Bob")

        result = slayer.role_behavior.act(slayer, game)
        assert game.players[1].alive is True
        assert "not the Imp" in result

    def test_drunk_slayer_does_nothing(self, game: GameManager) -> bool:
        slayer = game.players[0]
        setup_player(slayer, RoleName.SLAYER)
        slayer.actual_role = RoleName.DRUNK

        result = slayer.role_behavior.act(slayer, game)
        assert "Drunk" in result

    def test_poisoned_slayer_does_nothing(self, game: GameManager) -> bool:
        slayer = game.players[0]
        setup_player(slayer, RoleName.SLAYER)
        slayer.poisoned = True

        result = slayer.role_behavior.act(slayer, game)
        assert "poisoned" in result.lower()

class TestSoldier:
    def test_soldier_is_protected(self, game: GameManager) -> bool:
        soldier = game.players[0]
        setup_player(soldier, RoleName.SOLDIER)

        soldier.role_behavior.act(soldier, game)
        assert soldier.protected is True

    def test_drunk_soldier_not_protected(self, game: GameManager) -> bool:
        soldier = game.players[0]
        setup_player(soldier, RoleName.SOLDIER)
        soldier.actual_role = RoleName.DRUNK

        soldier.role_behavior.act(soldier, game)
        assert soldier.protected is False

    def test_poisoned_soldier_not_protected(self, game: GameManager) -> bool:
        soldier = game.players[0]
        setup_player(soldier, RoleName.SOLDIER)
        soldier.poisoned = True

        soldier.role_behavior.act(soldier, game)
        assert soldier.protected is False

class TestMayor:
    def test_good_wins_with_3_alive_no_execution(self, game: GameManager) -> bool:
        mayor = game.players[0]
        setup_player(mayor, RoleName.MAYOR)
        game.executed_player = ""
        game.players_alive = game.players[:3]

        result = mayor.role_behavior.act(mayor, game)
        assert game.game_over is True
        assert "Good Wins" in result

    def test_does_nothing_with_more_than_3_alive(self, game: GameManager) -> bool:
        mayor = game.players[0]
        setup_player(mayor, RoleName.MAYOR)
        game.executed_player = ""
        game.players_alive = game.players  # All 5 alive

        mayor.role_behavior.act(mayor, game)
        assert game.game_over is False

    def test_does_nothing_when_execution_occurred(self, game: GameManager) -> bool:
        mayor = game.players[0]
        setup_player(mayor, RoleName.MAYOR)
        game.executed_player = "Bob"
        game.players_alive = game.players[:3]

        mayor.role_behavior.act(mayor, game)
        assert game.game_over is False

    def test_drunk_mayor_does_not_trigger(self, game: GameManager) -> bool:
        mayor = game.players[0]
        setup_player(mayor, RoleName.MAYOR)
        mayor.actual_role = RoleName.DRUNK
        game.executed_player = ""
        game.players_alive = game.players[:3]

        result = mayor.role_behavior.act(mayor, game)
        assert game.game_over is False
        assert "DRUNK" in result

    def test_poisoned_mayor_does_not_trigger(self, game: GameManager) -> bool:
        mayor = game.players[0]
        setup_player(mayor, RoleName.MAYOR)
        mayor.poisoned = True
        game.executed_player = ""
        game.players_alive = game.players[:3]

        result = mayor.role_behavior.act(mayor, game)
        assert game.game_over is False
        assert "POISONED" in result
