"""Scripted agents, no model, each run as NanoAgent runs the task: read_board, then submit.

An exact agent, which knows the answers, must pass every board. A greedy agent reads only what the
model reads, read_board's rows, and plays the first move that gives check (by python-chess, from the
rows and the side to move); its verdicts must agree with whether that move is the forced mate.
"""

from __future__ import annotations

from pathlib import Path

import chess
from helpers import judge

from contract import BoardInput
from plugin import read_board
from verifier.puzzles import PUZZLES


def first_check(number: int, side: str) -> str:
    rows = read_board(BoardInput(board=number), Path(".")).rows
    board = chess.Board(_fen(rows, side))
    checks = [m.uci() for m in board.legal_moves if board.gives_check(m)]
    return min(checks) if checks else min(m.uci() for m in board.legal_moves)


def _fen(rows: list[str], side: str) -> str:
    ranks = []
    for row in rows:
        out, empty = "", 0
        for char in row:
            if char == ".":
                empty += 1
            else:
                out += (str(empty) if empty else "") + char
                empty = 0
        ranks.append(out + (str(empty) if empty else ""))
    return "/".join(ranks) + (" w" if side == "white" else " b") + " - - 0 1"


def test_an_exact_agent_passes_every_board() -> None:
    for number, puzzle in PUZZLES.items():
        assert judge(number, puzzle["to_move"], puzzle["best"][0])["valid"] is True


def test_a_greedy_agent_is_judged_by_its_move() -> None:
    found = 0
    for number, puzzle in PUZZLES.items():
        move = first_check(number, puzzle["to_move"])
        verdict = judge(number, puzzle["to_move"], move)
        assert verdict["valid"] is (move in puzzle["best"])
        assert verdict["score"] == (1.0 if move in puzzle["best"] else 0.25)
        found += move in puzzle["best"]
    print(f"playing the first check finds the forced mate on {found} of {len(PUZZLES)} boards")
