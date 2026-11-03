# Evaluación de desarrollo con REVIEW-CRITERIA v2: etiquetas propuestas (pendiente de confirmación)

**Evaluación asistida de desarrollo.** Claude propone la etiqueta v2 de cada caso y su razón; Joaquín la confirma o corrige. No es una revisión ciega ni sustituye a ningún resultado publicado: TC2–TC4 conservan sus veredictos, métricas y conclusiones. Criterio: `../REVIEW-CRITERIA-v2.md` (borrador del 2026-11-03).

**Alcance.** Las reglas que pueden ser candidatas a CRITICAL: las que tienen n ≥ 15 y ≥ 5 repos en TC2–TC4. Son PYVIBE-012 (65 casos), `blocking` (18) y PYVIBE-009 (18), en total 101 casos. `transactions` (44 casos) queda fuera porque v2 §3 la limita a WARNING; sus cambios van en E. Las demás reglas no llegan a n ≥ 15 y siguen en WARNING.

**Fuentes de cada propuesta:**

- tu veredicto y tu razón (`audit-joaquin.json`);
- la ficha;
- el código en el commit fijado, que he abierto en los casos que cambian o son dudosos;
- las razones de Claude y de Codex de las calibraciones, solo como pista; no deciden.

Esta propuesta no calcula tasas por regla: la selección (C) va después de tu confirmación.

## 1. Cambian respecto a tu etiqueta original (3)

| Corpus | ID | Repo | Original | v1 | v2 propuesta | Razón |
|---|---|---|---|---|---|---|
| TC2 | J015 | quarkusio/quarkus | TP | TP | **FP (context)** | `Counter.java:24–27`: `Thread.sleep(100)` cada 1 s en el job `increment()` de un fixture; Quartz de Quarkus tiene 25 hilos por defecto y el módulo no fija `thread-count`; nada espera detrás y la pausa es el trabajo deliberado del job (v2 §1, §3 `blocking`). |
| TC3 | J001 | axelixlabs/axelix | TP | TP | **FP (context)** ⚠ | `BookTestDataQueryRunner.java:22–24`: `Thread.sleep(10000)` en el único `@Scheduled` de la app (scheduler por defecto, `FeatureServiceApplication.java:10`); ningún otro job espera. Lo único incumplido es la propia cadencia `*/2` del job, que el sleep deliberado de un runner de datos de prueba hace imposible por diseño. |
| TC3 | P026 | hzy1522/tickflow-stock-panel | FP | TP | **TP** | `kline.py:1009`: `create_task(task())` sin conservar la referencia en una ruta de producción; que el cuerpo capture `Exception` solo afecta a la parte de excepciones del mensaje (Overstated). Igual que en v1 §6 y que P027/P028. |

- **TC2 J015 y TC3 J001** son pausas deliberadas que nada más espera. En v1 eran TP (§2.3: lo deliberado no hacía FP). En v2 no hay ninguna propiedad que se incumpla en una condición plausible (v2 §1). TC3 J001 está marcado ⚠: la cadencia `*/2` que declara el propio job no se cumple, y si consideras que esa cadencia es la propiedad explícita, sería TP.
- **TC3 P026** es el mismo cambio que ya hizo v1 §6.

## 2. No cambian respecto a la original, pero sí respecto a v1 (1)

| Corpus | ID | Repo | Original | v1 | v2 propuesta | Razón |
|---|---|---|---|---|---|---|
| TC2 | J001 | bage2014/study | FP | TP | **FP (context)** | `SampleBackground.java:38–41`: sleep aleatorio < 1 s que simula latencia en el único `@Async` del módulo, sobre el executor por defecto; ningún `@Scheduled` ni otro `@Async` en `study-spring-boot-zipkin`; nada espera detrás (v2 §1). Además es repositorio de estudio (exclusión c2). |

TC2 J001 era FP en tu etiqueta original y TP en v1 (§6, por la alcanzabilidad dentro de su propia app). En v2 vuelve a FP, pero por contexto: la ruta existe y nada espera detrás del sleep.

## 3. Se mantienen, pero son dudosos (1)

| Corpus | ID | Repo | Original | v1 | v2 propuesta | Razón |
|---|---|---|---|---|---|---|
| TC2 | J052 | risesoft-y9/WorkFlow-Engine | TP | TP | **TP** ⚠ | `Process4CompleteUtilServiceImpl.java:299`: `Thread.sleep(3000)` por proceso completado en `@Async saveToEs` de producción; el módulo no define executor propio, así que comparte el executor de `@Async` de la aplicación: con completaciones concurrentes, otros `@Async` esperan. |

## 4. Pregunta de interpretación que afecta a 64 casos (PYVIBE-012)

La propuesta lee la propiedad de PYVIBE-012 como **el contrato documentado** de `asyncio.create_task`: hay que guardar una referencia a la tarea, porque el loop solo guarda una referencia débil y una tarea no referenciada «puede ser recolectada en cualquier momento». Con esa lectura, no conservar la referencia en una ruta alcanzable es TP, y los 64 TP siguen siendo TP.

Hay una lectura más estricta: exigir que el repositorio muestre una condición en la que la recolección sea plausible en la práctica. En CPython, una tarea que espera un temporizador o E/S del loop queda referenciada a través de él; la recolección solo es real si la tarea espera un future que nadie más referencia. Con esa lectura habría que revisar caso por caso qué espera cada tarea y si sus excepciones se pierden. Muchos de tus TP con Overstated (el cuerpo captura sus excepciones) podrían pasar a FP por contexto. Si eliges esta lectura, hago esa revisión caso por caso antes de C.

## 5. Propuesta completa por regla

### PYVIBE-012 (65 casos)

| Corpus | ID | Repo | Original | v1 | v2 propuesta | Razón |
|---|---|---|---|---|---|---|
| TC2 | P145 | OtoDock/oto-dock | TP | TP | **TP** | Ruta de Joaquín: satellite/transport/ws_client.py:968. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC2 | P149 | OtoDock/oto-dock | TP | TP | **TP** | Ruta de Joaquín: `satellite/transport/ws_client.py:981`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC2 | P161 | OtoDock/oto-dock | TP | TP | **TP** | Ruta de Joaquín: `satellite/transport/ws_client.py:1045` descarta la referencia devuelta por `asyncio.create_task(self.sm.file_stat(msg, self))`. El registro `self.sm._pulls` y . Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC2 | P116 | OtoDock/oto-dock | TP | TP | **TP** | Ruta de Joaquín: `proxy/core/layers/codex/app_server_client.py:172–174` descarta la referencia devuelta por `asyncio.create_task()` para `_drain_stderr()`. La función se define . Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC2 | P153 | OtoDock/oto-dock | TP | TP | **TP** | Ruta de Joaquín: `satellite/transport/ws_client.py:1000–1002` crea una tarea para `self.sm.check_session_resumable(msg, self)` sin guardar su referencia ni adjuntar un callback . Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC3 | P026 | hzy1522/tickflow-stock-panel | FP | TP | **TP** | `kline.py:1009`: `create_task(task())` sin conservar la referencia en una ruta de producción; que el cuerpo capture `Exception` solo afecta a la parte de excepciones del mensaje (Overstated). Igual que en v1 §6 y que P027/P028. |
| TC3 | P020 | Deen-Bridge/dnb-ai | TP | TP | **TP** | Ruta de Joaquín: `main.py:1988`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC3 | P028 | hzy1522/tickflow-stock-panel | TP | TP | **TP** | Ruta de Joaquín: `backend/app/api/kline.py:1251`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC3 | P027 | hzy1522/tickflow-stock-panel | TP | TP | **TP** | Ruta de Joaquín: `backend/app/api/kline.py:1164`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC3 | P005 | apowerb/apowerb | TP | TP | **TP** | Ruta de Joaquín: `src/apowerb/main.py:680`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P102 | yujian0815/fnmedia-ext | TP | TP | **TP** | Ruta de Joaquín: `proxy/app.py:3006`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P057 | phucnguyentvp1/frameweaver | TP | TP | **TP** | Ruta de Joaquín: `agent/worker/processor.py:151`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P065 | runvnc/mindroot | TP | TP | **TP** | Ruta de Joaquín: `src/mindroot/coreplugins/admin/server_router.py:66`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P032 | dameng2026/xianyu-pilot | TP | TP | **TP** | Ruta de Joaquín: `rate_service.py:1457`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P054 | phucnguyentvp1/frameweaver | TP | TP | **TP** | Ruta de Joaquín: agent/services/flow_client.py:249 descarta la tarea creada con asyncio.create_task(self._sync_tier()); agent/main.py:62 llama a handle_message desde la ruta pri. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P008 | AndrewCTF/velocity | TP | TP | **TP** | Ruta de Joaquín: apps/api/app/mcp_server.py:321 descarta asyncio.create_task(_prewarm()); _ensure_backend se invoca desde las rutas de herramientas en las líneas 330, 362 y 382.. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P051 | ljxpython/ai-agent-platform | TP | TP | **TP** | Ruta de Joaquín: execution.py:100 descarta asyncio.create_task(_cleanup(...)); execution.py:102 registra late_cleanup como callback de creation.add_done_callback.. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P099 | yujian0815/fnmedia-ext | TP | TP | **TP** | Ruta de Joaquín: proxy/app.py:1366–1391 define la ruta POST /v/api/v1/item/list y descarta asyncio.create_task(catalog.refresh_routes(...)) en la línea 1390; hay otras creacione. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P090 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: `app/startup.py:102–103,396`; `app/main.py:35`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P104 | yujian0815/fnmedia-ext | TP | TP | **TP** | Ruta de Joaquín: `proxy/catalog.py:457,492–493,424,631,649`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P097 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: `app/startup.py:102–103,403`; `app/main.py:35`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P085 | TNT-Likely/BeeCount-Cloud | TP | TP | **TP** | Ruta de Joaquín: `src/mcp/server.py:117–144,193–206,491–493`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P041 | foodpm/timecut | TP | TP | **TP** | Ruta de Joaquín: `app/web/routes/diary.py:72–80`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P014 | asfaraguest/tatap | TP | TP | **TP** | Ruta de Joaquín: `android/app/src/main/python/backend/main.py:1635–1667,1762,1934`. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P081 | SpillwaveSolutions/agent-brain | TP | TP | **TP** | Ruta de Joaquín: indexing_service.py:208–210. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P006 | AndrewCTF/velocity | TP | TP | **TP** | Ruta de Joaquín: main.py:497. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P064 | runvnc/mindroot | TP | TP | **TP** | Ruta de Joaquín: server_router.py:40–54. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P092 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: startup.py:398. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P056 | phucnguyentvp1/frameweaver | TP | TP | **TP** | Ruta de Joaquín: flow_client.py:268–270; agent/main.py:62. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P055 | phucnguyentvp1/frameweaver | TP | TP | **TP** | Ruta de Joaquín: flow_client.py:252–266; agent/main.py:62. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P049 | liyupi/yu-ai-learn | TP | TP | **TP** | Ruta de Joaquín: knowledge_service.py:67; routes/knowledge.py:18. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P005 | AndrewCTF/velocity | TP | TP | **TP** | Ruta de Joaquín: main.py:482–489. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P091 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: startup.py:397. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P058 | riteshbonthalakoti/HELPDESK.AI | U | U | **U** | `.tmp-ci-venv/Lib/site-packages/realtime/_async/channel.py:247`: dependencia dentro de un virtualenv de CI comiteado; no se demuestra que la aplicación use esa copia. |
| TC4 | P096 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: app/startup.py:402. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P101 | yujian0815/fnmedia-ext | TP | TP | **TP** | Ruta de Joaquín: proxy/app.py:1463. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P077 | runvnc/mindroot | TP | TP | **TP** | Ruta de Joaquín: scheduler/mod.py:594,612. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P030 | crane-in-clear-sky/WorkWit-AI-Agent | TP | TP | **TP** | Ruta de Joaquín: workwit/backend/app.py:32–34. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P012 | antiv/mate | TP | TP | **TP** | Ruta de Joaquín: browser_tools.py:216; server/browser_routes.py:53. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P009 | AndrewCTF/velocity | TP | TP | **TP** | Ruta de Joaquín: routes/recon.py:601–652. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P095 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: app/startup.py:401. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P044 | HyxiaoGe/fusion | TP | TP | **TP** | Ruta de Joaquín: file_service.py:485; api/files.py:103. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P053 | metalogico/issued | TP | TP | **TP** | Ruta de Joaquín: server/opds/init.py:66,84. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P034 | dameng2026/xianyu-pilot | TP | TP | **TP** | Ruta de Joaquín: xianyu_order_sync.py:382–385; routes/order.py:246. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P016 | asfaraguest/tatap | TP | TP | **TP** | Ruta de Joaquín: backend/main.py:1667,1762,1934. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P050 | liyupi/yu-ai-learn | TP | TP | **TP** | Ruta de Joaquín: quiz_service.py:155; routes/quiz.py:34. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P029 | crane-in-clear-sky/WorkWit-AI-Agent | TP | TP | **TP** | Ruta de Joaquín: agent_endpoints.py:994–1004. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P007 | AndrewCTF/velocity | TP | TP | **TP** | Ruta de Joaquín: main.py:500–504,709. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P093 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: app/startup.py:399; app/main.py:35. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P087 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: app/startup.py:393; app/main.py:35. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P004 | AndrewCTF/velocity | TP | TP | **TP** | Ruta de Joaquín: localllm/manager.py:628; routes/ai_models.py:106. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P043 | HyxiaoGe/fusion | TP | TP | **TP** | Ruta de Joaquín: file_service.py:267–269; api/files.py:62. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P031 | crane-in-clear-sky/WorkWit-AI-Agent | TP | TP | **TP** | Ruta de Joaquín: automation_runner.py:153; app.py:34. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P042 | foodpm/timecut | TP | TP | **TP** | Ruta de Joaquín: highlights.py:217–228. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P098 | yujian0815/fnmedia-ext | TP | TP | **TP** | Ruta de Joaquín: proxy/app.py:867–868,1499. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P066 | runvnc/mindroot | TP | TP | **TP** | Ruta de Joaquín: agent.py:929–936; persona/mod.py:72. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P046 | jacebrowning/memegen | TP | TP | **TP** | Ruta de Joaquín: helpers.py:237; views/images.py:299,470. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P103 | yujian0815/fnmedia-ext | TP | TP | **TP** | Ruta de Joaquín: catalog.py:335–336; proxy/app.py:1427. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P040 | foodpm/timecut | TP | TP | **TP** | Ruta de Joaquín: recorder/manager.py:190; app/main.py:60,150. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P089 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: app/startup.py:395; app/main.py:35. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P094 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: app/startup.py:400; app/main.py:35. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P086 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: app/startup.py:215,393. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P100 | yujian0815/fnmedia-ext | TP | TP | **TP** | Ruta de Joaquín: proxy/app.py:1366–1367,1427. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P088 | xianer235/115-media-hub | TP | TP | **TP** | Ruta de Joaquín: app/startup.py:394; app/main.py:35. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |
| TC4 | P033 | dameng2026/xianyu-pilot | TP | TP | **TP** | Ruta de Joaquín: ws_client.py:876–882,654. Ninguna referencia a la tarea se conserva: se incumple el contrato de `asyncio.create_task` (v2 §3, PYVIBE-012). |

### blocking (18 casos)

| Corpus | ID | Repo | Original | v1 | v2 propuesta | Razón |
|---|---|---|---|---|---|---|
| TC2 | J015 | quarkusio/quarkus | TP | TP | **FP (context)** | `Counter.java:24–27`: `Thread.sleep(100)` cada 1 s en el job `increment()` de un fixture; Quartz de Quarkus tiene 25 hilos por defecto y el módulo no fija `thread-count`; nada espera detrás y la pausa es el trabajo deliberado del job (v2 §1, §3 `blocking`). |
| TC2 | J056 | terrakube-io/terrakube | FP | FP | **FP (context)** | `AzDevOpsPollingService.java:101–110`: espera de diseño con hilos virtuales (`application.properties:4`, Spring Boot 4.1.1): cada ejecución tiene su propio hilo y nada espera detrás. |
| TC2 | J001 | bage2014/study | FP | TP | **FP (context)** | `SampleBackground.java:38–41`: sleep aleatorio < 1 s que simula latencia en el único `@Async` del módulo, sobre el executor por defecto; ningún `@Scheduled` ni otro `@Async` en `study-spring-boot-zipkin`; nada espera detrás (v2 §1). Además es repositorio de estudio (exclusión c2). |
| TC2 | J052 | risesoft-y9/WorkFlow-Engine | TP | TP | **TP** ⚠ | `Process4CompleteUtilServiceImpl.java:299`: `Thread.sleep(3000)` por proceso completado en `@Async saveToEs` de producción; el módulo no define executor propio, así que comparte el executor de `@Async` de la aplicación: con completaciones concurrentes, otros `@Async` esperan. |
| TC3 | J003 | axelixlabs/axelix | TP | TP | **TP** | `SchedulerTestConfig.java:41,49–57,69`: scheduler de 3 hilos; `reEntrantLockTask` duerme 120 s con el lock tomado y `synchronizedBlockTask` también bloquea; hay 7 `@Scheduled` en el módulo (`cronTask` cada 5 s, `alive` cada 30 s…), que pueden quedarse sin hilo. Playground: alcanzable en su propia app. |
| TC3 | J001 | axelixlabs/axelix | TP | TP | **FP (context)** ⚠ | `BookTestDataQueryRunner.java:22–24`: `Thread.sleep(10000)` en el único `@Scheduled` de la app (scheduler por defecto, `FeatureServiceApplication.java:10`); ningún otro job espera. Lo único incumplido es la propia cadencia `*/2` del job, que el sleep deliberado de un runner de datos de prueba hace imposible por diseño. |
| TC3 | J010 | Evvvvvvvan/XianYuSmart | TP | TP | **TP** | `TokenRefreshServiceImpl.java:486–509`: 3–8 s de sleep por cuenta en un `@Scheduled`; scheduler de 2 hilos (`config/AsyncConfig.java:135–137`) compartido con 14 `@Scheduled`: los demás jobs pierden su cadencia. |
| TC4 | J057 | wujun728/jun_java_plugin | FP | FP | **FP (reachability)** | `AsyncTask.java:33–38`: el único llamador es un test (`ApplicationTests.java:33`). |
| TC4 | J056 | wujun728/jun_java_plugin | FP | FP | **FP (reachability)** | `AsyncTask.java:22–26`: el único llamador es un test (`ApplicationTests.java:31`). |
| TC4 | J033 | mrtylerzhou/AntFlow-activiti | U | U | **U** | La sobrecarga de 2 argumentos `MessageUtils.sendMessageBatch(List, MessageSendTypeEnum)` (`MessageUtils.java:44–46`) no tiene llamadores en el repositorio; el único que hay (`NotifyServiceImpl.java:202`) usa la de 1 argumento. Es API pública de un motor integrable: no se puede decidir. |
| TC4 | J032 | mrtylerzhou/AntFlow-activiti | U | U | **U** | La cadena interna está muerta: `NotifyServiceImpl.notifyCurrent` (`:168`) no tiene llamadores, y `map` es `null` en `:182`, así que `:184` lanza antes de `:202`. Pero `MessageUtils.sendMessageBatch(List)` (`MessageUtils.java:31`) es API pública de un motor que se integra en otras aplicaciones: no se puede decidir sin sus llamadores externos. La duda sobre el retorno `Boolean` ya no cambia la etiqueta. |
| TC4 | J035 | najiuwanan/xianyu-Plus | TP | TP | **TP** | `ItemDetailSyncServiceImpl.java:121,127–156`: `self.executeSync` pasa por el proxy `@Async` y duerme hasta 500 ms por artículo en `taskExecutor`, el executor que comparten los 25 `@Async` de la app: con lotes grandes, los demás esperan. |
| TC4 | J036 | najiuwanan/xianyu-Plus | TP | TP | **TP** | `TokenRefreshServiceImpl.java:496–519`: 3–8 s por cuenta en un `@Scheduled`; scheduler de `max(4, app.scheduler.pool-size)` hilos (`AsyncConfig.java:88–91`) con 13 `@Scheduled`: con varias cuentas, otros jobs esperan. |
| TC4 | J058 | ysy0915/chat-system | TP | TP | **TP** | `ModelAutoChatService.java:59–94`: `Future.get()` sin timeout sobre una llamada LLM en un `@Scheduled`: el hilo del scheduler puede quedar colgado sin cota (4 `@Scheduled` en `chat-core`). |
| TC4 | J009 | danielsobrado/edgar4j | TP | TP | **TP** | `FilingSyncJob.java:53–94`: sleep por empresa (limitación de frecuencia deliberada) en un `@Scheduled`; 11 `@Scheduled` y ninguna configuración del pool del scheduler (1 hilo por defecto): los demás jobs esperan todo el lote. |
| TC4 | J052 | sc2-pulse/sc2-pulse | TP | TP | **TP** | `SC2MetaService.java:98–108`: `.block()` espera un flujo completo en un `@Scheduled`; `spring.task.scheduling.pool.size=2` (`application.properties:6`) para 18 `@Scheduled`: con dos esperas así, el resto queda sin hilo. |
| TC4 | J012 | danielsobrado/edgar4j | TP | TP | **TP** | `CompanyEnrichmentService.java:88–97`, llamada desde `InsiderController.java:357`: 1 s de sleep por empresa, más la espera `.get()`, dentro de `CompletableFuture.runAsync` sin executor, es decir, en el ForkJoinPool común, que comparten otros 15 `runAsync`/`supplyAsync` del repositorio. El sleep no está en el hilo de `@Async` que dice el mensaje (Overstated). |
| TC4 | J051 | sc2-pulse/sc2-pulse | TP | TP | **TP** | `Cron.java:218–221`: `.block()` sobre `runIfAvailable()` en un `@Scheduled`; mismo scheduler de 2 hilos para 18 `@Scheduled` (`application.properties:6`). |

### PYVIBE-009 (18 casos)

| Corpus | ID | Repo | Original | v1 | v2 propuesta | Razón |
|---|---|---|---|---|---|---|
| TC2 | P083 | not-sekiun/Consortium | FP | FP | **FP (context)** | `start_server.py:49`: `open()` solo en el arranque, antes de servir (`:154–155`); nada más corre en el loop. |
| TC2 | P099 | OtoDock/oto-dock | FP | FP | **FP (reachability)** | `mcps/custom/tts-mcp/live_smoke.py:54`: script manual de humo, no es operación normal. |
| TC2 | P098 | OtoDock/oto-dock | TP | TP | **TP** | Ruta de Joaquín: mcps/custom/transcribe-mcp/server.py:696 (también :657). E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC2 | P073 | MoMoM101/RAG-ReActAgent | TP | TP | **TP** | Ruta de Joaquín: `backend/storage/files.py:208–212` ejecuta `open()` y lecturas síncronas dentro del generador asíncrono `open_read()`. `backend/storage/__init__.py:76` consume . E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC2 | P090 | OtoDock/oto-dock | TP | TP | **TP** | Ruta de Joaquín: `mcps/custom/image-gen-mcp/server.py:573–576` abre `mask_path` con `open()` síncrono dentro de `_edit_openai()`, una corrutina que realiza la petición HTTP medi. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC2 | P077 | not-sekiun/Consortium | TP | TP | **TP** | Ruta de Joaquín: `consortium/client/commands/core_commands/rc.py:50–51` hace E/S síncrona con `open()` dentro de `RcCommand.run`; `base_interpreter.py:178–179` lo invoca mediant. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P075 | manor-os/manor-ai | TP | TP | **TP** | Ruta de Joaquín: `packages/core/tasks/media_tasks.py:2859–2860`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P008 | apowerb/apowerb | TP | TP | **TP** | Ruta de Joaquín: `src/apowerb/routers/files.py:212–213, 246–253`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P087 | openclaw-easy/ViralMint | TP | TP | **TP** | Ruta de Joaquín: `backend/api/downloaded.py:485–488, 527–534`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P050 | manor-os/manor-ai | TP | TP | **TP** | Ruta de Joaquín: `packages/core/ai/tools/code_tool.py:1301–1314, 1325–1326`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P038 | manor-os/manor-ai | TP | TP | **TP** | Ruta de Joaquín: `apps/api/routers/sites.py:483–484, 533–537`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P056 | manor-os/manor-ai | TP | TP | **TP** | Ruta de Joaquín: `packages/core/ai/tools/file_tools.py:1066–1069, 1077–1078`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P060 | manor-os/manor-ai | TP | TP | **TP** | Ruta de Joaquín: `packages/core/ai/tools/media_tools.py:6112–6126`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P061 | manor-os/manor-ai | TP | TP | **TP** | Ruta de Joaquín: `packages/core/ai/tools/sandbox_tools.py:525–527`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P064 | manor-os/manor-ai | TP | TP | **TP** | Ruta de Joaquín: `packages/core/services/content_ledger.py:498–503`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P093 | pixeltable/pixeltable | TP | TP | **TP** | Ruta de Joaquín: `pixeltable/functions/twelvelabs.py:339–340`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P069 | manor-os/manor-ai | TP | TP | **TP** | Ruta de Joaquín: `packages/core/services/open_music_catalog.py:310–317`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |
| TC3 | P076 | manor-os/manor-ai | TP | TP | **TP** | Ruta de Joaquín: `packages/core/tasks/media_tasks.py:2892–2893`. E/S de fichero síncrona en el loop, en una ruta que se ejecuta mientras el loop atiende otro trabajo (v2 §3). |

## Ficheros

- `propuesta.py`: genera `propuesta-v2.json` a partir de `audit-joaquin.json`, las fichas y las razones propias de los casos revisados.
- `propuesta-v2.json`: la propuesta en formato legible por máquina (`v2_propuesta`, `fp_condition`, `dudoso`, `razon`).
- Este fichero: pendiente de tu confirmación. Las correcciones se registrarán aquí con fecha, antes de calcular la selección (C).
