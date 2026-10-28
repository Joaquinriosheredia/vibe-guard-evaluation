"""Joaquín's review sheet and its conversion to his verdicts (PREREGISTRATION.md, "Review method").

  python3 scripts/review_sheet.py sheet   -> REVIEW-SHEET.md: the IDs of REVIEW-AB.md (disagreements
                                             and audit sample) shuffled with random.Random(20261105),
                                             each with only a link to its card and empty fields (once)
  python3 scripts/review_sheet.py audit   -> audit-joaquin.json from REVIEW-SHEET.md; fails if any
                                             verdict is missing or not TP/FP/U, a reason is missing,
                                             or Overstated is not "Sí"/"No", optionally followed by
                                             " — " and a note (kept as overstated_note; test-corpus-2 DEVIATIONS.md §3c)
"""
import json
import random
import re
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
VERDICTS = ("TP", "FP", "U")
OVERSTATED = {"Sí": True, "No": False}
_OVERSTATED_RE = re.compile(r"^(Sí|No)(?: — (\S.*))?$")
SEED_SHEET = 20261105
FIELDS = ("Verdict", "Reason (file:line)", "Overstated")
_FIELD_RE = re.compile(r"^- (Verdict|Reason \(file:line\)|Overstated):[ \t]*(.*)$")


def render_sheet(ids):
    md = ["# Review sheet — test-corpus-3", "",
          f"Joaquín's verdicts on {len(ids)} findings (`PREREGISTRATION.md`, \"Review method\"), in a random order. One block per finding.",
          "Fill `Verdict` (TP, FP or U), `Reason (file:line)` and `Overstated` (Sí or No).",
          "Rules: `PREREGISTRATION.md`, \"Verdicts\". Any help received, only factual navigation: `REVIEW-LOG.md`.", ""]
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
        problems.append(f"the IDs are not exactly the expected ones in order (sheet {len(blocks)}, expected {len(ids)})")
    out = []
    for i in ids:
        b = blocks.get(i, {})
        verdict, reason, over = b.get("Verdict", ""), b.get("Reason (file:line)", ""), b.get("Overstated", "")
        if verdict not in VERDICTS:
            problems.append(f"{i}: verdict {verdict!r} is not TP, FP or U" if verdict else f"{i}: verdict missing")
        if not reason:
            problems.append(f"{i}: reason missing")
        om = _OVERSTATED_RE.match(over)
        if not om:
            problems.append(f"{i}: Overstated {over!r} is not Sí or No" if over else f"{i}: Overstated missing")
        out.append({"id": i, "verdict": verdict, "reason": reason, "overstated": OVERSTATED[om.group(1)] if om else None,
                    "overstated_note": over if om and om.group(2) else None})
    if problems:
        raise ValueError("\n".join(problems))
    return out


def ab_lists(text):
    """REVIEW-AB.md -> (disagreeing IDs, audit-sample IDs), each in the file's order."""
    groups, current = {"dis": [], "audit": []}, None
    for line in text.splitlines():
        if line.startswith("## Disagreements"):
            current = "dis"
        elif line.startswith("## Audit sample"):
            current = "audit"
        elif line.startswith("## "):
            current = None
        else:
            m = re.match(r"^- \[(\w+)\]\(cards/\1\.md\)$", line)
            if m and current:
                groups[current].append(m.group(1))
    return groups["dis"], groups["audit"]


def sheet_ids(ids, disagreeing, audit):
    """The reviewed IDs in review-set order, shuffled with random.Random(20261105)."""
    chosen = set(disagreeing) | set(audit)
    out = [i for i in ids if i in chosen]
    random.Random(SEED_SHEET).shuffle(out)
    return out


def joaquin_ids():
    return sheet_ids(review_ids(), *ab_lists((DIR / "REVIEW-AB.md").read_text()))


def review_ids():
    return [f["id"] for f in json.loads((DIR / "review-set.json").read_text())["findings"]]


def main(cmd):
    if cmd == "sheet":
        out = DIR / "REVIEW-SHEET.md"
        if out.exists():
            raise SystemExit("REVIEW-SHEET.md exists: it is generated once")
        ids = joaquin_ids()
        out.write_text(render_sheet(ids) + "\n")
        print(f"REVIEW-SHEET.md: {len(ids)} findings")
    elif cmd == "audit":
        out = DIR / "audit-joaquin.json"
        if out.exists():
            raise SystemExit("audit-joaquin.json exists")
        try:
            verdicts = parse_sheet((DIR / "REVIEW-SHEET.md").read_text(), joaquin_ids())
        except ValueError as e:
            raise SystemExit(f"REVIEW-SHEET.md is not complete:\n{e}")
        out.write_text(json.dumps({"reviewer": "Joaquín", "source": "REVIEW-SHEET.md", "verdicts": verdicts}, indent=2, ensure_ascii=False) + "\n")
        print(f"audit-joaquin.json: {len(verdicts)} verdicts")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
