"""Checks shared by the verifiers. Pure functions of contract instances and the boards' truth."""

import re

from .puzzles import COUNT

UCI = re.compile(r"^[a-h][1-8][a-h][1-8][qrbn]?$")


def result(valid, message, *, score=None, **details):
    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
    }


def board_problem(number):
    if not 1 <= number <= COUNT:
        return f"no board {number}: the boards are 1 to {COUNT}"
    return None
