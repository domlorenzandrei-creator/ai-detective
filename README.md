# AI Detective

A procedurally generated murder mystery game for the terminal, written in Python. Every case is built from a seed: interview suspects, search rooms, check alibis against a keycard database, and catch the killer in a lie.

```
Case #42

Victor Hale was found dead in the Library.
Rooms: Library, Kitchen, Study, Greenhouse, Ballroom
Suspects:
  - Iris Crane, the butler
  - ...

> talk iris
Iris Crane: I was in the Kitchen at 21:45. I never left.
> check iris
CONTRADICTION. Iris Crane was really in the Library.
```

## Quick start

```bash
git clone https://github.com/domlorenzandrei-creator/ai-detective.git
cd ai-detective
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\activate
pip install -r requirements.txt

python main.py --seed 42 --no-ai
python main.py --seed 42 --level hard --no-ai   # easy | normal | hard
```

| Flag | Effect |
|---|---|
| `--seed N` | Replay the same case every time. Omit for a random case. |
| `--no-ai` | Use plain statements, no API key needed. |
| `--load` | Resume the game saved in `saves/game.json`. |
| `--level` | `easy`, `normal` or `hard`. Changes suspect count and query budget. |

## How to play

Someone in the mansion was murdered. Two suspects lie about where they were: the killer and a decoy. Your job is to work out which is which, and prove it before you accuse.

| Command | What it does |
|---|---|
| `rooms` / `suspects` | List rooms and suspects |
| `search <room>` | Look for evidence in a room |
| `talk <name>` | Interview a suspect (partial names work) |
| `check <name>` | Compare their alibi to the keycard logs (costs 1 query) |
| `logs <name>` | Show their full keycard history (costs 1 query) |
| `notes <words>` | Search everything you have learned so far |
| `accuse <name>` | Make your final accusation and end the game |
| `save` / `quit` | Save your progress or leave |

You start with 6 database queries, so you cannot check everyone. Decide who is worth checking.

**Tip:** the killer's real location at the time of death is the crime scene. The decoy lied about somewhere else.

A correct accusation without ever catching the killer in a lie counts as a lucky guess.

## Design

**The truth is plain data, and the AI never decides facts.**

- A case is generated deterministically from a seed. The generator picks the killer, room, weapon and time first, then derives everything else (keycard logs, alibis, evidence) from that truth.
- World data is immutable (`frozen` dataclasses). Player progress lives separately in the `Game` object. Keeping the two apart is what makes saving simple: a save file stores only the seed plus what you have discovered, and the whole world is regenerated on load.
- Alibis are checked with a SQL query against an in-memory SQLite table, finding the most recent room entry at or before a given minute.
- Discovered clues and statements are added to an inverted index, so the `notes` command only searches what you have actually learned.
- If an API key is set, suspects rephrase their statements in character using Claude. The model only receives the character's name, role, and the exact sentence to reword. It is never told who the killer is, so it cannot leak the answer or invent contradictions. Without a key, or if the call fails, the game falls back to plain statements.

## Project structure

```
ai-detective/
├── main.py                 CLI loop and command dispatch
├── requirements.txt
├── detective/
│   ├── models.py           Immutable dataclasses: Case, Suspect, Evidence, Claim
│   ├── generator.py        Seeded procedural case generation
│   ├── store.py            SQLite access-log store and queries
│   ├── search.py           Inverted-index notebook search
│   ├── engine.py           Game state, rules, query budget, save/load
│   └── dialogue.py         Statement rendering with optional LLM voice
└── tests/
    └── test_generator.py   Invariant tests across many seeds
```

## Optional: AI-voiced suspects

Set an API key, then run without `--no-ai`:

```bash
export ANTHROPIC_API_KEY=your_key                # Git Bash / macOS / Linux
$env:ANTHROPIC_API_KEY="your_key"                # PowerShell
python main.py --seed 42
```

Never commit your key. `.env` is already in `.gitignore`.

## Tests

```bash
pytest -q
```

The tests check invariants across 50 seeds rather than single examples: the same seed always gives the same case, the killer was in the crime room, the killer's alibi contradicts the logs, and nobody else was at the scene.

## Roadmap

- [x] Difficulty levels (more suspects, smaller query budget)
- [ ] Suspects who also claim who they saw, so alibis can be cross-referenced
- [x] TF-IDF ranking for notebook search
- [ ] GitHub Actions to run tests on every push
- [ ] FastAPI wrapper around `Game`

## Requirements

- Python 3.9 or newer
- `anthropic` (only needed for AI-voiced suspects)
- `pytest` (for tests)
