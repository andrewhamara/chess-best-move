"""Scripted agents, no model, each run as NanoAgent runs the task: read_board, then submit.

An exact agent, which knows the answers, must pass every board. A greedy agent sees only what the
model sees and plays legal_moves's first check (or its first move when there is none); its verdicts
must agree with whether that move is the forced mate.
"""

from __future__ import annotations

from pathlib import Path

from helpers import judge

from contract import MovesInput, Side
from plugin import legal_moves
from verifier.puzzles import PUZZLES


def first_check(number: int, side: str) -> str:
    moves = legal_moves(MovesInput(board=number, to_move=Side(side)), Path("."))
    return (moves.checks or moves.others)[0]


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
