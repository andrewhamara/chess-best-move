# Chess Best Move

A `nanoagent.plugin/v0001` plugin: find the best move on a chess board image.
Each of 50 bundled boards is a position from a real game, a Lichess puzzle
with exactly one checkmate in one move. Its one tool reads the board's
pixels and returns the position as text; the agent must find the mate itself. The verifier holds every legal move and every move that forces the
fastest mate, computed exactly by exhaustive search, and checks the agent's
move against them.

## Tools

| Tool | Does | Code |
|---|---|---|
| `read_board` | Reads the position on a board image square by square, each square matched exactly against the 26 a board can hold (12 pieces and empty, on light and dark squares), and lists each side's pieces by square, e.g. `Kd3, Bd2, Pa2`. It never says which move is best | `src/plugin/read_board.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `best-move` | Finds the best move on a board for the side to move, e.g. "find the best move on board 7, white to move" | `agent`, with `read_board`; no reference (the verifier holds the answers) |
| `show-board` | Shows a board and the piece lists the agent reads | `tool` (`read_board`) |

The page draws each answer on the board (`ui/renderers.js`): the agent's move
as an orange arrow and, when it is wrong, the mating move as a dashed green
one, under a line naming both, with the verdict's checks folded away.

## The task

The input is a board, 1 to 50, and whose turn it is (`white` or `black`),
which an image cannot show. The agent submits the move in UCI, e.g. `g1f3` or
`e7e8q`. The best move is defined exactly: a move that forces checkmate in
the fewest moves. Neither side can castle or capture en passant (an image
cannot show those rights either), and every board was kept only if removing
them changes no answer.

## Ground truth

The positions are 50 puzzles from the [Lichess puzzle
database](https://database.lichess.org/#puzzles) (CC0): the first 50 mate-in-1
puzzles with 8 pieces or fewer, popularity 90 or more and 2,000 plays or
more, listed with their Lichess ids in `src/plugin/tools_dev/make_boards.py`. For
each, the generator computes with python-chess, by exhaustive search, every
legal move and every move that forces mate in the fewest moves, and writes
them to `verifier/puzzles.py`. On all 50 boards that is exactly one move,
Lichess's own solution, and the tests check both. The generator also draws
each board from the piece sprites in `ui/pieces.png` and refuses to write it
unless `read_board` reads the position back. The plugin's tool holds no
answers; the verifier, standard library only, judges from them.

## Constraints

`verifier/task.py` judges a `best-move` submission against 6 constraints, in
order. Each entry of `details.constraints` is
`{id, constraint, ok, expected, actual, message}`.

| # | id | What it checks |
|---|---|---|
| 1 | `board` | The board exists |
| 2 | `to-move` | The side given is the side to move on this board |
| 3 | `same-question` | The submission answers the question asked: its board and side |
| 4 | `move-form` | The move is written in UCI |
| 5 | `legal` | The move is legal in the position |
| 6 | `best` | The move forces checkmate in the fewest moves possible |

A best move scores 1. A legal move that is not best scores 0.25. Anything
else, an illegal move or a failure of 1 to 4, scores 0. Every tool output is
checked too: `read_board`'s pieces must be the board's position.

## Limitations

- **Small mates in one, because of the model's reply limit.** RUSH Lab's model must answer within 2,048-token replies, thinking included. On full-size puzzles (about 16 pieces), and on mates in two, it ran out of its reply before answering. On these boards, told to reason before moving, it finished 22 of 50; told not to reason but to pick the mate on instinct and submit at once, it finished 36 of 50 (29 right). It still runs out on some boards.
- **"Best" means the mate.** It is defined only where code can decide it exactly; positions won by other means would need an engine's judgment.
- **The agent never sees pixels.** It reasons over the position as text; the board reader does the seeing, on these rendered boards only.
- **White is always at the bottom,** and castling and en passant are never available.
- **A fixed set of 50 boards** could in principle be memorized.

## Data

The positions come from the Lichess puzzle database, released under CC0. The
piece sprites in `ui/pieces.png` were drawn from the chess glyphs of the
Apple Symbols font.

## Layout

```text
.
├── nanoagent.yaml   # manifest: id, runtime, permissions (no network), tools, tasks and the agent's instructions
├── contract.py      # each tool's and task's typed input and output: slimconfig Output classes
├── README.md
├── LICENSE
├── pyproject.toml   # pillow reads the boards; python-chess (dev only) builds them and their answers
├── uv.lock
├── .gitignore
├── .env             # needed environment variable names (none here)
├── src/plugin/      # the MCP server (__main__.py), read_board.py, and tools_dev/make_boards.py
├── tests/           # the reader, the answers against Lichess and python-chess, the verifier, scripted agents
├── ui/              # boards/ (the 50 PNGs), pieces.png (the sprites), renderers.js/.css (moves on the board)
├── product/         # the product page a catalog shows: product.yaml and icon.svg
└── verifier/        # deterministic verifier: puzzles.py (the answers), one module per tool, and task.py
```

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run python -m plugin.tools_dev.make_boards   # rewrites the same boards and answers
```

NanoAgent passes the folder the plugin may write to as `NANOAGENT_WORKSPACE`;
this plugin writes nothing there.
