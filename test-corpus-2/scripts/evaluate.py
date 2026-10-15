"""Metrics and acceptance criteria of PREREGISTRATION.md, per language (Java and Python are
evaluated separately; neither compensates for the other). Official verdicts: Joaquín's only.

  python3 scripts/evaluate.py <audit-joaquin.json> [--claude <audit-claude.json>] [--repeat <repeat-joaquin.json>]
      -> metrics.json and METRICS.md

Verdict files: {"reviewer": "...", "verdicts": [{"id", "verdict": "TP"|"FP"|"U", "reason", "overstated": bool}]}.
"""
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
Z = 1.959963984540054
LANGS = ("java", "python")
REQUIRED = {"java": 50, "python": 100}
PRECISION_TARGET = 0.90
FP_PER_1000_MAX = 5.0
VOLUME_D2 = {"critical": 5.0, "warning": 20.0}  # original D2, published always, does not decide
CAP_PER_REPO = 10
SEED_CAP = 20261022
SEED_BOOT = 20261024
BOOT_B = 2000
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
    return {"n": n1, "TP": tp, "FP": fp, "U": u,
            "primary": round(tp / n1, 4) if n1 else None, "primaryCI95": wilson(tp, n1),
            "secondary": round(tp / n2, 4) if n2 else None, "secondaryCI95": wilson(tp, n2)}


def fp_per_1000(p, critical_total, files):
    """FP/1000 = (FP+U)/reviewed × CRITICAL/files × 1000 (primary, U counted as FP); secondary without U."""
    density = 1000 * critical_total / files if files else None
    if density is None:
        return {"densityCriticalPer1000": None, "primary": None, "primaryCI95": None, "secondary": None}
    if p["n"] == 0:
        zero = 0.0 if critical_total == 0 else None
        return {"densityCriticalPer1000": round(density, 4), "primary": zero, "primaryCI95": None, "secondary": zero}
    bad = p["FP"] + p["U"]
    ci = wilson(bad, p["n"])
    n2 = p["TP"] + p["FP"]
    return {"densityCriticalPer1000": round(density, 4),
            "primary": round(density * bad / p["n"], 4),
            "primaryCI95": [round(density * ci[0], 4), round(density * ci[1], 4)],
            "secondary": round(density * p["FP"] / n2, 4) if n2 else None}


def criterion1(p, reviewed, required):
    reasons = []
    if reviewed < required:
        reasons.append(f"only {reviewed} CRITICAL reviewed, {required} required")
    if p["primary"] is None or p["primary"] < PRECISION_TARGET:
        reasons.append(f"primary precision {p['primary']} < {PRECISION_TARGET}")
    return {"met": not reasons, "status": "MET" if not reasons else "NOT MET", "reasons": reasons,
            "rule": f"primary point estimate >= {PRECISION_TARGET:.0%} with >= {required} reviewed"}


def criterion2(fp):
    v = fp["primary"]
    met = v is not None and v <= FP_PER_1000_MAX
    return {"met": met, "status": "MET" if met else "NOT MET", "rule": f"FP/1000 point estimate <= {FP_PER_1000_MAX}"}


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return {"n": 0, "raw": None, "cohenKappa": None}
    agree = sum(a == b for a, b in pairs) / n
    pa, pb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(pa[c] * pb[c] for c in CATS) / (n * n)
    return {"n": n, "raw": round(agree, 4), "cohenKappa": None if pe == 1 else round((agree - pe) / (1 - pe), 4)}


def cluster_bootstrap(repos, b=BOOT_B, seed=SEED_BOOT):
    """Percentile 95 % CI of FP/1000, resampling repositories with replacement (informational).
    repos: [{"critical", "files", "reviewed", "bad"}] for every included repository of the pool."""
    if not repos:
        return None
    rng = random.Random(seed)
    vals = []
    for _ in range(b):
        draw = [repos[rng.randrange(len(repos))] for _ in repos]
        reviewed = sum(r["reviewed"] for r in draw)
        files = sum(r["files"] for r in draw)
        if reviewed == 0 or files == 0:
            continue
        vals.append(1000 * sum(r["critical"] for r in draw) / files * sum(r["bad"] for r in draw) / reviewed)
    if not vals:
        return None
    vals.sort()
    return [round(vals[int(0.025 * (len(vals) - 1))], 4), round(vals[int(0.975 * (len(vals) - 1))], 4)]


def capped(findings, final, cap=CAP_PER_REPO, seed=SEED_CAP):
    rng = random.Random(seed)
    out = []
    for repo in sorted({f["repo"] for f in findings}, key=str.lower):
        fs = [f for f in findings if f["repo"] == repo]
        out += rng.sample(fs, cap) if len(fs) > cap else fs
    return precision(final[f["id"]] for f in out)


def load_verdicts(path, ids):
    data = json.loads(Path(path).read_text())
    v = {a["id"]: a for a in data["verdicts"]}
    bad = [i for i, a in v.items() if a["verdict"] not in CATS]
    if bad:
        raise SystemExit(f"{path}: invalid verdicts for {bad}")
    return v, data.get("reviewer")


def evaluate(rs, corpora, reports, joaquin, claude=None, repeat=None):
    """rs: review-set.json; corpora[lang]: corpus-<lang>.json; reports[lang][full_name]: wrapper report."""
    findings = rs["findings"]
    missing = [f["id"] for f in findings if f["id"] not in joaquin]
    if missing:
        raise SystemExit(f"official verdicts (Joaquín) missing for {missing}")
    final = {f["id"]: joaquin[f["id"]]["verdict"] for f in findings}
    m = {"officialReviewer": "Joaquín", "languages": {}}
    for lang in LANGS:
        fl = [f for f in findings if f["language"] == lang]
        info = rs["languages"][lang]
        p = precision(final[f["id"]] for f in fl)
        included = [c for c in corpora[lang]["processed"] if c["status"] == "included"]
        files = sum(c["files"][lang] for c in included)
        counts = Counter()
        per_repo = []
        for c in included:
            sev = Counter(f["severity"] for f in reports[lang][c["full_name"]]["findings"] if f["language"] == lang)
            counts.update(sev)
            rf = [f for f in fl if f["repo"] == c["full_name"]]
            per_repo.append({"critical": sev["critical"], "files": c["files"][lang], "reviewed": len(rf),
                             "bad": sum(final[f["id"]] in ("FP", "U") for f in rf)})
        fp = fp_per_1000(p, info["totalCritical"], files)
        fp["clusterBootstrapCI95"] = cluster_bootstrap(per_repo)
        per1000 = {s: round(1000 * counts[s] / files, 4) if files else None for s in ("critical", "major", "warning", "info")}
        groups = {}
        for key in ("ruleId", "repo", "subpool"):
            g = defaultdict(list)
            for f in fl:
                g[f[key]].append(final[f["id"]])
            groups[f"by_{key}"] = {k: precision(v) for k, v in sorted(g.items())}
        if lang == "java":
            g = defaultdict(list)
            for f in fl:
                for fam in f.get("families", []):
                    g[fam].append(final[f["id"]])
            groups["by_family"] = {k: precision(v) for k, v in sorted(g.items())}
        m["languages"][lang] = {
            "corpusFrozenReason": info["corpusFrozenReason"], "includedRepositories": len(included),
            "totalCritical": info["totalCritical"], "reviewed": info["reviewed"], "required": info["required"],
            "sampling": info["method"],
            "precision": p, "criterion1": criterion1(p, info["reviewed"], info["required"]),
            "fpPer1000": fp, "criterion2": criterion2(fp),
            "volume": {"files": files, "findings": dict(counts), "per1000": per1000,
                       "withinOriginalD2": {s: per1000[s] is not None and per1000[s] <= t for s, t in VOLUME_D2.items()},
                       "note": "published always; does not decide (amendment of 2026-10-14)"},
            "clusteringCap10": capped(fl, final),
            "messageOverstated": sum(1 for f in fl if joaquin[f["id"]].get("overstated") is True),
            **groups,
        }
    if claude is not None:
        pairs = [(claude[f["id"]]["verdict"], final[f["id"]]) for f in findings if f["id"] in claude]
        m["agreementClaudeSealed"] = {**kappa(pairs), "counts": "never", "changed": [f["id"] for f in findings if f["id"] in claude and claude[f["id"]]["verdict"] != final[f["id"]]]}
    if repeat is not None:
        pairs = [(final[i], a["verdict"]) for i, a in repeat.items() if i in final]
        m["repeatability"] = {**kappa(pairs), "changed": [i for i, a in repeat.items() if i in final and a["verdict"] != final[i]]}
    return m


def _fmt(x):
    return "—" if x is None else (f"{x[0]}–{x[1]}" if isinstance(x, list) else str(x))


def render(m):
    md = ["# Metrics — test-corpus-2", "", "Rendered by `scripts/evaluate.py` from `metrics.json`. Official verdicts: Joaquín's only.", "",
          "Reaching 90 % as a point estimate does **not** show with 95 % confidence that the true precision is ≥ 90 %; the Wilson interval is published next to it.", ""]
    for lang, L in m["languages"].items():
        p, fp, v = L["precision"], L["fpPer1000"], L["volume"]
        md += [f"## {lang}", "",
               f"- Corpus: {L['includedRepositories']} repositories; frozen: {L['corpusFrozenReason']}",
               f"- CRITICAL: {L['totalCritical']}; reviewed {L['reviewed']} (required {L['required']}; {L['sampling']})",
               f"- **Criterion 1 (precision): {L['criterion1']['status']}** — primary {_fmt(p['primary'])}, Wilson 95 % {_fmt(p['primaryCI95'])}, n {p['n']} (TP {p['TP']}, FP {p['FP']}, U {p['U']}); secondary {_fmt(p['secondary'])} {_fmt(p['secondaryCI95'])}" + (f"; {'; '.join(L['criterion1']['reasons'])}" if L['criterion1']['reasons'] else ""),
               f"- **Criterion 2 (FP/1000 ≤ {FP_PER_1000_MAX}): {L['criterion2']['status']}** — {_fmt(fp['primary'])} (Wilson-scaled 95 % {_fmt(fp['primaryCI95'])}; repository bootstrap {_fmt(fp['clusterBootstrapCI95'])}; without U {_fmt(fp['secondary'])}; CRITICAL density {_fmt(fp['densityCriticalPer1000'])}/1000)",
               f"- Volume (original D2, does not decide): {v['files']} files; CRITICAL {_fmt(v['per1000']['critical'])}/1000, WARNING {_fmt(v['per1000']['warning'])}/1000; within D2: {v['withinOriginalD2']}",
               f"- Clustering cap 10/repository (informational): primary {_fmt(L['clusteringCap10']['primary'])}, n {L['clusteringCap10']['n']}",
               f"- Messages overstated: {L['messageOverstated']}", "",
               "| rule | n | TP | FP | U | primary | Wilson 95 % |", "|---|---|---|---|---|---|---|"]
        md += [f"| {r} | {q['n']} | {q['TP']} | {q['FP']} | {q['U']} | {_fmt(q['primary'])} | {_fmt(q['primaryCI95'])} |" for r, q in L["by_ruleId"].items()]
        md.append("")
    if "agreementClaudeSealed" in m:
        a = m["agreementClaudeSealed"]
        md += [f"Claude's sealed verdicts (never count) vs Joaquín: n {a['n']}, raw {_fmt(a['raw'])}, kappa {_fmt(a['cohenKappa'])}.", ""]
    if "repeatability" in m:
        a = m["repeatability"]
        md += [f"Repeatability (Joaquín, ≥ 7 days): n {a['n']}, raw {_fmt(a['raw'])}, kappa {_fmt(a['cohenKappa'])}, changed {a['changed']}.", ""]
    return "\n".join(md)


def main(argv):
    if not argv or len(argv) % 2 != 1:
        raise SystemExit(__doc__)
    opts = dict(zip(argv[1::2], argv[2::2]))
    if set(opts) - {"--claude", "--repeat"}:
        raise SystemExit(__doc__)
    rs = json.loads((DIR / "review-set.json").read_text())
    ids = {f["id"] for f in rs["findings"]}
    joaquin, _ = load_verdicts(argv[0], ids)
    claude = load_verdicts(opts["--claude"], ids)[0] if "--claude" in opts else None
    repeat = load_verdicts(opts["--repeat"], ids)[0] if "--repeat" in opts else None
    corpora, reports = {}, {}
    for lang in LANGS:
        corpora[lang] = json.loads((DIR / f"corpus-{lang}.json").read_text())
        reports[lang] = {c["full_name"]: json.loads((DIR / "results" / lang / f"{c['full_name'].replace('/', '__')}.json").read_text())
                         for c in corpora[lang]["processed"] if c["status"] == "included"}
    m = evaluate(rs, corpora, reports, joaquin, claude, repeat)
    (DIR / "metrics.json").write_text(json.dumps(m, indent=2) + "\n")
    (DIR / "METRICS.md").write_text(render(m) + "\n")
    print(json.dumps({lang: {"criterion1": L["criterion1"]["status"], "criterion2": L["criterion2"]["status"]} for lang, L in m["languages"].items()}, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
