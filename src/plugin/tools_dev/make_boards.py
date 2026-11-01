"""Builds the bundled boards: ui/pieces.png (once), ui/boards/board-NN.png, and verifier/puzzles.py.

    uv run python -m plugin.tools_dev.make_boards

The positions are 50 puzzles from the Lichess puzzle database (database.lichess.org, CC0): the first
25 mate-in-1 and 25 mate-in-2 puzzles in it with 10 pieces or fewer, popularity 90 or more and 2,000
plays or more that stay clean below, listed in PUZZLES as Lichess gives them. Few pieces keep a
position within what RUSH Lab's model can work through in one 2,048-token reply. A puzzle's position is its FEN after the
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
# (Lichess puzzle id, FEN, the opponent's first move, Lichess's solution move): 25 mates in 1, then 25
# mates in 2.
PUZZLES = [
    ('00VIe', '8/8/8/P6p/8/2RnkN2/r7/3K4 w - - 1 60', 'f3e1', 'a2d2'),
    ('02Pxu', '6k1/R7/6K1/7P/8/6p1/8/7r b - - 3 58', 'g3g2', 'a7a8'),
    ('02SWp', 'Q7/6pk/7p/6PP/8/pq6/5PK1/8 b - - 0 39', 'a3a2', 'g5g6'),
    ('04vvt', '8/8/2p1RN2/4P1k1/3PK1P1/r7/4b3/8 w - - 7 52', 'e6c6', 'e2f3'),
    ('05jY1', '8/8/KPk5/8/8/5P2/1r1p3P/3R4 w - - 2 47', 'b6b7', 'b2a2'),
    ('06aAU', '8/3rk1p1/4p3/6Q1/1P3K2/r7/8/8 b - - 2 56', 'e7d6', 'g5c5'),
    ('09vxG', '2r5/8/8/P7/1K1P2NP/4Bq2/1R6/6k1 b - - 1 62', 'g1h1', 'b2h2'),
    ('0BrHk', '8/8/2R5/8/5Kpk/5N2/5rP1/8 b - - 2 61', 'g4f3', 'c6h6'),
    ('0C5UE', '6Q1/1p6/7k/8/3r4/Pp6/7r/1R1K2R1 w - - 2 59', 'd1c1', 'h2c2'),
    ('0CAJl', '8/1P6/4p1k1/6P1/1PpP3P/2K5/8/5q2 w - - 0 44', 'b7b8q', 'f1c1'),
    ('0CAsd', '8/8/8/p7/8/3Q3P/r3r1PK/3k4 b - - 16 54', 'a2d2', 'd3b1'),
    ('0D5c0', '8/4R3/3p2k1/6P1/1p2P1KP/8/r1p5/8 b - - 1 46', 'c2c1q', 'h4h5'),
    ('0FLeU', '8/R3b1k1/4P3/5P1p/4P1rK/8/P7/8 w - - 4 46', 'h4h5', 'g4h4'),
    ('0Ftzc', '6k1/R4p2/7p/4B2K/5P2/5b2/6r1/8 w - - 1 36', 'h5h6', 'g2g6'),
    ('0Gjvb', '1k6/6R1/1P5p/5B2/5P2/5nP1/1r6/6K1 w - - 1 46', 'g1h1', 'b2h2'),
    ('0Kk4G', '8/8/7p/2Q1Pp2/3K1P1k/2P5/8/1q6 w - - 3 47', 'e5e6', 'b1e4'),
    ('0Ljrm', '4Q3/8/3q3k/3p2pP/4p3/7P/5P2/6K1 b - - 7 44', 'd5d4', 'e8h8'),
    ('0MwbE', '6Q1/8/6pk/1q5p/5P2/8/1p3PK1/8 b - - 1 59', 'b2b1q', 'g8h8'),
    ('0NS5X', '8/8/3R4/1bk2p2/4pB2/4K1P1/2r4P/8 w - - 5 43', 'd6f6', 'c2e2'),
    ('0Og6f', '7k/7B/6K1/8/8/8/3p4/5R2 b - - 1 52', 'd2d1q', 'f1f8'),
    ('0Qi5Z', '8/8/4k3/R3P2P/6p1/3r4/2r3PK/6R1 w - - 1 56', 'h5h6', 'd3h3'),
    ('0QzFM', '8/6R1/4p3/4Pk2/2r2n2/P1p2K2/8/2B5 b - - 0 43', 'f4d3', 'g7g5'),
    ('0UEEc', '7k/3q1K2/7p/7Q/8/5P2/8/8 w - - 10 44', 'f7g6', 'd7e6'),
    ('0WC60', '8/P5R1/8/8/8/5k1p/r7/5K2 w - - 5 53', 'g7h7', 'a2a1'),
    ('0XdVp', '6R1/8/8/1r3P1k/5K2/4p3/8/8 b - - 2 62', 'e3e2', 'g8h8'),
    ('00FND', '8/1P6/8/7p/3P4/3k1p1P/4p3/3K4 w - - 0 49', 'd1e1', 'd3e3'),
    ('029mV', '8/8/5k2/1p4p1/1R1P2K1/6R1/3r2b1/8 w - - 0 37', 'b4b5', 'd2d4'),
    ('02DwR', 'k7/P7/1K6/1N6/8/4p1p1/3n4/8 b - - 1 59', 'd2c4', 'b6a6'),
    ('02ZzV', '8/7b/8/p7/2BNpn2/k1K1p3/P7/8 b - - 9 58', 'f4d3', 'c4b3'),
    ('02kCY', '8/8/8/7p/p1b5/P5kP/2p3P1/2B3K1 b - - 7 46', 'g3h4', 'g1h2'),
    ('035m4', '4r3/5k2/6R1/5PP1/8/r4K2/4p3/4R3 w - - 0 37', 'f3g4', 'e8e4'),
    ('0416t', '7k/1Q4bp/6p1/8/8/8/5RPP/q5K1 w - - 1 27', 'f2f1', 'g7d4'),
    ('04VNP', '8/8/5pkp/6p1/8/7P/2Q3PK/q7 b - - 3 52', 'g6h5', 'g2g4'),
    ('05t5o', '8/8/8/p1R5/6P1/1P3k2/r6P/6K1 w - - 1 39', 'g4g5', 'a2a1'),
    ('05xMB', '8/4p2k/3p4/4b3/8/2pq4/5PR1/2Q4K w - - 0 47', 'c1g5', 'd3f1'),
    ('06PHz', '8/8/P1p5/2P5/2P1Pk1p/7p/6p1/6K1 w - - 1 43', 'a6a7', 'f4g3'),
    ('06fJG', '6rk/5R2/8/5BKP/3b2P1/8/8/8 w - - 11 55', 'g5h6', 'd4e3'),
    ('07a2d', '5Q2/8/2p1k1p1/8/qP6/2PKP3/8/8 w - - 7 55', 'f8f4', 'a4d1'),
    ('08FHm', '8/5Kpk/p1Q5/1p3P2/8/2p1q3/P7/8 b - - 3 46', 'e3g3', 'c6h1'),
    ('09Pcz', '3k4/3P4/2P1K3/5p2/7p/6pP/8/8 b - - 0 49', 'g3g2', 'e6d6'),
    ('09aSK', '4q3/1k6/8/1K6/2Q1N3/b7/8/8 w - - 20 69', 'b5a5', 'e8a8'),
    ('0AbbE', '4k3/2R5/5P2/4p1B1/8/b7/r1p2PK1/8 b - - 0 40', 'e5e4', 'f6f7'),
    ('0C9ct', '8/8/2Q5/p5p1/Pq6/1k4K1/6P1/8 w - - 4 46', 'c6d7', 'b4f4'),
    ('0DZXq', 'Q7/6R1/2Bp4/2n5/5k2/2P1p3/1r2K3/8 w - - 0 50', 'e2d1', 'e3e2'),
    ('0DslH', 'r7/8/5p2/7p/p5kP/R5P1/5KP1/8 b - - 4 54', 'f6f5', 'a3f3'),
    ('0EcCu', '8/6R1/7k/8/5R2/6PK/8/3q4 w - - 4 82', 'g7g8', 'd1h1'),
    ('0EtoC', '8/8/5k1P/6p1/6Q1/5p1K/5P2/4q3 w - - 2 49', 'h6h7', 'e1h1'),
    ('0GzwQ', '6k1/1R6/6P1/6K1/8/6p1/7r/8 b - - 9 64', 'g3g2', 'g5f6'),
    ('0I1wj', 'R3bk2/5n1R/6K1/8/5r1P/8/8/8 b - - 5 56', 'f4b4', 'h7f7'),
    ('0IKWe', '8/8/8/1B6/1R6/p1P1nk2/r7/2K5 w - - 0 48', 'b4a4', 'a2a1'),
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
        if found is None or best_moves(position(fen, first)) != found or solution not in found[1]:
            raise SystemExit(f"puzzle {puzzle} is not a clean mate in 1 or 2 once castling and en passant are removed")
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
        checks = sorted(move.uci() for move in board.legal_moves if board.gives_check(move))
        truth.append((number, puzzle, board.fen(), side, depth, best, legal, checks, rows))
    lines = [
        '"""Each bundled board\'s position and answers, as src/plugin/tools_dev/make_boards.py computed them from',
        "Lichess puzzles (CC0) with python-chess. Generated: do not edit.",
        "",
        "best: every move that forces checkmate in mate_in moves, the fewest possible; legal: every legal move;",
        "checks: the legal moves that give check;",
        'rows: the position as read_board gives it."""',
        "",
        f"COUNT = {COUNT}",
        "PUZZLES = {",
    ]
    for number, puzzle, fen, side, depth, best, legal, checks, rows in truth:
        lines.append(
            f"    {number}: {{'lichess': {puzzle!r}, 'fen': {fen!r}, 'to_move': {side!r}, 'mate_in': {depth}, "
            f"'best': {tuple(best)!r}, 'legal': {tuple(legal)!r}, 'checks': {tuple(checks)!r}, 'rows': {tuple(rows)!r}}},"
        )
    lines.append("}")
    TRUTH.write_text("\n".join(lines) + "\n")
    print(f"wrote {COUNT} boards to {BOARDS} and their answers to {TRUTH}")


if __name__ == "__main__":
    main()
