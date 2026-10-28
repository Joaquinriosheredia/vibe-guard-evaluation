"""Calibration chain-v1 (2026-10-28): AI review vs Joaquín, by configuration, corpus and language.

usage: python3 table.py <work-dir> <vibe-guard-evaluation>
  <work-dir>/out-tc{2,3}/review-{a,b}.json   vibe-guard review --protocol chain-v1 outputs
Configurations: "A" = proposer only (review-a.json); "A+B" = proposer + refuter, B's final
verdict (review-b.json). Labels: Joaquín's original (test-corpus-{2,3}/audit-joaquin.json) and
REVIEW-CRITERIA v1 §6 (TC2 J001 FP->TP, TC3 P026 FP->TP). An invalid answer counts as a
disagreement, as in calibration-2026-10-27. Wilson 95 % intervals.
"""
import json
import math
import os
import re
import sys

W, E = sys.argv[1], sys.argv[2]
V1_RELABEL = {('TC2', 'J001'): 'TP', ('TC3', 'P026'): 'TP'}  # REVIEW-CRITERIA.md v1 §6


def wilson(k, n, z=1.959964):
    if n == 0:
        return float('nan'), float('nan'), float('nan')
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


def fmt(k, n):
    if not n:
        return '—'
    p, lo, hi = wilson(k, n)
    return f'{k}/{n} = {p:.2f} [{lo:.2f}–{hi:.2f}]'


def entries(path):
    return {e['id']: e for e in json.load(open(path))['entries']}


rows = []
for c in ('2', '3'):
    corp = f'TC{c}'
    orig = {v['id']: v['verdict'] for v in json.load(open(f'{E}/test-corpus-{c}/audit-joaquin.json'))['verdicts']}
    a = entries(f'{W}/out-tc{c}/review-a.json')
    b = entries(f'{W}/out-tc{c}/review-b.json')
    for i in sorted(orig):
        ea, eb = a.get(i), b.get(i)
        va = ea['verdict'] if ea and ea.get('valid') else None
        vb = eb['verdict'] if eb and eb.get('valid') else None
        rows.append({
            'corpus': corp, 'id': i, 'lang': 'Java' if i[0] == 'J' else 'Python',
            'orig': orig[i], 'v1': V1_RELABEL.get((corp, i), orig[i]),
            'A': va, 'AB': vb, 'ea': ea, 'eb': eb,
        })

CONFIGS = [('A', 'A (proposer only)'), ('AB', 'A+B (proposer + refuter)')]
GROUPS = [('Java', lambda r: r['lang'] == 'Java'), ('Python', lambda r: r['lang'] == 'Python'), ('Total', lambda r: True)]
out = []


def table(corp, title):
    out.append(f'### {title}\n')
    out.append('| Group | A vs original | A vs v1 | A+B vs original | A+B vs v1 |')
    out.append('|---|---|---|---|---|')
    for name, f in GROUPS:
        rs = [r for r in rows if r['corpus'] == corp and f(r)] if corp else [r for r in rows if f(r)]
        n = len(rs)
        cells = [fmt(sum(r[cfg] == r[lab] for r in rs), n) for cfg in ('A', 'AB') for lab in ('orig', 'v1')]
        out.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    out.append('')


def chain_str(e):
    if not e or not e.get('chain'):
        return '(no chain)'
    return ' → '.join(f"{'[' + h['entry'] + '] ' if h.get('entry') else ''}{h['symbol']} @ {h['at']}" for h in e['chain'])


def why(e):
    if not e:
        return 'no answer'
    if not e.get('valid'):
        return 'INVALID: ' + '; '.join(e.get('problems') or [])[:400]
    s = e.get('reason') or ''
    if e.get('coerced'):
        s = f"[coerced {e['coerced']['from']}→U: {'; '.join(e['coerced']['problems'])[:300]}] " + s
    crit = ', '.join(e.get('criteria') or [])
    fc = f" fails: {e['fpCondition']}" if e.get('fpCondition') else ''
    return f'({crit}{fc}) {s}'


out.append('## Agreement with Joaquín\n')
table('TC3', 'TC3 — clean exam (main figure)')
table('TC2', 'TC2 — contaminated by the few-shot examples (informative only)')
table(None, 'TC2+TC3 (informative)')

# Cases whose first run failed for infrastructure reasons (plan timeout), re-run on their own into
# <work-dir>/out-tc2-retry. Reported separately; the tables above keep the first run as it was.
retry_dir = f'{W}/out-tc2-retry'
if os.path.isdir(retry_dir):
    ra, rb = entries(f'{retry_dir}/review-a.json'), entries(f'{retry_dir}/review-b.json')
    first = {r['id']: r for r in rows if r['corpus'] == 'TC2'}
    out.append(f"### TC2 with {', '.join(sorted(ra))} re-run (informative)\n")
    out.append('| Id | Joaquín original | Joaquín v1 | first run A / A+B | re-run A / A+B |')
    out.append('|---|---|---|---|---|')
    swapped = []
    for i in sorted(ra):
        r = first[i]
        va = ra[i]['verdict'] if ra[i].get('valid') else None
        vb = rb[i]['verdict'] if i in rb and rb[i].get('valid') else None
        out.append(f"| {i} | {r['orig']} | {r['v1']} | {r['A'] or 'invalid'} / {r['AB'] or 'invalid'} | {va or 'invalid'} / {vb or 'invalid'} |")
        swapped.append({**r, 'A': va, 'AB': vb})
    rs = [r for r in rows if r['corpus'] == 'TC2' and r['id'] not in ra] + swapped
    cells = [fmt(sum(r[cfg] == r[lab] for r in rs), len(rs)) for cfg in ('A', 'AB') for lab in ('orig', 'v1')]
    out.append('')
    out.append('| TC2 Total with re-run | A vs original | A vs v1 | A+B vs original | A+B vs v1 |')
    out.append('|---|---|---|---|---|')
    out.append('| Total | ' + ' | '.join(cells) + ' |')
    out.append('')
    for i in sorted(ra):
        out.append(f"- re-run {i} A chain: {chain_str(ra[i])}")
        out.append(f"  - A why: {why(ra[i])}")
    out.append('')

# Comparison with 2026-10-27 (same 52 cases, original labels; legacy protocol, TC3 instructions).
prev = {}
for line in open(f'{E}/calibration-2026-10-27/table-output.txt'):
    m = re.match(r'\| (TC2\+TC3|TC2|TC3) (Java|Python|Total) \| (\d+)/(\d+)[^|]*\| (\d+)/(\d+)[^|]*\| (\d+)/(\d+)', line)
    if m:
        prev[(m.group(1), m.group(2))] = tuple(int(x) for x in m.groups()[2:])
out.append('## Compared with calibration-2026-10-27 (original labels)\n')
out.append('2026-10-27: legacy protocol, test-corpus-3 instructions for both corpora; "consensus" = A and B agree, scored on the cases where they do. Today: chain-v1, root instructions v1, TC2-only examples.\n')
out.append('| Group | 27 A | 27 B (final) | 27 consensus | 28 A | 28 A+B | 28 consensus |')
out.append('|---|---|---|---|---|---|---|')
for corp in ('TC3', 'TC2', 'TC2+TC3'):
    rs = [r for r in rows if corp == 'TC2+TC3' or r['corpus'] == corp]
    p = prev.get((corp, 'Total'))
    cons = [r for r in rs if r['A'] and r['A'] == r['AB']]
    today = [fmt(sum(r['A'] == r['orig'] for r in rs), len(rs)), fmt(sum(r['AB'] == r['orig'] for r in rs), len(rs)),
             fmt(sum(r['A'] == r['orig'] for r in cons), len(cons))]
    before = [fmt(p[0], p[1]), fmt(p[2], p[3]), fmt(p[4], p[5])] if p else ['—'] * 3
    out.append(f'| {corp} Total | ' + ' | '.join(before + today) + ' |')
out.append('')

# Run facts.
def allentries():
    for r in rows:
        for role, e in (('A', r['ea']), ('B', r['eb'])):
            if e:
                yield r, role, e


coerced = [(r['corpus'], r['id'], role, e['coerced']['from']) for r, role, e in allentries() if e.get('coerced')]
invalid = [(r['corpus'], r['id'], role) for r, role, e in allentries() if not e.get('valid')]
cost = sum((h.get('meta') or {}).get('costUsd') or 0 for _, _, e in allentries() for h in e.get('history', []))
retries = sum(1 for _, _, e in allentries() if (e.get('attempts') or 0) > 1)
out.append('## Run facts\n')
out.append(f'- answers: {sum(1 for _ in allentries())} (A and B over {len(rows)} cases); re-asked once: {retries}')
out.append(f'- invalid: {len(invalid)}' + (f" — {', '.join(f'{c} {i} {ro}' for c, i, ro in invalid)}" if invalid else ''))
out.append(f'- turned into U by rule e: {len(coerced)}' + (f" — {', '.join(f'{c} {i} {ro} (from {f})' for c, i, ro, f in coerced)}" if coerced else ''))
out.append(f'- API-equivalent cost reported by the CLI: ${cost:.2f} (billed to the Max subscription, not to an API key)')
out.append('')

# Failures.
out.append('## Failures (vs v1 labels)\n')
for corp in ('TC3', 'TC2'):
    out.append(f'### {corp}\n')
    for r in rows:
        if r['corpus'] != corp or (r['A'] == r['v1'] and r['AB'] == r['v1']):
            continue
        tag = [x for x, bad in (('A', r['A'] != r['v1']), ('A+B', r['AB'] != r['v1'])) if bad]
        note = f" (original {r['orig']})" if r['orig'] != r['v1'] else ''
        out.append(f"- **{r['id']}** ({r['lang']}): Joaquín v1 {r['v1']}{note} · A {r['A'] or 'invalid'} · A+B {r['AB'] or 'invalid'} — fails in {', '.join(tag)}")
        out.append(f"  - A chain: {chain_str(r['ea'])}")
        out.append(f"  - A why: {why(r['ea'])}")
        if r['AB'] != r['v1']:
            out.append(f"  - B ({(r['eb'] or {}).get('decision') or '—'}) chain: {chain_str(r['eb'])}")
            out.append(f"  - B why: {why(r['eb'])}")
    out.append('')

print('\n'.join(out))
