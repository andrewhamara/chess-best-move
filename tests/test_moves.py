from __future__ import annotations

from pathlib import Path

import chess
import pytest

from contract import MovesInput, Side
from plugin import legal_moves
from verifier.puzzles import PUZZLES


@pytest.mark.parametrize("number", sorted(PUZZLES))
def test_lists_every_legal_move_and_the_checks_apart(number: int) -> None:
    puzzle = PUZZLES[number]
    found = legal_moves(MovesInput(board=number, to_move=Side(puzzle["to_move"])), Path("."))
    board = chess.Board(puzzle["fen"])
    assert found.checks == sorted(m.uci() for m in board.legal_moves if board.gives_check(m)) == list(puzzle["checks"])
    assert sorted(found.checks + found.others) == list(puzzle["legal"])
    # Every best move is a legal move, and on these boards every first move of a forced mate gives check
    # or is quiet: the list never says which.
    assert set(puzzle["best"]) <= set(found.checks + found.others)
