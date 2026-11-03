"""Calibración Codex 2026-11-02 (informativa): Claude proponente, Codex solo y consenso Claude = Codex
frente a los veredictos de Joaquín, por corpus e idioma.

uso: python3 table.py <codex-work> <claude-v1-work> <tc4-ai-review> <vibe-guard-evaluation>
  <codex-work>/out-tc{2,3,4}/review-a.json       Codex, chain-v1, solo proponente
  <claude-v1-work>/out-tc{2,3}/review-a.json     Claude proponente, calibración v1 del 2026-10-28 (ejecución principal)
  <claude-v1-work>/out-tc2-retry/review-a.json   re-ejecución de TC2 J001/P116 (sección aparte)
  <tc4-ai-review>/review-a.json                  Claude proponente de TC4, sellado (ai-review.sha256)
Etiquetas: las originales de Joaquín (test-corpus-N/audit-joaquin.json) y las v1 (REVIEW-CRITERIA.md v1 §6:
TC2 J001 FP->TP, TC3 P026 FP->TP; TC4 se revisó ya con v1). Una respuesta inválida cuenta como desacuerdo;
en el consenso, un inválido en cualquiera de los dos es "sin acuerdo". Wilson 95 %.
"""
import hashlib
import json
import math
import sys

CW, VW, T4, E = sys.argv[1:5]
V1_RELABEL = {('TC2', 'J001'): 'TP', ('TC3', 'P026'): 'TP'}
CORPORA = ('2', '3', '4')


def wilson(k, n, z=1.959964):
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


def verdict(e):
    return e['verdict'] if e and e.get('valid') and e.get('verdict') in ('TP', 'FP', 'U') else None


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


sealed = open(f'{E}/test-corpus-4/ai-review.sha256').read().split()[0]
assert sha(f'{T4}/review-a.json') == sealed, 'TC4 Claude review-a.json does not match ai-review.sha256'
for c in CORPORA:
    assert sha(f'{E}/test-corpus-{c}/audit-joaquin.json') == open(f'{E}/test-corpus-{c}/audit-joaquin.sha256').read().split()[0]

rows = []
for c in CORPORA:
    corp = f'TC{c}'
    orig = {v['id']: v['verdict'] for v in json.load(open(f'{E}/test-corpus-{c}/audit-joaquin.json'))['verdicts']}
    cl = entries(f'{T4}/review-a.json' if c == '4' else f'{VW}/out-tc{c}/review-a.json')
    cx = entries(f'{CW}/out-tc{c}/review-a.json')
    for i in sorted(orig):
        rows.append({'corpus': corp, 'id': i, 'lang': 'Java' if i[0] == 'J' else 'Python',
                     'orig': orig[i], 'v1': V1_RELABEL.get((corp, i), orig[i]),
                     'claude': verdict(cl.get(i)), 'codex': verdict(cx.get(i)), 'ecl': cl.get(i), 'ecx': cx.get(i)})

GROUPS = [('Java', lambda r: r['lang'] == 'Java'), ('Python', lambda r: r['lang'] == 'Python'), ('Total', lambda r: True)]
out = ['# Calibración Codex 2026-11-02 — tablas', '',
       'Wilson 95 %. Inválido = desacuerdo. Consenso: cobertura = casos en que Claude y Codex dan el mismo veredicto válido; '
       'acierto = de esos, los que coinciden con Joaquín.', '']


def table(sel, title):
    out.append(f'## {title}\n')
    out.append('| Grupo | n | Claude vs original | Claude vs v1 | Codex vs original | Codex vs v1 | Consenso: cobertura | Consenso: acierto vs original | Consenso: acierto vs v1 |')
    out.append('|---|---|---|---|---|---|---|---|---|')
    for name, f in GROUPS:
        rs = [r for r in rows if sel(r) and f(r)]
        n = len(rs)
        agree = [r for r in rs if r['claude'] is not None and r['claude'] == r['codex']]
        cells = [fmt(sum(r[m] == r[lab] for r in rs), n) for m in ('claude', 'codex') for lab in ('orig', 'v1')]
        cells += [fmt(len(agree), n), fmt(sum(r['claude'] == r['orig'] for r in agree), len(agree)), fmt(sum(r['claude'] == r['v1'] for r in agree), len(agree))]
        out.append(f'| {name} | {n} | ' + ' | '.join(cells) + ' |')
    out.append('')


for c in CORPORA:
    table(lambda r, c=c: r['corpus'] == f'TC{c}', {'2': 'TC2 — contaminado por los ejemplos few-shot (informativo)',
                                                   '3': 'TC3', '4': 'TC4 (Claude: revisión sellada)'}[c])
table(lambda r: r['corpus'] in ('TC3', 'TC4'), 'TC3 + TC4 (sin el corpus de los ejemplos)')
table(lambda r: True, 'TC2 + TC3 + TC4')


def why(e):
    if e is None:
        return '(sin respuesta)'
    if not e.get('valid'):
        errs = [p for h in (e.get('history') or []) for p in (h.get('problems') or [])]
        return 'INVÁLIDA: ' + ('; '.join(errs)[-300:] if errs else 'sin detalle')
    cond = f" ({e['fpCondition']})" if e.get('fpCondition') else ''
    return f"{e['verdict']}{cond}: {' '.join((e.get('reason') or '').split())}"


out.append('## Fallos (vs etiquetas v1)\n')
out.append('Motivo = la razón que dio el modelo que falla (o el error, si su respuesta fue inválida).\n')
for c in CORPORA:
    corp = f'TC{c}'
    fails = [r for r in rows if r['corpus'] == corp and (r['claude'] != r['v1'] or r['codex'] != r['v1'])]
    out.append(f'### {corp}: {len(fails)} casos con algún fallo\n')
    out.append('| ID | Idioma | Joaquín v1 | Claude | Codex | Falla |')
    out.append('|---|---|---|---|---|---|')
    for r in fails:
        who = ' + '.join(m for m, k in (('Claude', 'claude'), ('Codex', 'codex')) if r[k] != r['v1'])
        out.append(f"| {r['id']} | {r['lang']} | {r['v1']} | {r['claude'] or 'inválido'} | {r['codex'] or 'inválido'} | {who} |")
    out.append('')
    for r in fails:
        if r['claude'] != r['v1']:
            out.append(f"- {corp} {r['id']} Claude — {why(r['ecl'])}")
        if r['codex'] != r['v1']:
            out.append(f"- {corp} {r['id']} Codex — {why(r['ecx'])}")
    out.append('')

out.append('## TC2 con la re-ejecución de Claude de J001/P116 (calibración del 28, informativa)\n')
retry = entries(f'{VW}/out-tc2-retry/review-a.json')
for i in sorted(retry):
    r = next(x for x in rows if x['corpus'] == 'TC2' and x['id'] == i)
    out.append(f"- {i}: Joaquín v1 {r['v1']}; Claude principal {r['claude'] or 'inválido'}, re-ejecución {verdict(retry[i]) or 'inválido'}; Codex {r['codex'] or 'inválido'}")
out.append('')

out.append('## Datos de la ejecución de Codex\n')
cx_all = [r['ecx'] for r in rows]
inv = [f"{r['corpus']} {r['id']}" for r in rows if r['codex'] is None]
out.append(f'- respuestas: {sum(e is not None for e in cx_all)} de {len(rows)}; inválidas: {len(inv)}' + (f" — {', '.join(inv)}" if inv else ''))
out.append(f"- re-preguntadas (más de un intento de revisión): {sum(1 for e in cx_all if e and (e.get('attempts') or 0) > 1)}")
coerced = [f"{r['corpus']} {r['id']}" for r in rows if r['ecx'] and r['ecx'].get('coerced')]
out.append(f'- convertidas a U por la regla e: {len(coerced)}' + (f" — {', '.join(coerced)}" if coerced else ''))
tok = {'input_tokens': 0, 'cached_input_tokens': 0, 'output_tokens': 0}
for e in cx_all:
    for h in (e or {}).get('history') or []:
        for k in tok:
            tok[k] += ((h.get('meta') or {}).get('usage') or {}).get(k) or 0
out.append(f"- tokens informados por Codex (todas las llamadas): entrada {tok['input_tokens']:,} (en caché {tok['cached_input_tokens']:,}), salida {tok['output_tokens']:,}")
models = sorted({m for e in cx_all if e for m in (e.get('modelsUsed') or [e.get('model')]) if m})
out.append(f"- modelo: {', '.join(models) or '—'}")
print('\n'.join(out))
