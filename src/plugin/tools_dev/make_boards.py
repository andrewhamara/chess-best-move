"""Builds the bundled boards: ui/pieces.png (once), ui/boards/board-NN.png, and verifier/puzzles.py.

    uv run python -m plugin.tools_dev.make_boards

The positions are 50 puzzles from the Lichess puzzle database (database.lichess.org, CC0): the first
25 mate-in-1 and 25 mate-in-2 puzzles in it with popularity 90 or more and 5,000 plays or more that
stay clean below, listed in PUZZLES as Lichess gives them. A puzzle's position is its FEN after the
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
    ('00Mbv', '2k2b1r/pp3ppp/1n6/BN2p1P1/2Q1Nn1P/8/PP3P2/2KR4 b - - 0 24', 'b6c4', 'd1d8'),
    ('00VIe', '8/8/8/P6p/8/2RnkN2/r7/3K4 w - - 1 60', 'f3e1', 'a2d2'),
    ('00y2j', '3r4/1pB3kp/2b1Pp2/1pN2RpK/1P6/7P/6r1/8 w - - 0 34', 'c7d8', 'c6e8'),
    ('015mX', 'r3k2r/1ppqb2p/p1b1N1p1/3pPR2/3P2Q1/2P5/PP4PP/RNB3K1 b kq - 0 14', 'g6f5', 'g4h5'),
    ('01bwq', 'r1b2k1r/pppq1ppp/1n6/1B1PQ1B1/8/2P5/P4PPP/R3K2R b KQ - 2 15', 'd7d6', 'e5e8'),
    ('01p5M', '1r6/p1p2n2/1pk2Pp1/6r1/8/2N5/PPP4K/3R1R2 w - - 2 24', 'f1g1', 'b8h8'),
    ('021U1', 'r7/bp6/4kNQ1/1b2Pp1p/p2R1P1N/P1q2K2/6PP/7R w - - 5 31', 'f3f2', 'a7d4'),
    ('0257T', 'r2qnr1k/pppb2pp/2n2b1B/3NN3/8/P5QP/1PP1B1P1/R4RK1 b - - 0 18', 'f6e5', 'f1f8'),
    ('030I0', '5r2/4r1k1/3p1pbp/1Pp5/2P5/P2PqR1B/4P2p/1R2QK2 w - - 0 32', 'h3g2', 'e3g1'),
    ('053dH', 'rn2kb1r/pQp1pppp/8/4q3/2b5/8/PP1PBPPP/R1B1K1NR b KQkq - 0 8', 'c4d5', 'b7c8'),
    ('056MT', '1rr3k1/2qN1p2/b3pbpQ/n1p5/P1P2P2/P3P2R/1B4PP/R5K1 b - - 1 23', 'f6b2', 'h6h7'),
    ('05CJZ', '8/2k2p1r/1p2p2P/p2pPnP1/P2P1PKB/2P1n3/5R2/4R3 w - - 10 47', 'g4h5', 'f5g7'),
    ('05StG', 'r2q1r1k/pp2b1pp/8/2p1Np2/2BpP1b1/P2P4/2P2PK1/R1BQ3R b - - 1 17', 'g4d1', 'e5g6'),
    ('060cV', 'r1bk3r/1p3R1p/pR1Bp1p1/3p4/B1nP4/2K1P3/P4PPP/8 b - - 2 23', 'c4b6', 'd6c7'),
    ('06W3x', '1b6/2p5/P1B5/1P6/1K1P1Q1k/4P3/3n4/2q5 b - - 2 45', 'h4h5', 'c6e8'),
    ('074gd', '2k2q2/1pp5/p1p5/4p1Rp/4N2n/3P3P/PPP2P1K/R7 w - - 2 26', 'h2g3', 'f8f4'),
    ('07IW0', 'r1bq1b1r/ppp2Q1p/2n1kn2/4N3/3Pp3/8/PPP2PPP/R1B1K2R b KQ - 3 12', 'e6f5', 'g2g4'),
    ('07Syw', '6k1/p4pp1/4p2p/8/P3Pq2/7B/3Q1P1n/4RK2 w - - 1 31', 'f1e2', 'f4f3'),
    ('08jJr', '1r1r2k1/2p3pp/2P2p2/p1n2P2/P1PNb3/2K5/4B2P/R5R1 w - - 0 29', 'd4e6', 'b8b3'),
    ('08qTY', 'r1b1kb1r/2q2p1p/p2p1n2/1pp1p1p1/3nP1PN/PP1P3P/1BP1NP2/R2QKB1R w KQkq - 0 12', 'h4g2', 'd4f3'),
    ('09K3K', '2r5/pp3p1p/4p3/1N2kp2/2P5/1P1K2P1/P2B3P/8 b - - 1 26', 'a7a6', 'd2c3'),
    ('09kAc', '8/4Q2p/5ppk/p7/P3BP2/4n1PK/4q2P/8 w - - 9 49', 'e7f6', 'e2g4'),
    ('09nQI', '6k1/8/4p2p/2b1P3/1p6/5qNp/PR1Q3B/6K1 w - - 3 36', 'd2f2', 'f3g2'),
    ('0BWCC', '2r1k2r/npqbb1p1/4ppp1/p2pP1N1/3P4/P1N1BQ2/1P3PPP/1R3RK1 w k - 0 17', 'e5f6', 'c7h2'),
    ('0BYqL', 'r2k1r2/1p4pQ/4R2p/p1p1b3/P4q2/BBp4P/6P1/R6K w - - 1 28', 'a3c5', 'f4h2'),
    ('005Bm', '4rk2/p1q5/1p3Q1b/8/1p5N/2P1p3/P3P3/2K5 b - - 0 43', 'c7f7', 'h4g6'),
    ('006pe', 'r4r2/2q1NN2/4bQpk/2n4p/pp5P/8/1PP2PP1/2KR3R b - - 0 28', 'e6f7', 'e7f5'),
    ('009BH', '3r2k1/6p1/4Q3/4B3/1p3P2/4PKP1/3q4/8 b - - 17 51', 'g8h8', 'e6h6'),
    ('00NUS', '4rk2/pbp2pp1/1p1b4/3P1q2/QPBPN3/1KP2P2/P5r1/R3R3 w - - 0 25', 'e4d6', 'f5c2'),
    ('00Se9', '5rk1/pp1n2r1/3p2N1/2pQ4/2P5/4P1P1/qP2KPP1/7R b - - 1 24', 'g7f7', 'g6e7'),
    ('00WqT', 'r4r2/1ppb1p2/p2p2pk/5P2/4P3/2PBB1R1/PKP2P1q/8 b - - 4 26', 'h6h5', 'd3e2'),
    ('00Wyh', '2r5/8/8/pNp1r2p/3kNppP/1P1P4/2R2K2/8 b - - 2 42', 'd4d3', 'c2d2'),
    ('00YbZ', 'b6k/8/6p1/4q2p/1Q3r1P/P1N3R1/1PP3PK/8 w - - 3 35', 'b4b6', 'f4h4'),
    ('00ZEc', '1r3bk1/5p2/3P1qRP/r1n1p3/ppB5/P2Q1P2/1PP5/1K6 b - - 0 35', 'g8h7', 'g6g7'),
    ('00aDl', 'r5k1/1p3p2/2p1ppp1/3p4/2nP4/1QB2B1P/rPP2PP1/qNKR3R w - - 3 22', 'f3e2', 'a1b1'),
    ('00hSr', 'r4rk1/5p2/1q2pnRP/p2p4/1ppP4/2P1P3/PPQN1P2/2K4R b - - 0 21', 'f7g6', 'c2g6'),
    ('00mRr', '8/2Q2kpp/1p1p2r1/1PnN4/2P1n3/6P1/1r3PK1/8 b - - 6 41', 'f7e6', 'c7e7'),
    ('00ouE', '2r5/2r3k1/1p2pp1p/p2pQ1p1/3P4/4P1P1/PPq2P1R/KR6 w - - 0 30', 'e5e6', 'c2b1'),
    ('00qk4', '3r4/ppN1kppp/5n2/8/1n3Nb1/4P3/1B3PPP/R3KB1R w KQ - 0 18', 'a1c1', 'b4c2'),
    ('00rNc', '1q5r/p3kpp1/2Q1p2p/3pP2P/2n3P1/2N2P2/PrP5/K3R1NR w - - 0 26', 'g1e2', 'b2a2'),
    ('00rqm', '2r2r1k/3b3n/p6q/1p1nN3/7P/3P2Q1/PPP2P2/1K4RR b - - 0 30', 'd7f5', 'g3g8'),
    ('00tgU', 'r4rk1/pbpp2p1/1pn3Qp/3N4/3q1N2/3B4/PP3PPP/5RK1 b - - 5 20', 'c6e5', 'd5e7'),
    ('00voi', '1r6/2r2p1R/7R/4pPk1/2B2n2/1P3P1P/P4K2/8 b - - 0 43', 'c7c4', 'h3h4'),
    ('00wft', '3r2k1/pp3pp1/7p/b7/2b3Q1/P2qPN1P/3N1PP1/3RK2R w K - 0 30', 'f3e5', 'a5d2'),
    ('00zNz', 'r1bqk2r/pp1np1bp/2p3p1/3pNB2/3P1B2/4P3/PPP2PPP/R2QK2R b KQkq - 0 10', 'g6f5', 'd1h5'),
    ('01EMd', 'r6k/4q1pp/1n1pBp2/2p1nP2/1p2R2Q/1P5P/r5P1/2B1R1K1 b - - 6 31', 'b6d7', 'h4h7'),
    ('01EUl', 'r2qk2r/ppp2pp1/2p2n2/7p/3bP1b1/2N3Q1/PPP2PPP/R1B1KB1R w KQkq - 0 9', 'h2h3', 'd4c3'),
    ('01GBu', '5r1k/3p2bp/p4pp1/qp1br3/4P3/1Q4B1/PP2RPPP/4R1K1 w - - 0 23', 'e4d5', 'a5e1'),
    ('01Hgu', '2k5/p1p5/r6q/3b4/8/3P4/PPP2P1P/R1B2RK1 w - - 0 31', 'c1h6', 'a6g6'),
    ('01J3q', 'r3r1k1/ppq1ppb1/2p3nN/2Pp3p/3Pn2N/1P2P2P/PB3QP1/R4RK1 b - - 9 23', 'g7h6', 'f2f7'),
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
