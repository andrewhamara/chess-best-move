"""read_board: the position on a bundled board image, read square by square from its pixels.

A board is 8x8 squares of SQUARE px inside a MARGIN of coordinates, white at the bottom. Every
square is a light or dark square, empty or with one of the 12 piece sprites in ui/pieces.png drawn
on it, so each square's pixels equal exactly one of 26 templates. The position comes back as each
side's pieces by square. A square that matches none is refused: the boards hold nothing else. read_board says what stands where and never which move is
best: only the verifier holds the answers.
"""

from __future__ import annotations

import re
from functools import cache
from pathlib import Path

from PIL import Image

from contract import BoardInput, BoardOutput

UI = Path(__file__).resolve().parents[2] / "ui"
BOARDS = UI / "boards"
PIECES = UI / "pieces.png"  # 12 sprites of SQUARE px in a row, in the order of LETTERS
BOARD_ID = re.compile(r"^\d+$")
SQUARE = 56
MARGIN = 24
SIZE = 2 * MARGIN + 8 * SQUARE
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
LETTERS = "KQRBNPkqrbnp"  # white pieces upper case, black lower case
COUNT = 50


def board_path(number: int) -> Path:
    path = BOARDS / f"board-{number:02d}.png"
    if not 1 <= number <= COUNT or not path.is_file():
        raise ValueError(f"no board {number}: the boards are 1 to {COUNT}")
    return path


def square_color(file: int, rank: int) -> tuple[int, int, int]:
    """The color of the square on ``file`` (0 = a) and ``rank`` (0 = 1): a1 is dark."""
    return DARK if (file + rank) % 2 == 0 else LIGHT


def square_box(file: int, rank: int) -> tuple[int, int, int, int]:
    left = MARGIN + file * SQUARE
    top = MARGIN + (7 - rank) * SQUARE
    return left, top, left + SQUARE, top + SQUARE


@cache
def sprites() -> tuple[Image.Image, ...]:
    with Image.open(PIECES) as sheet:
        sheet = sheet.convert("RGBA")
        return tuple(sheet.crop((i * SQUARE, 0, (i + 1) * SQUARE, SQUARE)) for i in range(len(LETTERS)))


def square_image(color: tuple[int, int, int], letter: str) -> Image.Image:
    """A square of ``color`` with the piece ``letter`` on it, or empty for '.'."""
    tile = Image.new("RGBA", (SQUARE, SQUARE), (*color, 255))
    if letter != ".":
        tile.alpha_composite(sprites()[LETTERS.index(letter)])
    return tile.convert("RGB")


@cache
def templates() -> dict[bytes, str]:
    """Each square's pixels -> what stands on it: 12 pieces and empty, on light and dark squares."""
    return {square_image(color, letter).tobytes(): letter for color in (LIGHT, DARK) for letter in "." + LETTERS}


def read_rows(image: Image.Image) -> list[str]:
    """The position as 8 rows, rank 8 first, files a to h: a piece letter or '.' per square."""
    if image.size != (SIZE, SIZE):
        raise ValueError(f"a board image is {SIZE}x{SIZE} px, not {image.size[0]}x{image.size[1]}")
    image = image.convert("RGB")
    known = templates()
    rows = []
    for rank in range(7, -1, -1):
        row = ""
        for file in range(8):
            pixels = image.crop(square_box(file, rank)).tobytes()
            if pixels not in known:
                raise ValueError(f"square {'abcdefgh'[file]}{rank + 1} holds nothing a board holds")
            row += known[pixels]
        rows.append(row)
    return rows


@cache
def _rows(number: int) -> tuple[str, ...]:
    """The board's rows, read once: the bundled images never change."""
    with Image.open(board_path(number)) as image:
        return tuple(read_rows(image))


ORDER = "KQRBNP"


def pieces(rows: list[str], white: bool) -> list[str]:
    """One side's pieces by square, e.g. ['Kd3', 'Bd2', 'Pa2']: king first, then by kind, then by square."""
    found = [
        (ORDER.index(char.upper()), "abcdefgh"[file] + str(8 - y), char.upper())
        for y, row in enumerate(rows)
        for file, char in enumerate(row)
        if char != "." and char.isupper() == white
    ]
    return [letter + square for _, square, letter in sorted(found)]


def read_board(given: BoardInput, workspace: Path) -> BoardOutput:
    """What stands on each square of the board, read from its pixels: each side's pieces by square."""
    rows = list(_rows(given.board))
    return BoardOutput(board=given.board, white=pieces(rows, True), black=pieces(rows, False))
