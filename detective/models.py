from dataclasses import dataclass


def fmt_time(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


@dataclass(frozen=True)
class Suspect:
    id: str
    name: str
    role: str
    motive: str
    secret: str


@dataclass(frozen=True)
class Evidence:
    id: str
    title: str
    text: str
    room: str


@dataclass(frozen=True)
class Claim:
    suspect_id: str
    room: str
    minute: int


@dataclass(frozen=True)
class Sighting:
    witness_id: str
    seen_id: str
    room: str
    minute: int


@dataclass(frozen=True)
class Case:
    seed: int
    victim: str
    crime_room: str
    weapon: str
    murder_minute: int
    rooms: tuple
    suspects: tuple
    evidence: tuple
    claims: dict
    killer_id: str
    access_log: tuple
    level: str
    sightings: dict