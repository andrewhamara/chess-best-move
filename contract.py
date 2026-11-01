"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    READ_BOARD = "read_board"


class Task(Enum):
    BEST_MOVE = "best-move"
    SHOW_BOARD = "show-board"


class Side(Enum):
    WHITE = "white"
    BLACK = "black"


BOARD = "A bundled board image's number, 1 to 50; each shows a position from a real game"
MOVE = (
    "The move in UCI: the from square and the to square, e.g. e2e4 or g1f3, with the promotion piece added for a "
    "pawn reaching the last rank, e.g. e7e8q"
)


@dataclass
class BoardInput(Output):
    board: Annotated[int, BOARD]


@dataclass
class BoardOutput(Output):
    board: Annotated[int, BOARD]
    white: Annotated[list[str], "White's pieces: K Q R B N P are king, queen, rook, bishop, knight, pawn; e.g. Kg1, Pe4"]
    black: Annotated[list[str], "Black's pieces, written the same way as white's (upper case), e.g. Kg8, Pe5"]


@dataclass
class MoveInput(Output):
    board: Annotated[int, BOARD]
    to_move: Annotated[Side, "Whose turn it is: the side that makes the move"]


@dataclass
class MoveOutput(Output):
    board: Annotated[int, "The board's number, as given"]
    to_move: Annotated[Side, "Whose turn it is, as given"]
    move: Annotated[str, MOVE]


TOOLS = {
    Tool.READ_BOARD: (BoardInput, BoardOutput),
}
TASKS = {
    Task.BEST_MOVE: (MoveInput, MoveOutput),
    Task.SHOW_BOARD: (BoardInput, BoardOutput),
}
