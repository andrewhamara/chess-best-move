// How this plugin's page draws its tasks' outputs: the board image (ui/boards/) with an SVG drawn
// over it as a data: image. A best-move answer draws the agent's move as an orange arrow and, when it
// is not a best move, the forced mate's first move as a dashed green one, then the verdict's checks;
// show-board shows the board and the rows the agent reads.
import { disclosure, h } from "./kit/components.js";

const SIZE = 496;
const MARGIN = 24;
const SQUARE = 56;
const AGENT = "#f08c00";
const BEST = "#2b8a3e";
const file = (n) => `boards/board-${String(n).padStart(2, "0")}.png`;

/** A square's center in the image, e.g. "e4" -> [x, y]. */
function center(square) {
  const col = "abcdefgh".indexOf(square[0]);
  const row = Number(square[1]) - 1;
  return [MARGIN + col * SQUARE + SQUARE / 2, MARGIN + (7 - row) * SQUARE + SQUARE / 2];
}

/** An arrow for a UCI move, or nothing when the move is not one. */
function arrow(move, color, id, dashed) {
  if (!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(move) || move.slice(0, 2) === move.slice(2, 4)) return "";
  const [x1, y1] = center(move.slice(0, 2));
  const [x2, y2] = center(move.slice(2, 4));
  const dash = dashed ? ' stroke-dasharray="9 7"' : "";
  return (
    `<defs><marker id="${id}" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" orient="auto">` +
    `<path d="M0 0L10 5L0 10z" fill="${color}"/></marker></defs>` +
    `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="8" stroke-linecap="round" ` +
    `opacity="0.85" marker-end="url(#${id})"${dash}/>`
  );
}

const svg = (parts) =>
  `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SIZE} ${SIZE}">${parts.join("")}</svg>`)}`;

const picture = (board, overlay) =>
  h(
    "div",
    { class: "chess-frame" },
    h("img", { class: "chess-img", src: file(board), alt: `Board ${board}`, width: SIZE, height: SIZE }),
    overlay ? h("img", { class: "chess-overlay", src: svg(overlay), alt: "", width: SIZE, height: SIZE }) : null,
  );

const MARKS = { true: ["✓", "ok"], false: ["✗", "bad"], null: ["·", "skipped"] };

/** The verdict's checks, each with its mark and, when it failed or was skipped, why. */
const checks = (constraints) =>
  h(
    "ol",
    { class: "chess-checks" },
    constraints.map(({ id, constraint, ok, message }) => {
      const [mark, tone] = MARKS[String(ok)];
      return h(
        "li",
        { class: `chess-check ${tone}` },
        h("span", { class: "chess-mark", text: mark }),
        h("span", {}, h("code", { text: id }), ` ${constraint}`, message ? h("span", { class: "chess-why", text: message }) : null),
      );
    }),
  );

export default {
  BoardOutput: ({ board, rows }) =>
    h(
      "div",
      { class: "chess-card" },
      picture(board, null),
      disclosure({ summary: "The rows the agent reads", className: "chess-text" }, h("pre", { class: "chess-rows", text: rows.join("\n") })),
    ),
  MoveOutput: ({ board, to_move, move }, { verdict }) => {
    const details = verdict.details || {};
    const best = (details.expected && details.expected.best) || [];
    const right = best.includes(move);
    const overlay = [arrow(move, AGENT, "agent", false)];
    if (best.length && !right) overlay.push(arrow(best[0], BEST, "best", true));
    return h(
      "div",
      { class: "chess-card" },
      h(
        "p",
        { class: "chess-move" },
        h("span", { class: "muted", text: `Board ${board}, ${to_move} to move · agent's move ` }),
        h("strong", { text: move }),
        details.expected ? h("span", { class: "muted", text: ` · forced mate in ${details.expected.mate_in}: ${best.join(" or ")}` }) : null,
      ),
      picture(board, overlay),
      h(
        "p",
        { class: "chess-legend muted" },
        h("span", { class: "chess-key" }, h("span", { class: "chess-swatch agent" }), "the agent's move"),
        best.length && !right ? h("span", { class: "chess-key" }, h("span", { class: "chess-swatch best" }), "the forced mate") : null,
      ),
      details.constraints ? checks(details.constraints) : null,
    );
  },
};
