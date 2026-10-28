"""Joaquín's review sheet and its conversion to his verdicts (PREREGISTRATION.md, "Review method"):
he reviews EVERY ID of the review set, under REVIEW-CRITERIA.md v1.

  python3 scripts/review_sheet.py sheet   -> REVIEW-SHEET.md: every review-set ID, in review-set order
                                             shuffled with random.Random(20261204), each with only a
                                             link to its card and empty fields (once)
  python3 scripts/review_sheet.py audit   -> audit-joaquin.json and audit-joaquin.sha256 from
                                             REVIEW-SHEET.md; fails if any verdict is missing or not
                                             TP/FP/U, an FP has no failing condition (or a TP/U has
                                             one), a reason cites no file:line, or Overstated is not
                                             "Sí"/"No", optionally followed by " — " and a note
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
VERDICTS = ("TP", "FP", "U")
CONDITIONS = ("detection", "context", "reachability")  # REVIEW-CRITERIA.md v1 §1, conditions 1-3
NO_CONDITION = "—"
OVERSTATED = {"Sí": True, "No": False}
_OVERSTATED_RE = re.compile(r"^(Sí|No)(?: — (\S.*))?$")
_FILE_LINE_RE = re.compile(r"[\w.@/-]+\.\w+:\d+")
SEED_SHEET = 20261204
FIELDS = ("Verdict", "FP condition", "Reason (file:line)", "Overstated")
_FIELD_RE = re.compile(r"^- (Verdict|FP condition|Reason \(file:line\)|Overstated):[ \t]*(.*)$")


def render_sheet(ids):
    md = ["# Review sheet — test-corpus-4", "",
          f"Joaquín's verdicts on all {len(ids)} findings of the review set (`PREREGISTRATION.md`, \"Review method\"), in a random order. One block per finding.",
          "Fill `Verdict` (TP, FP or U); `FP condition` (detection, context or reachability for an FP, `—` otherwise);",
          "`Reason (file:line)` (at least one `path:line`); and `Overstated` (Sí or No, optionally ` — note`).",
          "Criterion: `../REVIEW-CRITERIA.md` v1 (`PREREGISTRATION.md`, \"Verdict criterion\"). Any help received, only factual navigation: `REVIEW-LOG.md`.", ""]
    for i in ids:
        md += [f"## {i}", "", f"- Card: [cards/{i}.md](cards/{i}.md)", "- Verdict: ", "- FP condition: ", "- Reason (file:line): ", "- Overstated: ", ""]
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
        verdict, cond = b.get("Verdict", ""), b.get("FP condition", "")
        reason, over = b.get("Reason (file:line)", ""), b.get("Overstated", "")
        if verdict not in VERDICTS:
            problems.append(f"{i}: verdict {verdict!r} is not TP, FP or U" if verdict else f"{i}: verdict missing")
        if verdict == "FP" and cond not in CONDITIONS:
            problems.append(f"{i}: an FP needs its FP condition (detection, context or reachability), got {cond!r}")
        if verdict in ("TP", "U") and cond not in ("", NO_CONDITION):
            problems.append(f"{i}: FP condition {cond!r} on a {verdict} (use {NO_CONDITION})")
        if not reason:
            problems.append(f"{i}: reason missing")
        elif not _FILE_LINE_RE.search(reason):
            problems.append(f"{i}: reason cites no file:line")
        om = _OVERSTATED_RE.match(over)
        if not om:
            problems.append(f"{i}: Overstated {over!r} is not Sí or No" if over else f"{i}: Overstated missing")
        out.append({"id": i, "verdict": verdict, "fpCondition": cond if verdict == "FP" else None, "reason": reason,
                    "overstated": OVERSTATED[om.group(1)] if om else None,
                    "overstated_note": over if om and om.group(2) else None})
    if problems:
        raise ValueError("\n".join(problems))
    return out


def sheet_ids(ids):
    """Every review-set ID, in review-set order, shuffled with random.Random(20261204)."""
    out = list(ids)
    random.Random(SEED_SHEET).shuffle(out)
    return out


def review_ids():
    return [f["id"] for f in json.loads((DIR / "review-set.json").read_text())["findings"]]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(cmd):
    if cmd == "sheet":
        out = DIR / "REVIEW-SHEET.md"
        if out.exists():
            raise SystemExit("REVIEW-SHEET.md exists: it is generated once")
        ids = sheet_ids(review_ids())
        out.write_text(render_sheet(ids) + "\n")
        print(f"REVIEW-SHEET.md: {len(ids)} findings")
    elif cmd == "audit":
        out, sha = DIR / "audit-joaquin.json", DIR / "audit-joaquin.sha256"
        if out.exists() or sha.exists():
            raise SystemExit("audit-joaquin.json or audit-joaquin.sha256 exists")
        try:
            verdicts = parse_sheet((DIR / "REVIEW-SHEET.md").read_text(), sheet_ids(review_ids()))
        except ValueError as e:
            raise SystemExit(f"REVIEW-SHEET.md is not complete:\n{e}")
        out.write_text(json.dumps({"reviewer": "Joaquín", "source": "REVIEW-SHEET.md", "criterion": "REVIEW-CRITERIA.md v1",
                                   "verdicts": verdicts}, indent=2, ensure_ascii=False) + "\n")
        sha.write_text(f"{sha256(out)}  audit-joaquin.json\n")
        print(f"audit-joaquin.json: {len(verdicts)} verdicts; sha256 {sha256(out)} (commit both before evaluate.py)")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
