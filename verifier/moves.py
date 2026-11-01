"""legal_moves: the moves it lists are every legal move on the board, the checks apart, for the side to move."""

from .checks import board_problem, result
from .puzzles import PUZZLES


def verify_input(value):
    problem = board_problem(value.board)
    if problem:
        return result(False, problem)
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    """``output_value``: a contract MovesOutput, held to the board's true legal moves and checks."""
    number, side = input_value.board, input_value.to_move.value
    puzzle = PUZZLES[number]
    if (output_value.board, output_value.to_move.value) != (number, side):
        return result(False, f"the output is for board {output_value.board}, {output_value.to_move.value} to move")
    if side != puzzle["to_move"]:
        return result(False, f"on board {number} it is {puzzle['to_move']} to move, not {side}")
    checks = list(puzzle["checks"])
    others = [move for move in puzzle["legal"] if move not in checks]
    if list(output_value.checks) != checks or list(output_value.others) != others:
        return result(False, f"board {number}'s legal moves are not the position's: checks {checks}")
    return result(True, f"board {number}'s {len(puzzle['legal'])} legal moves, {len(checks)} of them checks")
