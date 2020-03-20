import pytest
import random

from ..src.game import CaptionThisGame

TOTAL_PLAYERS = 3
game = CaptionThisGame("1", TOTAL_PLAYERS)

@pytest.mark.xfail
def test_game_is_ready():
    game.add_player("1", "kevin")
    game.add_player("2", "kenny")
    data = game.to_json()
    assert data["game"]["total_players"] - len(data["game"]["players"]) == TOTAL_PLAYERS

def test_game_is_now_ready():
    game.add_player("3", "katie")
    game.start_game()
    data = game.to_json()
    assert len(data["game"]["players"]) == TOTAL_PLAYERS
    assert data["ready"] == True

def test_all_players_submitted():
    for player_id, value in game.players.items():
        game.add_caption(player_id, f"player {player_id}: {random.randint(0,10)}")

    assert game.all_players_submitted() == True

def test_one_player_disconnected():
    game.remove_player("1")

    data = game.to_json()
    assert len(data["game"]["players"]) == TOTAL_PLAYERS - 1
    assert len(data["game"]["captions"]) == TOTAL_PLAYERS - 1

def test_all_players_voted():
    game.vote_caption("3")
    game.vote_caption("3")
    
    assert game.all_players_voted() == True

def test_calculate_winners():
    game.calculate_winners()

    data = game.to_json()

    assert data["game"]["winners"] != []
    assert data["game"]["winners"] == ["katie"]
    assert data["game"]["win_captions"] != []

def test_game_is_playable():
    game.remove_player("2")

    assert game.is_playable() == False

def test_game_reset():
    game.reset()

    data = game.to_json()
    assert data["game"]["captions"] == {}
    assert data["game"]["winners"] == []