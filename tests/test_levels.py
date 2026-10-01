import pytest

from detective.difficulty import LEVELS
from detective.generator import generate_case
from detective.store import LogStore


@pytest.mark.parametrize("level", list(LEVELS))
def test_level_has_right_suspect_count(level):
    case = generate_case(1, level)
    assert len(case.suspects) == LEVELS[level].suspects


@pytest.mark.parametrize("level", list(LEVELS))
def test_killer_is_alone_in_crime_room(level):
    for seed in range(50):
        case = generate_case(seed, level)
        store = LogStore(case.access_log)
        in_room = [
            s.id for s in case.suspects
            if store.location_at(s.id, case.murder_minute) == case.crime_room
        ]
        assert in_room == [case.killer_id]


def test_unknown_level_is_rejected():
    with pytest.raises(ValueError):
        generate_case(1, "impossible")


def test_normal_matches_old_default():
    assert generate_case(42) == generate_case(42, "normal")