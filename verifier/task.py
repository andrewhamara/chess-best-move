"""The best-move task's verdict: the agent's move against every move that forces mate in the fewest moves.

Six constraints, in order; every one must hold. Each is {id, constraint, ok, expected, actual,
message}: ok is true, false, or null when a constraint it needs did not hold. Any failure of 1 to 4
scores 0, and so does an illegal move. A legal move that is not a best move scores 0.25; a best move
scores 1.
"""

from .checks import UCI, board_problem, result
from .puzzles import PUZZLES

CONSTRAINTS = (
    ("board", "The board exists"),
    ("to-move", "The side given is the side to move on this board"),
    ("same-question", "The submission answers the question asked: its board and side"),
    ("move-form", "The move is written in UCI, e.g. e2e4 or e7e8q"),
    ("legal", "The move is legal in the position"),
    ("best", "The move forces checkmate in the fewest moves possible"),
)
GUARDS = 4  # constraints 1 to 4: a failure scores 0
LEGAL = 0.25  # a legal move that does not force the fastest mate


def verify_task(arguments, output, reference, workspace):
    """``arguments``: a contract MoveInput; ``output``: MoveOutput. No reference: the verifier holds the answers."""
    checks = {}

    def put(key, ok, expected=None, actual=None, message=""):
        checks[key] = {"ok": ok, "expected": expected, "actual": actual, "message": "" if ok else message}

    number, side = arguments.board, arguments.to_move.value
    problem = board_problem(number)
    put("board", problem is None, message=problem)
    puzzle = PUZZLES[number] if problem is None else None
    if puzzle is not None:
        put(
            "to-move",
            side == puzzle["to_move"],
            puzzle["to_move"],
            side,
            f"On board {number} it is {puzzle['to_move']} to move, not {side}.",
        )
    answered = (output.board, output.to_move.value)
    put(
        "same-question",
        answered == (number, side),
        [number, side],
        list(answered),
        f"The question was board {number} with {side} to move; the submission answers board {answered[0]} with "
        f"{answered[1]} to move.",
    )
    move = output.move
    put("move-form", bool(UCI.fullmatch(move)), actual=move, message=f"{move!r} is not a move in UCI, such as e2e4.")
    if puzzle is not None and checks["move-form"]["ok"]:
        best = list(puzzle["best"])
        mate = f"mate in {puzzle['mate_in']}"
        put("legal", move in puzzle["legal"], actual=move, message=f"{move} is not a legal move on board {number}.")
        if checks["legal"]["ok"]:
            put(
                "best",
                move in best,
                best,
                move,
                f"{move} is legal but does not force the fastest mate: the {mate} starts with {' or '.join(best)}.",
            )

    constraints = []
    for key, text in CONSTRAINTS:
        check = checks.get(key)
        if check is None:
            waiting = next(k for k, _ in CONSTRAINTS if checks.get(k, {"ok": True})["ok"] is False)
            check = {"ok": None, "expected": None, "actual": None, "message": f"Not checked: {waiting} did not hold."}
        constraints.append({"id": key, "constraint": text, **check})
    failed = [item for item in constraints if item["ok"] is False]
    details = {"constraints": constraints}
    if puzzle is not None:
        details |= {"expected": {"best": list(puzzle["best"]), "mate_in": puzzle["mate_in"]}, "lichess": puzzle["lichess"]}
    if not failed:
        return result(
            True,
            f"All {len(CONSTRAINTS)} checks hold: {move} forces mate in {puzzle['mate_in']} on board {number}.",
            **details,
        )
    first = failed[0]
    message = f"{first['id']}: {first['message']}" + (f" (+{len(failed) - 1} more)" if len(failed) > 1 else "")
    ok = {item["id"]: item["ok"] for item in constraints}
    score = LEGAL if all(ok[key] for key, _ in CONSTRAINTS[:GUARDS]) and ok.get("legal") else 0.0
    return result(False, message, score=score, **details)
