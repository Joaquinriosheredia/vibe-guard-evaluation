"""Render METRICS.md from metrics.json (produced by evaluate.py).

evaluate.py computes the metrics and writes metrics.json; its docstring also names
METRICS.md but the code never emits it (see DEVIATIONS.md). This script renders that
human-readable table from metrics.json without recomputing anything and without touching
evaluate.py.

  python3 scripts/render_metrics.py  -> METRICS.md
"""
import json
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def ci(c):
    return f"{c[0]:.4f}–{c[1]:.4f}" if c else "—"


def pct(x):
    return "—" if x is None else f"{x:.4f}"


def prow(name, p):
    return (f"| {name} | {p['n']} | {p['TP']} | {p['FP']} | {p['U']} | "
            f"{pct(p['primary'])} | {ci(p['primaryCI95'])} | "
            f"{pct(p['secondary'])} | {ci(p['secondaryCI95'])} |")


def main():
    m = json.loads((DIR / "metrics.json").read_text())
    L = []
    L.append("# Metrics — test-corpus-1")
    L.append("")
    L.append("Generated from `metrics.json` by `scripts/render_metrics.py`. The numbers are"
             " computed by `scripts/evaluate.py` as pre-registered; this file only renders them.")
    L.append("")
    rs = m["reviewSet"]
    L.append(f"Review set: {rs['reviewed']} of {rs['totalCritical']} CRITICAL "
             f"({rs['method']}).")
    L.append("")

    L.append("## Criteria")
    L.append("")
    c1 = m["criterion1"]
    ov = m["overall"]
    L.append(f"- **Criterion 1 (precision, D1):** {'MET' if c1['met'] else 'NOT met'}. "
             f"Rule: {c1['rule']}. Primary point estimate {pct(ov['primary'])} "
             f"(Wilson 95% {ci(ov['primaryCI95'])}), n = {ov['n']}.")
    c2 = m["noise"]["criterion2Met"]
    L.append(f"- **Criterion 2 (noise, D2):** {'MET' if c2 else 'NOT met'}. "
             f"Thresholds per 1,000 files per language: "
             f"critical ≤ {m['noise']['thresholdsPer1000']['critical']}, "
             f"warning ≤ {m['noise']['thresholdsPer1000']['warning']}.")
    L.append("")

    L.append("## Precision")
    L.append("")
    head = ("| Group | n | TP | FP | U | primary | primary 95% CI | secondary | secondary 95% CI |\n"
            "|---|---|---|---|---|---|---|---|---|")
    L.append(head)
    L.append(prow("**overall**", ov))
    for lang, p in m["by_language"].items():
        tag = "" if p.get("conclusive", True) else " (not conclusive)"
        L.append(prow(f"language: {lang}{tag}", p))
    L.append(prow("clustering cap 10/repo", m["clusteringCap10"]))
    L.append("")

    L.append("### By rule")
    L.append("")
    L.append(head)
    for rid, p in m["by_ruleId"].items():
        L.append(prow(rid, p))
    L.append("")

    L.append("## Agreement of the two reviews (blind 20)")
    L.append("")
    ab = m["agreementBlind"]
    L.append(f"- n = {ab['n']}, raw agreement {pct(ab['raw'])}, Cohen's kappa {pct(ab['cohenKappa'])}.")
    L.append(f"- Verdicts changed by the second review: {', '.join(ab['changed']) or 'none'}.")
    us = m["undeterminedSecondReview"]
    L.append(f"- Undetermined re-reviewed: n = {us['n']}, changed from U: "
             f"{', '.join(us['changed']) or 'none'}.")
    L.append(f"- Messages flagged overstated (final verdicts): {m['messageOverstated']}.")
    L.append("")

    L.append("## Noise per 1,000 files")
    L.append("")
    L.append("| Language | files | critical/1000 | warning/1000 | per-repo critical (median/max) | per-repo warning (median/max) | within D2 |")
    L.append("|---|---|---|---|---|---|---|")
    for lang, d in m["noise"]["byLanguage"].items():
        pr = d["perRepo"]
        L.append(f"| {lang} | {d['files']} | {d['per1000']['critical']} | {d['per1000']['warning']} | "
                 f"{pr['critical']['median']}/{pr['critical']['max']} | "
                 f"{pr['warning']['median']}/{pr['warning']['max']} | {'yes' if d['met'] else 'no'} |")
    L.append("")

    (DIR / "METRICS.md").write_text("\n".join(L) + "\n")
    print("wrote METRICS.md")


if __name__ == "__main__":
    main()
