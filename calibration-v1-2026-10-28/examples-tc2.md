# Examples — test-corpus-2 only, with Joaquín's verdict and reason (verbatim)

Source: `test-corpus-2/audit-joaquin.json` and `test-corpus-2/cards/`. No test-corpus-3 case is used here.
The criterion numbers are those of `REVIEW-CRITERIA.md` v1 that the reason applies.

## J052 · blocking · risesoft-y9/WorkFlow-Engine

- Location: `y9-module-processadmin/risenet-y9boot-support-processadmin/src/main/java/net/risesoft/service/impl/Process4CompleteUtilServiceImpl.java:299`
- Message: Thread.sleep() detected in @Async method
- Verdict: **TP** (Overstated)
- Criteria (v1): §2.1, §5
- Reason (Joaquín): .../service/impl/Process4CompleteUtilServiceImpl.java:299 — Thread.sleep(3000) en método @Async de producción

## J015 · blocking · quarkusio/quarkus

- Location: `integration-tests/opentelemetry-quartz/src/main/java/io/quarkus/it/opentelemetry/quartz/Counter.java:26`
- Message: Thread.sleep() detected in @Scheduled method
- Verdict: **TP** (Overstated)
- Criteria (v1): §2.3, §5
- Reason (Joaquín): integration-tests/opentelemetry-quartz/.../Counter.java:26 — Thread.sleep(100) bloquea el hilo del @Scheduled

## P073 · PYVIBE-009 · MoMoM101/RAG-ReActAgent

- Location: `backend/storage/files.py:210`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: **TP**
- Criteria (v1): §2.1, §5
- Reason (Joaquín): `backend/storage/files.py:208–212` ejecuta `open()` y lecturas síncronas dentro del generador asíncrono `open_read()`. `backend/storage/__init__.py:76` consume el generador mediante `async for` en código de producción, así que la E/S puede bloquear el event loop durante una petición.

## P126 · PYVIBE-007 · OtoDock/oto-dock

- Location: `satellite/transport/lifecycle_update.py:165`
- Message: subprocess.run() blocks the event loop for the entire subprocess duration
- Verdict: **TP**
- Criteria (v1): §2.2, §5
- Reason (Joaquín): `satellite/transport/lifecycle_update.py:165–169` ejecuta `subprocess.run()` síncronamente con un timeout de hasta 15 segundos dentro de `_self_uninstall_and_exit`; las llamadas desde `satellite/transport/ws_client.py:453,834,1083` permiten alcanzar esta ruta desde el flujo asíncrono, por lo que puede bloquear el event loop.

## P083 · PYVIBE-009 · not-sekiun/Consortium

- Location: `consortium/server/start_server.py:49`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: **FP**
- Criteria (v1): §2.2, §5
- Reason (Joaquín): consortium/server/start_server.py:49 — open() síncrono solo en el arranque, antes de atender peticiones

## P099 · PYVIBE-009 · OtoDock/oto-dock

- Location: `mcps/custom/tts-mcp/live_smoke.py:54`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: **FP**
- Criteria (v1): §2.3
- Reason (Joaquín): mcps/custom/tts-mcp/live_smoke.py:54 — script de prueba manual, escritura secuencial al final

## P065 · PYVIBE-013 · MoMoM101/RAG-ReActAgent

- Location: `backend/rag/retriever.py:308`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: **FP** (Overstated)
- Criteria (v1): §5
- Reason (Joaquín): `backend/rag/retriever.py:318–336` recoge e inspecciona las excepciones del `gather` exterior, las registra y devuelve indicadores de fallo. Aunque `backend/textdb/bm25_search.py:348–403` deja propagar excepciones de operaciones internas, esas excepciones de `_keyword()` quedan recogidas y observadas por el `gather` exterior; no se demuestra que los resultados o excepciones posteriores de las búsquedas restantes queden sin observar.
