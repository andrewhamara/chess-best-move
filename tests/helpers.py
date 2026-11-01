"""Shared test helpers: judging a submission as NanoAgent's sandbox would."""

from __future__ import annotations

from slimconfig import build_output

import verifier
from contract import TASKS, Task


def judge(board: int, side: str, move: str, changes: dict | None = None) -> dict:
    given, made = TASKS[Task.BEST_MOVE]
    question = {"board": board, "to_move": side}
    answer = question | {"move": move} | (changes or {})
    return verifier.verify_task("best-move", build_output(question, given), build_output(answer, made), None, ".")


def checks(verdict: dict) -> dict:
    return {item["id"]: item["ok"] for item in verdict["details"]["constraints"]}
