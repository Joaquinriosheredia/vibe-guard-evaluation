"""Evaluación de desarrollo con REVIEW-CRITERIA v2 (asistida): etiquetas v2 propuestas por Claude y confirmadas o
corregidas por Joaquín, y la selección por regla (C) sobre la población declarada.

uso: python3 criterio-v2-desarrollo/propuesta.py  (desde la raíz del repo)
     -> propuesta-v2.json, PROPUESTA-v2.md; luego python3 criterio-v2-desarrollo/comprobar.py

Población de selección (decisión de Joaquín, 2026-11-03): SOLO TC4, todos los casos con su veredicto (revisión
humana completa, test-corpus-4/PREREGISTRATION.md). TC3 queda aparte (sus 25 casos son los 5 desacuerdos A/B y una
muestra de 20 acuerdos, test-corpus-3/REVIEW-AB.md) y TC2 como ejemplos auxiliares.
PYVIBE-012: (a) contrato y, por separado, tres mecanismos del escenario de fallo (pyvibe-012-mecanismos.tsv):
b1 pérdida por no retención, b2 excepción sin supervisión, b3 ausencia de recuperación. Ningún recuento causal se
da por demostrado: los tres se cuentan por separado.
"""
import json
import math
import re
from collections import Counter, defaultdict

POPULATION = ('4',)
APART = ('3',)
AUX = ('2',)
V1 = {('2', 'J001'): 'TP', ('3', 'P026'): 'TP'}  # REVIEW-CRITERIA.md v1 §6
D = 'criterio-v2-desarrollo'
SELECTION = {'n_min': 15, 'repos_min': 5, 'tp_rate_min': 0.90}  # REVIEW-CRITERIA-v2 §2; U cuenta como no-TP

CUSTOM = {
    ('2', 'J015'): ('FP', 'context', 'Fixture: `Thread.sleep(100)` en el job `increment()` con `cron = "*/1 * * * * ?"` (`integration-tests/opentelemetry-quartz/src/main/java/io/quarkus/it/opentelemetry/quartz/Counter.java:24–27`), igual que `FailedBasicScheduler.java:10–13`. La cadencia de un cron no es una propiedad (v2 §1), y el módulo no exige ningún plazo, así que no se incumple ninguna propiedad.'),
    ('2', 'J001'): ('FP', 'context', '`SampleBackground.java:38–41`: sleep aleatorio < 1 s, con cota, en el único `@Async` del módulo (`study-spring-boot-zipkin`, sin `@Scheduled` ni configuración de executor); la ruta `/async` no espera el resultado (`SampleController.java:85–88`) y nada en el módulo exige un plazo, así que no se incumple ninguna propiedad.'),
    ('3', 'J001'): ('FP', 'context', '`BookTestDataQueryRunner.java:22–24`: `Thread.sleep(10000)` en el único `@Scheduled` de la app. Un cron fija activaciones, no un SLA: Spring se salta las activaciones mientras la anterior sigue ocupada, y el repositorio no exige ningún plazo ni frescura a este runner de datos de prueba (v2 §1).'),
    ('2', 'J052'): ('U', None, '`saveToEs` duerme 3 s por cada proceso que termina (`y9-module-processadmin/risenet-y9boot-support-processadmin/src/main/java/net/risesoft/service/impl/Process4CompleteUtilServiceImpl.java:283–299`, llamado en `TaskListener4ProcessCompleted.java:61`). La app activa `@EnableAsync` (`risenet-y9boot-server-processadmin/src/main/java/net/risesoft/ProcessAdminApplication.java:23`) sin executor propio ni `spring.task` en el módulo, así que el executor efectivo puede venir de los starters `risenet-y9boot-starter-*` (`risenet-y9boot-server-processadmin/pom.xml:37,49,66`), que están fuera del repositorio. Ningún código muestra la frecuencia o el volumen que llenarían un executor acotado. Falta configuración decisiva.'),
    ('2', 'J056'): ('FP', 'context', 'El `join()` (`AzDevOpsPollingService.java:101–110`) tiene cota: HTTP con connect 5 s, respuesta 30 s y espera de pool 2 s (`WebhookHttpClientConfig.java:33–46`, usado en `WebhookServiceBase.java:125–128`) y token SP/MI con `block(30 s)` (`AzDevOpsTokenService.java:115`). Sí retrasa al otro job `fixedDelay` (`CliAuthSessionCleanupTask.java:19`), porque con `SimpleAsyncTaskScheduler` los `fixedDelay` comparten un hilo, pero la purga no tiene plazo exigido: las sesiones caducadas se rechazan al usarlas (`CliLoginService.java:228`). La etiqueta es la misma que la original, por otra razón (decisión 1 del 2026-11-03).'),
    ('4', 'J053'): ('TP', None, '`ingestEvent` es `@Transactional` (`IngestionServiceImpl.java:46`) y llama a `diagnoseIssueAsync` solo para issues nuevos (`:155–156`). La rama local es rápida (`AIDiagnosticServiceImpl.java:124–130`), y el worker relee el issue en su propia transacción y descarta el resultado sin avisar si no lo encuentra (`:143–146`). Es lo que afirma el mensaje: el worker no ve los cambios sin confirmar del llamador. Confirmado por Joaquín (decisión 5 del 2026-11-03).'),
}


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 4), round(c - h, 4), round(c + h, 4)]


def card_info(c, i):
    card = open(f'test-corpus-{c}/cards/{i}.md').read()
    return re.search(r'Rule: `([^`]+)`', card).group(1), re.search(r'github\.com/([\w.-]+/[\w.-]+)/tree', card).group(1)


def load_mech():
    lines = open(f'{D}/pyvibe-012-mecanismos.tsv', encoding='utf-8').read().splitlines()
    hdr = lines[0].split('\t')
    return {(r[0], r[1]): dict(zip(hdr, r)) for r in (l.split('\t') for l in lines[1:])}


def main():
    mech = load_mech()
    cases, pop = [], defaultdict(Counter)
    for c in POPULATION + APART + AUX:
        for v in json.load(open(f'test-corpus-{c}/audit-joaquin.json'))['verdicts']:
            rule, repo = card_info(c, v['id'])
            if c in POPULATION:
                pop[rule][repo] += 1
            orig, v1 = v['verdict'], V1.get((c, v['id']), v['verdict'])
            role = 'poblacion' if c in POPULATION else ('aparte' if c in APART else 'auxiliar')
            x = {'corpus': f'TC{c}', 'id': v['id'], 'rule': rule, 'repo': repo, 'papel': role,
                 'original': orig, 'v1': v1, 'overstated_original': v.get('overstated')}
            if rule == 'PYVIBE-012':
                m = mech[(c, v['id'])]
                v2 = 'U' if (c, v['id']) == ('4', 'P058') else 'TP'
                x.update(v2=v2, fp_condition=None, a=m['a_contrato'], b1=m['b1_perdida_no_retencion'],
                         b2=m['b2_excepcion_sin_supervision'], b3=m['b3_ausencia_recuperacion'], razon=m['razon'],
                         categoria='incumplimiento de recomendación documentada de uso seguro', gravedad='WARNING')
            elif (c, v['id']) in CUSTOM:
                v2, cond, why = CUSTOM[(c, v['id'])]
                x.update(v2=v2, fp_condition=cond, razon=why)
            else:
                continue
            cases.append(x)
    sel = selection(cases, pop)
    json.dump({'criterio': 'REVIEW-CRITERIA-v2.md (borrador, revisado el 2026-11-03)', 'asistida': True,
               'propone': 'Claude', 'confirma': 'Joaquín', 'poblacion': 'TC4', 'aparte': 'TC3', 'auxiliar': 'TC2',
               'umbral_seleccion': SELECTION, 'poblacion_por_regla': {r: dict(sorted(cnt.items())) for r, cnt in
                                                                       sorted(pop.items(), key=lambda kv: -sum(kv[1].values()))},
               'seleccion': sel, 'casos': cases}, open(f'{D}/propuesta-v2.json', 'w'), indent=1, ensure_ascii=False)
    render(cases, pop, sel)


def selection(cases, pop):
    p12 = [x for x in cases if x['rule'] == 'PYVIBE-012' and x['papel'] == 'poblacion']
    n = len(p12)
    def count(pred):
        k = sum(1 for x in p12 if pred(x))
        return {'k': k, 'n': n, 'wilson95': wilson(k, n)}
    out = {'PYVIBE-012': {
        'n': n, 'repos': len(pop['PYVIBE-012']),
        'a_contrato_TP': count(lambda x: x['v2'] == 'TP'),
        'b1_si': count(lambda x: x['b1'] == 'sí'),
        'b2_si': count(lambda x: x['b2'] == 'sí'),
        'b2_y_b3_si': count(lambda x: x['b2'] == 'sí' and x['b3'] == 'sí'),
        'U': count(lambda x: x['v2'] == 'U'),
    }}
    s = out['PYVIBE-012']
    s['pasa_umbral_CRITICAL'] = {k: (s['n'] >= SELECTION['n_min'] and s['repos'] >= SELECTION['repos_min']
                                     and s[k]['k'] / s['n'] >= SELECTION['tp_rate_min']) for k in ('b1_si', 'b2_si', 'b2_y_b3_si')}
    return out


def render(cases, pop, sel):
    s = sel['PYVIBE-012']
    fmt = lambda c: f"{c['k']}/{c['n']} = {c['wilson95'][0]:.2f} [{c['wilson95'][1]:.2f}–{c['wilson95'][2]:.2f}]"
    L = ['# Evaluación de desarrollo con REVIEW-CRITERIA v2: etiquetas y selección', '',
         '**Evaluación asistida de desarrollo.** Claude propone la etiqueta v2 de cada caso y su razón; Joaquín la confirma o corrige. No es una revisión ciega ni sustituye a ningún resultado publicado: TC1–TC4 conservan sus veredictos, métricas y conclusiones. Criterio: `../REVIEW-CRITERIA-v2.md`. Las cifras de este fichero salen de `propuesta-v2.json`, y `comprobar.py` verifica que coinciden.', '',
         '## Registro', '',
         '- **2026-11-03, primera propuesta:** 101 casos de TC2–TC4.',
         '- **2026-11-03, primeras correcciones de Joaquín:**',
         '  - TC2 J015, TC3 J001 y TC2 J001: FP por contexto.',
         '  - TC2 J052: U.',
         '  - TC3 P026: TP por contrato.',
         '  - PYVIBE-012: campos (a) y (b).',
         '  - Decisiones sobre las segundas opiniones de Codex (J056 FP, frontera FP/U, cadencias, `transactions` opción (a), J053 TP, Kafka, Celery, confirmación CRITICAL).',
         '- **2026-11-03, decisiones de Joaquín tras la segunda opinión de Codex sobre B** (`~/vibe-guard-evaluation-work/second-opinions/2026-11-03-criterio-v2-propuesta-b/`):',
         '  1. **Población de selección:** solo TC4 (55 casos de PYVIBE-012, 18 repos). TC3 queda aparte, porque su revisión dependió del desacuerdo A/B y de un muestreo. P058 cuenta como U (no-TP).',
         '  2. **Campos separados:** «categoría» y «gravedad» (WARNING/CRITICAL), sin ninguna escala de contrato.',
         '  3. **PYVIBE-012:** (b) se separa en tres mecanismos: b1 pérdida por no retención, b2 excepción sin supervisión, b3 ausencia de recuperación. No se da por demostrado ningún recuento causal.',
         '  4. **Una detección, una alerta.** Separar los mensajes no autoriza dos alertas basadas en la misma detección: `DISENO-PYVIBE-012.md` (propuesta, sin implementar).',
         '  5–7. **Redacción.** «Ninguna regla evaluada reúne hoy los requisitos para CRITICAL automático». WARNING no tiene umbral, pero publica su evidencia y sus limitaciones. Se conservan los U y las cuestiones abiertas.',
         '  8. **TC5:** borrador de pre-registro, `../tc5-borrador/PREREGISTRATION-BORRADOR.md`. No se ejecuta.',
         '  9. **Proyecto:** TC5 se aparca y se pasa a pilotos de auditoría (`~/vibe-guard`, `DECISIONS.md`).',
         '  - **Además:** P094 pasa a b2/b3 sí; «nadie lo nota» se sustituye por «sin observador ni recuperación en el código»; P087 se limita a las tareas de monitorización.',
         '- **2026-11-03, debate con Codex aprobado por Joaquín** (`~/vibe-guard-evaluation-work/second-opinions/2026-11-03-criterio-v2-debate/final.md`):',
         '  - **O1:** TC5 solo validaría R como WARNING.',
         '  - **O2:** se reescribe la fila de PYVIBE-013 en v2.',
         '  - **O3:** TC4 P046 pasa a b2 = sí y b3 = no; b2 sí en TC4 pasa de 12 a 13, y b2 y b3 sigue en 6.',
         '  - **O4:** las modalidades de cadencia se describen por separado en v2.',
         '  - **O5:** `comprobar.py` comprueba etiquetas y campos por caso, distribuciones por repo y árboles de TC1–TC4.',
         '  - **Puntos 2 y 3 de la consulta `…/2026-11-03-criterio-v2-cierre/`:** manejador global y análisis de propietarios y alias, en `DISENO-PYVIBE-012.md`.', '',
         '## 1. Población de selección (declarada)', '',
         'Todos los casos con tu veredicto en **TC4**, que tuvo revisión humana completa. **TC3 queda aparte:** sus 25 casos son los 5 desacuerdos A/B y una muestra de 20 acuerdos, así que su inclusión depende de las IAs y del muestreo. TC2 solo aporta ejemplos auxiliares. Las cifras de TC3 y TC2 no se suman a las de TC4.', '',
         '| Regla | n | Repos | Máx. por repo | ¿Candidata? (n ≥ 15 y ≥ 5 repos) |', '|---|---|---|---|---|']
    for r, cnt in sorted(pop.items(), key=lambda kv: (-sum(kv[1].values()), kv[0])):
        n, k = sum(cnt.values()), len(cnt)
        cand = 'no: WARNING como máximo (v2 §3)' if r == 'transactions' else ('**sí**' if n >= 15 and k >= 5 else 'no')
        L.append(f'| {r} | {n} | {k} | {max(cnt.values())} | {cand} |')
    L += ['', '**La única regla candidata es PYVIBE-012.** n por repo:', '', '| Repo | n |', '|---|---|']
    L += [f'| {repo} | {n} |' for repo, n in sorted(pop['PYVIBE-012'].items(), key=lambda kv: (-kv[1], kv[0]))]
    L += ['', '## 2. Selección (C): PYVIBE-012 en TC4', '',
          f"n = {s['n']}, {s['repos']} repos. Umbral CRITICAL: n ≥ {SELECTION['n_min']}, ≥ {SELECTION['repos_min']} repos y TP/n ≥ {SELECTION['tp_rate_min']:.2f}, con U como no-TP. Wilson 95 %.", '',
          '| Campo | Casos | ¿Pasa el umbral CRITICAL? |', '|---|---|---|',
          f"| (a) contrato: TP v2 (incumple la recomendación de retención) | {fmt(s['a_contrato_TP'])} | no aplica: es la categoría «incumplimiento de recomendación documentada de uso seguro», con gravedad WARNING |",
          f"| b1 pérdida por no retención | {fmt(s['b1_si'])} | {'sí' if s['pasa_umbral_CRITICAL']['b1_si'] else 'no'} |",
          f"| b2 excepción sin supervisión | {fmt(s['b2_si'])} | {'sí' if s['pasa_umbral_CRITICAL']['b2_si'] else 'no'} |",
          f"| b2 y b3 (excepción sin supervisión y sin recuperación) | {fmt(s['b2_y_b3_si'])} | {'sí' if s['pasa_umbral_CRITICAL']['b2_y_b3_si'] else 'no'} |",
          f"| U (P058) | {fmt(s['U'])} | cuenta como no-TP |", '',
          '- **Ninguna regla evaluada reúne hoy los requisitos para CRITICAL automático.** PYVIBE-012 queda en WARNING, con categoría «incumplimiento de recomendación documentada de uso seguro».',
          '- **Sin causalidad.** Los tres mecanismos se cuentan por separado, y ningún recuento atribuye un fallo a la falta de retención. b2 y b3 describen fallos del manejo de errores del cuerpo de la tarea; conservar la referencia no los evita por sí solo, si nadie supervisa la tarea.',
          '- **Cómo se lee b1, b2 y b3:**',
          '  - **sí:** el código muestra la condición;',
          '  - **no:** he leído el cuerpo de la corrutina, y lo que llama donde hacía falta, y no la muestra; eso no afirma que sea imposible;',
          '  - **U:** no se puede decidir;',
          '  - **—:** no aplica (b3 solo se evalúa si b2 es sí).',
          '- **Límite de b1:** solo se miró a qué espera la tarea en su propio cuerpo. Ningún caso espera un future que solo referencie la propia tarea.', '',
          '## 3. PYVIBE-012 caso por caso', '',
          'Categoría: «incumplimiento de recomendación documentada de uso seguro». Gravedad: WARNING. Veredicto v2: TP por contrato salvo P058 (U).', '']
    H = '| Corpus | ID | Repo | Original | v2 | (a) | b1 | b2 | b3 | Razón |\n|---|---|---|---|---|---|---|---|---|---|'
    row = lambda x: f"| {x['corpus']} | {x['id']} | {x['repo']} | {x['original']} | {x['v2']} | {x['a']} | {x['b1']} | **{x['b2']}** | **{x['b3']}** | {x['razon']} |"
    p12 = [x for x in cases if x['rule'] == 'PYVIBE-012']
    order = lambda x: ({'sí': 0, 'U': 1}.get(x['b2'], 2), {'sí': 0, 'no': 1}.get(x['b3'], 2), x['id'])
    L += ['### 3.1 Población (TC4), primero los que tienen b2 = sí o U', '', H] + [row(x) for x in sorted((x for x in p12 if x['papel'] == 'poblacion'), key=order)]
    L += ['', '### 3.2 Aparte (TC3) y auxiliares (TC2), fuera de la selección', '', H] + [row(x) for x in p12 if x['papel'] != 'poblacion']
    other = [x for x in cases if x['rule'] != 'PYVIBE-012']
    L += ['', '## 4. Otros casos corregidos el 2026-11-03 (reglas no candidatas)', '',
          'Son ejemplos y casos que tocan tus decisiones; no entran en la selección.', '',
          '| Corpus | ID | Regla | Repo | Original | v1 | v2 | Razón |', '|---|---|---|---|---|---|---|---|']
    L += [f"| {x['corpus']} | {x['id']} | {x['rule']} | {x['repo']} | {x['original']} | {x['v1']} | **{x['v2']}{' (' + x['fp_condition'] + ')' if x['fp_condition'] else ''}** | {x['razon']} |" for x in other]
    L += ['', 'Los demás casos de `blocking` y PYVIBE-009 de la primera propuesta no se han revisado con las decisiones del 2026-11-03, porque esas reglas no son candidatas.', '',
          '## 5. Cuestiones abiertas (se conservan)', '',
          '- **U de la población:** TC4 P058 (copia vendorizada en `.tmp-ci-venv`). Cerrar v2 no lo resuelve.',
          '- **U auxiliares y de ejemplos:** TC2 J052 (executor de starters externos) y TC4 J032/J033 (API pública de un motor integrable).',
          '- **Límite de b1:** no se ha seguido el árbol completo de awaits de cada tarea.',
          '- **Caso límite:** P066 (b2 depende de un fallo de E/S de disco).',
          '- **TC3:** sus casos de PYVIBE-012 se conservan aparte, sin sumarlos a ninguna tasa.',
          '- **`blocking` y PYVIBE-009:** sin revisar con las reglas nuevas de cadencia y de frontera FP/U.',
          '- **Analizadores:** sin cambios. El diseño de la separación de PYVIBE-012 está en `DISENO-PYVIBE-012.md` y no está implementado.', '',
          '## Ficheros', '',
          '- `propuesta.py`: genera `propuesta-v2.json` y este fichero.',
          '- `pyvibe-012-mecanismos.tsv`: (a), b1, b2 y b3 de los 65 casos de PYVIBE-012, con su razón y sus `file:line`.',
          '- `comprobar.py`: recalcula las cifras desde el TSV y las fichas, y comprueba que el JSON, este fichero, `REVIEW-CRITERIA-v2.md` y el borrador de TC5 dicen lo mismo.',
          '- `DISENO-PYVIBE-012.md`: propuesta de separar retención y supervisión, sin implementar.']
    open(f'{D}/PROPUESTA-v2.md', 'w').write('\n'.join(L) + '\n')
    print({k: (v['k'] if isinstance(v, dict) and 'k' in v else v) for k, v in s.items()})


main()
