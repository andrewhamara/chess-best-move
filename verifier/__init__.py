"""The deterministic verifier: each tool's checks live in its own module, on contract instances.

It holds the ground truth, verifier/puzzles.py: each board's position, every legal move and every
move that forces mate in the fewest moves. Nothing else does: the plugin's tool reads the board's
pixels and never knows the answer.
"""

from contract import Task, Tool

from . import read_board, task

TOOLS = {
    Tool.READ_BOARD: read_board,
}


def _tool_output(module):
    """A tool task's check: its output judged as its one tool's verify_output judges it."""
    return lambda arguments, output, reference, workspace: module.verify_output(arguments, output, workspace)


# task -> its output's check, verify_task(arguments, output, reference, workspace)
TASKS = {
    Task.BEST_MOVE: task.verify_task,
    Task.SHOW_BOARD: _tool_output(read_board),
}


def verify_input(tool, value):
    return TOOLS[Tool(tool)].verify_input(value)


def verify_output(tool, input_value, output_value, workspace):
    return TOOLS[Tool(tool)].verify_output(input_value, output_value, workspace)


def verify_task(task, arguments, output, reference, workspace):
    return TASKS[Task(task)](arguments, output, reference, workspace)
