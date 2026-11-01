"""read_board: the rows it gives are the board's position, square for square."""

from .checks import board_problem, result
from .puzzles import PUZZLES


def verify_input(value):
    problem = board_problem(value.board)
    if problem:
        return result(False, problem)
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    """``output_value``: a contract BoardOutput, held to the board's true position."""
    number = input_value.board
    if output_value.board != number:
        return result(False, f"the output is for board {output_value.board}, not board {number}")
    rows = list(output_value.rows)
    true = list(PUZZLES[number]["rows"])
    if rows != true:
        wrong = [8 - y for y, (row, real) in enumerate(zip(rows, true)) if row != real]
        where = f"rank {wrong[0]}" if wrong else f"{len(rows)} ranks, not 8"
        return result(False, f"board {number}'s rows are not its position: {where} differs")
    return result(True, f"board {number}'s rows are its position")
