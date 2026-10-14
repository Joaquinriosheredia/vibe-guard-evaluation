"""Review set and blind sample, with the seeds fixed in PREREGISTRATION.md.

  python3 scripts/sample.py review-set       -> review-set.json (every CRITICAL, or the D4 sample)
  python3 scripts/sample.py blind <audit>    -> blind-sample.json / .md (20, no verdicts) and
                                                undetermined.json (every U not in the 20)
"""
import json
import random
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
REVIEW_MAX = 150
SEED_REVIEW = 20261014
SEED_BLIND = 20261015
BLIND_N = 20


def sort_key(f):
    return (f["language"], f["repo"].lower(), f["file"], f["line"] or 0, f["ruleId"], f["message"])


def all_critical():
    corpus = json.loads((DIR / "corpus.json").read_text())
    if not corpus.get("frozen"):
        sys.exit("corpus.json is not frozen")
    out = []
    for p in corpus["processed"]:
        if p["status"] != "included":
            continue
        report = json.loads((DIR / "results" / f"{p['full_name'].replace('/', '__')}.json").read_text())
        for f in report["findings"]:
            if f["severity"] == "critical":
                out.append({"repo": p["full_name"], "commit": p["commit"], "pool": p["pool"], **f})
    out.sort(key=sort_key)
    for i, f in enumerate(out, 1):
        f["id"] = f"C{i:03d}"
    return out


def review_set():
    found = all_critical()
    if len(found) <= REVIEW_MAX:
        chosen, method = found, "every CRITICAL finding"
    else:
        # D4: stratified by language, proportional allocation, one RNG, Java stratum first.
        by_lang = {lang: [f for f in found if f["language"] == lang] for lang in ("java", "python")}
        n_java = round(REVIEW_MAX * len(by_lang["java"]) / len(found))
        alloc = {"java": n_java, "python": REVIEW_MAX - n_java}
        rng = random.Random(SEED_REVIEW)
        chosen = []
        for lang in ("java", "python"):
            chosen += rng.sample(by_lang[lang], alloc[lang])
        chosen.sort(key=sort_key)
        method = f"stratified random sample: {alloc}, seed {SEED_REVIEW}"
    out = {"totalCritical": len(found), "reviewed": len(chosen), "method": method, "findings": chosen}
    (DIR / "review-set.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"{len(found)} CRITICAL; review set: {len(chosen)} ({method})")


def blind(audit_path):
    rs = json.loads((DIR / "review-set.json").read_text())["findings"]
    audit = {a["id"]: a for a in json.loads(Path(audit_path).read_text())["verdicts"]}
    missing = [f["id"] for f in rs if f["id"] not in audit]
    if missing:
        sys.exit(f"audit incomplete: {missing}")
    sample = random.Random(SEED_BLIND).sample(rs, BLIND_N)
    sample.sort(key=sort_key)
    ids = {f["id"] for f in sample}
    undetermined = [f for f in rs if audit[f["id"]]["verdict"] == "U" and f["id"] not in ids]
    keep = ("id", "repo", "commit", "language", "engine", "ruleId", "severity", "message", "file", "line")
    strip = lambda f: {k: f[k] for k in keep}
    (DIR / "blind-sample.json").write_text(json.dumps({"seed": SEED_BLIND, "findings": [strip(f) for f in sample]}, indent=2) + "\n")
    (DIR / "undetermined.json").write_text(json.dumps({"note": "every U of the first review not in the blind sample", "findings": [strip(f) for f in undetermined]}, indent=2) + "\n")
    md = ["# Blind sample — second review", "", f"{BLIND_N} CRITICAL findings drawn with `random.Random({SEED_BLIND}).sample` from the review set. No first-review verdict is shown.", "",
          "For each: TP / FP / U by the criteria of PREREGISTRATION.md (review protocol), a one-line reason with file:line evidence, and message accuracy (overstated: yes/no).", ""]
    for f in sample:
        line = f"#L{f['line']}" if f["line"] else ""
        md += [f"## {f['id']} · {f['ruleId']} · {f['repo']}", "",
               f"- Location: [`{f['file']}:{f['line']}`](https://github.com/{f['repo']}/blob/{f['commit']}/{f['file']}{line}) at `{f['commit'][:12]}`",
               f"- Message: {f['message']}", "- Verdict: ", "- Reason: ", "- Message overstated: ", ""]
    (DIR / "blind-sample.md").write_text("\n".join(md))
    print(f"blind sample: {len(sample)}; undetermined outside it: {len(undetermined)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "review-set":
        review_set()
    elif cmd == "blind" and len(sys.argv) == 3:
        blind(sys.argv[2])
    else:
        sys.exit(__doc__)
