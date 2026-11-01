from __future__ import annotations

from pathlib import Path

import pytest
from helpers import checks, judge
from slimconfig import build_output, plain_output

import verifier
from contract import TASKS, TOOLS, BoardInput, Task, Tool
from plugin import read_board
from verifier.puzzles import PUZZLES


def board_with(mate_in: int) -> int:
    return next(n for n, p in sorted(PUZZLES.items()) if p["mate_in"] == mate_in)


def legal_but_not_best(number: int) -> str:
    return next(m for m in PUZZLES[number]["legal"] if m not in PUZZLES[number]["best"])


# Correct


@pytest.mark.parametrize("mate_in", [1, 2])
def test_approves_the_forced_mate(mate_in: int) -> None:
    n = board_with(mate_in)
    p = PUZZLES[n]
    verdict = judge(n, p["to_move"], p["best"][0])
    assert verdict["valid"] is True and verdict["score"] == 1.0
    assert verdict["message"] == f"All 6 checks hold: {p['best'][0]} forces mate in {mate_in} on board {n}."


# Incorrect


def test_a_legal_move_that_does_not_mate_scores_a_quarter() -> None:
    n = board_with(2)
    p = PUZZLES[n]
    move = legal_but_not_best(n)
    verdict = judge(n, p["to_move"], move)
    assert verdict["valid"] is False and verdict["score"] == 0.25
    assert verdict["message"] == (
        f"best: {move} is legal but does not force the fastest mate: the mate in 2 starts with {p['best'][0]}."
    )


def test_an_illegal_move_scores_zero() -> None:
    n = 1
    p = PUZZLES[n]
    move = next(f + r + g + s for f in "abcdefgh" for r in "12345678" for g in "abcdefgh" for s in "12345678"
                if f + r != g + s and f + r + g + s not in p["legal"])
    verdict = judge(n, p["to_move"], move)
    assert verdict["valid"] is False and verdict["score"] == 0.0
    assert verdict["message"] == f"legal: {move} is not a legal move on board 1."
    assert checks(verdict)["best"] is None


def test_the_wrong_side_to_move_scores_zero() -> None:
    p = PUZZLES[1]
    other = "black" if p["to_move"] == "white" else "white"
    verdict = judge(1, other, p["best"][0])
    assert verdict["valid"] is False and verdict["score"] == 0.0
    assert verdict["message"].startswith(f"to-move: On board 1 it is {p['to_move']} to move, not {other}.")


# Malformed and missing


@pytest.mark.parametrize("move", ["Bc3#", "d2-c3", "D2C3", "e2e9", "e7e8k", "", "d2"])
def test_a_move_not_in_uci_scores_zero(move: str) -> None:
    verdict = judge(1, PUZZLES[1]["to_move"], move)
    assert verdict["valid"] is False and verdict["score"] == 0.0 and verdict["message"].startswith("move-form:")


def test_answering_another_question_scores_zero() -> None:
    p = PUZZLES[1]
    for changes in ({"board": 2}, {"to_move": "black" if p["to_move"] == "white" else "white"}):
        verdict = judge(1, p["to_move"], p["best"][0], changes)
        assert verdict["valid"] is False and verdict["score"] == 0.0 and verdict["message"].startswith("same-question:")


@pytest.mark.parametrize("number", [0, 51])
def test_a_board_that_does_not_exist_scores_zero(number: int) -> None:
    verdict = judge(number, "white", "e2e4")
    assert verdict["valid"] is False and verdict["score"] == 0.0 and verdict["message"].startswith("board:")


# Boundary


def test_a_promotion_needs_its_piece() -> None:
    promoting = [(n, m) for n, p in PUZZLES.items() for m in p["legal"] if len(m) == 5]
    if not promoting:
        pytest.skip("no board allows a promotion")
    n, move = promoting[0]
    assert judge(n, PUZZLES[n]["to_move"], move)["score"] in (0.25, 1.0)
    assert judge(n, PUZZLES[n]["to_move"], move[:4])["score"] == 0.0  # without its piece it is not a legal move


def test_black_to_move_boards_are_judged_for_black() -> None:
    n = next(n for n, p in sorted(PUZZLES.items()) if p["to_move"] == "black")
    assert judge(n, "black", PUZZLES[n]["best"][0])["valid"] is True


# Tool calls


def test_checks_read_board_calls() -> None:
    def verify_input(number: int) -> bool:
        return verifier.verify_input("read_board", build_output({"board": number}, TOOLS[Tool.READ_BOARD][0]))["valid"]

    assert verify_input(1) and verify_input(50) and not verify_input(0) and not verify_input(51)

    def verify_output(number: int, made: dict) -> dict:
        given, output = TOOLS[Tool.READ_BOARD]
        return verifier.verify_output("read_board", build_output({"board": number}, given), build_output(made, output), ".")

    found = plain_output(read_board(BoardInput(board=1), Path(".")))
    assert verify_output(1, found)["valid"] is True
    rows = found["rows"]
    moved = found | {"rows": [rows[0], rows[1].replace("p", ".", 1), *rows[2:]]}
    assert "rank 7 differs" in verify_output(1, moved)["message"]
    assert verify_output(2, found)["valid"] is False
    assert verify_output(1, found | {"rows": rows[:7]})["valid"] is False


def test_the_show_board_task_is_judged_as_its_tool() -> None:
    found = plain_output(read_board(BoardInput(board=5), Path(".")))
    given, made = TASKS[Task.SHOW_BOARD]
    verdict = verifier.verify_task("show-board", build_output({"board": 5}, given), build_output(found, made), None, ".")
    assert verdict["valid"] is True


def test_the_verdict_is_the_same_twice() -> None:
    assert judge(3, "white", "a1a2") == judge(3, "white", "a1a2")
