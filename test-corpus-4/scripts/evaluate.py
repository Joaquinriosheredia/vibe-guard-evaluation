"""Metrics and acceptance criteria of PREREGISTRATION.md, per language (Java and Python are
evaluated separately; neither compensates for the other), with its review method: Joaquín
reviews every ID of the review set, and his verdict is the final one. No AI verdict enters.

Assisted verdicts (PREREGISTRATION.md, "Assistance during the review"): REVIEW-LOG.md must hold
exactly one line `**Assisted IDs:** none` or `**Assisted IDs:** J001, P002, ...`. Only when it
lists IDs, criteria 1 and 2 are computed (a) with all verdicts and (b) with the assisted verdicts
counted as U; per language the less favourable decides, and both are published.

  python3 scripts/evaluate.py      -> checks audit-joaquin.json against audit-joaquin.sha256, then
                                      writes metrics.json and METRICS.md

Verdict file: {"reviewer": "Joaquín", "verdicts": [{"id", "verdict": "TP"|"FP"|"U", "fpCondition", "reason", "overstated": bool}]}.
"""
import json
import math
import random
import re
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
SEED_CAP = 20261202
SEED_BOOT = 20261203
BOOT_B = 2000
CATS = ("TP", "FP", "U")
ASSISTED_RE = re.compile(r"^\*\*Assisted IDs:\*\*[ \t]*(.*?)[ \t]*$", re.M)
ID_RE = re.compile(r"^[JP]\d{3}$")


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


def assisted_ids(log_text):
    """The assisted IDs declared in REVIEW-LOG.md: exactly one `**Assisted IDs:**` line, `none` or
    comma-separated IDs. Refuses a missing, repeated or malformed line."""
    lines = ASSISTED_RE.findall(log_text)
    if len(lines) != 1:
        raise SystemExit(f"REVIEW-LOG.md must hold exactly one '**Assisted IDs:**' line (found {len(lines)})")
    value = lines[0]
    if value == "none":
        return []
    ids = [x.strip() for x in value.split(",")]
    bad = [x for x in ids if not ID_RE.match(x)]
    if bad or len(set(ids)) != len(ids):
        raise SystemExit(f"REVIEW-LOG.md '**Assisted IDs:**': invalid or repeated IDs {bad or ids}")
    return ids


def final_verdicts(findings, joaquin, assisted=()):
    """PREREGISTRATION.md, "Review method": Joaquín's verdict for every ID of the review set.
    With `assisted` (version (b)), those IDs count as U. Returns {id: {"verdict", "overstated", "source"}}."""
    ids = [f["id"] for f in findings]
    if set(joaquin) != set(ids):
        raise SystemExit(f"Joaquín's verdicts must cover exactly the {len(ids)} review-set IDs: "
                         f"missing {sorted(set(ids) - set(joaquin))}, extra {sorted(set(joaquin) - set(ids))}")
    assisted = set(assisted)
    if not assisted <= set(ids):
        raise SystemExit(f"assisted IDs not in the review set: {sorted(assisted - set(ids))}")
    return {i: {"verdict": "U" if i in assisted else joaquin[i]["verdict"], "overstated": joaquin[i]["overstated"] is True,
                "source": "assisted -> U" if i in assisted else "Joaquín"} for i in ids}


def load_verdicts(path, ids):
    data = json.loads(Path(path).read_text())
    v = {a["id"]: a for a in data["verdicts"]}
    bad = [i for i, a in v.items() if a["verdict"] not in CATS]
    if bad:
        raise SystemExit(f"{path}: invalid verdicts for {bad}")
    return v, data.get("reviewer")


def evaluate(rs, corpora, reports, final_full, assisted=()):
    """rs: review-set.json; corpora[lang]: corpus-<lang>.json; reports[lang][full_name]: wrapper report;
    final_full: from final_verdicts()."""
    findings = rs["findings"]
    missing = [f["id"] for f in findings if f["id"] not in final_full]
    if missing:
        raise SystemExit(f"final verdicts missing for {missing}")
    final = {f["id"]: final_full[f["id"]]["verdict"] for f in findings}
    m = {"reviewMethod": "every finding of the review set reviewed by Joaquín under REVIEW-CRITERIA.md v1; no AI verdict (PREREGISTRATION.md)",
         "assistedAsU": sorted(assisted), "languages": {}}
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
            "messageOverstated": sum(1 for f in fl if final_full[f["id"]]["overstated"]),
            **groups,
        }
    return m


def both(m_a, m_b, assisted):
    """Both versions are published; per language, if criterion 1 or criterion 2 differs between (a) and
    (b), the less favourable (NOT MET) is taken. m_b is None when no ID is assisted: (a) decides alone."""
    def decide(key):
        out = {}
        for lang in LANGS:
            sa = m_a["languages"][lang][key]["status"]
            sb = m_b["languages"][lang][key]["status"] if m_b else None
            out[lang] = {"a": sa, "b": sb, "status": "MET" if sa == "MET" and sb in ("MET", None) else "NOT MET",
                         "differs": sb is not None and sa != sb}
        return out
    return {"assisted": list(assisted),
            "rule": ("criteria 1 and 2 computed (a) with all verdicts and (b) with the assisted verdicts as U; "
                     "if they differ, the less favourable is taken (PREREGISTRATION.md)") if m_b else
                    "no assisted verdict declared in REVIEW-LOG.md: (a) all verdicts decides",
            "criterion1": decide("criterion1"), "criterion2": decide("criterion2"),
            "a": m_a, "b": m_b}


def _fmt(x):
    return "—" if x is None else (f"{x[0]}–{x[1]}" if isinstance(x, list) else str(x))


def render(m, level="#", title="Metrics — test-corpus-4"):
    sub = level + "#"
    md = [f"{level} {title}", "", "Rendered by `scripts/evaluate.py` from `metrics.json`.", "",
          "Every finding of the review set reviewed by the author (Joaquín) under REVIEW-CRITERIA.md v1; no AI verdict enters (`PREREGISTRATION.md`, \"Review method\").", "",
          "Reaching 90 % as a point estimate does **not** show with 95 % confidence that the true precision is ≥ 90 %; the Wilson interval is published next to it.", ""]
    for lang, L in m["languages"].items():
        p, fp, v = L["precision"], L["fpPer1000"], L["volume"]
        md += [f"{sub} {lang}", "",
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
    if m["assistedAsU"]:
        md += [f"Assisted verdicts counted as U: {', '.join(m['assistedAsU'])}.", ""]
    return "\n".join(md)


def render_both(m):
    if m["b"] is None:
        md = ["# Metrics — test-corpus-4", "", f"Assisted verdicts (`REVIEW-LOG.md`): none. Rule: {m['rule']}.", ""]
        return "\n".join(md + [render(m["a"], "##", "All verdicts")])
    md = ["# Metrics — test-corpus-4", "",
          f"Assisted verdicts (`REVIEW-LOG.md`): {', '.join(m['assisted'])}. Rule: {m['rule']}.", "",
          "| language | criterion | (a) all verdicts | (b) without assisted | **decides** |", "|---|---|---|---|---|"]
    md += [f"| {lang} | {k[-1]} | {m[k][lang]['a']} | {m[k][lang]['b']} | **{m[k][lang]['status']}** |" for lang in LANGS for k in ("criterion1", "criterion2")]
    md += [""]
    md += [render(m["a"], "##", "(a) All verdicts"), render(m["b"], "##", "(b) Assisted verdicts as U")]
    return "\n".join(md)


def main(argv):
    if argv:
        raise SystemExit(__doc__)
    import review_sheet
    audit = DIR / "audit-joaquin.json"
    if review_sheet.sha256(audit) != (DIR / "audit-joaquin.sha256").read_text().split()[0]:
        raise SystemExit("audit-joaquin.json does not match audit-joaquin.sha256")
    rs = json.loads((DIR / "review-set.json").read_text())
    ids = [f["id"] for f in rs["findings"]]
    joaquin, _ = load_verdicts(audit, ids)
    assisted = assisted_ids((DIR / "REVIEW-LOG.md").read_text())
    corpora, reports = {}, {}
    for lang in LANGS:
        corpora[lang] = json.loads((DIR / f"corpus-{lang}.json").read_text())
        reports[lang] = {c["full_name"]: json.loads((DIR / "results" / lang / f"{c['full_name'].replace('/', '__')}.json").read_text())
                         for c in corpora[lang]["processed"] if c["status"] == "included"}
    m = both(evaluate(rs, corpora, reports, final_verdicts(rs["findings"], joaquin)),
             evaluate(rs, corpora, reports, final_verdicts(rs["findings"], joaquin, assisted), assisted) if assisted else None, assisted)
    (DIR / "metrics.json").write_text(json.dumps(m, indent=2) + "\n")
    (DIR / "METRICS.md").write_text(render_both(m) + "\n")
    print(json.dumps({lang: {k: {x: m[k][lang][x] for x in ("a", "b", "status")} for k in ("criterion1", "criterion2")} for lang in LANGS}, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
