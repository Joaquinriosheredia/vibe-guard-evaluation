# Review sheet — test-corpus-2

Joaquín's verdicts on 27 findings (`DEVIATIONS.md` §3a), in a random order. One block per finding.
Fill `Verdict` (TP, FP or U), `Reason (file:line)` and `Overstated` (Sí or No).
Rules: `REVIEW-GUIDE.md`. Any help received: `REVIEW-LOG.md`.

## P145

- Card: [cards/P145.md](cards/P145.md)
- Verdict: TP
- Reason (file:line): satellite/transport/ws_client.py:968 — asyncio.create_task() sin guardar la referencia
- Overstated: No

## J015

- Card: [cards/J015.md](cards/J015.md)
- Verdict: TP
- Reason (file:line): integration-tests/opentelemetry-quartz/.../Counter.java:26 — Thread.sleep(100) bloquea el hilo del @Scheduled
- Overstated: Sí

## P083

- Card: [cards/P083.md](cards/P083.md)
- Verdict: FP
- Reason (file:line): consortium/server/start_server.py:49 — open() síncrono solo en el arranque, antes de atender peticiones
- Overstated: No

## P099

- Card: [cards/P099.md](cards/P099.md)
- Verdict: FP
- Reason (file:line): mcps/custom/tts-mcp/live_smoke.py:54 — script de prueba manual, escritura secuencial al final
- Overstated: No

## P098

- Card: [cards/P098.md](cards/P098.md)
- Verdict: TP
- Reason (file:line): mcps/custom/transcribe-mcp/server.py:696 (también :657) — open() síncrono en handler async de un servidor MCP
- Overstated: Sí

## J038

- Card: [cards/J038.md](cards/J038.md)
- Verdict: TP
- Reason (file:line): .../service/impl/AsyncUtilServiceImpl.java:522 — @Async + @Transactional en el mismo método
- Overstated: Sí

## J056

- Card: [cards/J056.md](cards/J056.md)
- Verdict: FP
- Reason (file:line): api/.../azdevops/AzDevOpsPollingService.java:110 — join() deliberado con fixedDelay; el trabajo corre en pollExecutor
- Overstated: No

## P072

- Card: [cards/P072.md](cards/P072.md)
- Verdict: TP
- Reason (file:line): backend/storage/files.py:185 — lectura y hash síncronos en bucle dentro de async def, sin await
- Overstated: No

## P149

- Card: [cards/P149.md](cards/P149.md)
- Verdict: TP
- Reason (file:line): `satellite/transport/ws_client.py:981` — `asyncio.create_task(self.sm.stop_turn(msg))` descarta la referencia a la tarea; `_message_loop()` se ejecuta desde `main` en la línea 435.
- Overstated: No — la guía confirma el riesgo cuando no se conserva ninguna referencia, y la función se ejecuta en el funcionamiento normal de la aplicación.

## P127

- Card: [cards/P127.md](cards/P127.md)
- Verdict: TP
- Reason (file:line): `satellite/transport/lifecycle_update.py:188` ejecuta `subprocess.run()` dentro de `_self_uninstall_and_exit()`, una corrutina llamada mediante `await` desde `satellite/transport/ws_client.py:453` y `:834`, y mediante `asyncio.create_task()` en `:1083`; por tanto, puede bloquear el event loop durante el proceso.
- Overstated: No — el bloqueo es real, y `timeout=15` permite que la llamada síncrona lo mantenga bloqueado hasta 15 segundos.

## P002

- Card: [cards/P002.md](cards/P002.md)
- Verdict: FP
- Reason (file:line): `server/app/services/domain_dns.py:66–85` captura las excepciones DNS habituales (`NXDOMAIN`, `NoAnswer`, `NoNameservers` y `DNSException`), y las funciones `check_*` convierten el resultado `None` en `"error"`. No hay evidencia aportada de que un fallo normal de verificación propague una excepción hasta `asyncio.gather()`; los errores DNS contemplados se manejan internamente.
- Overstated: No — la regla describe correctamente el comportamiento de `gather()` si una tarea lanza una excepción, pero ese escenario no está demostrado para estos verificadores.

## P046

- Card: [cards/P046.md](cards/P046.md)
- Verdict: FP
- Reason (file:line): `backend/app/processing/ingest/tasks_common.py:23,227` importa `App` de `procrastinate` y define `task_app = App(...)`; `backend/app/processing/ingest/tasks_vrt.py:455–457` registra `ingest_vrt` en esa aplicación. El repo no contiene Celery, por lo que no se cumple el patrón específico que nombra PYVIBE-005.
- Overstated: Sí — atribuir el riesgo a la ausencia de límites de Celery en una tarea de Procrastinate no está justificado por esta regla; tampoco se ha demostrado que la tarea pueda colgarse indefinidamente.

## P161

- Card: [cards/P161.md](cards/P161.md)
- Verdict: TP
- Reason (file:line): `satellite/transport/ws_client.py:1045` descarta la referencia devuelta por `asyncio.create_task(self.sm.file_stat(msg, self))`. El registro `self.sm._pulls` y el callback de `:1035–1038` corresponden a otra rama (`file_pull`) y no retienen esta tarea `file_stat`.
- Overstated: No — la referencia a la tarea se descarta realmente; no hay evidencia aportada de que se almacene en otro lugar.

## P073

- Card: [cards/P073.md](cards/P073.md)
- Verdict: TP
- Reason (file:line): `backend/storage/files.py:208–212` ejecuta `open()` y lecturas síncronas dentro del generador asíncrono `open_read()`. `backend/storage/__init__.py:76` consume el generador mediante `async for` en código de producción, así que la E/S puede bloquear el event loop durante una petición.
- Overstated: No — el bloqueo síncrono está presente en el camino de ejecución de producción; no hay evidencia de que se ejecute en un hilo separado.

## J036

- Card: [cards/J036.md](cards/J036.md)
- Verdict: TP
- Reason (file:line): .../service/impl/AsyncUtilServiceImpl.java:463 — @Async + @Transactional en el mismo método
- Overstated: Sí

## P057

- Card: [cards/P057.md](cards/P057.md)
- Verdict: TP
- Reason (file:line): `database.py:2682` ejecuta `asyncio.gather()` sin `return_exceptions=True` ni un `try/except` envolvente. `_vector_search` deja sin capturar errores de adquisición y consultas en `:2727–2750`; `_keyword_search` tampoco captura excepciones y deja sin proteger operaciones como `conn.fetch` en `:3159–3217`. Un fallo normal de conexión o consulta puede propagarse mientras la otra corrutina continúa sin que se inspeccione su resultado.
- Overstated: No — las funciones contienen operaciones susceptibles de fallar y no capturan sus excepciones de forma general; el riesgo descrito por la regla es plausible y está respaldado por el código.

## P116

- Card: [cards/P116.md](cards/P116.md)
- Verdict: TP
- Reason (file:line): `proxy/core/layers/codex/app_server_client.py:172–174` descarta la referencia devuelta por `asyncio.create_task()` para `_drain_stderr()`. La función se define en `:368–401` y la búsqueda no encontró ningún registro, atributo o callback que retenga esa tarea. `satellite/sessions/cli_session.py:468` guarda otra tarea de otra clase, por lo que no cuenta como referencia a esta
- Overstated: No

## J001

- Card: [cards/J001.md](cards/J001.md)
- Verdict: FP
- Reason (file:line): study-spring-boot-zipkin/.../SampleBackground.java:41 — sleep aleatorio que simula latencia para trazas de Zipkin, proyecto didáctico
- Overstated: No

## J020

- Card: [cards/J020.md](cards/J020.md)
- Verdict: TP
- Reason (file:line): .../service/impl/AsyncUtilServiceImpl.java:85 — @Async + @Transactional en el mismo método
- Overstated: Sí

## P090

- Card: [cards/P090.md](cards/P090.md)
- Verdict: TP
- Reason (file:line): `mcps/custom/image-gen-mcp/server.py:573–576` abre `mask_path` con `open()` síncrono dentro de `_edit_openai()`, una corrutina que realiza la petición HTTP mediante `httpx.AsyncClient`. La línea `:569` abre también `image_path` de forma síncrona. `_edit_openai()` se invoca con `await` en `:697`, por lo que la E/S de apertura puede bloquear el event loop durante una petición.
- Overstated: No — las aperturas síncronas ocurren en el camino de ejecución asíncrono; el impacto concreto depende del tamaño y del almacenamiento de los archivos.

## P065

- Card: [cards/P065.md](cards/P065.md)
- Verdict: FP
- Reason (file:line): `backend/rag/retriever.py:318–336` recoge e inspecciona las excepciones del `gather` exterior, las registra y devuelve indicadores de fallo. Aunque `backend/textdb/bm25_search.py:348–403` deja propagar excepciones de operaciones internas, esas excepciones de `_keyword()` quedan recogidas y observadas por el `gather` exterior; no se demuestra que los resultados o excepciones posteriores de las búsquedas restantes queden sin observar.
- Overstated: Sí — el mensaje describe el riesgo del `gather` interior sin reflejar que el código envolvente recoge e inspecciona las excepciones de `_keyword()`

## P077

- Card: [cards/P077.md](cards/P077.md)
- Verdict: TP
- Reason (file:line): `consortium/client/commands/core_commands/rc.py:50–51` hace E/S síncrona con `open()` dentro de `RcCommand.run`; `base_interpreter.py:178–179` lo invoca mediante `await` desde el bucle asyncio del cliente, alcanzable en el funcionamiento normal.
- Overstated: No — el bloqueo del event loop es real; no hay evidencia de que el impacto descrito esté exagerado.

## J023

- Card: [cards/J023.md](cards/J023.md)
- Verdict: TP
- Reason (file:line): .../service/impl/AsyncUtilServiceImpl.java:155 — @Async + @Transactional en el mismo método
- Overstated: Sí

## P126

- Card: [cards/P126.md](cards/P126.md)
- Verdict: TP
- Reason (file:line): `satellite/transport/lifecycle_update.py:165–169` ejecuta `subprocess.run()` síncronamente con un timeout de hasta 15 segundos dentro de `_self_uninstall_and_exit`; las llamadas desde `satellite/transport/ws_client.py:453,834,1083` permiten alcanzar esta ruta desde el flujo asíncrono, por lo que puede bloquear el event loop.
- Overstated: No — el bloqueo potencial de hasta 15 segundos está respaldado por el código

## J052

- Card: [cards/J052.md](cards/J052.md)
- Verdict: TP
- Reason (file:line): .../service/impl/Process4CompleteUtilServiceImpl.java:299 — Thread.sleep(3000) en método @Async de producción
- Overstated: Sí

## P153

- Card: [cards/P153.md](cards/P153.md)
- Verdict: TP
- Reason (file:line): `satellite/transport/ws_client.py:1000–1002` crea una tarea para `self.sm.check_session_resumable(msg, self)` sin guardar su referencia ni adjuntar un callback que la retenga. `_message_loop` se invoca en el flujo principal en `ws_client.py:435`.
- Overstated: No — la referencia descartada está confirmada; que la tarea llegue a ser recolectada y cancelada es un riesgo potencial, no un resultado demostrado

## J021

- Card: [cards/J021.md](cards/J021.md)
- Verdict: TP
- Reason (file:line): .../service/impl/AsyncUtilServiceImpl.java:107 — @Async + @Transactional en el mismo método
- Overstated: Sí

