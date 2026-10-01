from dataclasses import dataclass


@dataclass(frozen=True)
class Difficulty:
    name: str
    suspects: int
    queries: int


LEVELS = {
    "easy": Difficulty("easy", 4, 8),
    "normal": Difficulty("normal", 5, 6),
    "hard": Difficulty("hard", 6, 5),
}