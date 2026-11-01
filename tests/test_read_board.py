from __future__ import annotations

from pathlib import Path

import chess
import pytest
from PIL import Image

from contract import BoardInput
from plugin import read_board
from plugin.read_board import SIZE, _rows, pieces, read_rows, templates
from verifier.puzzles import PUZZLES

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("number", sorted(PUZZLES))
def test_reads_each_boards_position_from_its_pixels(tmp_path: Path, number: int) -> None:
    rows = list(_rows(number))
    assert rows == list(PUZZLES[number]["rows"])
    # The rows are the position in the puzzle's FEN, as python-chess draws it.
    assert rows == [row.replace(" ", "") for row in str(chess.Board(PUZZLES[number]["fen"])).splitlines()]
    found = read_board(BoardInput(board=number), tmp_path)
    board = chess.Board(PUZZLES[number]["fen"])
    for color, listed in ((chess.WHITE, found.white), (chess.BLACK, found.black)):
        expected = {p.symbol().upper() + chess.square_name(s) for s, p in board.piece_map().items() if p.color == color}
        assert set(listed) == expected and len(listed) == len(expected)
        assert listed[0][0] == "K"
    assert found.white == pieces(rows, True) and found.black == pieces(rows, False)


def test_the_26_square_templates_are_all_different() -> None:
    assert len(templates()) == 26


@pytest.mark.parametrize("number", [0, 51, -1])
def test_refuses_a_board_that_is_not_bundled(tmp_path: Path, number: int) -> None:
    with pytest.raises(ValueError, match="no board"):
        read_board(BoardInput(board=number), tmp_path)


def test_refuses_an_image_of_another_size() -> None:
    with pytest.raises(ValueError, match=f"{SIZE}x{SIZE}"):
        read_rows(Image.new("RGB", (400, 400)))


def test_refuses_a_square_that_holds_something_else() -> None:
    with Image.open(ROOT / "ui" / "boards" / "board-01.png") as image:
        image = image.convert("RGB")
    image.putpixel((24 + 3 * 56 + 5, 24 + 5), (255, 0, 0))  # d8
    with pytest.raises(ValueError, match="square d8"):
        read_rows(image)


def test_nothing_the_agent_can_reach_holds_the_answers() -> None:
    for path in (ROOT / "src").rglob("*.py"):
        if path.name == "make_boards.py":
            continue  # the generator computes the answers; the plugin never runs it
        code = [line for line in path.read_text().splitlines() if not line.lstrip().startswith("#")]
        assert not any("verifier" in line for line in code if line.lstrip().startswith(("import ", "from "))), path
        assert not any("PUZZLES" in line or "best" in line for line in code if "import" in line), path
