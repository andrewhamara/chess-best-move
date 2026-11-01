"""read_board: the pieces it lists are the board's position, square for square."""

from .checks import board_problem, result
from .puzzles import PUZZLES

ORDER = "KQRBNP"


def pieces(rows, white):
    """One side's pieces by square, king first, then by kind, then by square: as read_board lists them."""
    found = [
        (ORDER.index(char.upper()), "abcdefgh"[file] + str(8 - y), char.upper())
        for y, row in enumerate(rows)
        for file, char in enumerate(row)
        if char != "." and char.isupper() == white
    ]
    return [letter + square for _, square, letter in sorted(found)]


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
    true = list(PUZZLES[number]["rows"])
    for side, white, given in (("white", True, output_value.white), ("black", False, output_value.black)):
        if list(given) != pieces(true, white):
            return result(False, f"board {number}'s {side} pieces are not its position: {pieces(true, white)}")
    return result(True, f"board {number}'s pieces are its position")
