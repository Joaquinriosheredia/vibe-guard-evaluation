"""Evaluación de desarrollo con REVIEW-CRITERIA v2 (asistida): etiqueta v2 PROPUESTA por Claude para cada caso
de TC2-TC4 de las reglas que pueden ser candidatas, con su razón. Joaquín confirma o corrige.

uso: python3 criterio-v2-desarrollo/propuesta.py  (desde la raíz del repo) -> propuesta-v2.json
Reglas: PYVIBE-012, blocking, PYVIBE-009 (n >= 15 y >= 5 repos en TC2-TC4). transactions queda fuera:
v2 §3 la limita a WARNING, así que no puede ser candidata.
"""
import json
import re

RULES = ('PYVIBE-012', 'blocking', 'PYVIBE-009')
V1 = {('2', 'J001'): 'TP', ('3', 'P026'): 'TP'}  # REVIEW-CRITERIA.md v1 §6

# Casos con razón propia: (etiqueta v2, condición FP o None, razón, dudoso)
CUSTOM = {
    ('2', 'J015'): ('FP', 'context', '`Counter.java:24–27`: `Thread.sleep(100)` cada 1 s en el job `increment()` de un fixture; Quartz de Quarkus tiene 25 hilos por defecto y el módulo no fija `thread-count`; nada espera detrás y la pausa es el trabajo deliberado del job (v2 §1, §3 `blocking`).', False),
    ('2', 'J001'): ('FP', 'context', '`SampleBackground.java:38–41`: sleep aleatorio < 1 s que simula latencia en el único `@Async` del módulo, sobre el executor por defecto; ningún `@Scheduled` ni otro `@Async` en `study-spring-boot-zipkin`; nada espera detrás (v2 §1). Además es repositorio de estudio (exclusión c2).', False),
    ('3', 'J001'): ('FP', 'context', '`BookTestDataQueryRunner.java:22–24`: `Thread.sleep(10000)` en el único `@Scheduled` de la app (scheduler por defecto, `FeatureServiceApplication.java:10`); ningún otro job espera. Lo único incumplido es la propia cadencia `*/2` del job, que el sleep deliberado de un runner de datos de prueba hace imposible por diseño.', True),
    ('2', 'J052'): ('TP', None, '`Process4CompleteUtilServiceImpl.java:299`: `Thread.sleep(3000)` por proceso completado en `@Async saveToEs` de producción; el módulo no define executor propio, así que comparte el executor de `@Async` de la aplicación: con completaciones concurrentes, otros `@Async` esperan.', True),
    ('3', 'J003'): ('TP', None, '`SchedulerTestConfig.java:41,49–57,69`: scheduler de 3 hilos; `reEntrantLockTask` duerme 120 s con el lock tomado y `synchronizedBlockTask` también bloquea; hay 7 `@Scheduled` en el módulo (`cronTask` cada 5 s, `alive` cada 30 s…), que pueden quedarse sin hilo. Playground: alcanzable en su propia app.', False),
    ('3', 'J010'): ('TP', None, '`TokenRefreshServiceImpl.java:486–509`: 3–8 s de sleep por cuenta en un `@Scheduled`; scheduler de 2 hilos (`config/AsyncConfig.java:135–137`) compartido con 14 `@Scheduled`: los demás jobs pierden su cadencia.', False),
    ('4', 'J035'): ('TP', None, '`ItemDetailSyncServiceImpl.java:121,127–156`: `self.executeSync` pasa por el proxy `@Async` y duerme hasta 500 ms por artículo en `taskExecutor`, el executor que comparten los 25 `@Async` de la app: con lotes grandes, los demás esperan.', False),
    ('4', 'J036'): ('TP', None, '`TokenRefreshServiceImpl.java:496–519`: 3–8 s por cuenta en un `@Scheduled`; scheduler de `max(4, app.scheduler.pool-size)` hilos (`AsyncConfig.java:88–91`) con 13 `@Scheduled`: con varias cuentas, otros jobs esperan.', False),
    ('4', 'J058'): ('TP', None, '`ModelAutoChatService.java:59–94`: `Future.get()` sin timeout sobre una llamada LLM en un `@Scheduled`: el hilo del scheduler puede quedar colgado sin cota (4 `@Scheduled` en `chat-core`).', False),
    ('4', 'J009'): ('TP', None, '`FilingSyncJob.java:53–94`: sleep por empresa (limitación de frecuencia deliberada) en un `@Scheduled`; 11 `@Scheduled` y ninguna configuración del pool del scheduler (1 hilo por defecto): los demás jobs esperan todo el lote.', False),
    ('4', 'J012'): ('TP', None, '`CompanyEnrichmentService.java:88–97`, llamada desde `InsiderController.java:357`: 1 s de sleep por empresa, más la espera `.get()`, dentro de `CompletableFuture.runAsync` sin executor, es decir, en el ForkJoinPool común, que comparten otros 15 `runAsync`/`supplyAsync` del repositorio. El sleep no está en el hilo de `@Async` que dice el mensaje (Overstated).', False),
    ('4', 'J052'): ('TP', None, '`SC2MetaService.java:98–108`: `.block()` espera un flujo completo en un `@Scheduled`; `spring.task.scheduling.pool.size=2` (`application.properties:6`) para 18 `@Scheduled`: con dos esperas así, el resto queda sin hilo.', False),
    ('4', 'J051'): ('TP', None, '`Cron.java:218–221`: `.block()` sobre `runIfAvailable()` en un `@Scheduled`; mismo scheduler de 2 hilos para 18 `@Scheduled` (`application.properties:6`).', False),
    ('2', 'J056'): ('FP', 'context', '`AzDevOpsPollingService.java:101–110`: espera de diseño con hilos virtuales (`application.properties:4`, Spring Boot 4.1.1): cada ejecución tiene su propio hilo y nada espera detrás.', False),
    ('4', 'J056'): ('FP', 'reachability', '`AsyncTask.java:22–26`: el único llamador es un test (`ApplicationTests.java:31`).', False),
    ('4', 'J057'): ('FP', 'reachability', '`AsyncTask.java:33–38`: el único llamador es un test (`ApplicationTests.java:33`).', False),
    ('4', 'J032'): ('U', None, 'La cadena interna está muerta: `NotifyServiceImpl.notifyCurrent` (`:168`) no tiene llamadores, y `map` es `null` en `:182`, así que `:184` lanza antes de `:202`. Pero `MessageUtils.sendMessageBatch(List)` (`MessageUtils.java:31`) es API pública de un motor que se integra en otras aplicaciones: no se puede decidir sin sus llamadores externos. La duda sobre el retorno `Boolean` ya no cambia la etiqueta.', False),
    ('4', 'J033'): ('U', None, 'La sobrecarga de 2 argumentos `MessageUtils.sendMessageBatch(List, MessageSendTypeEnum)` (`MessageUtils.java:44–46`) no tiene llamadores en el repositorio; el único que hay (`NotifyServiceImpl.java:202`) usa la de 1 argumento. Es API pública de un motor integrable: no se puede decidir.', False),
    ('2', 'P083'): ('FP', 'context', '`start_server.py:49`: `open()` solo en el arranque, antes de servir (`:154–155`); nada más corre en el loop.', False),
    ('2', 'P099'): ('FP', 'reachability', '`mcps/custom/tts-mcp/live_smoke.py:54`: script manual de humo, no es operación normal.', False),
    ('4', 'P058'): ('U', None, '`.tmp-ci-venv/Lib/site-packages/realtime/_async/channel.py:247`: dependencia dentro de un virtualenv de CI comiteado; no se demuestra que la aplicación use esa copia.', False),
    ('3', 'P026'): ('TP', None, '`kline.py:1009`: `create_task(task())` sin conservar la referencia en una ruta de producción; que el cuerpo capture `Exception` solo afecta a la parte de excepciones del mensaje (Overstated). Igual que en v1 §6 y que P027/P028.', False),
}


def cite(reason):
    r = (reason or '').strip()
    return r.split(' — ')[0] if ' — ' in r else r[:160]


def main():
    out = []
    for c in '234':
        for v in json.load(open(f'test-corpus-{c}/audit-joaquin.json'))['verdicts']:
            card = open(f'test-corpus-{c}/cards/{v["id"]}.md').read()
            rule = re.search(r'Rule: `([^`]+)`', card).group(1)
            if rule not in RULES:
                continue
            repo = re.search(r'github\.com/([\w.-]+/[\w.-]+)/tree', card).group(1)
            orig, v1 = v['verdict'], V1.get((c, v['id']), v['verdict'])
            if (c, v['id']) in CUSTOM:
                v2, cond, why, doubt = CUSTOM[(c, v['id'])]
            elif v1 == 'TP' and rule == 'PYVIBE-012':
                v2, cond, doubt = 'TP', None, False
                why = (f'Ruta de Joaquín: {cite(v["reason"])}. Ninguna referencia a la tarea se conserva: se incumple el contrato '
                       'de `asyncio.create_task` (v2 §3, PYVIBE-012).')
            elif v1 == 'TP' and rule == 'PYVIBE-009':
                v2, cond, doubt = 'TP', None, False
                why = (f'Ruta de Joaquín: {cite(v["reason"])}. E/S de fichero síncrona en el loop, en una ruta que se ejecuta '
                       'mientras el loop atiende otro trabajo (v2 §3).')
            else:
                raise SystemExit(f'sin propuesta: TC{c} {v["id"]} {rule} {v1}')
            out.append({'corpus': f'TC{c}', 'id': v['id'], 'rule': rule, 'repo': repo, 'original': orig, 'v1': v1,
                        'v2_propuesta': v2, 'fp_condition': cond, 'overstated_original': v.get('overstated'),
                        'dudoso': doubt, 'razon': why})
    json.dump({'criterio': 'REVIEW-CRITERIA-v2.md (borrador 2026-11-03)', 'asistida': True, 'propone': 'Claude',
               'confirma': 'Joaquín (pendiente)', 'casos': out}, open('criterio-v2-desarrollo/propuesta-v2.json', 'w'),
              indent=1, ensure_ascii=False)
    print(len(out), 'casos;', sum(x['v2_propuesta'] != x['original'] for x in out), 'cambian respecto a la original;',
          sum(x['v2_propuesta'] != x['v1'] for x in out), 'respecto a v1;', sum(x['dudoso'] for x in out), 'dudosos')


main()
