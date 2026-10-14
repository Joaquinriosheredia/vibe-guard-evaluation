"""Metrics of PREREGISTRATION.md: precision (primary, secondary, Wilson 95 %), per language and
per rule, clustering cap, noise rates against the thresholds, and the agreement of the two
reviews (raw and Cohen's kappa).

  python3 scripts/evaluate.py <audit-claude.json> [<audit-joaquin.json>]  -> metrics.json, METRICS.md
"""
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
Z = 1.959963984540054
CAP_PER_REPO = 10
SEED_CAP = 20261016
PRECISION_TARGET = 0.90
MIN_REVIEWED = 50
NOISE = {"critical": 5.0, "warning": 20.0}  # per 1,000 files, per language (D2)
CATS = ("TP", "FP", "U")


def wilson(k, n):
    if n == 0:
        return None
    p = k / n
    den = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / den
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return [round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)]


def precision(verdicts):
    c = Counter(verdicts)
    tp, fp, u = c["TP"], c["FP"], c["U"]
    n1, n2 = tp + fp + u, tp + fp
    return {
        "n": n1, "TP": tp, "FP": fp, "U": u,
        "primary": round(tp / n1, 4) if n1 else None, "primaryCI95": wilson(tp, n1),
        "secondary": round(tp / n2, 4) if n2 else None, "secondaryCI95": wilson(tp, n2),
    }


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None, None
    agree = sum(a == b for a, b in pairs) / n
    pa, pb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(pa[c] * pb[c] for c in CATS) / (n * n)
    k = None if pe == 1 else (agree - pe) / (1 - pe)
    return round(agree, 4), None if k is None else round(k, 4)


def main(claude_path, joaquin_path=None):
    rs = json.loads((DIR / "review-set.json").read_text())
    findings = rs["findings"]
    claude = {a["id"]: a for a in json.loads(Path(claude_path).read_text())["verdicts"]}
    joaquin = {a["id"]: a for a in json.loads(Path(joaquin_path).read_text())["verdicts"]} if joaquin_path else {}
    blind_ids = [f["id"] for f in json.loads((DIR / "blind-sample.json").read_text())["findings"]] if (DIR / "blind-sample.json").exists() else []

    # Final verdict: Joaquín's where he reviewed (it decides disagreements), else Claude's.
    final = {f["id"]: (joaquin.get(f["id"]) or claude[f["id"]])["verdict"] for f in findings}
    m = {"reviewSet": {k: rs[k] for k in ("totalCritical", "reviewed", "method")}}
    m["overall"] = precision(final.values())
    m["criterion1"] = {
        "met": m["overall"]["n"] >= MIN_REVIEWED and (m["overall"]["primary"] or 0) >= PRECISION_TARGET,
        "rule": f"primary point estimate >= {PRECISION_TARGET:.0%} with >= {MIN_REVIEWED} reviewed",
    }
    for key in ("language", "ruleId", "repo"):
        groups = defaultdict(list)
        for f in findings:
            groups[f[key]].append(final[f["id"]])
        m[f"by_{key}"] = {g: precision(v) for g, v in sorted(groups.items())}
    for lang, p in m["by_language"].items():
        p["conclusive"] = p["n"] >= 20

    rng = random.Random(SEED_CAP)
    capped = []
    for repo in sorted({f["repo"] for f in findings}, key=str.lower):
        fs = [f for f in findings if f["repo"] == repo]
        capped += rng.sample(fs, CAP_PER_REPO) if len(fs) > CAP_PER_REPO else fs
    m["clusteringCap10"] = precision(final[f["id"]] for f in capped)

    m["messageOverstated"] = sum(1 for f in findings if (joaquin.get(f["id"]) or claude[f["id"]]).get("overstated") is True)

    # Agreement: the blind 20 (both reviews independent).
    pairs = [(claude[i]["verdict"], joaquin[i]["verdict"]) for i in blind_ids if i in joaquin]
    raw, k = kappa(pairs)
    m["agreementBlind"] = {"n": len(pairs), "raw": raw, "cohenKappa": k,
                           "changed": [i for i in blind_ids if i in joaquin and claude[i]["verdict"] != joaquin[i]["verdict"]]}
    u_ids = [i for i, a in claude.items() if a["verdict"] == "U" and i not in blind_ids and i in joaquin]
    m["undeterminedSecondReview"] = {"n": len(u_ids), "changed": [i for i in u_ids if joaquin[i]["verdict"] != "U"]}

    # Noise: every finding a user sees, per language, against that language's files.
    corpus = json.loads((DIR / "corpus.json").read_text())
    files, counts, per_repo = Counter(), defaultdict(Counter), defaultdict(list)
    for p in corpus["processed"]:
        if p["status"] != "included":
            continue
        report = json.loads((DIR / "results" / f"{p['full_name'].replace('/', '__')}.json").read_text())
        c = defaultdict(Counter)
        for f in report["findings"]:
            c[f["language"]][f["severity"]] += 1
        for lang in ("java", "python"):
            files[lang] += p["files"][lang]
            counts[lang].update(c[lang])
            if p["files"][lang]:
                per_repo[lang].append({sev: 1000 * c[lang][sev] / p["files"][lang] for sev in ("critical", "major", "warning", "info")})
    noise = {}
    for lang in ("java", "python"):
        rates = {sev: round(1000 * counts[lang][sev] / files[lang], 3) if files[lang] else None for sev in ("critical", "major", "warning", "info")}
        med = {}
        for sev in ("critical", "warning"):
            v = sorted(r[sev] for r in per_repo[lang])
            med[sev] = {"median": round(v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2, 3) if v else None,
                        "max": round(max(v), 3) if v else None}
        noise[lang] = {"files": files[lang], "findings": dict(counts[lang]), "per1000": rates, "perRepo": med,
                       "met": all(rates[s] is not None and rates[s] <= t for s, t in NOISE.items())}
    m["noise"] = {"thresholdsPer1000": NOISE, "byLanguage": noise, "criterion2Met": all(n["met"] for n in noise.values())}

    (DIR / "metrics.json").write_text(json.dumps(m, indent=2) + "\n")
    print(json.dumps({"overall": m["overall"], "criterion1": m["criterion1"], "criterion2Met": m["noise"]["criterion2Met"]}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
