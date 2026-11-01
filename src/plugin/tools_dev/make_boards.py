"""Builds the bundled boards: ui/pieces.png (once), ui/boards/board-NN.png, and verifier/puzzles.py.

    uv run python -m plugin.tools_dev.make_boards

The positions are 50 puzzles from the Lichess puzzle database (database.lichess.org, CC0): the first
50 mate-in-1 puzzles in it with 8 pieces or fewer, popularity 90 or more and 2,000 plays or more
that stay clean below, listed in PUZZLES as Lichess gives them. Few pieces, and a mate in one, keep a
position within what RUSH Lab's model can work through in its 2,048-token replies. A puzzle's position is its FEN after the
opponent's first move, with castling and en passant rights removed (an image cannot show them), and
is kept only if that removal changes no answer. Its answers are computed exactly by exhaustive search with python-chess:
the best moves are every move that forces checkmate in the fewest moves (1 or 2), and the legal
moves are all of them. Running it again writes the same files.
"""

from __future__ import annotations

import random
from pathlib import Path

import chess
from PIL import Image, ImageDraw, ImageFont

from plugin.read_board import (
    BOARDS,
    COUNT,
    LETTERS,
    MARGIN,
    PIECES,
    SIZE,
    SQUARE,
    read_rows,
    square_box,
    square_color,
    square_image,
)

ROOT = Path(__file__).resolve().parents[3]
TRUTH = ROOT / "verifier" / "puzzles.py"
FONT = "/System/Library/Fonts/Apple Symbols.ttf"  # draws ui/pieces.png the first time only
GLYPHS = "♚♛♜♝♞♟"  # king, queen, rook, bishop, knight, pawn
SEED = 4804
# (Lichess puzzle id, FEN, the opponent's first move, Lichess's solution move): 50 mates in 1.
PUZZLES = [
    ('00VIe', '8/8/8/P6p/8/2RnkN2/r7/3K4 w - - 1 60', 'f3e1', 'a2d2'),
    ('02Pxu', '6k1/R7/6K1/7P/8/6p1/8/7r b - - 3 58', 'g3g2', 'a7a8'),
    ('05jY1', '8/8/KPk5/8/8/5P2/1r1p3P/3R4 w - - 2 47', 'b6b7', 'b2a2'),
    ('06aAU', '8/3rk1p1/4p3/6Q1/1P3K2/r7/8/8 b - - 2 56', 'e7d6', 'g5c5'),
    ('0BrHk', '8/8/2R5/8/5Kpk/5N2/5rP1/8 b - - 2 61', 'g4f3', 'c6h6'),
    ('0CAsd', '8/8/8/p7/8/3Q3P/r3r1PK/3k4 b - - 16 54', 'a2d2', 'd3b1'),
    ('0Og6f', '7k/7B/6K1/8/8/8/3p4/5R2 b - - 1 52', 'd2d1q', 'f1f8'),
    ('0UEEc', '7k/3q1K2/7p/7Q/8/5P2/8/8 w - - 10 44', 'f7g6', 'd7e6'),
    ('0WC60', '8/P5R1/8/8/8/5k1p/r7/5K2 w - - 5 53', 'g7h7', 'a2a1'),
    ('0XdVp', '6R1/8/8/1r3P1k/5K2/4p3/8/8 b - - 2 62', 'e3e2', 'g8h8'),
    ('0Xnci', '2k5/8/8/8/P2Q1b1q/8/1P5P/7K w - - 0 43', 'b2b4', 'h4h2'),
    ('0ZRIo', '8/8/4R3/8/4p3/P1Pk4/1P4r1/2K5 w - - 11 56', 'a3a4', 'g2g1'),
    ('0abZ0', '6R1/8/8/7p/5p1k/4r3/6PK/8 b - - 29 66', 'f4f3', 'g2g3'),
    ('0bE9W', '8/8/6R1/5k2/8/5q1K/6R1/8 w - - 10 62', 'g2g3', 'f3h1'),
    ('0iBrx', '5Q2/8/6kR/8/6p1/4K3/6r1/q7 b - - 3 56', 'g6g5', 'f8f4'),
    ('0jMPv', '6Q1/8/8/7p/4q2P/6P1/6K1/2k5 w - - 5 74', 'g2h3', 'e4h1'),
    ('0qVaO', '8/1P6/8/4n3/6Bp/6p1/5pK1/4k3 w - - 3 87', 'b7b8q', 'f2f1q'),
    ('0rTqn', '5q2/8/8/8/3R1K2/8/3R1Pk1/8 w - - 1 78', 'f4e3', 'f8f3'),
    ('0wWwD', '5k2/2R5/5K2/5P2/6P1/8/2p5/6r1 b - - 2 58', 'g1g4', 'c7c8'),
    ('0xS2c', '8/7p/6p1/5nB1/4kPK1/8/7P/8 w - - 5 48', 'h2h3', 'h7h5'),
    ('0zRQx', '4K3/7r/4k3/7P/4PB2/6P1/8/8 w - - 2 57', 'h5h6', 'h7h8'),
    ('13JMk', '3k4/3r4/2K3p1/8/1Q6/8/3p1P2/8 b - - 39 94', 'd2d1q', 'b4f8'),
    ('14ZHz', '8/P7/8/8/8/4kn2/7r/5K2 w - - 1 52', 'a7a8q', 'h2f2'),
    ('14bnF', '5R2/5P2/8/8/4p3/1P2k2p/r7/5K2 w - - 1 47', 'f8h8', 'a2a1'),
    ('17MPE', '5k2/1R6/5K2/5p1P/6P1/8/1p6/1r6 b - - 1 47', 'f5g4', 'b7b8'),
    ('18gFE', '4q3/8/6b1/k1QK4/3B4/8/8/8 b - - 5 97', 'a5a6', 'c5b6'),
    ('19qgq', '5R1K/5P2/5kr1/8/8/8/8/8 w - - 5 77', 'f8g8', 'g6h6'),
    ('1FNp3', '8/8/8/6p1/1R3k1p/7P/2r3P1/6K1 b - - 10 56', 'f4g3', 'b4g4'),
    ('1Gz9X', '8/KP6/2k5/8/8/8/8/1r6 w - - 0 80', 'b7b8q', 'b1a1'),
    ('1KnOW', '8/8/P5R1/8/8/4kp2/r7/5K2 w - - 11 60', 'g6f6', 'a2a1'),
    ('1MKox', '8/5k1K/R4p2/5pr1/6P1/8/8/8 w - - 0 61', 'g4f5', 'g5h5'),
    ('1NXEf', '7k/1R5P/3B4/1p6/5K2/nr6/8/8 b - - 2 53', 'b3d3', 'd6e5'),
    ('1QmBm', '8/8/8/R1N2k2/5p2/4p3/P3K1r1/8 w - - 4 42', 'e2f3', 'g2f2'),
    ('1SKwK', '8/8/6pk/R7/5PPK/2r5/8/8 w - - 0 52', 'f4f5', 'g6g5'),
    ('1TbuF', '3Q4/5K2/8/6kp/5pq1/8/8/8 b - - 1 70', 'g5f5', 'd8d5'),
    ('1VzrL', '8/8/8/R7/P7/2k5/r7/2K5 w - - 9 61', 'a5a8', 'a2a1'),
    ('1X96n', '8/6k1/6p1/5nq1/8/2Q5/1P4BK/8 b - - 2 41', 'g7h6', 'c3h8'),
    ('1ZSzV', '4k3/4p3/8/3q3p/5Q1K/6P1/5P2/8 w - - 37 57', 'f4g5', 'd5h1'),
    ('1bJVC', '8/8/6Qp/5p2/7P/4K1P1/4q3/5k2 w - - 7 62', 'e3f4', 'e2e4'),
    ('1dXXW', '8/6PK/5k2/6r1/8/8/8/8 w - - 1 73', 'g7g8q', 'g5h5'),
    ('1hJ6e', '8/8/8/5P2/r6p/5K1k/8/6R1 b - - 2 68', 'a4a5', 'g1h1'),
    ('1hdF1', '8/8/3R4/4N3/4ppb1/4k3/4r3/6K1 b - - 1 57', 'g4f3', 'e5c4'),
    ('1mCoO', '5k2/2R5/5K2/8/6pP/4r1P1/8/8 b - - 2 62', 'e3g3', 'c7c8'),
    ('1sfcM', '4Q3/8/5pkp/3P4/2q5/5K2/8/8 b - - 1 73', 'g6f5', 'e8h5'),
    ('23WyH', '5k2/5P2/4PK2/p2B4/P7/8/2p5/8 b - - 0 59', 'c2c1q', 'e6e7'),
    ('24yL4', '1R6/8/k1K5/8/8/p1P5/8/r7 b - - 8 64', 'a6a5', 'b8a8'),
    ('25B4i', '3k4/5R2/3K4/2B3r1/2p5/3b4/8/8 b - - 27 68', 'g5h5', 'f7f8'),
    ('28Hh7', '8/2Q5/6pk/2R2p2/6K1/6P1/8/7q w - - 0 58', 'g4f4', 'h1e4'),
    ('2CPwD', '4R3/8/5k2/3Qp3/6P1/3K1P2/8/3q4 w - - 4 58', 'd3e4', 'd1e2'),
    ('2ILpx', '2K5/1P2k3/3q4/8/8/8/8/8 w - - 32 80', 'b7b8q', 'd6d7'),
]


def make_pieces() -> None:
    """ui/pieces.png: the 12 sprites, white pieces white with a black outline, black pieces black."""
    font = ImageFont.truetype(FONT, 46)
    sheet = Image.new("RGBA", (SQUARE * len(LETTERS), SQUARE), (0, 0, 0, 0))
    pen = ImageDraw.Draw(sheet)
    for i, letter in enumerate(LETTERS):
        glyph = GLYPHS["KQRBNP".index(letter.upper())]
        center = (i * SQUARE + SQUARE // 2, SQUARE // 2 + 2)
        if letter.isupper():
            pen.text(center, glyph, font=font, anchor="mm", fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
        else:
            pen.text(center, glyph, font=font, anchor="mm", fill=(0, 0, 0, 255))
    sheet.save(PIECES)


def position(fen: str, first: str) -> chess.Board:
    """The puzzle's position: its FEN after the opponent's first move."""
    board = chess.Board(fen)
    board.push_uci(first)
    return chess.Board(board.fen())


def mates_within(board: chess.Board, depth: int) -> bool:
    """Whether the side to move can force checkmate within ``depth`` of its own moves."""
    for move in list(board.legal_moves):
        board.push(move)
        won = wins_after(board, depth)
        board.pop()
        if won:
            return True
    return False


def wins_after(board: chess.Board, depth: int) -> bool:
    """After the attacker's move: whether every defense still loses to mate within ``depth`` moves in all."""
    if board.is_checkmate():
        return True
    if depth == 1 or board.is_game_over():
        return False
    for reply in list(board.legal_moves):
        board.push(reply)
        won = mates_within(board, depth - 1)
        board.pop()
        if not won:
            return False
    return True


def best_moves(board: chess.Board) -> tuple[int, list[str]] | None:
    """(the fewest moves to a forced mate, 1 or 2, and every move that forces it), or None."""
    for depth in (1, 2):
        best = []
        for move in list(board.legal_moves):
            board.push(move)
            if wins_after(board, depth):
                best.append(move.uci())
            board.pop()
        if best:
            return depth, sorted(best)
    return None


def without_rights(board: chess.Board) -> chess.Board:
    parts = board.fen().split()
    parts[2], parts[3] = "-", "-"
    return chess.Board(" ".join(parts))


def draw(board: chess.Board) -> Image.Image:
    image = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    pen = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=14)
    for rank in range(8):
        for file in range(8):
            piece = board.piece_at(chess.square(file, rank))
            image.paste(square_image(square_color(file, rank), piece.symbol() if piece else "."), square_box(file, rank)[:2])
    for i in range(8):
        middle = MARGIN + i * SQUARE + SQUARE // 2
        pen.text((middle, SIZE - MARGIN // 2), "abcdefgh"[i], font=font, fill=(90, 90, 90), anchor="mm")
        pen.text((MARGIN // 2, middle), "87654321"[i], font=font, fill=(90, 90, 90), anchor="mm")
    return image


def main() -> None:
    if not PIECES.is_file():
        make_pieces()
    chosen = []
    for puzzle, fen, first, solution in PUZZLES:
        board = without_rights(position(fen, first))
        found = best_moves(board)
        if found is None or found[0] != 1 or best_moves(position(fen, first)) != found or solution not in found[1]:
            raise SystemExit(f"puzzle {puzzle} is not a clean mate in 1 once castling and en passant are removed")
        chosen.append((puzzle, board, *found))
    if len(chosen) != COUNT:
        raise SystemExit(f"{len(chosen)} puzzles, not {COUNT}")
    random.Random(SEED).shuffle(chosen)
    BOARDS.mkdir(parents=True, exist_ok=True)
    truth = []
    for number, (puzzle, board, depth, best) in enumerate(chosen, 1):
        image = draw(board)
        path = BOARDS / f"board-{number:02d}.png"
        image.save(path, optimize=True)
        rows = [row.replace(" ", "") for row in str(board).splitlines()]
        with Image.open(path) as saved:
            if read_rows(saved) != rows:
                raise SystemExit(f"{path}: read_board does not read back the position drawn")
        side = "white" if board.turn == chess.WHITE else "black"
        legal = sorted(move.uci() for move in board.legal_moves)
        truth.append((number, puzzle, board.fen(), side, depth, best, legal, rows))
    lines = [
        '"""Each bundled board\'s position and answers, as src/plugin/tools_dev/make_boards.py computed them from',
        "Lichess puzzles (CC0) with python-chess. Generated: do not edit.",
        "",
        "best: every move that forces checkmate in mate_in moves, the fewest possible; legal: every legal move;",
        'rows: the position as read_board gives it."""',
        "",
        f"COUNT = {COUNT}",
        "PUZZLES = {",
    ]
    for number, puzzle, fen, side, depth, best, legal, rows in truth:
        lines.append(
            f"    {number}: {{'lichess': {puzzle!r}, 'fen': {fen!r}, 'to_move': {side!r}, 'mate_in': {depth}, "
            f"'best': {tuple(best)!r}, 'legal': {tuple(legal)!r}, 'rows': {tuple(rows)!r}}},"
        )
    lines.append("}")
    TRUTH.write_text("\n".join(lines) + "\n")
    print(f"wrote {COUNT} boards to {BOARDS} and their answers to {TRUTH}")


if __name__ == "__main__":
    main()
