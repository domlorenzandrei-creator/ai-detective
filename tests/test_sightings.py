from detective.engine import Game
from detective.generator import generate_case
from detective.store import LogStore


def test_honest_witnesses_report_true_sightings():
    for seed in range(50):
        case = generate_case(seed)
        store = LogStore(case.access_log)
        for wid, sighting in case.sightings.items():
            claim = case.claims[wid]
            if store.location_at(wid, claim.minute) == claim.room:
                seen_at = store.location_at(sighting.seen_id, sighting.minute)
                assert seen_at == sighting.room


def test_sightings_match_the_witnesses_own_alibi():
    for seed in range(50):
        case = generate_case(seed)
        for wid, sighting in case.sightings.items():
            assert sighting.room == case.claims[wid].room
            assert sighting.seen_id != wid


def test_cross_check_finds_exactly_the_conflicts():
    case = generate_case(3)
    game = Game(case, LogStore(case.access_log))
    for s in case.suspects:
        game.interview(s.id, use_ai=False)
    expected = [
        wid for wid, sg in case.sightings.items()
        if case.claims[sg.seen_id].room != sg.room
    ]
    assert len(game.cross_check()) == len(expected)