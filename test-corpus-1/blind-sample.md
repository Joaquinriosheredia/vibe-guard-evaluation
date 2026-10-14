# Blind sample — second review

20 CRITICAL findings drawn with `random.Random(20261015).sample` from the review set. No first-review verdict is shown.

For each: TP / FP / U by the criteria of PREREGISTRATION.md (review protocol), a one-line reason with file:line evidence, and message accuracy (overstated: yes/no).

## C003 · PYVIBE-009 · alikon-art/DeterminFlow

- Location: [`src/compression/post_processor.py:179`](https://github.com/alikon-art/DeterminFlow/blob/8ad6886303fe78b75bf8c1e37c5c3f0489d68145/src/compression/post_processor.py#L179) at `8ad6886303fe`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: TP
- Reason: open() síncrono en async def _read_file_content (src/compression/post_processor.py:154/179), awaited desde process (:60), usado por scheduler.py:159; sin to_thread. Lectura limitada a 1 MB (:175).
- Message overstated: No

## C011 · PYVIBE-013 · Anil-matcha/open-agent-connector

- Location: [`server/app/providers/builtins/developer/hackernews.py:225`](https://github.com/Anil-matcha/open-agent-connector/blob/e857af1c737b1ef64965ffe19b87c99c055d8953/server/app/providers/builtins/developer/hackernews.py#L225) at `e857af1c737b`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: Las tareas de :225 son _build_tree; su única E/S es _fetch_firebase_item, que captura todo con try/except Exception (hackernews.py:159–167); sin fallo normal no capturado.
- Message overstated: No

## C017 · PYVIBE-012 · arvin341az-glitch/RVG

- Location: [`main.py:607`](https://github.com/arvin341az-glitch/RVG/blob/cdece8ea86d2bdda11530e9e6c27cfaa5f467ea7/main.py#L607) at `cdece8ea86d2`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: TP
- Reason: asyncio.create_task(mtproto.stop_instance(uuid)) en async def _update_mtproto_ad_tag (main.py:563/607) sin guardar referencia; ningún registro de tareas ni add_done_callback en main.py.
- Message overstated: No

## C026 · PYVIBE-012 · arvin341az-glitch/RVG

- Location: [`main.py:1141`](https://github.com/arvin341az-glitch/RVG/blob/cdece8ea86d2bdda11530e9e6c27cfaa5f467ea7/main.py#L1141) at `cdece8ea86d2`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: TP
- Reason: asyncio.create_task(save_state()) en endpoint POST /api/subs/{sub_id}/links (main.py:1122/1141) sin guardar referencia.
- Message overstated: No

## C027 · PYVIBE-012 · arvin341az-glitch/RVG

- Location: [`main.py:1465`](https://github.com/arvin341az-glitch/RVG/blob/cdece8ea86d2bdda11530e9e6c27cfaa5f467ea7/main.py#L1465) at `cdece8ea86d2`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: TP
- Reason: asyncio.create_task(save_state()) en endpoint POST /api/mtproto/fix-proxy (main.py:1417/1465) sin guardar referencia.
- Message overstated: No

## C086 · PYVIBE-007 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/indextts2_fal.py:87`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/indextts2_fal.py#L87) at `51cd2c4f833f`
- Message: subprocess.run() blocks the event loop for the entire subprocess duration
- Verdict: TP
- Reason: subprocess.run(ffprobe) sin timeout en async def _audio_duration_seconds (indextts2_fal.py:85/87), awaited desde generate/_generate_via_fal (:361, :456), ejecutado por el backend de tareas; sin to_thread ni executor.
- Message overstated: No

## C092 · PYVIBE-009 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/nanobanana_grid.py:5260`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/nanobanana_grid.py#L5260) at `51cd2c4f833f`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: TP
- Reason: open() en async def generate_grid (nanobanana_grid.py:4381/5260), llamado desde task_backend/runners/sketch.py:542/585 y director_world/control_frame_to_sketch.py:608; sin to_thread.
- Message overstated: No

## C093 · PYVIBE-009 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/nanobanana_grid.py:5505`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/nanobanana_grid.py#L5505) at `51cd2c4f833f`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: FP
- Reason: generate_action_grid (nanobanana_grid.py:5298/5505) solo se llama desde tests/test_p0g4k_grid_family_image_egress.py:320; no alcanzable en producción.
- Message overstated: No

## C097 · PYVIBE-009 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/nanobanana_grid.py:7204`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/nanobanana_grid.py#L7204) at `51cd2c4f833f`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: FP
- Reason: _render_single_panel_gemini (nanobanana_grid.py:7160/7204) solo lo llama _generate_render_from_sketch (:7102), que no tiene llamadores en el repositorio: código muerto.
- Message overstated: No

## C103 · PYVIBE-009 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/nanobanana_grid.py:7422`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/nanobanana_grid.py#L7422) at `51cd2c4f833f`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: FP
- Reason: upscale_with_nanobanana (nanobanana_grid.py:7312/7422) solo se llama desde tests/test_p0g4k_grid_family_image_egress.py:341; no alcanzable en producción.
- Message overstated: No

## C124 · PYVIBE-013 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/utils/bounded_concurrency.py:77`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/utils/bounded_concurrency.py#L77) at `51cd2c4f833f`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: gather recibe run(item), que captura toda excepción de worker(item) y devuelve None (bounded_concurrency.py:65–74); cada tarea contiene sus excepciones.
- Message overstated: No

## C170 · PYVIBE-012 · Mafifrizi/ARES

- Location: [`ares/worker/controller.py:296`](https://github.com/Mafifrizi/ARES/blob/3e1a9dd5137cc778b19a0aae6cd4218853f4f603/ares/worker/controller.py#L296) at `3e1a9dd5137c`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: FP
- Reason: create_task sin referencia en _dispatch_loop (ares/worker/controller.py:296), pero WorkerController no se instancia en ningún punto del repo (solo un comentario en artifact_intel/engine.py:22): no alcanzable.
- Message overstated: No

## C171 · PYVIBE-012 · martian56/redcell

- Location: [`apps/api/app/routers/resources.py:472`](https://github.com/martian56/redcell/blob/01afb711829d31be7e82bef31d6edd4046d02ac0/apps/api/app/routers/resources.py#L472) at `01afb711829d`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: TP
- Reason: asyncio.create_task(_answer_chat(...)) sin referencia en endpoint POST /runs/{rid}/chat (apps/api/app/routers/resources.py:459/472); router registrado en apps/api/app/main.py:63.
- Message overstated: No

## C180 · PYVIBE-013 · Pipelex/pipelex

- Location: [`pipelex/providers/mistral/mistral_factory.py:85`](https://github.com/Pipelex/pipelex/blob/284ec40840493d7b9f0443746961feff9ac57603/pipelex/providers/mistral/mistral_factory.py#L85) at `284ec4084049`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: TP
- Reason: gather de make_mistral_image_url (mistral_factory.py:85/95) → prepare_prompt_image (cogt/image/prompt_image_utils.py:30) hace HTTP/disco/storage sin try; un fallo de red propaga y las demás tareas siguen sin observarse.
- Message overstated: No

## C184 · PYVIBE-013 · Pipelex/pipelex

- Location: [`wip/judgment-family/spike/typesafe_followups_spike.py:109`](https://github.com/Pipelex/pipelex/blob/284ec40840493d7b9f0443746961feff9ac57603/wip/judgment-family/spike/typesafe_followups_spike.py#L109) at `284ec4084049`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: Script experimental en wip/judgment-family/spike/ ejecutado a mano (docstring :1–10); ningún código lo importa; no es producción.
- Message overstated: No

## C203 · PYVIBE-013 · SenteLabsAI/OpenExecutive

- Location: [`packages/core/openexecutive/orchestrator/router.py:445`](https://github.com/SenteLabsAI/OpenExecutive/blob/5541ed062d2579a4764afb3681b766a1b0543478/packages/core/openexecutive/orchestrator/router.py#L445) at `5541ed062d25`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: _retrieve_for_call (router.py:278) y _retrieve_failures_for_call (:310) capturan con try/except Exception las excepciones de sus operaciones de recuperación y devuelven ""; get_settings() queda fuera de esos bloques, sin evidencia de que falle en condiciones normales.
- Message overstated: No

## C208 · PYVIBE-013 · skygazer42/MimirQ

- Location: [`app/rag/engine_support/standard_stream_retrieval.py:199`](https://github.com/skygazer42/MimirQ/blob/5d08b54beb8011a17ce274319fb79a5f121568c9/app/rag/engine_support/standard_stream_retrieval.py#L199) at `5d08b54beb80`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: TP
- Reason: _run_stream_retrieval_query (app/rag/engine.py:214) relanza RetrievalAdmissionTimeoutError (rag_runtime_limiter.py:317/342, 503 por saturación bajo carga); gather en standard_stream_retrieval.py:199 la propaga y las demás búsquedas siguen.
- Message overstated: No

## C220 · PYVIBE-013 · skygazer42/MimirQ

- Location: [`app/services/rag_runtime_warmup.py:324`](https://github.com/skygazer42/MimirQ/blob/5d08b54beb8011a17ce274319fb79a5f121568c9/app/services/rag_runtime_warmup.py#L324) at `5d08b54beb80`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: Ambas sondas capturan TimeoutError y Exception y devuelven estado failed (rag_runtime_warmup.py:159, :253); gather en :324 durante el calentamiento al arrancar.
- Message overstated: No

## C231 · PYVIBE-013 · yaojingang/GEORank

- Location: [`backend/app/web/company_pages.py:1867`](https://github.com/yaojingang/GEORank/blob/424a0cf92b37ad63c94ae9dc6f39745189ab7c94/backend/app/web/company_pages.py#L1867) at `424a0cf92b37`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: TP
- Reason: rank_similar_companies (company_retrieval.py:213) llama a fallback_similar_companies (:181) fuera del try, con consulta a BD sin captura; un fallo de BD propaga desde gather (company_pages.py:1867) en endpoint GET /companies/{id}.
- Message overstated: No

## C240 · PYVIBE-013 · zrt-ai-lab/ViNote

- Location: [`backend/services/content_summarizer.py:280`](https://github.com/zrt-ai-lab/ViNote/blob/e8e46a144caa718eb85bf053619892fc261fc1f9/backend/services/content_summarizer.py#L280) at `e8e46a144caa`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: merge_group → _integrate_chunk_summaries (content_summarizer.py:208) captura los fallos del LLM y devuelve el texto original; los grupos están acotados por smart_chunk_text; gather en :280.
- Message overstated: No
