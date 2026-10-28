import json, math, sys
S = sys.argv[1]; E = sys.argv[2]

def wilson(k, n, z=1.959964):
    if n == 0: return (float('nan'),) * 3
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return p, c - h, c + h

def entries(path):
    d = json.load(open(path)); es = d['entries']
    return {e['id']: e for e in es}

rows = []  # (corpus, id, lang, J, A, B, cons)
for c in ('2', '3'):
    j = {v['id']: v['verdict'] for v in json.load(open(f'{E}/test-corpus-{c}/audit-joaquin.json'))['verdicts']}
    a = entries(f'{S}/out-tc{c}/review-a.json'); b = entries(f'{S}/out-tc{c}/review-b.json')
    def v(e): return e['verdict'] if e and e.get('valid') else None
    for i in sorted(j):
        va, vb = v(a.get(i)), v(b.get(i))
        rows.append((f'TC{c}', i, 'Java' if i[0] == 'J' else 'Python', j[i], va, vb, va if va and va == vb else None))

def fmt(k, n):
    p, lo, hi = wilson(k, n)
    return f'{k}/{n} = {p:.2f} [{lo:.2f}–{hi:.2f}]' if n else '—'

print('| Grupo | A vs Joaquín | B vs Joaquín | Consenso (A=B) vs Joaquín | Cobertura del consenso |')
print('|---|---|---|---|---|')
groups = [('Java', lambda r: r[2] == 'Java'), ('Python', lambda r: r[2] == 'Python'), ('Total', lambda r: True)]
for corp in ('TC2', 'TC3', None):
    for name, f in groups:
        rs = [r for r in rows if f(r) and (corp is None or r[0] == corp)]
        n = len(rs)
        ka = sum(r[4] == r[3] for r in rs); kb = sum(r[5] == r[3] for r in rs)
        cs = [r for r in rs if r[6]]; kc = sum(r[6] == r[3] for r in cs)
        print(f'| {corp or "TC2+TC3"} {name} | {fmt(ka,n)} | {fmt(kb,n)} | {fmt(kc,len(cs))} | {fmt(len(cs),n)} |')

print('\nFallos (ID: Joaquín / A / B):')
for r in rows:
    if r[4] != r[3] or r[5] != r[3]:
        tags = [x for x, bad in (('A', r[4] != r[3]), ('B', r[5] != r[3]), ('consenso', r[6] is not None and r[6] != r[3]), ('sin consenso', r[6] is None)) if bad]
        print(f'{r[0]} {r[1]}: J={r[3]} A={r[4] or "inválido"} B={r[5] or "inválido"}  [{", ".join(tags)}]')
