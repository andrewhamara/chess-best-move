"""legal_moves: every legal move on a board for the side to move, the checks apart from the rest.

It follows from the rules alone, so a tool computes it (python-chess, on the position read_board
reads from the image, with no castling or en passant); which move is best is the agent's judgment.
"""

from __future__ import annotations

from pathlib import Path

import chess

from contract import MovesInput, MovesOutput
from plugin.read_board import _rows


def fen(rows: list[str], white: bool) -> str:
    """The position as a FEN: the rows, the side to move, no castling and no en passant."""
    ranks = []
    for row in rows:
        rank, empty = "", 0
        for char in row:
            if char == ".":
                empty += 1
                continue
            rank += (str(empty) if empty else "") + char
            empty = 0
        ranks.append(rank + (str(empty) if empty else ""))
    return "/".join(ranks) + (" w" if white else " b") + " - - 0 1"


def legal_moves(given: MovesInput, workspace: Path) -> MovesOutput:
    """Every legal move for the side to move, in UCI: those that give check, then the others."""
    board = chess.Board(fen(list(_rows(given.board)), given.to_move.value == "white"))
    moves = list(board.legal_moves)
    checks = sorted(move.uci() for move in moves if board.gives_check(move))
    others = sorted(move.uci() for move in moves if not board.gives_check(move))
    return MovesOutput(board=given.board, to_move=given.to_move, checks=checks, others=others)
