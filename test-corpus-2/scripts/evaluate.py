"""Metrics and acceptance criteria of PREREGISTRATION.md, per language (Java and Python are
evaluated separately; neither compensates for the other), with the review method of
DEVIATIONS.md §3/§3a: final verdict = Joaquín's where he reviewed (the A/B disagreements and the
audit sample of REVIEW-AB.md), otherwise the agreeing verdict of reviews A and B.
DEVIATIONS.md §3b: everything is computed (a) with all of Joaquín's verdicts and (b) without the
ASSISTED ones in the audit sample; criterion 1 takes the less favourable of (a) and (b).

  python3 scripts/evaluate.py <audit-claude.json> <audit-claude-B.json> <audit-joaquin.json>
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
AUDIT_N = 20
AUDIT_MAX_CHANGES = 3  # >= 3 changes of the 20 (15 %) -> AI review NOT RELIABLE, criterion 1 NOT MET in both languages
# DEVIATIONS.md §3b: verdicts given after an AI assistant's assessments and a provisional percentage
ASSISTED = ("J015", "J038", "J056", "J036", "J001", "J020", "J023", "J052", "J021", "P145", "P083", "P099", "P098", "P072")


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


def criterion1(p, reviewed, required, audit=None):
    reasons = []
    if audit is not None and not audit["reliable"]:
        reasons.append(f"AI review NOT RELIABLE: Joaquín changed {audit['changed']} of {audit['n']} in the audit (>= {audit['maxChanges']})")
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


def audit_max_changes(n):
    """Changes that make the AI review NOT RELIABLE: the 15 % of the original rule (3 of 20), rounded up
    (DEVIATIONS.md §3b: 2 of 10)."""
    return -(-AUDIT_MAX_CHANGES * n // AUDIT_N)


def final_verdicts(findings, a, b, joaquin, disagreeing, audit):
    """DEVIATIONS.md §3/§3a. a, b, joaquin: {id: {"verdict", "overstated"}}.
    Returns (final {id: {"verdict", "overstated", "source"}}, review summary)."""
    reviewed = set(disagreeing) | set(audit)
    if set(joaquin) != reviewed:
        raise SystemExit(f"Joaquín's verdicts must cover exactly the {len(reviewed)} reviewed IDs: "
                         f"missing {sorted(reviewed - set(joaquin))}, extra {sorted(set(joaquin) - reviewed)}")
    final, disputed = {}, 0
    for f in findings:
        i = f["id"]
        if i in reviewed:
            final[i] = {"verdict": joaquin[i]["verdict"], "overstated": joaquin[i]["overstated"] is True, "source": "Joaquín"}
            continue
        if a[i]["verdict"] != b[i]["verdict"]:
            raise SystemExit(f"{i}: A and B disagree but Joaquín did not review it")
        final[i] = {"verdict": a[i]["verdict"], "overstated": a[i]["overstated"] is True or b[i]["overstated"] is True, "source": "A=B"}
    for f in findings:
        i = f["id"]
        if i not in disagreeing and a[i]["verdict"] == b[i]["verdict"] and (a[i]["overstated"] is True) != (b[i]["overstated"] is True):
            disputed += 1
    lang_of = {f["id"]: f["language"] for f in findings}

    def rate(ids):
        ch = [i for i in ids if joaquin[i]["verdict"] != a[i]["verdict"]]
        return {"n": len(ids), "changed": len(ch), "rate": round(len(ch) / len(ids), 4) if ids else None,
                "rateCI95": wilson(len(ch), len(ids)), "changedIds": ch}
    total = rate(list(audit))
    max_changes = audit_max_changes(total["n"])
    summary = {
        "agreementAB": kappa([(a[f["id"]]["verdict"], b[f["id"]]["verdict"]) for f in findings]),
        "agreementABByLanguage": {lang: kappa([(a[f["id"]]["verdict"], b[f["id"]]["verdict"]) for f in findings if f["language"] == lang]) for lang in LANGS},
        "disagreements": list(disagreeing),
        "overstatedDisputedSetToYes": disputed,
        "audit": {**total, "maxChanges": max_changes, "reliable": total["n"] > 0 and total["changed"] < max_changes,
                  "rule": f">= {max_changes} of {total['n']} changed -> AI review NOT RELIABLE, criterion 1 NOT MET in both languages",
                  "byLanguage": {lang: rate([i for i in audit if lang_of[i] == lang]) for lang in LANGS}},
    }
    return final, summary


def final_verdicts_unassisted(findings, a, b, joaquin, disagreeing, audit, assisted=ASSISTED):
    """DEVIATIONS.md §3b, version (b): the assisted IDs of the audit sample leave the audit and keep the
    A = B verdict; the assisted disagreements have no unassisted verdict and count as U."""
    assisted = set(assisted)
    if not assisted <= set(disagreeing) | set(audit):
        raise SystemExit(f"assisted IDs not reviewed by Joaquín: {sorted(assisted - set(disagreeing) - set(audit))}")
    audit_b = [i for i in audit if i not in assisted]
    joaquin_b = {i: ({**v, "verdict": "U"} if i in assisted else v) for i, v in joaquin.items() if i not in assisted or i in disagreeing}
    final, summary = final_verdicts(findings, a, b, joaquin_b, disagreeing, audit_b)
    for i in assisted & set(disagreeing):
        final[i]["source"] = "assisted disagreement -> U"
    summary["assistedExcluded"] = {"audit": [i for i in audit if i in assisted], "disagreementsAsU": [i for i in disagreeing if i in assisted]}
    return final, summary


def load_verdicts(path, ids):
    data = json.loads(Path(path).read_text())
    v = {a["id"]: a for a in data["verdicts"]}
    bad = [i for i, a in v.items() if a["verdict"] not in CATS]
    if bad:
        raise SystemExit(f"{path}: invalid verdicts for {bad}")
    return v, data.get("reviewer")


def evaluate(rs, corpora, reports, final_full, review):
    """rs: review-set.json; corpora[lang]: corpus-<lang>.json; reports[lang][full_name]: wrapper report;
    final_full, review: from final_verdicts()."""
    findings = rs["findings"]
    missing = [f["id"] for f in findings if f["id"] not in final_full]
    if missing:
        raise SystemExit(f"final verdicts missing for {missing}")
    final = {f["id"]: final_full[f["id"]]["verdict"] for f in findings}
    m = {"reviewMethod": "two independent AI reviews (A, B); disagreements and an audit sample of 20 decided by Joaquín (DEVIATIONS.md §3/§3a)",
         "review": review, "languages": {}}
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
            "precision": p, "criterion1": criterion1(p, info["reviewed"], info["required"], review["audit"]),
            "fpPer1000": fp, "criterion2": criterion2(fp),
            "volume": {"files": files, "findings": dict(counts), "per1000": per1000,
                       "withinOriginalD2": {s: per1000[s] is not None and per1000[s] <= t for s, t in VOLUME_D2.items()},
                       "note": "published always; does not decide (amendment of 2026-10-14)"},
            "clusteringCap10": capped(fl, final),
            "messageOverstated": sum(1 for f in fl if final_full[f["id"]]["overstated"]),
            **groups,
        }
    return m


def both(m_a, m_b):
    """DEVIATIONS.md §3b: both versions are published; per language, if criterion 1 differs between
    (a) and (b), the less favourable (NOT MET) is taken."""
    c1 = {}
    for lang in LANGS:
        sa, sb = m_a["languages"][lang]["criterion1"]["status"], m_b["languages"][lang]["criterion1"]["status"]
        c1[lang] = {"a": sa, "b": sb, "status": "MET" if sa == sb == "MET" else "NOT MET", "differs": sa != sb}
    no_audit = [lang for lang, x in m_b["review"]["audit"]["byLanguage"].items() if x["n"] == 0]
    return {"assisted": list(ASSISTED),
            "rule": "criterion 1 computed (a) with all verdicts and (b) without the assisted IDs in the audit sample; if they differ, the less favourable is taken (DEVIATIONS.md §3b)",
            "criterion1": c1,
            "notes": [f"In (b) no {lang} audit case remains: the {lang} audit exists only in the assisted version (a)." for lang in no_audit],
            "a": m_a, "b": m_b}


def _fmt(x):
    return "—" if x is None else (f"{x[0]}–{x[1]}" if isinstance(x, list) else str(x))


def render(m, level="#", title="Metrics — test-corpus-2"):
    sub = level + "#"
    md = [f"{level} {title}", "", "Rendered by `scripts/evaluate.py` from `metrics.json`.", "",
          "Reviewed by two independent AIs; disagreements and a sample of 20 audited by the author (`DEVIATIONS.md` §3/§3a).", "",
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
    r = m["review"]
    ab, au = r["agreementAB"], r["audit"]
    md += [f"{sub} Review", "",
           f"- Agreement A–B: n {ab['n']}, raw {_fmt(ab['raw'])}, kappa {_fmt(ab['cohenKappa'])}; disagreements {len(r['disagreements'])}, decided by Joaquín.",
           f"- Corrections in the audit: {au['changed']}/{au['n']} (Wilson 95 % {_fmt(au['rateCI95'])}) — AI review **{'RELIABLE' if au['reliable'] else 'NOT RELIABLE'}** (rule: {au['rule']}).",
           *[f"  - {lang}: {x['changed']}/{x['n']} (Wilson 95 % {_fmt(x['rateCI95'])})" for lang, x in au["byLanguage"].items()],
           f"- Overstated in dispute between A and B (set to yes): {r['overstatedDisputedSetToYes']}.", ""]
    if "assistedExcluded" in r:
        md += [f"- Assisted IDs left out of the audit (A = B verdict): {', '.join(r['assistedExcluded']['audit']) or '—'}; assisted disagreements counted as U: {', '.join(r['assistedExcluded']['disagreementsAsU']) or '—'}.", ""]
    return "\n".join(md)


def render_both(m):
    md = ["# Metrics — test-corpus-2", "",
          f"Assisted verdicts (`DEVIATIONS.md` §3b): {', '.join(m['assisted'])}. Rule: {m['rule']}.", "",
          "| language | criterion 1 (a) all verdicts | criterion 1 (b) without assisted | **criterion 1** |", "|---|---|---|---|"]
    md += [f"| {lang} | {c['a']} | {c['b']} | **{c['status']}** |" for lang, c in m["criterion1"].items()]
    md += [""] + [f"- **{n}**" for n in m["notes"]] + [""]
    md += [render(m["a"], "##", "(a) All verdicts"), render(m["b"], "##", "(b) Without the assisted verdicts in the audit sample")]
    return "\n".join(md)


def main(argv):
    if len(argv) != 3:
        raise SystemExit(__doc__)
    import review_ab  # here, not at import: review_ab imports this module
    import review_sheet
    for path, name in ((argv[0], "audit-claude.sha256"), (argv[1], "audit-claude-B.sha256")):
        if review_ab.sha256(path) != review_ab.committed(name):
            raise SystemExit(f"{path} does not match {name}")
    rs = json.loads((DIR / "review-set.json").read_text())
    ids = [f["id"] for f in rs["findings"]]
    a, _ = load_verdicts(argv[0], ids)
    b, _ = load_verdicts(argv[1], ids)
    joaquin, _ = load_verdicts(argv[2], ids)
    disagreeing, audit = review_sheet.ab_lists((DIR / "REVIEW-AB.md").read_text())
    cmp = review_ab.compare([a[i] for i in ids], [b[i] for i in ids], ids)
    if cmp["all"]["disagreeing"] != disagreeing or review_ab.audit_sample([i for i in ids if i not in set(disagreeing)]) != audit:
        raise SystemExit("REVIEW-AB.md does not match A and B")
    final_a, review_a = final_verdicts(rs["findings"], a, b, joaquin, disagreeing, audit)
    final_b, review_b = final_verdicts_unassisted(rs["findings"], a, b, joaquin, disagreeing, audit)
    corpora, reports = {}, {}
    for lang in LANGS:
        corpora[lang] = json.loads((DIR / f"corpus-{lang}.json").read_text())
        reports[lang] = {c["full_name"]: json.loads((DIR / "results" / lang / f"{c['full_name'].replace('/', '__')}.json").read_text())
                         for c in corpora[lang]["processed"] if c["status"] == "included"}
    m = both(evaluate(rs, corpora, reports, final_a, review_a), evaluate(rs, corpora, reports, final_b, review_b))
    (DIR / "metrics.json").write_text(json.dumps(m, indent=2) + "\n")
    (DIR / "METRICS.md").write_text(render_both(m) + "\n")
    print(json.dumps({lang: {"criterion1": c["status"], "criterion1a": c["a"], "criterion1b": c["b"],
                             "criterion2a": m["a"]["languages"][lang]["criterion2"]["status"],
                             "criterion2b": m["b"]["languages"][lang]["criterion2"]["status"]} for lang, c in m["criterion1"].items()}, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
