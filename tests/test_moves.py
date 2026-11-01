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


@pytest.mark.parametrize("number", sorted(PUZZLES))
def test_consider_move_gives_only_the_position_after_the_move(number: int) -> None:
    from contract import ConsiderInput, ConsiderOutput
    from plugin import consider_move

    puzzle = PUZZLES[number]
    side = Side(puzzle["to_move"])
    for move in list(puzzle["legal"])[:10] + list(puzzle["best"]):
        found = consider_move(ConsiderInput(board=number, to_move=side, move=move, note="why"), Path("."))
        board = chess.Board(puzzle["fen"])
        board.push_uci(move)
        for color, listed in ((chess.WHITE, found.white), (chess.BLACK, found.black)):
            expected = {p.symbol().upper() + chess.square_name(s) for s, p in board.piece_map().items() if p.color == color}
            assert set(listed) == expected
        assert (found.move, found.note) == (move, "why")
    # It says nothing about whether the move is good: no check, mate or replies anywhere in its output.
    assert set(ConsiderOutput.__dataclass_fields__) == {"board", "to_move", "move", "note", "white", "black"}


def test_consider_move_refuses_an_illegal_move() -> None:
    from contract import ConsiderInput
    from plugin import consider_move

    with pytest.raises(ValueError, match="not a legal move"):
        consider_move(ConsiderInput(board=1, to_move=Side(PUZZLES[1]["to_move"]), move="a1a1", note=""), Path("."))
