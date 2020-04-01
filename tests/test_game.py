import pytest
import random

from ..src.game import CaptionThisGame

TOTAL_PLAYERS = 3
TOTAL_GAMES = 2
GAME_DURATION = 5

@pytest.fixture
def game():
    game = CaptionThisGame("1", total_players=TOTAL_PLAYERS, total_games=TOTAL_GAMES, game_duration=GAME_DURATION)
    game.add_player("1", "kevin")
    game.add_player("2", "kenny")
    game.add_player("3", "katie")
    return game

@pytest.mark.xfail
def test_game_is_ready(game):
    data = game.to_json()
    assert data["game"]["total_players"] - len(data["game"]["players"]) == TOTAL_PLAYERS

def test_game_is_now_ready(game):
    game.start_game()
    data = game.to_json()
    assert len(data["game"]["players"]) == TOTAL_PLAYERS
    assert data["ready"] == True

def test_game_has_image(game):
    game.start_game()
    data = game.to_json()
    assert data["game"]["image"] != ""

def test_all_players_submitted(game):
    for player_id, value in game.players.items():
        game.add_caption(player_id, f"player {player_id}: {random.randint(0,10)}")

    assert game.all_players_submitted() == True

def test_one_player_disconnected(game):
    game.remove_player("1")

    data = game.to_json()
    assert len(data["game"]["players"]) == TOTAL_PLAYERS - 1
    assert game.is_playable() == True
    game.remove_player("2")
    assert game.is_playable() == False

def test_all_players_voted_one_caption(game):
    game.add_caption("1", "player 1's caption msg")
    game.add_caption("2", "player 2's caption msg")
    game.add_caption("3", "player 3's caption msg")

    game.vote_caption("1")
    game.vote_caption("1")
    game.vote_caption("1")    
    assert game.all_players_voted() == True

    game.calculate_winners()
    game.set_flag("win") # must set to add winners and captions to the payload in to_json()
    data = game.to_json()

    assert len(data["game"]["winners"]) == 1
    assert data["game"]["win_captions"] == ["player 1's caption msg"]
    assert data["game"]["players"]["1"][1] == 1

def test_all_players_voted_two_caption(game):
    game.add_caption("1", "player 1's caption msg")
    game.add_caption("2", "player 2's caption msg")
    game.add_caption("3", "player 3's caption msg")

    game.vote_caption("1")
    game.vote_caption("2")

    game.calculate_winners()
    game.set_flag("win") # must set to add winners and captions to the payload in to_json()
    data = game.to_json()

    assert data["game"]["winners"] == ["kevin", "kenny"]
    assert data["game"]["win_captions"] == ["player 1's caption msg", "player 2's caption msg"]

def test_game_reset_and_done_and_new_game(game):
    game.start_game()
    game.add_caption("1", "player 1's caption msg")
    game.add_caption("2", "player 2's caption msg")
    game.add_caption("3", "player 3's caption msg")

    game.vote_caption("1")
    game.vote_caption("1")
    game.calculate_winners()
    game.set_flag("win")

    data = game.to_json()
    assert data["game"]["games_played"] == 1
    assert data["game"]["total_games"] == 2

    game.reset()
    data = game.to_json()
    assert data["game"]["captions"] == {}
    assert data["game"]["votes"] == 0
    assert data["flag"] == "reset"
    assert data["game"]["games_played"] == 2

    # test_game_is_done

    game.add_caption("1", "player 1's caption msg")
    game.add_caption("2", "player 2's caption msg")
    game.add_caption("3", "player 3's caption msg")

    game.vote_caption("1")
    game.vote_caption("1")
    game.calculate_winners()
    game.set_flag("win")

    game.reset()
    data = game.to_json()
    assert data["flag"] == "done"
    assert data["game"].get("memelords") != None
    assert data["game"]["memelords"] == ["kevin"]

    # test_new_game

    game.reset(new_game=True)
    data = game.to_json()
    assert data["flag"] == "reset"
    assert data["game"]["games_played"] == 1