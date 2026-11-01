"""legal_moves and consider_move: the rules' bookkeeping for a board, never which move is best.

legal_moves lists every legal move for the side to move, the checks apart. consider_move is a
reasoning step: the agent names one candidate and a note, and gets back only the position after it,
so it can think about one move per step. Both follow from the rules alone (python-chess, on the
position read_board reads from the image, with no castling or en passant); which move is best is the
agent's judgment.
"""

from __future__ import annotations

from pathlib import Path

import chess

from contract import ConsiderInput, ConsiderOutput, MovesInput, MovesOutput
from plugin.read_board import _rows, pieces


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


def consider_move(given: ConsiderInput, workspace: Path) -> ConsiderOutput:
    """A reasoning step: the position after one candidate move, as read_board lists a position. It says
    nothing about the move (not check, not mate, not the replies): judging it is the agent's work."""
    rows = list(_rows(given.board))
    board = chess.Board(fen(rows, given.to_move.value == "white"))
    legal = {move.uci(): move for move in board.legal_moves}
    if given.move not in legal:
        raise ValueError(f"{given.move!r} is not a legal move on board {given.board}: legal_moves lists them")
    board.push(legal[given.move])
    after = [row.replace(" ", "") for row in str(board).splitlines()]
    return ConsiderOutput(
        board=given.board,
        to_move=given.to_move,
        move=given.move,
        note=given.note,
        white=pieces(after, True),
        black=pieces(after, False),
    )
