# Review sheet — test-corpus-4

Joaquín's verdicts on all 160 findings of the review set (`PREREGISTRATION.md`, "Review method"), in a random order. One block per finding.
Fill `Verdict` (TP, FP or U); `FP condition` (detection, context or reachability for an FP, `—` otherwise);
`Reason (file:line)` (at least one `path:line`); and `Overstated` (Sí or No, optionally ` — note`).
Criterion: `../REVIEW-CRITERIA.md` v1 (`PREREGISTRATION.md`, "Verdict criterion"). Any help received, only factual navigation: `REVIEW-LOG.md`.

## P102

- Card: [cards/P102.md](cards/P102.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `proxy/app.py:3006` — se descarta la referencia a la tarea creada con `asyncio.create_task(produce())`; la función captura excepciones y las registra en `2999–3002`, pero eso no elimina el problema de seguimiento de la tarea. `_get_playlist_cached` se alcanza desde rutas de producción (`2642`, `2785`, `3180`, `3192`).
- Overstated: Sí — afirmar que las excepciones nunca se recuperan es exagerado, porque `produce()` captura `Exception` y registra el fallo; el descarte de la referencia sigue siendo real.

## J054

- Card: [cards/J054.md](cards/J054.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `BelegKiAnalyseService.java:84–86` — `analysiereBelegAsync` combina `@Async` y `@Transactional`, y `BelegService.java:244,254` confirma llamadas desde código de producción; la ejecución asíncrona puede usar una transacción distinta de la del llamador.
- Overstated: Sí — la separación transaccional es el comportamiento habitual de Spring, pero el fragmento no demuestra que exista un fallo concreto de consistencia ni que el llamador tenga cambios sin confirmar.

## J060

- Card: [cards/J060.md](cards/J060.md)
- Verdict: U
- FP condition: —
- Reason (file:line): `NovelServiceImpl.java:1387` — solo se aporta la implementación y `NovelService.java:125` declara el método en la interfaz; no hay evidencia de un llamador de producción que permita confirmar su alcanzabilidad.
- Overstated: Sí — la combinación de anotaciones está demostrada, pero no se ha acreditado que el método se invoque en ejecución ni que se materialicen los efectos transaccionales descritos.

## P045

- Card: [cards/P045.md](cards/P045.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): `backend/app/services/mcp/client.py:519–520` — `_http_exchange_record.set(HttpExchangeRecord())` inicializa el `ContextVar` al comienzo de cada intento, reemplazando el valor anterior; no se demuestra contaminación entre tareas, porque sus contextos están aislados. Las llamadas a `run_attempts()` en las líneas 579 y 583 confirman que se ejecuta en producción.
- Overstated: Sí — la falta de `.reset()` no demuestra por sí sola una fuga entre tareas async.

## P057

- Card: [cards/P057.md](cards/P057.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `agent/worker/processor.py:151` — se crea una tarea con `asyncio.create_task(self._run_one(req))` sin conservar su referencia; `_run_loop()` forma parte del flujo principal y se ejecuta mediante `await self._run_loop()` en la línea 74.
- Overstated: Sí — el descarte de la referencia está demostrado, pero no que el GC elimine prematuramente la tarea ni que sus excepciones nunca se recuperen.

## P065

- Card: [cards/P065.md](cards/P065.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `src/mindroot/coreplugins/admin/server_router.py:66` — `stop_server()` crea `delayed_exit()` mediante `asyncio.create_task()` y descarta la referencia; el endpoint HTTP `POST /stop` constituye una ruta de producción alcanzable.
- Overstated: Sí — el descarte de la referencia está demostrado, pero no que el GC elimine la tarea antes de terminar ni que sus excepciones nunca se recuperen.

## P032

- Card: [cards/P032.md](cards/P032.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `rate_service.py:1457` — se crea `_background_refresh_account(account_id)` con `asyncio.create_task()` y se descarta la referencia. La función `create_rate` tiene llamadores de producción en `routes/rates.py:222` y `auto_rate_scheduler.py:344`, por lo que es alcanzable.
- Overstated: Sí — el descarte de la referencia está demostrado, pero no que el GC recoja la tarea antes de finalizar ni que sus excepciones queden necesariamente sin recuperar; el `try/except` de `1458–1459` solo captura errores al crearla, no los de su ejecución.

## P054

- Card: [cards/P054.md](cards/P054.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): agent/services/flow_client.py:249 descarta la tarea creada con asyncio.create_task(self._sync_tier()); agent/main.py:62 llama a handle_message desde la ruta principal de mensajes.
- Overstated: Sí — el descarte de la referencia está probado, pero no que la tarea sea recolectada antes de terminar ni que una excepción quede sin recuperar.

## P008

- Card: [cards/P008.md](cards/P008.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): apps/api/app/mcp_server.py:321 descarta asyncio.create_task(_prewarm()); _ensure_backend se invoca desde las rutas de herramientas en las líneas 330, 362 y 382.
- Overstated: Sí — el descarte está probado; la recolección prematura o una excepción no recuperada no quedan demostradas.

## P023

- Card: [cards/P023.md](cards/P023.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): backend/app/services/jira.py:146,155 define get_projects como async y ejecuta requests.get de forma síncrona; backend/app/api/jira.py:322 llama al método mediante await.
- Overstated: No — la llamada síncrona está dentro de una función async alcanzable desde la API.

## J038

- Card: [cards/J038.md](cards/J038.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): CertificateServiceImpl.java:1089–1093 combina @Async con @Transactional(propagation = Propagation.NOT_SUPPORTED). NOT_SUPPORTED suspende/no inicia una transacción, así que no respalda la afirmación de que se ejecuta en una nueva transacción.
- Overstated: Sí — detecta las anotaciones, pero describe incorrectamente la semántica transaccional concreta.

## P059

- Card: [cards/P059.md](cards/P059.md)
- Verdict: FP
- FP condition: reachability
- Reason (file:line): semantic_duplicate_service.py:232–252 contiene reindex_all y el bucle sin await; la búsqueda exhaustiva de referencias solo muestra la definición y una llamada desde backend/tests/test_semantic_duplicates.py:261, sin caller de producción.
- Overstated: Sí — el bloqueo potencial se ve en el código, pero la ficha no acredita una ruta de producción.

## J059

- Card: [cards/J059.md](cards/J059.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): NovelServiceImpl.java:154–156 declara processNovelFileAsync con @Async y @Transactional(propagation = Propagation.REQUIRES_NEW); la línea 138 llama al método.
- Overstated: Sí — las anotaciones y la llamada están probadas; el método captura excepciones internamente (líneas 183–190), así que no debe insinuarse que necesariamente se propagan al llamador.

## P025

- Card: [cards/P025.md](cards/P025.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): backend/app/services/jira.py:243–244 define create_issue_internal como async y la línea 292 ejecuta requests.post síncrono; la línea 231 lo llama desde el flujo de creación.
- Overstated: No — llamada de red síncrona en una función async alcanzable.

## P051

- Card: [cards/P051.md](cards/P051.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): execution.py:100 descarta asyncio.create_task(_cleanup(...)); execution.py:102 registra late_cleanup como callback de creation.add_done_callback.
- Overstated: Sí — está probado que se descarta la referencia, no que ocurra recolección prematura ni que quede una excepción sin recuperar.

## P099

- Card: [cards/P099.md](cards/P099.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): proxy/app.py:1366–1391 define la ruta POST /v/api/v1/item/list y descarta asyncio.create_task(catalog.refresh_routes(...)) en la línea 1390; hay otras creaciones similares en 1427 y 1463.
- Overstated: Sí — la tarea se lanza desde una ruta activa, pero los efectos de GC/excepción alegados no están demostrados.

## J015

- Card: [cards/J015.md](cards/J015.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): NotificationBroadcastJobProcessor.java:58–60 combina @Async("taskExecutor") y @Transactional; NotificationBroadcastServiceImpl.java:64 llama a processor.process mediante runAfterCommit.
- Overstated: Sí — el procesamiento asíncrono y su transacción son reales, pero la afirmación sobre rollback del llamador y cambios no confirmados no encaja plenamente con la llamada tras el commit.

## P090

- Card: [cards/P090.md](cards/P090.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `app/startup.py:102–103,396`; `app/main.py:35` — el evento de arranque crea `cross_copy_staging_cleanup_watcher()` mediante `asyncio.create_task()` sin conservar su referencia.
- Overstated: Sí — no se demuestra que la tarea sea recolectada prematuramente ni que falle sin registrar su excepción.

## J057

- Card: [cards/J057.md](cards/J057.md)
- Verdict: FP
- FP condition: reachability
- Reason (file:line): `AsyncTask.java:33–38`; `ApplicationTests.java:33` — existe `Thread.sleep()` dentro de un método `@Async`, pero la única llamada acreditada está en una prueba.
- Overstated: Sí — no se acredita ejecución desde una ruta productiva.

## J010

- Card: [cards/J010.md](cards/J010.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `CompanyEnrichmentService.java:38–40`; `InsiderController.java:333–335` — `enrichCompanyData(String)` combina `@Async` y `@Transactional` y es invocado desde un controlador.
- Overstated: Sí — el comportamiento transaccional está acreditado, pero no un fallo efectivo por rollback o lecturas no confirmadas.

## P060

- Card: [cards/P060.md](cards/P060.md)
- Verdict: U
- FP condition: —
- Reason (file:line): `backend/services/sla_engine.py:343,348–362,323` — hay un `requests.post()` síncrono dentro de un método asíncrono, pero solo como alternativa cuando falla la importación de `aiohttp`. Con las referencias aportadas no queda acreditada una ruta productiva hasta ese método.
- Overstated: Sí — el bloqueo es condicional y la alcanzabilidad no está suficientemente demostrada.

## J056

- Card: [cards/J056.md](cards/J056.md)
- Verdict: FP
- FP condition: reachability
- Reason (file:line): `AsyncTask.java:22–26`; `ApplicationTests.java:31` — `Thread.sleep(3000)` está dentro de `@Async`, pero únicamente se documenta una llamada desde pruebas.
- Overstated: Sí — no hay evidencia de invocación productiva.

## P104

- Card: [cards/P104.md](cards/P104.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `proxy/catalog.py:457,492–493,424,631,649` — `get_page()` descarta la referencia de la tarea `work()` y tiene llamadas en código principal.
- Overstated: Sí — `work()` captura excepciones; no está demostrado que se produzcan recolección prematura o excepciones no recuperadas.

## P097

- Card: [cards/P097.md](cards/P097.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `app/startup.py:102–103,403`; `app/main.py:35` — el evento de arranque descarta la referencia de la tarea `resource_jobs_housekeeper()`.
- Overstated: Sí — el riesgo existe, pero no se demuestra una pérdida efectiva de la tarea.

## P085

- Card: [cards/P085.md](cards/P085.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `src/mcp/server.py:117–144,193–206,491–493` — `_logged_call()` crea una tarea para registrar la auditoría sin conservar su referencia; existen llamadas desde herramientas MCP.
- Overstated: Sí — no se demuestra que la tarea se pierda ni que falle.

## P041

- Card: [cards/P041.md](cards/P041.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `app/web/routes/diary.py:72–80` — el endpoint `POST /trigger` ejecuta `asyncio.create_task(_run_async(date))` y descarta su resultado.
- Overstated: Sí — no se acredita recolección prematura ni una excepción no recuperada.

## P014

- Card: [cards/P014.md](cards/P014.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `android/app/src/main/python/backend/main.py:1635–1667,1762,1934` — `_check_and_prewarm()` descarta la referencia de una tarea de precalentamiento y tiene llamadas en el código principal.
- Overstated: Sí — el `except` mostrado no permite afirmar que se recuperen las excepciones de la tarea, pero tampoco demuestra que ocurran.

## J014

- Card: [cards/J014.md](cards/J014.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): `CouponBatchIssueServiceImpl.java:253–256`; `AdminPromotionController.java:409–411` — `retryFailedItems()` combina `@Async` y `@Transactional` y es invocado desde un controlador.
- Overstated: Sí — no se demuestra que haya ocurrido una inconsistencia transaccional.

## J037

- Card: [cards/J037.md](cards/J037.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): AcmeServiceImpl.java:753,765–767 — La única llamada al método anotado es interna a la misma instancia. En el modo proxy habitual de Spring, esa llamada no activa @Async ni el interceptor transaccional del método; el escenario denunciado no se produce.
- Overstated: Sí — afirma ejecución en otro hilo y una transacción nueva sin considerar la autoinvocación. docs.spring.io

## P081

- Card: [cards/P081.md](cards/P081.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): indexing_service.py:208–210 — Se crea la tarea del pipeline y se descarta su referencia. Cumple PYVIBE-012 v1 aunque el pipeline capture excepciones.
- Overstated: Sí — descartar la referencia no demuestra que necesariamente se pierdan excepciones.

## P006

- Card: [cards/P006.md](cards/P006.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): main.py:497 — El arranque de producción crea la tarea warm_basemap() sin conservarla. Su carácter opcional no elimina el patrón.
- Overstated: Sí — es un precalentamiento recuperable; el fragmento no justifica severidad crítica.

## P064

- Card: [cards/P064.md](cards/P064.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): server_router.py:40–54 — La ruta /restart crea delayed_exit() y descarta la tarea. Retrasar intencionadamente la salida no exime de conservar la referencia.
- Overstated: No

## P092

- Card: [cards/P092.md](cards/P092.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): startup.py:398 — El evento de arranque crea cross_copy_progress_watcher() sin guardar la tarea. Según v1, basta ese descarte.
- Overstated: Sí — no se demuestra que las excepciones del watcher queden sin gestionar.

## J048

- Card: [cards/J048.md](cards/J048.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): JobOrchestrator.java:267 — La publicación espera mediante .get() sin plazo local. El catch posterior no limita la espera y esta retrasa también la ingesta directa de las líneas 288–309.
- Overstated: Sí — los tiempos concretos dependen de la configuración del productor, no aportada.

## J039

- Card: [cards/J039.md](cards/J039.md)
- Verdict: FP
- FP condition: detection
- Reason (file:line): ComplianceServiceImpl.java:366–371 — Propagation.NOT_SUPPORTED indica ejecución sin transacción; no abre la nueva transacción que afirma el mensaje. Existe llamada de producción desde ComplianceControllerImpl.java:46.
- Overstated: Sí — atribuye a NOT_SUPPORTED un comportamiento contrario a su semántica.

## P056

- Card: [cards/P056.md](cards/P056.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): flow_client.py:268–270; agent/main.py:62 — Un mensaje de producción puede crear _refresh_media_urls() descartando la tarea. La captura interna de excepciones no cambiaría el TP en v1.
- Overstated: Sí — no se ha demostrado que sus excepciones queden sin gestionar.

## P061

- Card: [cards/P061.md](cards/P061.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): mod.py:27–33; router.py:49 — La ruta espera directamente una función asíncrona que ejecuta subprocess.run() de forma síncrona. El timeout limita el proceso, pero no evita bloquear el event loop.
- Overstated: No

## P055

- Card: [cards/P055.md](cards/P055.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): flow_client.py:252–266; agent/main.py:62 — La rama extension_ready crea _sync_tier() y descarta su referencia. Es alcanzable desde el manejador de mensajes.
- Overstated: Sí — la afirmación sobre excepciones sin recuperar requiere revisar _sync_tier().

## J028

- Card: [cards/J028.md](cards/J028.md)
- Verdict: U
- FP condition: —
- Reason (file:line): SystemPreferencesService.java:252–259 — El listener combina ambas anotaciones, pero falta el publicador del evento. No puede determinarse si necesita compartir la transacción del emisor o si la persistencia independiente es correcta.
- Overstated: Sí — la combinación, por sí sola, no demuestra un defecto transaccional.

## J023

- Card: [cards/J023.md](cards/J023.md)
- Verdict: FP
- FP condition: reachability
- Reason (file:line): UserBehaviorTrackingServiceImpl.java:128; UserBehaviorTrackingService.java:42 — La búsqueda exhaustiva aportada solo muestra declaración e implementación; no identifica ninguna llamada de producción a trackShare.
- Overstated: Sí — además, REQUIRES_NEW expresa explícitamente independencia transaccional.

## J055

- Card: [cards/J055.md](cards/J055.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): BadgeEventHandler.java:21–29 — El listener se ejecuta después del commit y solicita REQUIRES_NEW. La transacción independiente permite persistir la concesión de insignias tras confirmar la operación original.
- Overstated: Sí — denuncia como defecto el aislamiento previsto por AFTER_COMMIT.

## P049

- Card: [cards/P049.md](cards/P049.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): knowledge_service.py:67; routes/knowledge.py:18 — La subida crea _process_document() sin conservar su tarea y devuelve el documento como processing. Cumple PYVIBE-012 v1.
- Overstated: Sí — no se demuestra que _process_document() deje escapar excepciones.

## P005

- Card: [cards/P005.md](cards/P005.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): main.py:482–489 — El arranque crea _get_catalog() descartando la tarea. Que sea un precalentamiento opcional no elimina el TP según v1.
- Overstated: Sí — el propio contexto indica que una petición posterior puede rellenar la caché; no justifica severidad crítica.

## P068

- Card: [cards/P068.md](cards/P068.md)
- Verdict: U
- FP condition: —
- Reason (file:line): services.py:610–615 — El except: captura cualquier excepción que surja dentro del bloque. Para confirmar el problema de cancelación falta conocer las colas: si son asyncio.Queue sin límite, put() puede completarse sin suspender.
- Overstated: Sí — el fragmento no demuestra que se rompa el apagado ni que ese await sea un punto efectivo de cancelación.

## J041

- Card: [cards/J041.md](cards/J041.md)
- Verdict: FP
- FP condition: detection
- Reason (file:line): ComplianceServiceImpl.java:518–521 — NOT_SUPPORTED no inicia una transacción nueva. La llamada externa desde el controlador existe, pero no produce la semántica transaccional denunciada.
- Overstated: Sí — el mensaje ignora la propagación declarada.

## J044

- Card: [cards/J044.md](cards/J044.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): EmbeddingConsumer.java:43–46,81 — El consumidor Kafka espera la publicación con .get() sin timeout local. Capturar el error después no limita cuánto tiempo permanece bloqueado el listener.
- Overstated: Sí — los valores temporales por defecto no acreditan la configuración efectiva.

## P091

- Card: [cards/P091.md](cards/P091.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): startup.py:397 — El arranque crea cross_copy_organize_watcher() y descarta su tarea. Cumple v1 aunque el watcher gestione sus propias excepciones.
- Overstated: Sí — no se demuestra que existan excepciones sin recuperar.

## P018

- Card: [cards/P018.md](cards/P018.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): shopify.py:309–310,361–365 — El endpoint asíncrono ejecuta requests.post() directamente, bloqueando el event loop durante la petición. Además, no establece timeout.
- Overstated: No

## J049

- Card: [cards/J049.md](cards/J049.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): JobOrchestrator.java:477; OisIngestController.java:161; RuntimePushDocumentDispatcher.java:176 — Hay llamadas de producción y la publicación espera con .get() sin límite local.
- Overstated: Sí — la duración concreta depende de la configuración efectiva del productor.

## P076

- Card: [cards/P076.md](cards/P076.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): scheduler/mod.py:493–499; scheduler/router.py:186 — El except: engloba await f.read() y puede absorber CancelledError, continuando con el historial en vez de propagar la cancelación. Existe una ruta de producción.
- Overstated: No

## P058

- Card: [cards/P058.md](cards/P058.md)
- Verdict: U
- FP condition: —
- Reason (file:line): .tmp-ci-venv/Lib/site-packages/realtime/_async/channel.py:247 — Se descarta la tarea, pero falta demostrar que producción utiliza esta copia de la dependencia del entorno temporal. El registro del callback no demuestra esa ruta.
- Overstated: Sí — no está acreditado el impacto en la aplicación.

## J019

- Card: [cards/J019.md](cards/J019.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): UserBehaviorTrackingServiceImpl.java:48–60; BehaviorTrackingController.java:68 — Es registro independiente de telemetría de búsqueda, con REQUIRES_NEW explícito y datos recibidos como valores. No se demuestra necesidad de compartir la transacción del llamador.
- Overstated: Sí — independencia transaccional no equivale por sí sola a defecto.

## P096

- Card: [cards/P096.md](cards/P096.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): app/startup.py:402 — El arranque crea memory_housekeeper() y descarta la referencia a la tarea. Cumple PYVIBE-012 v1.
- Overstated: No

## P101

- Card: [cards/P101.md](cards/P101.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): proxy/app.py:1463 — El endpoint crea la tarea de actualización de caché sin conservarla. El except exterior no captura errores posteriores de su ejecución.
- Overstated: Sí — el contexto muestra una actualización de caché recuperable; no acredita severidad crítica.

## P062

- Card: [cards/P062.md](cards/P062.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): admin/mod.py:41–47; admin/router.py:49 — La ruta espera directamente la función que ejecuta subprocess.run(). El timeout no evita bloquear el event loop.
- Overstated: No

## J033

- Card: [cards/J033.md](cards/J033.md)
- Verdict: U
- FP condition: —
- Reason (file:line): UserMessagePreServiceImpl.java:172–176; MessageUtils.java:46 — Existe llamada, pero el método @Async devuelve Boolean, un retorno incompatible con el interceptor estándar de Spring. Falta comprobar si la ejecución real llega al cuerpo mediante proxy o por otra vía.
- Overstated: Sí — presupone ejecución asíncrona efectiva.

## J008

- Card: [cards/J008.md](cards/J008.md)
- Verdict: U
- FP condition: —
- Reason (file:line): BikeController.java:85–89 — Hay llamadas a .block(), pero falta comprobar la configuración WebFlux y el tipo de Mono. Además, la llamada de la línea 85 podría fallar antes de alcanzar la señalada.
- Overstated: Sí — «lanza en cada llamada» no queda demostrado para la línea 89.

## P077

- Card: [cards/P077.md](cards/P077.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): scheduler/mod.py:594,612 — El bucle del scheduler se inicia y descarta las tareas de los comandos vencidos. Conservar scheduler_task no conserva las tareas que este crea.
- Overstated: No

## P026

- Card: [cards/P026.md](cards/P026.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): services/jira.py:308; api/jira.py:401 — La ruta espera una función asíncrona que llama directamente a requests.get(), sin descargarla a otro hilo.
- Overstated: No

## P074

- Card: [cards/P074.md](cards/P074.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): server_installer.py:51; mcp_manager.py:745 — El gestor espera directamente una instalación mediante subprocess.run(). Durante el proceso se bloquea el event loop; el timeout de 60 segundos no lo evita.
- Overstated: No

## P082

- Card: [cards/P082.md](cards/P082.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): support.py:111–128,137 — La dependencia asíncrona establece deliberadamente identificadores para el endpoint dentro del contexto de su petición. La ausencia de reset() no demuestra contaminación entre tareas de peticiones independientes.
- Overstated: Sí — ContextVar no comparte automáticamente las modificaciones entre tareas.

## J011

- Card: [cards/J011.md](cards/J011.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): CompanyEnrichmentService.java:44,56,96 — Las llamadas de producción identificadas al overload anotado son internas a la misma instancia. Con el proxy estándar no activan sus anotaciones; no se produce el escenario denunciado.
- Overstated: Sí — además, el callback thenApply no queda necesariamente cubierto por la transacción del método.

## P030

- Card: [cards/P030.md](cards/P030.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): workwit/backend/app.py:32–34 — El evento de arranque crea el scheduler sin conservar la tarea.
- Overstated: No

## P012

- Card: [cards/P012.md](cards/P012.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): browser_tools.py:216; server/browser_routes.py:53 — Una ruta de producción inicia el bucle de limpieza descartando la tarea. _cleanup_task_started conserva un booleano, no una referencia a ella.
- Overstated: No

## P009

- Card: [cards/P009.md](cards/P009.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): routes/recon.py:601–652 — El endpoint crea la tarea del pipeline y descarta su resultado. La variable task contiene la coroutine, no el objeto Task devuelto.
- Overstated: No

## J032

- Card: [cards/J032.md](cards/J032.md)
- Verdict: U
- FP condition: —
- Reason (file:line): UserMessagePreServiceImpl.java:120–124; MessageUtils.java:33 — Hay llamada de producción, pero el retorno Boolean es incompatible con @Async estándar. Falta verificar cómo se invoca realmente antes de afirmar que el worker ejecuta el sleep.
- Overstated: Sí — presupone que el interceptor permite ejecutar el cuerpo.

## J035

- Card: [cards/J035.md](cards/J035.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): ItemDetailSyncServiceImpl.java:121,127–156 — La sincronización invoca executeSync mediante self y contiene una pausa bloqueante por elemento. Su finalidad de espaciar peticiones no elimina la ocupación del hilo.
- Overstated: Sí — una pausa de hasta 500 ms con interrupción gestionada no acredita por sí sola severidad crítica.

## P095

- Card: [cards/P095.md](cards/P095.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): app/startup.py:401 — Se descarta la tarea del scheduler al arrancar. Que la operación de firma dependa de configuración no impide crear y ejecutar el bucle.
- Overstated: No

## J027

- Card: [cards/J027.md](cards/J027.md)
- Verdict: U
- FP condition: —
- Reason (file:line): SystemPreferencesService.java:240–245 — Falta el publicador del evento para comprobar su ruta de producción y si existe una dependencia transaccional que haga incorrecta la persistencia independiente.
- Overstated: Sí — las dos anotaciones no bastan para demostrar un defecto.

## P038

- Card: [cards/P038.md](cards/P038.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): vector_store.py:1006–1043; server/main.py:845 — El endpoint espera un recorrido completo con llamadas síncronas a scroll() y sin ningún await dentro del bucle. Bloquea el event loop hasta terminar.
- Overstated: No — el mensaje reconoce que el bucle puede finalizar.

## P044

- Card: [cards/P044.md](cards/P044.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): file_service.py:485; api/files.py:103 — La confirmación de subida crea el procesamiento LLM descartando la tarea después de marcar el archivo como parsing.
- Overstated: No

## J004

- Card: [cards/J004.md](cards/J004.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): KafkaProducer.java:78–82 — @TransactionalEventListener usa por defecto AFTER_COMMIT. La operación se programa tras confirmar la transacción original; que no participe en ella no constituye el defecto denunciado.
- Overstated: Sí — el rollback original no puede deshacer una operación iniciada después de su commit.

## P053

- Card: [cards/P053.md](cards/P053.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): server/opds/init.py:66,84 — El lifespan registrado crea _print_startup_messages() y descarta su tarea. Cumple v1 aunque solo escriba mensajes.
- Overstated: Sí — el efecto mostrado se limita a mensajes informativos de arranque.

## P034

- Card: [cards/P034.md](cards/P034.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): xianyu_order_sync.py:382–385; routes/order.py:246 — La sincronización alcanzable desde producción descarta las tareas de republicación. Nombrarlas no conserva sus referencias.
- Overstated: Sí — existe un barrido periódico de respaldo declarado; no se acredita pérdida definitiva.

## P013

- Card: [cards/P013.md](cards/P013.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): android/app/src/main/python/backend/main.py:270–278 — El endpoint asíncrono ejecuta httpx.get() síncrono cuando falla el primer intento. Esa rama poco frecuente sigue siendo alcanzable.
- Overstated: No

## P016

- Card: [cards/P016.md](cards/P016.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): backend/main.py:1667,1762,1934 — El helper invocado crea la traducción anticipada descartando su tarea. El except exterior no gestiona las excepciones posteriores de esa tarea.
- Overstated: Sí — es precalentamiento opcional; no se demuestra impacto crítico.

## J040

- Card: [cards/J040.md](cards/J040.md)
- Verdict: FP
- FP condition: detection
- Reason (file:line): ComplianceServiceImpl.java:497–501 — Propagation.NOT_SUPPORTED indica ejecución sin transacción, no una transacción nueva como afirma la alerta.
- Overstated: Sí — interpreta incorrectamente la propagación declarada.

## P002

- Card: [cards/P002.md](cards/P002.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): src/vanchor/ui/server.py:671–689 — La ruta de reinicio descarta la tarea devuelta por ensure_future(), sin conservarla durante la espera y la parada del runtime.
- Overstated: Sí — la recolección de una tarea pendiente no equivale técnicamente a una cancelación silenciosa mediante cancel().

## P050

- Card: [cards/P050.md](cards/P050.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): quiz_service.py:155; routes/quiz.py:34 — La ruta crea la generación de preguntas descartando la tarea y devuelve su identificador. El registro en base de datos no conserva el objeto Task.
- Overstated: No

## J018

- Card: [cards/J018.md](cards/J018.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): UserBehaviorTrackingServiceImpl.java:27–40; BehaviorTrackingController.java:46 — Registra telemetría de visualización con valores recibidos y REQUIRES_NEW explícito. El contexto no muestra que necesite participar en una transacción del llamador.
- Overstated: Sí — presenta la independencia transaccional prevista como un fallo.

## P021

- Card: [cards/P021.md](cards/P021.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): services/jira.py:113; api/jira.py:107 — Las rutas esperan directamente una función asíncrona que ejecuta requests.post() síncrono, sin timeout.
- Overstated: No

## P022

- Card: [cards/P022.md](cards/P022.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): services/jira.py:131; api/jira.py:220 — La consulta de recursos Jira ejecuta requests.get() directamente en el flujo asíncrono del endpoint.
- Overstated: No

## P036

- Card: [cards/P036.md](cards/P036.md)
- Verdict: FP
- FP condition: reachability
- Reason (file:line): vector_store.py:862,877 — La búsqueda exhaustiva solo muestra la definición y una referencia documental; no aparece una ruta de producción que invoque hard_delete_account.
- Overstated: Sí — el bloqueo existe potencialmente, pero su ejecución no está acreditada.

## J013

- Card: [cards/J013.md](cards/J013.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): GitHubDeploymentService.java:61–78; GitHubController.java:55 — Procesa un evento externo de despliegue como trabajo independiente. El contexto aportado no requiere compartir una transacción del controlador ni leer cambios suyos sin confirmar.
- Overstated: Sí — la independencia transaccional no demuestra un defecto.

## P069

- Card: [cards/P069.md](cards/P069.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): catalog_commands.py:112; plugin_info.json:27; mcp_catalog.jinja2:188 — El comando registrado y expuesto por la interfaz ejecuta subprocess.run() dentro de una función asíncrona.
- Overstated: Sí — consultar uvx --help no acredita por sí solo severidad crítica.

## J005

- Card: [cards/J005.md](cards/J005.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): Backup.java:93–122; BackupService.java:64 — El trabajo genera una copia de seguridad leyendo repositorios dentro de su propia transacción de solo lectura. No se muestra dependencia de cambios pendientes del llamador.
- Overstated: Sí — una transacción independiente es coherente con este trabajo asíncrono.

## J016

- Card: [cards/J016.md](cards/J016.md)
- Verdict: FP
- FP condition: reachability
- Reason (file:line): NotificationServiceImpl.java:279; NotificationService.java:112 — La búsqueda aportada no contiene una llamada al método del servicio. El método homónimo del controlador y las llamadas frontend no prueban que lo invoquen.
- Overstated: Sí — no está acreditada la ejecución del método señalado.

## P029

- Card: [cards/P029.md](cards/P029.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): agent_endpoints.py:994–1004 — El endpoint crea la tarea de automatización y descarta su referencia. El except exterior no captura sus excepciones posteriores.
- Overstated: No

## P048

- Card: [cards/P048.md](cards/P048.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): taskuary/server.py:9844–9849 — El bucle interior drena elementos ya disponibles mediante get_nowait() hasta QueueEmpty; después cede el control con to_thread(). No contiene I/O bloqueante ni espera activa.
- Overstated: Sí — omite que es un drenaje finito entre puntos de suspensión.

## P035

- Card: [cards/P035.md](cards/P035.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): vector_store.py:821–844; server/main.py:736 — El endpoint espera una paginación con llamadas síncronas a scroll() y sin ningún punto de suspensión dentro del bucle.
- Overstated: No

## J043

- Card: [cards/J043.md](cards/J043.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): EmbeddingConsumer.java:43–60 — El listener procesa mensajes DELETE esperando una publicación Kafka con .get() sin timeout local. El catch no limita la espera.
- Overstated: No — el mensaje identifica los tiempos como valores por defecto, no como configuración comprobada.

## P007

- Card: [cards/P007.md](cards/P007.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): main.py:500–504,709 — El lifespan registrado crea _warm_apple() sin conservar la tarea. Cumple PYVIBE-012 v1.
- Overstated: Sí — el efecto mostrado es precalentamiento de mapas; no acredita severidad crítica.

## J024

- Card: [cards/J024.md](cards/J024.md)
- Verdict: U
- FP condition: —
- Reason (file:line): SecurityServiceAsyncExectuion.java:24–49; CurrencypairJpaRepositoryImpl.java:353 — Hay llamadas de producción, pero falta saber si pasan entidades recién persistidas o cambios sin confirmar que el worker necesita consultar. El TransactionTemplate no resuelve esa posible carrera.
- Overstated: Sí — las anotaciones solas no demuestran que esa dependencia exista.

## P093

- Card: [cards/P093.md](cards/P093.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): app/startup.py:399; app/main.py:35 — El arranque crea cross_copy_temp_cleanup_watcher() y descarta su tarea.
- Overstated: Sí — no se ha comprobado la afirmación adicional sobre excepciones sin gestionar.

## P047

- Card: [cards/P047.md](cards/P047.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): taskuary/server.py:9805–9812 — El bucle agrupa datos ya encolados hasta vaciar la cola o encontrar un marcador; después espera send_frame(). Es procesamiento por lotes, sin espera activa.
- Overstated: Sí — presenta como bloqueo problemático un drenaje finito de la cola.

## P087

- Card: [cards/P087.md](cards/P087.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): app/startup.py:393; app/main.py:35 — El evento de arranque descarta la tarea de monitor_scheduler(). Sus esperas y capturas internas no cambian el TP según v1.
- Overstated: Sí — no se demuestra que las excepciones terminen sin gestionar.

## P079

- Card: [cards/P079.md](cards/P079.md)
- Verdict: U
- FP condition: —
- Reason (file:line): integrations/gmail.py:257–269; services/task_jobs/gmail.py:95 — El bucle usa HTTP síncrono, pero las rutas identificadas lo delegan a Celery. Falta revisar cómo el worker ejecuta la coroutine y si comparte su event loop con otros trabajos.
- Overstated: Sí — no se demuestra bloqueo del event loop que atiende la API.

## P075

- Card: [cards/P075.md](cards/P075.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): server_installer.py:63; mcp_manager.py:749 — El gestor espera directamente una función asíncrona que ejecuta npm install mediante subprocess.run(). El timeout no evita el bloqueo.
- Overstated: No

## P004

- Card: [cards/P004.md](cards/P004.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): localllm/manager.py:628; routes/ai_models.py:106 — La ruta inicia la descarga descartando el objeto Task. _JOBS conserva el registro del trabajo, no la tarea creada.
- Overstated: Sí — falta revisar _run_job() para afirmar que sus excepciones quedan sin gestionar.

## P020

- Card: [cards/P020.md](cards/P020.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): services/jira.py:92; api/jira.py:217 — El intercambio OAuth ejecuta requests.post() síncrono directamente desde una función esperada por el endpoint.
- Overstated: No

## J036

- Card: [cards/J036.md](cards/J036.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): TokenRefreshServiceImpl.java:496–519 — El método programado duerme entre 3 y 8 segundos por cuenta que requiere refresco, ocupando el hilo del scheduler.
- Overstated: Sí — falta la configuración del scheduler para justificar impacto crítico sobre otras tareas.

## P024

- Card: [cards/P024.md](cards/P024.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): services/jira.py:180; api/jira.py:362 — El endpoint espera una función asíncrona que hace una petición requests.get() síncrona, sin timeout.
- Overstated: No

## P003

- Card: [cards/P003.md](cards/P003.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): app/api/cron.py:105–106,133–134 — El endpoint asíncrono usa un cliente HTTP síncrono y ejecuta client.post() directamente. Ser una operación de diagnóstico no elimina su alcanzabilidad.
- Overstated: No — el bloqueo efectivo está en la petición de la línea 134.

## J030

- Card: [cards/J030.md](cards/J030.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): BzLogServiceImpl.java:120–125; MultiLogService.java:32,36 — El método persiste registros de log mediante un servicio independiente. No se muestra una necesidad de que el log participe en la transacción de negocio del llamador.
- Overstated: Sí — persistir logs independientemente no constituye por sí solo un fallo.

## J031

- Card: [cards/J031.md](cards/J031.md)
- Verdict: U
- FP condition: —
- Reason (file:line): QuartzJobServiceImpl.java:151–169; ExecutionJob.java:81 — Hay llamada de producción, pero falta el contexto de ExecutionJob para determinar si los subtrabajos dependen de cambios pendientes del emisor. La espera a Redis plantea otro problema distinto.
- Overstated: Sí — la combinación de anotaciones no demuestra la inconsistencia denunciada.

## J058

- Card: [cards/J058.md](cards/J058.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): ModelAutoChatService.java:59–94 — En el horario y puerto habilitados, el scheduler espera una llamada LLM mediante Future.get() sin timeout local. Los filtros no hacen inalcanzable esa ruta.
- Overstated: No

## J007

- Card: [cards/J007.md](cards/J007.md)
- Verdict: U
- FP condition: —
- Reason (file:line): BikeController.java:85–87 — Falta verificar el runtime WebFlux y el Mono devuelto. La llamada previa a .block() de la línea 85 también puede impedir alcanzar la señalada.
- Overstated: Sí — no está demostrado que la línea 87 lance una excepción en cada llamada.

## J009

- Card: [cards/J009.md](cards/J009.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): FilingSyncJob.java:53–94 — El trabajo programado ejecuta Thread.sleep() por empresa cuando el retraso configurado supera el mínimo. La limitación de frecuencia es intencional, pero sigue ocupando el hilo.
- Overstated: Sí — falta conocer el executor y el retraso efectivo para justificar severidad crítica.

## P043

- Card: [cards/P043.md](cards/P043.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): file_service.py:267–269; api/files.py:62 — La subida de archivos no gráficos crea tareas de análisis LLM descartando sus referencias. Las capturas del método de subida no supervisan esas tareas.
- Overstated: Sí — no se ha comprobado que _parse_file_with_llm() deje escapar excepciones.

## P031

- Card: [cards/P031.md](cards/P031.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): automation_runner.py:153; app.py:34 — El scheduler iniciado en producción descarta las tareas de las automatizaciones vencidas. El except del bucle no captura sus errores posteriores.
- Overstated: No

## J002

- Card: [cards/J002.md](cards/J002.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): KafkaProducer.java:77–81 — @TransactionalEventListener usa por defecto AFTER_COMMIT; el envío asíncrono se inicia tras confirmar la transacción original. No necesita participar en una transacción ya finalizada.
- Overstated: Sí — presenta la separación posterior al commit como un defecto transaccional.

## J017

- Card: [cards/J017.md](cards/J017.md)
- Verdict: U
- FP condition: —
- Reason (file:line): HomestayIndexingServiceImpl.java:85–93; HomestayCommandServiceImpl.java:370 — El worker relee la vivienda y actualiza Elasticsearch. Falta comprobar si las llamadas ocurren antes del commit; en ese caso podría indexar datos antiguos o borrar el documento.
- Overstated: Sí — la carrera transaccional es posible, pero no está confirmada.

## J029

- Card: [cards/J029.md](cards/J029.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): BzLogServiceImpl.java:95–117; OprLogAspect.java:78,95 — Persiste un registro de operaciones de forma independiente. El contexto mostrado no exige que ese registro comparta el rollback de la operación auditada.
- Overstated: Sí — independencia transaccional no implica por sí sola un defecto.

## P042

- Card: [cards/P042.md](cards/P042.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): highlights.py:217–228 — El endpoint crea la tarea de generación y descarta su referencia. Cumple PYVIBE-012 v1.
- Overstated: No

## P011

- Card: [cards/P011.md](cards/P011.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): dashboard_server.py:3884–3885 — El endpoint asíncrono ejecuta una petición mediante httpx.Client síncrono, sin delegarla a otro hilo.
- Overstated: No

## P019

- Card: [cards/P019.md](cards/P019.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): faq_article_import.py:500–514 — El cliente es síncrono, pero las operaciones de descubrimiento y descarga se ejecutan mediante asyncio.to_thread(). Construir el cliente no equivale a ejecutar las peticiones en el event loop.
- Overstated: Sí — ignora la delegación explícita del I/O.

## P098

- Card: [cards/P098.md](cards/P098.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): proxy/app.py:867–868,1499 — Se descarta la tarea de work(). Conservar y esperar fut no conserva automáticamente la tarea que produce su resultado.
- Overstated: Sí — work() captura las excepciones ordinarias; v1 mantiene el TP por el descarte.

## J050

- Card: [cards/J050.md](cards/J050.md)
- Verdict: FP
- FP condition: reachability
- Reason (file:line): PolicyIndexService.java:42 — La búsqueda exhaustiva solo encuentra la definición; no aparece una llamada ni un registro de ejecución automática.
- Overstated: Sí — no está acreditada su ejecución en producción.

## J025

- Card: [cards/J025.md](cards/J025.md)
- Verdict: U
- FP condition: —
- Reason (file:line): SystemPreferencesService.java:216–221 — Falta localizar el publicador del evento y comprobar si necesita compartir una transacción. Los otros listeners no resuelven esa cuestión.
- Overstated: Sí — las anotaciones no bastan para demostrar inconsistencia.

## P078

- Card: [cards/P078.md](cards/P078.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): volcengine_tts.py:413–415,579,635 — El cierre alcanzable captura cualquier excepción del await websocket.close(), incluida una cancelación que se entregue durante esa espera.
- Overstated: Sí — no absorbe necesariamente una cancelación previa que ya estuviera propagándose por el finally.

## P015

- Card: [cards/P015.md](cards/P015.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): backend/main.py:270–278 — El endpoint asíncrono ejecuta httpx.get() síncrono en la rama de respaldo. Que solo se alcance cuando falla el primer intento no elimina el TP.
- Overstated: No

## J034

- Card: [cards/J034.md](cards/J034.md)
- Verdict: FP
- FP condition: detection
- Reason (file:line): UserMessageBizService.java:16–21 — @Transactional pertenece a sendMailOnly; @Async pertenece a otro método, sendMessagePre. No están aplicadas al mismo método.
- Overstated: Sí — el patrón denunciado no existe.

## P066

- Card: [cards/P066.md](cards/P066.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): agent.py:929–936; persona/mod.py:72 — El servicio invocado desde producción crea agent.handle_cmds() descartando su tarea. Esperar run_command() no espera la tarea interna.
- Overstated: No

## P052

- Card: [cards/P052.md](cards/P052.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): store.py:827–837; orchestrator.py:1558 — La operación asíncrona abre y modifica SQLite directamente, incluyendo un commit, sin descargar ese I/O a otro hilo.
- Overstated: No

## P083

- Card: [cards/P083.md](cards/P083.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): support.py:1882–1883,1946 — La ruta de diagnóstico ejecuta httpx.get() síncrono. El control de acceso y el timeout no evitan bloquear el event loop.
- Overstated: No

## P084

- Card: [cards/P084.md](cards/P084.md)
- Verdict: U
- FP condition: —
- Reason (file:line): jobs.py:1063–1082 — El bucle no cede el control mientras reclama trabajos. Falta revisar _claim() para determinar si realiza I/O síncrono repetido y qué limita el volumen; el gather() posterior no evita ese tramo sin suspensión.
- Overstated: Sí — no se demuestra una duración problemática ni severidad crítica.

## P071

- Card: [cards/P071.md](cards/P071.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): server_installer.py:12–14; mcp_/mod.py:339 — La función esperada ejecuta cuatro comprobaciones de procesos de forma síncrona, bloqueando durante cada ejecución.
- Overstated: Sí — comprobar versiones no acredita por sí solo impacto crítico.

## J021

- Card: [cards/J021.md](cards/J021.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): UserBehaviorTrackingServiceImpl.java:85–98; UserFavoriteServiceImpl.java:69 — Registra telemetría con datos recibidos como valores y solicita explícitamente una transacción independiente. No se muestra dependencia de datos sin confirmar.
- Overstated: Sí — la independencia declarada no demuestra un fallo.

## J052

- Card: [cards/J052.md](cards/J052.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): SC2MetaService.java:98–108 — El método programado espera la finalización del flujo mediante .block(), ocupando el hilo del scheduler.
- Overstated: Sí — falta conocer el scheduler y los límites de la operación para justificar severidad crítica.

## J012

- Card: [cards/J012.md](cards/J012.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): CompanyEnrichmentService.java:88–97; InsiderController.java:357 — El trabajo alcanzable duerme un segundo por empresa. La pausa se ejecuta dentro de CompletableFuture.runAsync(), cuyo executor no se especifica.
- Overstated: Sí — el sleep ocurre en el executor de runAsync, no directamente en el hilo que ejecuta el cuerpo exterior de @Async.

## P072

- Card: [cards/P072.md](cards/P072.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): server_installer.py:27; mcp_manager.py:741 — El gestor espera una función asíncrona que ejecuta subprocess.run() directamente.
- Overstated: Sí — ejecutar uvx --help no acredita por sí solo severidad crítica.

## J042

- Card: [cards/J042.md](cards/J042.md)
- Verdict: FP
- FP condition: detection
- Reason (file:line): DiscoveryServiceImpl.java:872–876 — Propagation.NOT_SUPPORTED establece ejecución sin transacción; no abre la nueva transacción que afirma el mensaje.
- Overstated: Sí — interpreta incorrectamente la propagación.

## P010

- Card: [cards/P010.md](cards/P010.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): tiles.py:465–466 — ensure_future() recibe el Future ya creado por gather() y lo devuelve sin crear otra tarea. gather() mantiene y supervisa sus tareas hijas; el mensaje presupone un lanzamiento directo de una coroutine.
- Overstated: Sí — además, recolección y cancelación silenciosa no son equivalentes.

## P017

- Card: [cards/P017.md](cards/P017.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): shopify.py:82–83,126 — El endpoint asíncrono ejecuta requests.post() directamente y sin timeout explícito.
- Overstated: No

## J001

- Card: [cards/J001.md](cards/J001.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): KafkaProducer.java:57–61 — @TransactionalEventListener usa por defecto AFTER_COMMIT; el envío se inicia después de confirmar la operación original.
- Overstated: Sí — no compartir una transacción ya confirmada no constituye el defecto denunciado.

## J051

- Card: [cards/J051.md](cards/J051.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): Cron.java:218–221 — El método programado espera mediante .block() el resultado de runIfAvailable().
- Overstated: Sí — falta revisar la operación y la configuración del scheduler para acreditar impacto crítico.

## P046

- Card: [cards/P046.md](cards/P046.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): helpers.py:237; views/images.py:299,470 — Las rutas de imágenes crean la tarea de seguimiento sin conservar su referencia. Cumple PYVIBE-012 v1.
- Overstated: Sí — el efecto mostrado es seguimiento de uso; no se acredita severidad crítica.

## P073

- Card: [cards/P073.md](cards/P073.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): server_installer.py:39; mcp_manager.py:753 — Se ejecuta npx --help mediante subprocess.run() dentro de una función asíncrona esperada directamente.
- Overstated: Sí — la comprobación no demuestra por sí sola impacto crítico.

## P063

- Card: [cards/P063.md](cards/P063.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): admin/router.py:107–119 — La ruta asíncrona ejecuta una actualización pip síncrona, bloqueando el event loop durante el proceso. El timeout de cinco minutos no lo evita.
- Overstated: No

## P103

- Card: [cards/P103.md](cards/P103.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): catalog.py:335–336; proxy/app.py:1427 — La actualización alcanzable crea tareas de precalentamiento sin guardar sus referencias.
- Overstated: Sí — el contexto muestra precalentamiento, sin acreditar impacto crítico.

## P040

- Card: [cards/P040.md](cards/P040.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): recorder/manager.py:190; app/main.py:60,150 — El arranque de grabación crea _monitor_process() descartando su tarea. Guardar el proceso FFmpeg no guarda el objeto Task.
- Overstated: No

## J047

- Card: [cards/J047.md](cards/J047.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): IngestionConsumer.java:83–86,271–284 — El listener espera cada publicación de fragmento con .get() sin timeout local; los retrasos pueden acumularse por documento.
- Overstated: No — el mensaje presenta los tiempos como valores por defecto.

## P089

- Card: [cards/P089.md](cards/P089.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): app/startup.py:395; app/main.py:35 — El arranque crea el watcher de limpieza y descarta su tarea.
- Overstated: Sí — no se ha comprobado que sus excepciones queden sin gestionar.

## J020

- Card: [cards/J020.md](cards/J020.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): UserBehaviorTrackingServiceImpl.java:68–77; BehaviorTrackingController.java:87 — Registra clics como telemetría independiente con REQUIRES_NEW; no se muestra necesidad de compartir la transacción del controlador.
- Overstated: Sí — confunde independencia transaccional con defecto.

## P094

- Card: [cards/P094.md](cards/P094.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): app/startup.py:400; app/main.py:35 — El evento de arranque descarta la tarea de subscription_scheduler(). Sus esperas internas no cambian el TP según v1.
- Overstated: Sí — no se demuestra la afirmación adicional sobre excepciones sin recuperar.

## J006

- Card: [cards/J006.md](cards/J006.md)
- Verdict: U
- FP condition: —
- Reason (file:line): BikeController.java:76–85 — Existe .block() en el handler, pero falta verificar el runtime WebFlux y la implementación de findBike() para confirmar el hilo y el comportamiento efectivo.
- Overstated: Sí — no se demuestra que lance IllegalStateException en cada llamada.

## P027

- Card: [cards/P027.md](cards/P027.md)
- Verdict: U
- FP condition: —
- Reason (file:line): services/jira.py:334,362 — La petición síncrona está confirmada, pero la búsqueda solo muestra un helper llamador. Falta comprobar si ese helper tiene una ruta de producción alcanzable.
- Overstated: Sí — el impacto sobre producción no está acreditado.

## P086

- Card: [cards/P086.md](cards/P086.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): app/startup.py:215,393 — El scheduler iniciado en producción descarta la tarea de importación cuando vence una tarea de recepción habilitada.
- Overstated: Sí — falta revisar la coroutine para afirmar que deja excepciones sin gestionar.

## J046

- Card: [cards/J046.md](cards/J046.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): IngestionConsumer.java:83–109 — La rama DELETE del listener espera el envío Kafka mediante .get() sin timeout local. Capturar errores después no limita la espera.
- Overstated: No

## P039

- Card: [cards/P039.md](cards/P039.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): processor.py:280,373 — El procesamiento asíncrono espera directamente una función que ejecuta pg_dump mediante subprocess.run(), con posible bloqueo prolongado.
- Overstated: No

## P100

- Card: [cards/P100.md](cards/P100.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): proxy/app.py:1366–1367,1427 — El endpoint crea la actualización de rutas descartando su tarea. _refreshing es un indicador, no una referencia al objeto Task.
- Overstated: Sí — no se acredita severidad crítica para esta actualización en segundo plano.

## P088

- Card: [cards/P088.md](cards/P088.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): app/startup.py:394; app/main.py:35 — El evento de arranque descarta la tarea de offline_completion_watcher().
- Overstated: Sí — no se ha comprobado la gestión interna de excepciones del watcher.

## P080

- Card: [cards/P080.md](cards/P080.md)
- Verdict: U
- FP condition: —
- Reason (file:line): integrations/gmail.py:336–348; contacts_routes/sync.py:269 — La paginación HTTP síncrona está confirmada. La búsqueda muestra su importación en la ruta, pero falta el código posterior para verificar si se espera directamente o se ejecuta fuera del event loop de la API.
- Overstated: Sí — no está confirmado el contexto efectivo de ejecución.

## J026

- Card: [cards/J026.md](cards/J026.md)
- Verdict: U
- FP condition: —
- Reason (file:line): SystemPreferencesService.java:228–233 — Falta revisar el publicador del evento para determinar si existe alguna dependencia de cambios sin confirmar. Los listeners y tests no prueban ese defecto.
- Overstated: Sí — la combinación de anotaciones no basta para establecerlo.

## J045

- Card: [cards/J045.md](cards/J045.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): OzoneMigrationWriterConsumer.java:65–69,111 — El listener espera el envío a Ozone mediante .block(), ocupando el hilo consumidor hasta que termina. La espera permite propagar fallos al contenedor.
- Overstated: Sí — un listener Kafka imperativo admite trabajo bloqueante; sin duración ni configuración adicionales no se justifica severidad crítica.

## J053

- Card: [cards/J053.md](cards/J053.md)
- Verdict: U
- FP condition: —
- Reason (file:line): AIDiagnosticServiceImpl.java:143–146; IngestionServiceImpl.java:156 — El worker relee el issue antes de guardar el diagnóstico. Falta verificar si la ingesta lo invoca antes de confirmar su creación; en ese caso podría no encontrarlo y perder el resultado.
- Overstated: Sí — la carrera es plausible, pero el fragmento del llamador no está disponible.

## J022

- Card: [cards/J022.md](cards/J022.md)
- Verdict: U
- FP condition: —
- Reason (file:line): UserBehaviorTrackingServiceImpl.java:106–119; OrderLifecycleServiceImpl.java:386 — El evento representa una reserva. Falta comprobar si se dispara antes del commit y si un rollback dejaría registrada una reserva inexistente; REQUIRES_NEW no resuelve esa cuestión semántica.
- Overstated: Sí — no se ha demostrado que ocurra esa inconsistencia.

## P033

- Card: [cards/P033.md](cards/P033.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): ws_client.py:876–882,654 — La conexión alcanzable crea _bg_sync() y descarta su tarea. La captura interna de excepciones no elimina el TP en v1.
- Overstated: Sí — las excepciones ordinarias de _do_sync() se capturan y registran explícitamente.

## J003

- Card: [cards/J003.md](cards/J003.md)
- Verdict: FP
- FP condition: context
- Reason (file:line): KafkaProducer.java:57–61 — El listener transaccional se ejecuta por defecto después del commit. El envío asíncrono no necesita participar en la transacción original ya finalizada.
- Overstated: Sí — presenta la separación posterior al commit como un fallo.

## P070

- Card: [cards/P070.md](cards/P070.md)
- Verdict: TP
- FP condition: —
- Reason (file:line): catalog_commands.py:116; plugin_info.json:27; mcp_catalog.jinja2:188 — El comando registrado ejecuta npx --version síncronamente dentro de una función asíncrona, sin timeout explícito.
- Overstated: Sí — el patrón es real, pero comprobar una versión no acredita por sí solo impacto crítico.

