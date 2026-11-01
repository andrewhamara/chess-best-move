"""The answers in verifier/puzzles.py, checked against Lichess's own solutions and python-chess."""

from __future__ import annotations

from collections import Counter

import chess
import pytest

from plugin.tools_dev.make_boards import PUZZLES as SOURCES
from verifier.puzzles import PUZZLES

SOLUTIONS = {puzzle: solution for puzzle, _, _, solution in SOURCES}


@pytest.mark.parametrize("number", sorted(PUZZLES))
def test_the_best_move_is_lichesss_solution_and_it_is_unique(number: int) -> None:
    puzzle = PUZZLES[number]
    assert list(puzzle["best"]) == [SOLUTIONS[puzzle["lichess"]]]


@pytest.mark.parametrize("number", sorted(PUZZLES))
def test_the_legal_moves_and_the_mate_are_the_positions(number: int) -> None:
    puzzle = PUZZLES[number]
    board = chess.Board(puzzle["fen"])
    assert list(puzzle["legal"]) == sorted(move.uci() for move in board.legal_moves)
    assert puzzle["to_move"] == ("white" if board.turn else "black")
    assert board.castling_rights == 0 and board.ep_square is None

    def mates_now(position: chess.Board) -> bool:
        for move in list(position.legal_moves):
            position.push(move)
            mate = position.is_checkmate()
            position.pop()
            if mate:
                return True
        return False

    if puzzle["mate_in"] == 2:
        assert not mates_now(board)  # no mate in 1, so 2 is the fewest
    board.push(chess.Move.from_uci(puzzle["best"][0]))
    if puzzle["mate_in"] == 1:
        assert board.is_checkmate()
    else:
        # The defender has moves, and every one of them allows a mate on the next move.
        assert not board.is_checkmate() and any(True for _ in board.legal_moves)
        for reply in list(board.legal_moves):
            board.push(reply)
            mates = False
            for move in list(board.legal_moves):
                board.push(move)
                mates = mates or board.is_checkmate()
                board.pop()
            assert mates, (number, reply.uci())
            board.pop()


def test_every_board_is_a_mate_in_one_of_eight_pieces_or_fewer() -> None:
    assert Counter(puzzle["mate_in"] for puzzle in PUZZLES.values()) == {1: 50}
    assert all(sum(c.isalpha() for c in p["fen"].split()[0]) <= 8 for p in PUZZLES.values())
