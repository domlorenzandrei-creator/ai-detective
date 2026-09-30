import random

from .models import Case, Claim, Evidence, Suspect, fmt_time

FIRST_NAMES = ["Eleanor", "Victor", "Marcus", "Iris", "Julian", "Nora", "Felix", "Clara", "Otis"]
LAST_NAMES = ["Blackwood", "Hale", "Ashford", "Crane", "Voss", "Lark", "Pryce", "Thorne", "Quill"]
ROLES = ["butler", "niece", "business partner", "doctor", "chef", "gardener"]
ROOMS = ["Library", "Kitchen", "Study", "Greenhouse", "Wine Cellar", "Ballroom"]
WEAPONS = ["candlestick", "letter opener", "fireplace poker", "marble bookend"]
MOTIVES = ["inheritance", "blackmail", "jealousy", "business debt", "revenge"]
SECRETS = ["an affair", "a gambling debt", "a forged signature",
           "a secret meeting", "stolen jewelry", "a hidden will"]


def generate_case(seed: int) -> Case:
    rng = random.Random(seed)

    names = [f"{f} {l}" for f, l in zip(rng.sample(FIRST_NAMES, 6), rng.sample(LAST_NAMES, 6))]
    victim, *suspect_names = names

    suspects = tuple(
        Suspect(
            id=f"s{i}",
            name=name,
            role=role,
            motive=rng.choice(MOTIVES),
            secret=secret,
        )
        for i, (name, role, secret) in enumerate(
            zip(suspect_names, rng.sample(ROLES, 5), rng.sample(SECRETS, 5))
        )
    )

    rooms = tuple(rng.sample(ROOMS, 5))
    crime_room = rng.choice(rooms)
    weapon = rng.choice(WEAPONS)
    murder_minute = rng.randrange(21 * 60, 23 * 60, 5)

    killer = rng.choice(suspects)
    others = [s for s in suspects if s.id != killer.id]
    red_herring = rng.choice(others)

    non_crime = [r for r in rooms if r != crime_room]
    log = []
    true_room = {}
    for s in suspects:
        log.append((s.id, rng.choice(rooms), 19 * 60 + rng.randrange(0, 60, 5)))
        room = crime_room if s.id == killer.id else rng.choice(non_crime)
        true_room[s.id] = room
        log.append((s.id, room, murder_minute - rng.randrange(10, 30, 5)))
        if s.id == killer.id:
            log.append((s.id, rng.choice(non_crime), murder_minute + rng.randrange(10, 25, 5)))

    claims = {}
    for s in suspects:
        if s.id in (killer.id, red_herring.id):
            options = [r for r in rooms if r not in (true_room[s.id], crime_room)]
            claims[s.id] = Claim(s.id, rng.choice(options), murder_minute)
        else:
            claims[s.id] = Claim(s.id, true_room[s.id], murder_minute)

    evidence = (
        Evidence("e0", "Coroner's note",
                 f"Time of death estimated near {fmt_time(murder_minute)}.", crime_room),
        Evidence("e1", "Murder weapon",
                 f"A {weapon}, wiped clean but not carefully enough.", crime_room),
        Evidence("e2", "Torn letter",
                 f"A letter mentioning {killer.motive} and a threat against {victim}.",
                 rng.choice(rooms)),
        Evidence("e3", "Crumpled receipt",
                 f"A receipt tied to {red_herring.secret}, belonging to {red_herring.name}.",
                 rng.choice(rooms)),
    )

    return Case(
        seed=seed, victim=victim, crime_room=crime_room, weapon=weapon,
        murder_minute=murder_minute, rooms=rooms, suspects=suspects,
        evidence=evidence, claims=claims, killer_id=killer.id,
        access_log=tuple(log),
    )