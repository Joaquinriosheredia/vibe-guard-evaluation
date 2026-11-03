"""Comprueba que documentos, JSON y cálculos dicen lo mismo (criterio v2, evaluación de desarrollo).

uso: python3 criterio-v2-desarrollo/comprobar.py  (desde la raíz del repo); sale con 1 si algo no cuadra.
Recalcula desde cero, sin importar propuesta.py: la población (fichas y audit-joaquin.json de TC4) y los recuentos de
PYVIBE-012 (pyvibe-012-mecanismos.tsv). Después compara con propuesta-v2.json, con las cifras de PROPUESTA-v2.md,
con DISENO-PYVIBE-012.md, con REVIEW-CRITERIA-v2.md y con el borrador de TC5. También comprueba que los resultados
publicados de TC1–TC4 siguen coincidiendo con su sha256.
"""
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict

D = 'criterio-v2-desarrollo'
problems = []


def check(cond, msg):
    if not cond:
        problems.append(msg)


def wilson(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 4), round(c - h, 4), round(c + h, 4)]


# 1. Población TC4 recalculada desde las fichas
pop = defaultdict(Counter)
ids4 = {}
for v in json.load(open('test-corpus-4/audit-joaquin.json'))['verdicts']:
    card = open(f'test-corpus-4/cards/{v["id"]}.md').read()
    rule = re.search(r'Rule: `([^`]+)`', card).group(1)
    repo = re.search(r'github\.com/([\w.-]+/[\w.-]+)/tree', card).group(1)
    pop[rule][repo] += 1
    ids4[v['id']] = rule
p12_ids = sorted(i for i, r in ids4.items() if r == 'PYVIBE-012')
n, repos = len(p12_ids), len(pop['PYVIBE-012'])

# 2. Mecanismos desde el TSV
lines = open(f'{D}/pyvibe-012-mecanismos.tsv', encoding='utf-8').read().splitlines()
hdr = lines[0].split('\t')
mech = [dict(zip(hdr, l.split('\t'))) for l in lines[1:]]
m4 = {r['id']: r for r in mech if r['corpus'] == '4'}
check(sorted(m4) == p12_ids, f'el TSV de TC4 no tiene exactamente los {n} IDs de PYVIBE-012 de las fichas')
for r in mech:
    for k in ('b1_perdida_no_retencion', 'b2_excepcion_sin_supervision', 'b3_ausencia_recuperacion'):
        check(r[k] in ('sí', 'no', 'U', '—'), f"{r['corpus']} {r['id']}: {k}={r[k]!r}")
    check(r['b3_ausencia_recuperacion'] == '—' or r['b2_excepcion_sin_supervision'] == 'sí',
          f"{r['corpus']} {r['id']}: b3 evaluado sin b2 = sí")
    check(r['b2_excepcion_sin_supervision'] != 'sí' or r['b3_ausencia_recuperacion'] in ('sí', 'no'),
          f"{r['corpus']} {r['id']}: b2 = sí sin b3")
k = {
    'b1_si': sum(r['b1_perdida_no_retencion'] == 'sí' for r in m4.values()),
    'b2_si': sum(r['b2_excepcion_sin_supervision'] == 'sí' for r in m4.values()),
    'b2_y_b3_si': sum(r['b2_excepcion_sin_supervision'] == 'sí' and r['b3_ausencia_recuperacion'] == 'sí' for r in m4.values()),
    'U': sum(r['b2_excepcion_sin_supervision'] == 'U' for r in m4.values()),
}
k['a_contrato_TP'] = n - k['U']

# 3. JSON
js = json.load(open(f'{D}/propuesta-v2.json'))
s = js['seleccion']['PYVIBE-012']
check(js['poblacion'] == 'TC4', 'el JSON no declara la población TC4')
check((s['n'], s['repos']) == (n, repos), f"JSON n/repos {s['n']}/{s['repos']} != {n}/{repos}")
for key, val in k.items():
    check(s[key]['k'] == val and s[key]['n'] == n, f'JSON {key} {s[key]} != {val}/{n}')
    check(s[key]['wilson95'] == wilson(val, n), f'JSON {key} Wilson {s[key]["wilson95"]} != {wilson(val, n)}')
check(js['poblacion_por_regla'] == {r: dict(sorted(c.items())) for r, c in js['poblacion_por_regla'].items()} and
      {r: sum(c.values()) for r, c in js['poblacion_por_regla'].items()} == {r: sum(c.values()) for r, c in pop.items()},
      'JSON: población por regla distinta de las fichas')
check(all(not v for v in s['pasa_umbral_CRITICAL'].values()), 'JSON: algún mecanismo pasa el umbral CRITICAL')
cases = {(c['corpus'], c['id']): c for c in js['casos']}
for r in mech:
    c = cases[(f"TC{r['corpus']}", r['id'])]
    check((c['b1'], c['b2'], c['b3']) == (r['b1_perdida_no_retencion'], r['b2_excepcion_sin_supervision'], r['b3_ausencia_recuperacion']),
          f"JSON y TSV difieren en {r['corpus']} {r['id']}")
    check(c.get('gravedad') == 'WARNING' and c.get('categoria') == 'incumplimiento de recomendación documentada de uso seguro',
          f"{r['corpus']} {r['id']}: categoría/gravedad")


# 4. Documentos
def fmt(key):
    w = wilson(k[key], n)
    return f'{k[key]}/{n} = {w[0]:.2f} [{w[1]:.2f}–{w[2]:.2f}]'


prop = open(f'{D}/PROPUESTA-v2.md').read()
check(f'| PYVIBE-012 | {n} | {repos} |' in prop, 'PROPUESTA: fila de población de PYVIBE-012')
for key in k:
    check(fmt(key) in prop, f'PROPUESTA: falta la cifra {key} = {fmt(key)}')
check(f'solo TC4 ({n} casos de PYVIBE-012, {repos} repos)' in prop, 'PROPUESTA: registro de la población')
check('Ninguna regla evaluada reúne hoy los requisitos para CRITICAL automático' in prop, 'PROPUESTA: frase de CRITICAL')
tbl = [l for l in prop.splitlines() if re.match(r'^\| TC4 \| P\d{3} \|', l)]
check(len(tbl) == n, f'PROPUESTA: {len(tbl)} filas de TC4 en la tabla de PYVIBE-012, se esperaban {n}')
dis = open(f'{D}/DISENO-PYVIBE-012.md').read()
for label, key in (('b1, pérdida por no retención', 'b1_si'), ('b2, excepción sin supervisión', 'b2_si'), ('b2 y b3 (además, sin recuperación)', 'b2_y_b3_si')):
    check(f'| {label} | {k[key]} |' in dis, f'DISEÑO: cifra de {label}')
check(f'(n = {n})' in dis, 'DISEÑO: n')
crit = open('REVIEW-CRITERIA-v2.md').read()
check('Ninguna regla evaluada reúne hoy los requisitos para CRITICAL automático' in crit, 'v2: frase de CRITICAL')
check('No tiene umbral de aceptación' in crit, 'v2: WARNING sin umbral')
check('Cerrar v2 aprueba el criterio, no valida reglas ni resuelve casos sin evidencia' in crit, 'v2: cierre no valida')
check('CONTRACT' not in crit + prop + dis, 'aparece una escala CONTRACT')
tc5 = open('tc5-borrador/PREREGISTRATION-BORRADOR.md').read()
for frag in ('≥ 30', '≥ 5', '≥ 0,90', 'U como no-TP', 'Sin CRITICAL automático', 'TC5 está aparcado'):
    check(frag in tc5, f'TC5: falta «{frag}»')

# 5. TC1–TC4 intactos
for c in '1234':
    for f in ('audit-joaquin.json',):
        try:
            data = open(f'test-corpus-{c}/{f}', 'rb').read()
        except FileNotFoundError:
            continue
        exp = open(f'test-corpus-{c}/audit-joaquin.sha256').read().split()[0]
        check(hashlib.sha256(data).hexdigest() == exp, f'TC{c} audit-joaquin.json no coincide con su sha256')

print(f'PYVIBE-012 TC4: n={n}, repos={repos}, ' + ', '.join(f'{key}={val}' for key, val in k.items()))
if problems:
    print('NO CUADRA:\n- ' + '\n- '.join(problems))
    sys.exit(1)
print('OK: documentos, JSON y cálculos coinciden; TC1–TC4 intactos')
