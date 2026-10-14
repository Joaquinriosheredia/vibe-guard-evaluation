# Blind sample — second review

20 CRITICAL findings drawn with `random.Random(20261015).sample` from the review set. No first-review verdict is shown.

For each: TP / FP / U by the criteria of PREREGISTRATION.md (review protocol), a one-line reason with file:line evidence, and message accuracy (overstated: yes/no).

## C003 · PYVIBE-009 · alikon-art/DeterminFlow

- Location: [`src/compression/post_processor.py:179`](https://github.com/alikon-art/DeterminFlow/blob/8ad6886303fe78b75bf8c1e37c5c3f0489d68145/src/compression/post_processor.py#L179) at `8ad6886303fe`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: FP
- Reason: 
- Message overstated: 

## C011 · PYVIBE-013 · Anil-matcha/open-agent-connector

- Location: [`server/app/providers/builtins/developer/hackernews.py:225`](https://github.com/Anil-matcha/open-agent-connector/blob/e857af1c737b1ef64965ffe19b87c99c055d8953/server/app/providers/builtins/developer/hackernews.py#L225) at `e857af1c737b`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: 
- Message overstated: 

## C017 · PYVIBE-012 · arvin341az-glitch/RVG

- Location: [`main.py:607`](https://github.com/arvin341az-glitch/RVG/blob/cdece8ea86d2bdda11530e9e6c27cfaa5f467ea7/main.py#L607) at `cdece8ea86d2`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: FP
- Reason: 
- Message overstated: 

## C026 · PYVIBE-012 · arvin341az-glitch/RVG

- Location: [`main.py:1141`](https://github.com/arvin341az-glitch/RVG/blob/cdece8ea86d2bdda11530e9e6c27cfaa5f467ea7/main.py#L1141) at `cdece8ea86d2`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: FP
- Reason: 
- Message overstated: 

## C027 · PYVIBE-012 · arvin341az-glitch/RVG

- Location: [`main.py:1465`](https://github.com/arvin341az-glitch/RVG/blob/cdece8ea86d2bdda11530e9e6c27cfaa5f467ea7/main.py#L1465) at `cdece8ea86d2`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: FP
- Reason: 
- Message overstated: 

## C086 · PYVIBE-007 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/indextts2_fal.py:87`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/indextts2_fal.py#L87) at `51cd2c4f833f`
- Message: subprocess.run() blocks the event loop for the entire subprocess duration
- Verdict: FP
- Reason: 
- Message overstated: 

## C092 · PYVIBE-009 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/nanobanana_grid.py:5260`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/nanobanana_grid.py#L5260) at `51cd2c4f833f`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: FP
- Reason: 
- Message overstated: 

## C093 · PYVIBE-009 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/nanobanana_grid.py:5505`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/nanobanana_grid.py#L5505) at `51cd2c4f833f`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: FP
- Reason: 
- Message overstated: 

## C097 · PYVIBE-009 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/nanobanana_grid.py:7204`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/nanobanana_grid.py#L7204) at `51cd2c4f833f`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: FP
- Reason: 
- Message overstated: 

## C103 · PYVIBE-009 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/generators/nanobanana_grid.py:7422`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/generators/nanobanana_grid.py#L7422) at `51cd2c4f833f`
- Message: open() performs synchronous file I/O — blocks the event loop
- Verdict: FP
- Reason: 
- Message overstated: 

## C124 · PYVIBE-013 · dramaclaw/dramaclaw

- Location: [`src/novelvideo/utils/bounded_concurrency.py:77`](https://github.com/dramaclaw/dramaclaw/blob/51cd2c4f833fc31e2167d3f06d144ee64d728c09/src/novelvideo/utils/bounded_concurrency.py#L77) at `51cd2c4f833f`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: 
- Message overstated: 

## C170 · PYVIBE-012 · Mafifrizi/ARES

- Location: [`ares/worker/controller.py:296`](https://github.com/Mafifrizi/ARES/blob/3e1a9dd5137cc778b19a0aae6cd4218853f4f603/ares/worker/controller.py#L296) at `3e1a9dd5137c`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: FP
- Reason: 
- Message overstated: 

## C171 · PYVIBE-012 · martian56/redcell

- Location: [`apps/api/app/routers/resources.py:472`](https://github.com/martian56/redcell/blob/01afb711829d31be7e82bef31d6edd4046d02ac0/apps/api/app/routers/resources.py#L472) at `01afb711829d`
- Message: asyncio.create_task() return value discarded — task may be GC'd and silently cancelled
- Verdict: FP
- Reason: 
- Message overstated: 

## C180 · PYVIBE-013 · Pipelex/pipelex

- Location: [`pipelex/providers/mistral/mistral_factory.py:85`](https://github.com/Pipelex/pipelex/blob/284ec40840493d7b9f0443746961feff9ac57603/pipelex/providers/mistral/mistral_factory.py#L85) at `284ec4084049`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: 
- Message overstated: 

## C184 · PYVIBE-013 · Pipelex/pipelex

- Location: [`wip/judgment-family/spike/typesafe_followups_spike.py:109`](https://github.com/Pipelex/pipelex/blob/284ec40840493d7b9f0443746961feff9ac57603/wip/judgment-family/spike/typesafe_followups_spike.py#L109) at `284ec4084049`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: 
- Message overstated: 

## C203 · PYVIBE-013 · SenteLabsAI/OpenExecutive

- Location: [`packages/core/openexecutive/orchestrator/router.py:445`](https://github.com/SenteLabsAI/OpenExecutive/blob/5541ed062d2579a4764afb3681b766a1b0543478/packages/core/openexecutive/orchestrator/router.py#L445) at `5541ed062d25`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: 
- Message overstated: 

## C208 · PYVIBE-013 · skygazer42/MimirQ

- Location: [`app/rag/engine_support/standard_stream_retrieval.py:199`](https://github.com/skygazer42/MimirQ/blob/5d08b54beb8011a17ce274319fb79a5f121568c9/app/rag/engine_support/standard_stream_retrieval.py#L199) at `5d08b54beb80`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: 
- Message overstated: 

## C220 · PYVIBE-013 · skygazer42/MimirQ

- Location: [`app/services/rag_runtime_warmup.py:324`](https://github.com/skygazer42/MimirQ/blob/5d08b54beb8011a17ce274319fb79a5f121568c9/app/services/rag_runtime_warmup.py#L324) at `5d08b54beb80`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: 
- Message overstated: 

## C231 · PYVIBE-013 · yaojingang/GEORank

- Location: [`backend/app/web/company_pages.py:1867`](https://github.com/yaojingang/GEORank/blob/424a0cf92b37ad63c94ae9dc6f39745189ab7c94/backend/app/web/company_pages.py#L1867) at `424a0cf92b37`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: 
- Message overstated: 

## C240 · PYVIBE-013 · zrt-ai-lab/ViNote

- Location: [`backend/services/content_summarizer.py:280`](https://github.com/zrt-ai-lab/ViNote/blob/e8e46a144caa718eb85bf053619892fc261fc1f9/backend/services/content_summarizer.py#L280) at `e8e46a144caa`
- Message: asyncio.gather() without return_exceptions=True: if one awaitable raises, gather re-raises it and the others keep running with nobody observing their results or later exceptions
- Verdict: FP
- Reason: 
- Message overstated: 
