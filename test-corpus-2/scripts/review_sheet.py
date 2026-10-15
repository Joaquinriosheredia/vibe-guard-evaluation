"""Joaquín's review sheet and its conversion to the official verdicts (PREREGISTRATION.md,
"Reviewers, cards and blindness").

  python3 scripts/review_sheet.py sheet   -> REVIEW-SHEET.md: the review-set IDs in order, each with
                                             only a link to its card and empty fields (once)
  python3 scripts/review_sheet.py audit   -> audit-joaquin.json from REVIEW-SHEET.md; fails if any
                                             verdict is missing or not TP/FP/U, a reason is missing,
                                             or Overstated is not Sí/No
"""
import json
import re
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
VERDICTS = ("TP", "FP", "U")
OVERSTATED = {"sí": True, "si": True, "no": False}
FIELDS = ("Verdict", "Reason (file:line)", "Overstated")
_FIELD_RE = re.compile(r"^- (Verdict|Reason \(file:line\)|Overstated):[ \t]*(.*)$")


def render_sheet(ids):
    md = ["# Review sheet — test-corpus-2", "",
          "Official verdicts: Joaquín only. One block per finding, in the order of `review-set.json`.",
          "Fill `Verdict` (TP, FP or U), `Reason (file:line)` and `Overstated` (Sí or No).",
          "Rules: `REVIEW-GUIDE.md`. Any help received: `REVIEW-LOG.md`.", ""]
    for i in ids:
        md += [f"## {i}", "", f"- Card: [cards/{i}.md](cards/{i}.md)", "- Verdict: ", "- Reason (file:line): ", "- Overstated: ", ""]
    return "\n".join(md)


def parse_sheet(text, ids):
    """REVIEW-SHEET.md text -> verdict list in `ids` order. Raises ValueError listing every problem."""
    blocks, current = {}, None
    for line in text.splitlines():
        h = re.match(r"^## (\S+)\s*$", line)
        if h:
            current = h.group(1)
            if current in blocks:
                raise ValueError(f"{current}: appears twice")
            blocks[current] = {}
            continue
        m = _FIELD_RE.match(line)
        if m and current:
            blocks[current][m.group(1)] = m.group(2).strip()
    problems = []
    if list(blocks) != list(ids):
        problems.append(f"the IDs are not exactly the review set in order (sheet {len(blocks)}, review set {len(ids)})")
    out = []
    for i in ids:
        b = blocks.get(i, {})
        verdict, reason, over = b.get("Verdict", ""), b.get("Reason (file:line)", ""), b.get("Overstated", "")
        if verdict not in VERDICTS:
            problems.append(f"{i}: verdict {verdict!r} is not TP, FP or U" if verdict else f"{i}: verdict missing")
        if not reason:
            problems.append(f"{i}: reason missing")
        if over.lower() not in OVERSTATED:
            problems.append(f"{i}: Overstated {over!r} is not Sí or No" if over else f"{i}: Overstated missing")
        out.append({"id": i, "verdict": verdict, "reason": reason, "overstated": OVERSTATED.get(over.lower())})
    if problems:
        raise ValueError("\n".join(problems))
    return out


def review_ids():
    return [f["id"] for f in json.loads((DIR / "review-set.json").read_text())["findings"]]


def main(cmd):
    if cmd == "sheet":
        out = DIR / "REVIEW-SHEET.md"
        if out.exists():
            raise SystemExit("REVIEW-SHEET.md exists: it is generated once")
        out.write_text(render_sheet(review_ids()) + "\n")
        print(f"REVIEW-SHEET.md: {len(review_ids())} findings")
    elif cmd == "audit":
        out = DIR / "audit-joaquin.json"
        if out.exists():
            raise SystemExit("audit-joaquin.json exists")
        try:
            verdicts = parse_sheet((DIR / "REVIEW-SHEET.md").read_text(), review_ids())
        except ValueError as e:
            raise SystemExit(f"REVIEW-SHEET.md is not complete:\n{e}")
        out.write_text(json.dumps({"reviewer": "Joaquín", "source": "REVIEW-SHEET.md", "verdicts": verdicts}, indent=2, ensure_ascii=False) + "\n")
        print(f"audit-joaquin.json: {len(verdicts)} verdicts")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
