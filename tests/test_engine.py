from detective.engine import Game
from detective.generator import generate_case
from detective.store import LogStore


def test_game_can_be_created_on_every_level():
    for level in ("easy", "normal", "hard"):
        case = generate_case(1, level)
        game = Game(case, LogStore(case.access_log))
        assert game.queries_left > 0