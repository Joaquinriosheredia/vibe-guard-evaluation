"""Review set and repeatability sample, with the seeds fixed in PREREGISTRATION.md.

  python3 scripts/sample.py review-set   -> review-set.json (per language: every CRITICAL of the
                                            pool's language, or a sample of 100; Java first)
  python3 scripts/sample.py repeat       -> repeat-sample.json (10 findings, no verdicts)
"""
import json
import random
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
REVIEW_MAX = {"java": 100, "python": 100}
REQUIRED = {"java": 50, "python": 100}
SEED_REVIEW = 20261021
SEED_REPEAT = 20261023
REPEAT_N = 10
PREFIX = {"java": "J", "python": "P"}


def sort_key(f):
    return (f["repo"].lower(), f["file"], f["line"] or 0, f["ruleId"], f["message"])


def pool_critical(corpus, language, load_report):
    """Every CRITICAL of the pool's language in the frozen pool, sorted and numbered J001…/P001…"""
    if not corpus.get("frozen"):
        raise SystemExit(f"corpus-{corpus.get('pool')}.json is not frozen")
    out = []
    for p in corpus["processed"]:
        if p["status"] != "included":
            continue
        for f in load_report(p)["findings"]:
            if f["severity"] == "critical" and f["language"] == language:
                out.append({"repo": p["full_name"], "commit": p["commit"], "pool": p["pool"], "subpool": p["subpool"],
                            "families": p.get("families", []), **f})
    out.sort(key=sort_key)
    for i, f in enumerate(out, 1):
        f["id"] = f"{PREFIX[language]}{i:03d}"
    return out


def draw(by_lang, rng):
    """One RNG, Java first, then Python: every finding if <= REVIEW_MAX, else rng.sample."""
    chosen, method = {}, {}
    for lang in ("java", "python"):
        found = by_lang[lang]
        if len(found) <= REVIEW_MAX[lang]:
            chosen[lang], method[lang] = list(found), "every CRITICAL finding"
        else:
            chosen[lang] = sorted(rng.sample(found, REVIEW_MAX[lang]), key=sort_key)
            method[lang] = f"random.Random({SEED_REVIEW}).sample of {REVIEW_MAX[lang]}"
    return chosen, method


def repeat_sample(findings, n=REPEAT_N, seed=SEED_REPEAT):
    ordered = sorted(findings, key=lambda f: f["id"])
    return sorted(random.Random(seed).sample(ordered, n), key=lambda f: f["id"])


def main(cmd):
    if cmd == "review-set":
        by_lang, frozen = {}, {}
        for lang in ("java", "python"):
            corpus = json.loads((DIR / f"corpus-{lang}.json").read_text())
            load = lambda p, lang=lang: json.loads((DIR / "results" / lang / f"{p['full_name'].replace('/', '__')}.json").read_text())
            by_lang[lang] = pool_critical(corpus, lang, load)
            frozen[lang] = corpus["frozenReason"]
        chosen, method = draw(by_lang, random.Random(SEED_REVIEW))
        out = {"seed": SEED_REVIEW, "languages": {lang: {
            "totalCritical": len(by_lang[lang]), "reviewed": len(chosen[lang]), "required": REQUIRED[lang],
            "method": method[lang], "corpusFrozenReason": frozen[lang]} for lang in ("java", "python")},
            "findings": chosen["java"] + chosen["python"]}
        (DIR / "review-set.json").write_text(json.dumps(out, indent=2) + "\n")
        for lang in ("java", "python"):
            print(f"{lang}: {len(by_lang[lang])} CRITICAL; review set {len(chosen[lang])} ({method[lang]}); required {REQUIRED[lang]}")
    elif cmd == "repeat":
        rs = json.loads((DIR / "review-set.json").read_text())["findings"]
        keep = ("id", "repo", "commit", "language", "ruleId", "file", "line")
        sample = [{k: f[k] for k in keep} for f in repeat_sample(rs)]
        (DIR / "repeat-sample.json").write_text(json.dumps({"seed": SEED_REPEAT, "findings": sample}, indent=2) + "\n")
        print(f"repeat sample: {[f['id'] for f in sample]}")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
