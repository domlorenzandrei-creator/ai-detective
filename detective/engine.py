from .dialogue import render_statement
from .difficulty import LEVELS
from .generator import generate_case
from .search import SearchIndex
from .store import LogStore

class GameError(Exception):
    pass


class Game:
    
    def __init__(self, case, store):
        self.case = case
        self.store = store
        self.found = set()
        self.caught = set()
        self.statements = {}
        self.queries_left = LEVELS[case.level].queries
        self.notebook = SearchIndex()

    def suspect(self, suspect_id):
        for s in self.case.suspects:
            if s.id == suspect_id:
                return s
        raise GameError(f"No such suspect: {suspect_id}")

    def _note(self, doc_id, text):
        self.notebook.add(doc_id, text)

    def search_room(self, room):
        if room not in self.case.rooms:
            raise GameError(f"Unknown room: {room}")
        new = []
        for ev in self.case.evidence:
            if ev.room == room and ev.id not in self.found:
                self.found.add(ev.id)
                self._note(ev.id, f"{ev.title}. {ev.text}")
                new.append(ev)
        return new

    def interview(self, suspect_id, use_ai=True):
        s = self.suspect(suspect_id)
        text = render_statement(s, self.case.claims[suspect_id], use_ai)
        self.statements[suspect_id] = text
        self._note(f"stmt:{suspect_id}", f"{s.name} said: {text}")
        return text

    def check_alibi(self, suspect_id):
        if suspect_id not in self.statements:
            raise GameError("Interview them first. You need a statement to check.")
        if self.queries_left <= 0:
            raise GameError("No database queries left.")
        self.queries_left -= 1
        claim = self.case.claims[suspect_id]
        actual = self.store.location_at(suspect_id, claim.minute)
        lied = actual != claim.room
        if lied:
            self.caught.add(suspect_id)
        name = self.suspect(suspect_id).name
        self._note(f"log:{suspect_id}",
                   f"Log check: {name} was actually in the {actual}. Claimed {claim.room}. "
                   f"{'Contradiction.' if lied else 'Consistent.'}")
        return lied, actual

    def accuse(self, suspect_id):
        s = self.suspect(suspect_id)
        if suspect_id != self.case.killer_id:
            return False, f"{s.name} is innocent. The real killer walks free."
        if suspect_id in self.caught:
            return True, f"Airtight. {s.name} lied and the logs prove it."
        return True, f"Correct, but you never caught {s.name} in a lie. A lucky guess."

    def to_dict(self):
        return {
            "seed": self.case.seed,
            "level": self.case.level,
            "found": sorted(self.found),
            "caught": sorted(self.caught),
            "statements": self.statements,
            "queries_left": self.queries_left,
        }

    @classmethod
    def from_dict(cls, data):
        case = generate_case(data["seed"], data.get("level", "normal"))
        game = cls(case, LogStore(case.access_log))
        game.found = set(data["found"])
        game.caught = set(data["caught"])
        game.statements = data["statements"]
        game.queries_left = data["queries_left"]
        for ev in case.evidence:
            if ev.id in game.found:
                game._note(ev.id, f"{ev.title}. {ev.text}")
        for sid, text in game.statements.items():
            game._note(f"stmt:{sid}", f"{game.suspect(sid).name} said: {text}")
        return game
    