from detective.generator import generate_case
from detective.store import LogStore


def test_same_seed_same_case():
    assert generate_case(7) == generate_case(7)


def test_killer_was_in_crime_room():
    for seed in range(50):
        case = generate_case(seed)
        store = LogStore(case.access_log)
        assert store.location_at(case.killer_id, case.murder_minute) == case.crime_room


def test_killer_claim_contradicts_logs():
    for seed in range(50):
        case = generate_case(seed)
        store = LogStore(case.access_log)
        claim = case.claims[case.killer_id]
        assert store.location_at(case.killer_id, claim.minute) != claim.room


def test_only_killer_in_crime_room():
    for seed in range(50):
        case = generate_case(seed)
        store = LogStore(case.access_log)
        for s in case.suspects:
            in_room = store.location_at(s.id, case.murder_minute) == case.crime_room
            assert in_room == (s.id == case.killer_id)