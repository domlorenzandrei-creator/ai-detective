import argparse
import json
import random
from pathlib import Path

from detective.difficulty import LEVELS
from detective.engine import Game, GameError
from detective.generator import generate_case
from detective.models import fmt_time
from detective.store import LogStore

SAVE_PATH = Path("saves/game.json")

HELP = """Commands:
  rooms                 list rooms
  suspects              list suspects
  search <room>         search a room for evidence
  talk <name>           interview a suspect
  check <name>          check their alibi against the logs (costs a query)
  logs <name>           full keycard history (costs a query)
  notes <words>         search your notebook
  accuse <name>         make your accusation
  save / quit"""


def find_suspect(game, text):
    text = text.lower()
    for s in game.case.suspects:
        if text and text in s.name.lower():
            return s
    raise GameError(f"No suspect matching '{text}'.")


def find_room(game, text):
    for r in game.case.rooms:
        if r.lower() == text.lower():
            return r
    raise GameError(f"No room named '{text}'.")


def intro(game):
    c = game.case
    print(f"\n{c.victim} was found dead in the {c.crime_room}.")
    print(f"Rooms: {', '.join(c.rooms)}")
    print("Suspects:")
    for s in c.suspects:
        print(f"  - {s.name}, the {s.role}")
    print("\nType 'help' for commands.\n")


def handle(game, cmd, arg, use_ai):
    if cmd == "help":
        print(HELP)
    elif cmd == "rooms":
        print(", ".join(game.case.rooms))
    elif cmd == "suspects":
        for s in game.case.suspects:
            print(f"  {s.name} ({s.role}) - motive: {s.motive}")
    elif cmd == "search":
        found = game.search_room(find_room(game, arg))
        if not found:
            print("Nothing new here.")
        for ev in found:
            print(f"Found: {ev.title} - {ev.text}")
    elif cmd == "talk":
        s = find_suspect(game, arg)
        print(f"{s.name}: {game.interview(s.id, use_ai)}")
    elif cmd == "check":
        s = find_suspect(game, arg)
        lied, actual = game.check_alibi(s.id)
        if lied:
            print(f"CONTRADICTION. {s.name} was really in the {actual}.")
        else:
            print(f"{s.name}'s alibi holds.")
        print(f"Queries left: {game.queries_left}")
    elif cmd == "logs":
        s = find_suspect(game, arg)
        if game.queries_left <= 0:
            raise GameError("No database queries left.")
        game.queries_left -= 1
        for room, minute in game.store.history(s.id):
            print(f"  {fmt_time(minute)}  entered {room}")
        print(f"Queries left: {game.queries_left}")
    elif cmd == "notes":
        results = game.notebook.search(arg)
        if not results:
            print("Nothing in your notes matches.")
        for _, text in results:
            print(f"  * {text}")
    elif cmd == "accuse":
        correct, verdict = game.accuse(find_suspect(game, arg).id)
        print(verdict)
        return True
    elif cmd == "save":
        SAVE_PATH.parent.mkdir(exist_ok=True)
        SAVE_PATH.write_text(json.dumps(game.to_dict(), indent=2))
        print(f"Saved to {SAVE_PATH}.")
    else:
        print("Unknown command. Try 'help'.")
    return False


def main():
    parser = argparse.ArgumentParser(description="AI Detective")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--load", action="store_true")
    parser.add_argument("--no-ai", action="store_true")
    parser.add_argument("--level", choices=list(LEVELS), default="normal")
    args = parser.parse_args()

    if args.load:
        game = Game.from_dict(json.loads(SAVE_PATH.read_text()))
    else:
        seed = args.seed if args.seed is not None else random.randrange(10**6)
        case = generate_case(seed, args.level)
        game = Game(case, LogStore(case.access_log))
        print(f"Case #{seed} ({args.level})")
    intro(game)

    while True:
        raw = input("> ").strip()
        if not raw:
            continue
        if raw in ("quit", "exit"):
            break
        cmd, _, arg = raw.partition(" ")
        try:
            if handle(game, cmd.lower(), arg.strip(), not args.no_ai):
                break
        except GameError as err:
            print(f"! {err}")


if __name__ == "__main__":
    main()