"""Evaluación de desarrollo con REVIEW-CRITERIA v2 (asistida): etiqueta v2 PROPUESTA por Claude, con su razón,
para los casos con veredicto de Joaquín. Joaquín confirma o corrige.

uso: python3 criterio-v2-desarrollo/propuesta.py  (desde la raíz del repo) -> propuesta-v2.json, PROPUESTA-v2.md

Población de selección (decisión de Joaquín, 2026-11-03): SOLO TC3 + TC4, solo casos con su veredicto.
TC2 queda como ejemplos auxiliares. Reglas que pueden ser candidatas en esa población: las de n >= 15 y
>= 5 repos; transactions queda fuera porque REVIEW-CRITERIA-v2 §3 la limita a WARNING.
PYVIBE-012 lleva dos campos por caso: (a) contrato de retención de asyncio; (b) escenario de fallo
funcional respaldado por código (pyvibe-012-campo-b.tsv, revisado caso por caso). Para CRITICAL cuenta (b).
No calcula tasas: la selección (C) va después de la confirmación de Joaquín.
"""
import json
import re
from collections import Counter, defaultdict

POPULATION = ('3', '4')
AUX = ('2',)
V1 = {('2', 'J001'): 'TP', ('3', 'P026'): 'TP'}  # REVIEW-CRITERIA.md v1 §6
D = 'criterio-v2-desarrollo'

# blocking / PYVIBE-009 / transactions revisados con las decisiones del 2026-11-03: (v2, condición FP, razón)
CUSTOM = {
    ('2', 'J015'): ('FP', 'context', 'Fixture: `Thread.sleep(100)` en el job `increment()` con `cron = "*/1 * * * * ?"` (`integration-tests/opentelemetry-quartz/src/main/java/io/quarkus/it/opentelemetry/quartz/Counter.java:24–27`), igual que `FailedBasicScheduler.java:10–13`. La cadencia de un cron no es una propiedad (v2 §1), y el módulo no exige ningún plazo, así que no se incumple ninguna propiedad.'),
    ('2', 'J001'): ('FP', 'context', '`SampleBackground.java:38–41`: sleep aleatorio < 1 s, con cota, en el único `@Async` del módulo (`study-spring-boot-zipkin`, sin `@Scheduled` ni configuración de executor); la ruta `/async` no espera el resultado (`SampleController.java:85–88`) y nada en el módulo exige un plazo, así que no se incumple ninguna propiedad.'),
    ('3', 'J001'): ('FP', 'context', '`BookTestDataQueryRunner.java:22–24`: `Thread.sleep(10000)` en el único `@Scheduled` de la app. Un cron fija activaciones, no un SLA: Spring se salta las activaciones mientras la anterior sigue ocupada, y el repositorio no exige ningún plazo ni frescura a este runner de datos de prueba (v2 §1).'),
    ('2', 'J052'): ('U', None, '`saveToEs` duerme 3 s por cada proceso que termina (`y9-module-processadmin/risenet-y9boot-support-processadmin/src/main/java/net/risesoft/service/impl/Process4CompleteUtilServiceImpl.java:283–299`, llamado en `TaskListener4ProcessCompleted.java:61`). La app activa `@EnableAsync` (`risenet-y9boot-server-processadmin/src/main/java/net/risesoft/ProcessAdminApplication.java:23`) sin executor propio ni `spring.task` en el módulo, así que el executor efectivo puede venir de los starters `risenet-y9boot-starter-*` (`risenet-y9boot-server-processadmin/pom.xml:37,49,66`), que están fuera del repositorio. Ningún código muestra la frecuencia o el volumen que llenarían un executor acotado. Falta configuración decisiva.'),
    ('2', 'J056'): ('FP', 'context', 'El `join()` (`AzDevOpsPollingService.java:101–110`) tiene cota: HTTP con connect 5 s, respuesta 30 s y espera de pool 2 s (`WebhookHttpClientConfig.java:33–46`, usado en `WebhookServiceBase.java:125–128`) y token SP/MI con `block(30 s)` (`AzDevOpsTokenService.java:115`). Sí retrasa al otro job `fixedDelay` (`CliAuthSessionCleanupTask.java:19`), porque con `SimpleAsyncTaskScheduler` los `fixedDelay` comparten un hilo, pero la purga no tiene plazo exigido: las sesiones caducadas se rechazan al usarlas (`CliLoginService.java:228`). La etiqueta es la misma que la original, por otra razón (decisión 1 del 2026-11-03).'),
    ('3', 'P026'): ('TP', None, 'Contrato: `create_task(task())` sin conservar la referencia en una ruta de producción (`backend/app/api/kline.py:1009`).'),
    ('4', 'J053'): ('TP', None, '`ingestEvent` es `@Transactional` (`IngestionServiceImpl.java:46`) y llama a `diagnoseIssueAsync` solo para issues nuevos (`:155–156`). La rama local es rápida (`AIDiagnosticServiceImpl.java:124–130`), y el worker relee el issue en su propia transacción y descarta el resultado sin avisar si no lo encuentra (`:143–146`). Es lo que afirma el mensaje: el worker no ve los cambios sin confirmar del llamador. Confirmado por Joaquín (decisión 5 del 2026-11-03).'),
}


def card_info(c, i):
    card = open(f'test-corpus-{c}/cards/{i}.md').read()
    return (re.search(r'Rule: `([^`]+)`', card).group(1), re.search(r'github\.com/([\w.-]+/[\w.-]+)/tree', card).group(1))


def main():
    campo_b = {(r[0], r[1]): (r[2], r[3]) for r in (l.rstrip('\n').split('\t') for l in open(f'{D}/pyvibe-012-campo-b.tsv', encoding='utf-8'))}
    cases = []
    for c in POPULATION + AUX:
        for v in json.load(open(f'test-corpus-{c}/audit-joaquin.json'))['verdicts']:
            rule, repo = card_info(c, v['id'])
            orig, v1 = v['verdict'], V1.get((c, v['id']), v['verdict'])
            x = {'corpus': f'TC{c}', 'id': v['id'], 'rule': rule, 'repo': repo, 'poblacion': c in POPULATION,
                 'original': orig, 'v1': v1, 'overstated_original': v.get('overstated')}
            if rule == 'PYVIBE-012':
                b, why_b = campo_b[(c, v['id'])]
                x.update(v2=v1 if (c, v['id']) != ('3', 'P026') else 'TP', fp_condition=None,
                         a='sí', b=b, razon=why_b)
                if (c, v['id']) == ('4', 'P058'):
                    x.update(v2='U', a='sí (patrón presente; alcanzabilidad no demostrada)')
            elif (c, v['id']) in CUSTOM:
                v2, cond, why = CUSTOM[(c, v['id'])]
                x.update(v2=v2, fp_condition=cond, razon=why)
            else:
                continue
            cases.append(x)
    # Población declarada: todos los casos con veredicto de Joaquín en TC3 + TC4, por regla y por repo.
    pop = defaultdict(Counter)
    for c in POPULATION:
        for v in json.load(open(f'test-corpus-{c}/audit-joaquin.json'))['verdicts']:
            rule, repo = card_info(c, v['id'])
            pop[rule][repo] += 1
    json.dump({'criterio': 'REVIEW-CRITERIA-v2.md (borrador, revisado el 2026-11-03)', 'asistida': True, 'propone': 'Claude',
               'confirma': 'Joaquín (pendiente salvo lo indicado)', 'poblacion': 'TC3 + TC4', 'auxiliar': 'TC2',
               'poblacion_por_regla': {r: dict(sorted(cnt.items())) for r, cnt in sorted(pop.items(), key=lambda kv: -sum(kv[1].values()))},
               'casos': cases}, open(f'{D}/propuesta-v2.json', 'w'), indent=1, ensure_ascii=False)
    render(cases, pop)


def render(cases, pop):
    L = ['# Evaluación de desarrollo con REVIEW-CRITERIA v2: etiquetas propuestas', '',
         '**Evaluación asistida de desarrollo.** Claude propone la etiqueta v2 de cada caso y su razón; Joaquín la confirma o corrige. No es una revisión ciega ni sustituye a ningún resultado publicado: TC2–TC4 conservan sus veredictos, métricas y conclusiones. Criterio: `../REVIEW-CRITERIA-v2.md`. Esta propuesta no calcula tasas por regla: la selección (C) va después de tu confirmación.', '',
         '## Registro', '',
         '- **2026-11-03, primera propuesta:** 101 casos de TC2–TC4 (PYVIBE-012, `blocking`, PYVIBE-009).',
         '- **2026-11-03, correcciones de Joaquín a B, aplicadas aquí:**',
         '  - **Población de selección:** solo TC3 + TC4; TC2 queda como ejemplos auxiliares.',
         '  - **TC2 J015:** FP por contexto; es un fixture y no se incumple ninguna propiedad. No se usan los 25 hilos de Quartz como prueba.',
         '  - **TC3 J001:** FP por contexto. Un cron fija activaciones, no un SLA; solo sería TP con una obligación de plazo o frescura en el repositorio.',
         '  - **TC2 J001:** FP por contexto. La exclusión de repositorios de estudio es una regla de triaje, no la razón del veredicto.',
         '  - **TC2 J052:** TP solo con una contención plausible apoyada en código; U si falta configuración decisiva; FP si el contexto demuestra que no se incumple nada. Revisado: U.',
         '  - **TC3 P026:** TP por contrato.',
         '  - **PYVIBE-012:** dos campos por caso, (a) contrato y (b) fallo funcional respaldado por código. Para CRITICAL cuenta (b). Revisados los 65 casos uno a uno.',
         '- **2026-11-03, decisiones de Joaquín sobre las segundas opiniones de Codex, aplicadas en `REVIEW-CRITERIA-v2.md` y aquí:**',
         '  - **J056:** comprobado que el `join()` tiene cota y que no hay plazo exigido, así que es FP.',
         '  - **Frontera FP/U:** FP solo si el repositorio demuestra que no se incumple nada; U si falta configuración decisiva. Con esta regla se re-evaluaron TC2 J001, TC2 J015 y TC3 J001.',
         '  - **Cadencias:** la cadencia del propio job no es una propiedad sin un plazo exigido.',
         '  - **`transactions`:** opción (a).',
         '  - **J053:** pasa de U a TP.',
         '  - **`kafka-send-timeout`:** comprobado en TC3 J017.',
         '  - **Celery:** solo un límite duro.',
         '  - **§2:** la confirmación CRITICAL remite al pre-registro de TC5.', '',
         '## 1. Población de selección (declarada)', '',
         'Todos los casos con tu veredicto en **TC3 + TC4**. TC3 y TC4 no comparten ninguna ubicación ni ningún repositorio. TC2 no entra en la selección; solo aporta ejemplos auxiliares.', '',
         '| Regla | n | Repos | Máx. por repo | ¿Candidata? (n ≥ 15 y ≥ 5 repos) |', '|---|---|---|---|---|']
    for r, cnt in sorted(pop.items(), key=lambda kv: -sum(kv[1].values())):
        n, k = sum(cnt.values()), len(cnt)
        cand = 'no: WARNING como máximo (v2 §3)' if r == 'transactions' else ('**sí**' if n >= 15 and k >= 5 else 'no')
        L.append(f'| {r} | {n} | {k} | {max(cnt.values())} | {cand} |')
    L += ['', '**La única regla candidata es PYVIBE-012.** n por repo en la población:', '',
          '| Repo | n |', '|---|---|'] + [f'| {repo} | {n} |' for repo, n in sorted(pop['PYVIBE-012'].items(), key=lambda kv: (-kv[1], kv[0]))]
    p12 = [x for x in cases if x['rule'] == 'PYVIBE-012']
    H = '| Corpus | ID | Repo | Original | v1 | v2 | (a) contrato | (b) fallo funcional | Razón de (b) |\n|---|---|---|---|---|---|---|---|---|'
    row = lambda x: f"| {x['corpus']} | {x['id']} | {x['repo']} | {x['original']} | {x['v1']} | {x['v2']} | {x['a']} | **{x['b']}** | {x['razon']} |"
    L += ['', '## 2. PYVIBE-012: dos campos por caso', '',
          '- **(a) Contrato:** se incumple la recomendación de retención de `asyncio.create_task` (no se conserva ninguna referencia). El veredicto v2 por contrato es TP cuando (a) es sí y la ruta es alcanzable; es la etiqueta que ya tenías, salvo P026 (FP → TP) y P058 (U).',
          '- **(b) Fallo funcional respaldado por código: sí / no / U** (`REVIEW-CRITERIA-v2.md` §3). Revisado leyendo el cuerpo de cada corrutina lanzada y lo que llama. **Para la selección CRITICAL cuenta (b).**', '',
          '### 2.1 Población (TC3 + TC4), primero los que tienen (b) = sí o U', '', H]
    popl = [x for x in p12 if x['poblacion']]
    L += [row(x) for x in sorted(popl, key=lambda x: (x['b'] == 'no', x['corpus'], x['id']))]
    L += ['', '### 2.2 Auxiliares (TC2, fuera de la selección)', '', H] + [row(x) for x in p12 if not x['poblacion']]
    other = [x for x in cases if x['rule'] != 'PYVIBE-012']
    H2 = '| Corpus | ID | Regla | Repo | Original | v1 | v2 propuesta | Razón |\n|---|---|---|---|---|---|---|---|'
    L += ['', '## 3. Otros casos corregidos el 2026-11-03 (reglas no candidatas)', '',
          'Son ejemplos y casos que tus decisiones tocan. No entran en la selección: `blocking` (14) y PYVIBE-009 (12) no llegan a n ≥ 15 en TC3 + TC4, y `transactions` tiene WARNING como máximo.', '', H2]
    L += [f"| {x['corpus']} | {x['id']} | {x['rule']} | {x['repo']} | {x['original']} | {x['v1']} | **{x['v2']}{' (' + x['fp_condition'] + ')' if x['fp_condition'] else ''}** | {x['razon']} |" for x in other]
    L += ['', 'Los demás casos de `blocking` y PYVIBE-009 de la primera propuesta no se han revisado con las decisiones del 2026-11-03, porque esas reglas no son candidatas. Si alguna vuelve a serlo, hay que revisarlos.', '',
          '## Ficheros', '',
          '- `propuesta.py`: genera `propuesta-v2.json` y este fichero.',
          '- `pyvibe-012-campo-b.tsv`: el campo (b) de los 65 casos de PYVIBE-012, con su razón y sus `file:line`.']
    open(f'{D}/PROPUESTA-v2.md', 'w').write('\n'.join(L) + '\n')
    print(len(cases), 'casos;', Counter((x['poblacion'], x['b']) for x in p12))


main()
