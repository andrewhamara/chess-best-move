"""legal_moves and consider_move: what they say about a board's moves is what the rules say, for the side to move."""

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


def verify_consider_input(value):
    problem = board_problem(value.board)
    if problem:
        return result(False, problem)
    if len(value.note) > 300:
        return result(False, "the note is one short line, not a page")
    return result(True, "input is valid")


def verify_consider_output(input_value, output_value, workspace):
    """``output_value``: a contract ConsiderOutput: the move and note echoed, and the true position after it."""
    from .read_board import pieces

    number, side, move = input_value.board, input_value.to_move.value, input_value.move
    puzzle = PUZZLES[number]
    echoed = (output_value.board, output_value.to_move.value, output_value.move, output_value.note)
    if echoed != (number, side, move, input_value.note):
        return result(False, "the output does not echo the board, side, move and note given")
    if side != puzzle["to_move"]:
        return result(False, f"on board {number} it is {puzzle['to_move']} to move, not {side}")
    if move not in puzzle["after"]:
        return result(False, f"{move} is not a legal move on board {number}")
    rows = list(puzzle["after"][move])
    if list(output_value.white) != pieces(rows, True) or list(output_value.black) != pieces(rows, False):
        return result(False, f"the position after {move} on board {number} is misreported")
    return result(True, f"the position after {move} on board {number}")
