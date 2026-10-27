# Review sheet — test-corpus-3

Joaquín's verdicts on 25 findings (`PREREGISTRATION.md`, "Review method"), in a random order. One block per finding.
Fill `Verdict` (TP, FP or U), `Reason (file:line)` and `Overstated` (Sí or No).
Rules: `PREREGISTRATION.md`, "Verdicts". Any help received, only factual navigation: `REVIEW-LOG.md`.

## P075

- Card: [cards/P075.md](cards/P075.md)
- Verdict: TP
- Reason (file:line): `packages/core/tasks/media_tasks.py:2859–2860` — `_ensure_public_url` realiza E/S síncrona con `open()` y `f.read()` dentro de `async def`. La función se utiliza en el flujo de generación de vídeo; `process_video_job_task` ejecuta `process_video_job` mediante `_run_async`, que en el flujo normal mantiene un event loop activo durante la tarea. [GitHub](https://raw.githubusercontent.com/manor-os/manor-ai/6518720e7b2781bd24cbdf549e23fbfc04053fce/packages/core/tasks/media_tasks.py)
- Overstated: No — la E/S síncrona puede bloquear el event loop; el impacto concreto depende del archivo y de las condiciones de ejecución.

## J003

- Card: [cards/J003.md](cards/J003.md)
- Verdict: TP
- Reason (file:line): `playgrounds/spring-petclinic-maven-sb-2/src/main/java/org/springframework/samples/petclinic/scheduled/SchedulerTestConfig.java:49–57` — `reEntrantLockTask()` está anotado con `@Scheduled` y ejecuta `Thread.sleep(120000)`, bloqueando el hilo del scheduler durante dos minutos mientras mantiene el `reentrantLock`.
- Overstated: Sí — el bloqueo de dos minutos es real, pero la etiqueta `critical` no queda justificada solo por este fragmento.

## P008

- Card: [cards/P008.md](cards/P008.md)
- Verdict: TP
- Reason (file:line): `src/apowerb/routers/files.py:212–213, 246–253` — el endpoint `upload_complete` es una función `async` de una ruta HTTP y ejecuta `open()` y lecturas síncronas de fragmentos en la rama S3 antes de un `await`. La E/S puede bloquear el event loop durante la lectura de los archivos.
- Overstated: Sí — el bloqueo está demostrado, pero la severidad `critical` no se justifica únicamente con este fragmento; su impacto depende del tamaño y número de fragmentos y de la concurrencia.

## P087

- Card: [cards/P087.md](cards/P087.md)
- Verdict: TP
- Reason (file:line): `backend/api/downloaded.py:485–488, 527–534` — el endpoint HTTP `import_local_video` abre el archivo de destino con `open(dest_path, "wb")` y escribe síncronamente cada fragmento mediante `f.write(chunk)` dentro de `async def`. Aunque la lectura de la carga usa `await`, las escrituras bloquean el event loop mientras se ejecutan.
- Overstated: Sí — el bloqueo síncrono está confirmado, pero la severidad `critical` no queda demostrada solo por este código; depende de la duración de la escritura y de la concurrencia.

## P050

- Card: [cards/P050.md](cards/P050.md)
- Verdict: TP
- Reason (file:line): `packages/core/ai/tools/code_tool.py:1301–1314, 1325–1326` — `_handle_notebook_edit` es asíncrona y realiza lectura síncrona con `open()`/`json.load()` y escritura síncrona con `open()`/`json.dump()`. La línea `1447` registra la función como herramienta `notebook_edit`, por lo que es alcanzable desde el flujo normal de herramientas.
- Overstated: Sí — el bloqueo del event loop es real, pero la severidad `critical` no queda justificada sin evidencia sobre el tamaño de los notebooks, la concurrencia o el impacto operativo.

## P038

- Card: [cards/P038.md](cards/P038.md)
- Verdict: TP
- Reason (file:line): `apps/api/routers/sites.py:483–484, 533–537` — `serve_site` es un endpoint HTTP asíncrono que abre y lee sincrónicamente los archivos HTML antes de devolver `HTMLResponse`. Las peticiones que sirven HTML pueden bloquear el event loop durante la E/S.
- Overstated: Sí — el bloqueo es real, pero la severidad `critical` no queda demostrada sin evidencia del tamaño de los archivos o del impacto bajo concurrencia.

## J001

- Card: [cards/J001.md](cards/J001.md)
- Verdict: TP
- Reason (file:line): `playgrounds/feature-service-maven-sb-3/src/main/java/com/sivalabs/ft/features/testdata/BookTestDataQueryRunner.java:22–25` — `runTests()` se ejecuta mediante `@Scheduled(cron = "*/2 * * * * *")` y bloquea el hilo del scheduler durante 10 segundos con `Thread.sleep(10000)`. El intervalo programado es de 2 segundos, inferior al bloqueo.
- Overstated: Sí — el bloqueo del hilo del scheduler está demostrado, pero la severidad `critical` no se justifica sin evidencia del impacto sobre otras tareas o servicios.

## P026

- Card: [cards/P026.md](cards/P026.md)
- Verdict: FP
- Reason (file:line): `backend/app/api/kline.py:948–950, 1003–1007` — aunque `asyncio.create_task(task())` en la línea 1009 descarta la referencia, `task()` captura sus excepciones (`except Exception`) y registra el fallo mediante `job_store.fail`; además, el trabajo se ejecuta a través de una ruta normal de API. El riesgo de excepción no recuperada descrito por la regla no se cumple en este flujo.
- Overstated: Sí — el mensaje afirma que las excepciones nunca se recuperan, pero la función las captura explícitamente.

## J010

- Card: [cards/J010.md](cards/J010.md)
- Verdict: TP
- Reason (file:line): `src/main/java/com/xianyusmart/service/impl/TokenRefreshServiceImpl.java:486–509` — `scheduledRefreshWebSocketToken()` está anotado con `@Scheduled` y ejecuta `Thread.sleep(randomInterval)`, bloqueando el hilo del scheduler entre 3 y 8 segundos por cada cuenta cuyo token necesita actualizarse.
- Overstated: Sí — el bloqueo es real y puede acumularse entre cuentas, pero la severidad `critical` no queda demostrada sin evidencia del impacto sobre otras tareas programadas.

## P056

- Card: [cards/P056.md](cards/P056.md)
- Verdict: TP
- Reason (file:line): `packages/core/ai/tools/file_tools.py:1066–1069, 1077–1078` — `_read_supported_text` es asíncrona y abre y lee archivos de texto de forma síncrona. Sus llamadas desde `file_tools.py:1896,2676` y `creative_studio_tools.py:384` usan `await`, por lo que la lectura puede bloquear el event loop durante la E/S.
- Overstated: Sí — el bloqueo potencial está confirmado, pero la severidad `critical` no queda demostrada sin evidencia del tamaño de los archivos o del impacto operativo bajo concurrencia.

## P060

- Card: [cards/P060.md](cards/P060.md)
- Verdict: TP
- Reason (file:line): `packages/core/ai/tools/media_tools.py:6112–6126` — `_load_entity_json` es asíncrona y abre y parsea un archivo JSON mediante `open()` y `json.load()` síncronos. La llamada en `media_tools.py:1688` usa `await _load_entity_json(...)`, por lo que esta lectura puede bloquear el event loop durante la E/S y el parseo.
- Overstated: Sí — el bloqueo potencial está confirmado, pero la severidad `critical` no se demuestra sin evidencia del tamaño de los JSON ni del impacto operativo bajo concurrencia.

## P020

- Card: [cards/P020.md](cards/P020.md)
- Verdict: TP
- Reason (file:line): `main.py:1988` — `asyncio.create_task(_persist_chat_history(...))` descarta la referencia a una tarea de persistencia en la ruta principal `/chat`; el contexto confirma que no es solo código de prueba o ejemplo.
- Overstated: No — la tarea se lanza sin conservar explícitamente su referencia, así que el hallazgo de PYVIBE-012 aplica. La afirmación de que una excepción «nunca se recupera» es más absoluta de lo que demuestra el fragmento, pero no invalida el hallazgo central.

## P061

- Card: [cards/P061.md](cards/P061.md)
- Verdict: TP
- Reason (file:line): `packages/core/ai/tools/sandbox_tools.py:525–527` — `_read_workspace_bytes` abre y lee el archivo sincrónicamente dentro de una función `async`; el llamador de producción en la línea 1505 lo espera con `await`.
- Overstated: Sí — la E/S síncrona puede bloquear el event loop, pero el fragmento no demuestra que el bloqueo alcance una duración crítica ni que cause un impacto observable grave.

## P035

- Card: [cards/P035.md](cards/P035.md)
- Verdict: FP
- Reason (file:line): `apps/api/routers/documents.py:1041–1042` — el `except BaseException` vacío solo captura excepciones mientras se espera la tarea cancelada tras un timeout; en la rama de cancelación externa, las líneas 1043–1049 vuelven a lanzar `CancelledError`, preservando la cancelación del waiter.
- Overstated: Sí — el mensaje generaliza que se rompe la cancelación y el apagado limpio, pero el código mostrado propaga explícitamente la cancelación externa.

## P028

- Card: [cards/P028.md](cards/P028.md)
- Verdict: TP
- Reason (file:line): `backend/app/api/kline.py:1251` — la ruta de producción descarta la referencia de `asyncio.create_task(task())`; aunque el cuerpo captura `Exception` y actualiza `job_store`, no conserva la tarea en un registro ni garantiza su ciclo de vida.
- Overstated: Sí — la afirmación de que las excepciones nunca se recuperan es exagerada: las líneas 1244–1247 registran excepciones ordinarias y marcan el trabajo como fallido.

## P064

- Card: [cards/P064.md](cards/P064.md)
- Verdict: TP
- Reason (file:line): `packages/core/services/content_ledger.py:498–503` — `reserve_content` ejecuta `open()` y `json.load()` síncronos cuando falla la creación del archivo, dentro de una función `async` invocada desde producción en `content_ledger_tools.py:197`.
- Overstated: Sí — el bloqueo del event loop es real, pero ocurre en la rama condicional `if not created`, y no se demuestra que su duración o frecuencia justifique una severidad crítica.

## P027

- Card: [cards/P027.md](cards/P027.md)
- Verdict: TP
- Reason (file:line): `backend/app/api/kline.py:1164` — la ruta de producción descarta la referencia de `asyncio.create_task(task())`; aunque el cuerpo captura `Exception` y actualiza `job_store` en `1157–1160`, no conserva la tarea en un registro ni garantiza su ciclo de vida.
- Overstated: Sí — el mensaje afirma que las excepciones nunca se recuperan, pero las excepciones ordinarias se registran y el trabajo se marca como fallido; el riesgo de no retener la tarea sí permanece.

## P093

- Card: [cards/P093.md](cards/P093.md)
- Verdict: TP
- Reason (file:line): `pixeltable/functions/twelvelabs.py:339–340` — `_embed_av_content` ejecuta `open()` y `fp.read()` de forma síncrona dentro de una función `async`; las llamadas de producción en las líneas 196 y 222 esperan esta función con `await`.
- Overstated: Sí — la lectura bloquea el event loop mientras se lee y codifica el archivo, pero solo en la rama de archivos que no superan `TWELVELABS_INLINE_LIMIT_BYTES`; no se demuestra que el impacto sea crítico.

## P005

- Card: [cards/P005.md](cards/P005.md)
- Verdict: TP
- Reason (file:line): `src/apowerb/main.py:680` — la rutina de arranque crea `memory_retention_loop()` sin conservar la referencia a la tarea ni añadir un callback que recupere sus excepciones; `_start_webhook_renewal()` se invoca desde el flujo principal en las líneas 836, 845 y 850.
- Overstated: Sí — el riesgo de perder el seguimiento de la tarea existe, pero el fragmento no demuestra que el recolector la elimine prematuramente ni que se produzca un fallo crítico.

## P044

- Card: [cards/P044.md](cards/P044.md)
- Verdict: TP
- Reason (file:line): `packages/core/ai/runtime/tool_effect_intents.py:237` — `_tool_effect_pending_checkpoints.set(...)` actualiza el `ContextVar` sin restaurar explícitamente el valor anterior; la función se usa desde el flujo principal de ejecución de herramientas (`tool_execution.py:829,1091`). Esto confirma la ausencia de restauración local, aunque no demuestra por sí solo una fuga entre tareas async.
- Overstated: Sí — los `ContextVar` se aíslan entre tareas, así que la ausencia de `.reset()` no basta para afirmar contaminación entre ellas.

## J016

- Card: [cards/J016.md](cards/J016.md)
- Verdict: TP
- Reason (file:line): `AbstractKafkaDomainEventSender.java:78,84` — ambas rutas bloquean con `send(...).get()` sin timeout explícito; los handlers programados ejecutan `sendMqEvent()` cada 3 segundos, por ejemplo `hp-demo-kafka/.../DomainEventSenderJobHandler.java:23–26`.
- Overstated: Sí — el bloqueo sin timeout explícito está demostrado, pero los límites concretos de 120 s y 60 s dependen de la configuración efectiva de Kafka y no se verifican con el código aportado.

## P069

- Card: [cards/P069.md](cards/P069.md)
- Verdict: TP
- Reason (file:line): `packages/core/services/open_music_catalog.py:310–317` — la función async abre el archivo con `open()` y ejecuta `target.write(chunk)` en el event loop durante la descarga; `apps/api/routers/media.py:271` confirma que se invoca desde una ruta de producción mediante `await`.
- Overstated: Sí — la E/S síncrona puede bloquear el event loop, pero el impacto crítico depende del tamaño de las escrituras y de la latencia del sistema de archivos, aspectos que el fragmento no demuestra.

## P097

- Card: [cards/P097.md](cards/P097.md)
- Verdict: FP
- Reason (file:line): `scanner/feed_hub.py:297,323–327` — el bucle externo espera antes de procesar y el interno de la línea 300 termina cuando `get_nowait()` lanza `queue.Empty`; además, el fan-out cede explícitamente el event loop cada `_FANOUT_CHUNK` elementos.
- Overstated: Sí — el mensaje de la regla describe un bucle sin ningún `await`, pero el bucle señalado sí termina y la función incluye varios puntos de cesión al event loop.

## P076

- Card: [cards/P076.md](cards/P076.md)
- Verdict: TP
- Reason (file:line): `packages/core/tasks/media_tasks.py:2892–2893` — `_ensure_inline_data_url` ejecuta `open()` y `f.read()` síncronos dentro de una corrutina; la referencia de producción en la línea 1482 pasa esta función como `ensure_inline_data_url` al adaptador.
- Overstated: Sí — el bloqueo del event loop es posible, pero la gravedad crítica no queda demostrada y el tamaño del archivo puede variar; además, la función lee el archivo completo antes de comprobar `max_bytes`.

## J017

- Card: [cards/J017.md](cards/J017.md)
- Verdict: TP
- Reason (file:line): `AbstractKafkaDomainEventSender.java:84` — `op.send(rc).get()` bloquea esperando el resultado sin timeout explícito dentro de `executeInTransaction`; el método `sendMqEvent()` se ejecuta desde handlers programados cada 3 segundos.
- Overstated: Sí — el bloqueo sin timeout explícito está demostrado, pero los límites de 120 s y 60 s citados dependen de la configuración efectiva de Kafka y no se verifican con el código aportado.

