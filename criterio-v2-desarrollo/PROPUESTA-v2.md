# Evaluación de desarrollo con REVIEW-CRITERIA v2: etiquetas propuestas

**Evaluación asistida de desarrollo.** Claude propone la etiqueta v2 de cada caso y su razón; Joaquín la confirma o corrige. No es una revisión ciega ni sustituye a ningún resultado publicado: TC2–TC4 conservan sus veredictos, métricas y conclusiones. Criterio: `../REVIEW-CRITERIA-v2.md`. Esta propuesta no calcula tasas por regla: la selección (C) va después de tu confirmación.

## Registro

- **2026-11-03, primera propuesta:** 101 casos de TC2–TC4 (PYVIBE-012, `blocking`, PYVIBE-009).
- **2026-11-03, correcciones de Joaquín a B, aplicadas aquí:**
  - **Población de selección:** solo TC3 + TC4; TC2 queda como ejemplos auxiliares.
  - **TC2 J015:** FP por contexto; es un fixture y no se incumple ninguna propiedad. No se usan los 25 hilos de Quartz como prueba.
  - **TC3 J001:** FP por contexto. Un cron fija activaciones, no un SLA; solo sería TP con una obligación de plazo o frescura en el repositorio.
  - **TC2 J001:** FP por contexto. La exclusión de repositorios de estudio es una regla de triaje, no la razón del veredicto.
  - **TC2 J052:** TP solo con una contención plausible apoyada en código; U si falta configuración decisiva; FP si el contexto demuestra que no se incumple nada. Revisado: U.
  - **TC3 P026:** TP por contrato.
  - **PYVIBE-012:** dos campos por caso, (a) contrato y (b) fallo funcional respaldado por código. Para CRITICAL cuenta (b). Revisados los 65 casos uno a uno.
- **2026-11-03, decisiones de Joaquín sobre las segundas opiniones de Codex, aplicadas en `REVIEW-CRITERIA-v2.md` y aquí:**
  - **J056:** comprobado que el `join()` tiene cota y que no hay plazo exigido, así que es FP.
  - **Frontera FP/U:** FP solo si el repositorio demuestra que no se incumple nada; U si falta configuración decisiva. Con esta regla se re-evaluaron TC2 J001, TC2 J015 y TC3 J001.
  - **Cadencias:** la cadencia del propio job no es una propiedad sin un plazo exigido.
  - **`transactions`:** opción (a).
  - **J053:** pasa de U a TP.
  - **`kafka-send-timeout`:** comprobado en TC3 J017.
  - **Celery:** solo un límite duro.
  - **§2:** la confirmación CRITICAL remite al pre-registro de TC5.

## 1. Población de selección (declarada)

Todos los casos con tu veredicto en **TC3 + TC4**. TC3 y TC4 no comparten ninguna ubicación ni ningún repositorio. TC2 no entra en la selección; solo aporta ejemplos auxiliares.

| Regla | n | Repos | Máx. por repo | ¿Candidata? (n ≥ 15 y ≥ 5 repos) |
|---|---|---|---|---|
| PYVIBE-012 | 60 | 21 | 12 | **sí** |
| transactions | 39 | 16 | 10 | no: WARNING como máximo (v2 §3) |
| blocking | 14 | 8 | 2 | no |
| PYVIBE-009 | 12 | 4 | 9 | no |
| PYVIBE-002 | 11 | 2 | 10 | no |
| PYVIBE-007 | 11 | 2 | 10 | no |
| PYVIBE-018 | 10 | 6 | 3 | no |
| kafka-send-timeout | 8 | 2 | 6 | no |
| PYVIBE-017 | 4 | 3 | 2 | no |
| PYVIBE-006 | 3 | 3 | 1 | no |
| reactor-block | 3 | 1 | 3 | no |
| PYVIBE-010 | 3 | 2 | 2 | no |
| PYVIBE-016 | 3 | 3 | 1 | no |
| PYVIBE-014 | 2 | 2 | 1 | no |
| PYVIBE-008 | 1 | 1 | 1 | no |
| blocking-kafka | 1 | 1 | 1 | no |

**La única regla candidata es PYVIBE-012.** n por repo en la población:

| Repo | n |
|---|---|
| xianer235/115-media-hub | 12 |
| yujian0815/fnmedia-ext | 7 |
| AndrewCTF/velocity | 6 |
| phucnguyentvp1/frameweaver | 4 |
| runvnc/mindroot | 4 |
| crane-in-clear-sky/WorkWit-AI-Agent | 3 |
| dameng2026/xianyu-pilot | 3 |
| foodpm/timecut | 3 |
| hzy1522/tickflow-stock-panel | 3 |
| HyxiaoGe/fusion | 2 |
| asfaraguest/tatap | 2 |
| liyupi/yu-ai-learn | 2 |
| Deen-Bridge/dnb-ai | 1 |
| SpillwaveSolutions/agent-brain | 1 |
| TNT-Likely/BeeCount-Cloud | 1 |
| antiv/mate | 1 |
| apowerb/apowerb | 1 |
| jacebrowning/memegen | 1 |
| ljxpython/ai-agent-platform | 1 |
| metalogico/issued | 1 |
| riteshbonthalakoti/HELPDESK.AI | 1 |

## 2. PYVIBE-012: dos campos por caso

- **(a) Contrato:** se incumple la recomendación de retención de `asyncio.create_task` (no se conserva ninguna referencia). El veredicto v2 por contrato es TP cuando (a) es sí y la ruta es alcanzable; es la etiqueta que ya tenías, salvo P026 (FP → TP) y P058 (U).
- **(b) Fallo funcional respaldado por código: sí / no / U** (`REVIEW-CRITERIA-v2.md` §3). Revisado leyendo el cuerpo de cada corrutina lanzada y lo que llama. **Para la selección CRITICAL cuenta (b).**

### 2.1 Población (TC3 + TC4), primero los que tienen (b) = sí o U

| Corpus | ID | Repo | Original | v1 | v2 | (a) contrato | (b) fallo funcional | Razón de (b) |
|---|---|---|---|---|---|---|---|---|
| TC4 | P004 | AndrewCTF/velocity | TP | TP | TP | sí | **sí** | `_run_job` atrapa los fallos de `mkdir` y de la descarga, pero no los de `_verify_sha256`, el cálculo de tamaño ni `_write_metadata` (`apps/api/app/localllm/manager.py:531,551–558`). Un `OSError` ahí (disco lleno, fichero ilegible) deja `job.status` en `"verifying"` para siempre, y nadie observa la excepción porque la tarea no se conserva (`:628`). |
| TC4 | P040 | foodpm/timecut | TP | TP | TP | sí | **sí** | `_monitor_process` es la recuperación automática de la grabación: reinicia con `await self.start()` (`app/recorder/manager.py:255,261`). `start()` pone `self._running = True` antes de `_ensure_dirs()` y `create_subprocess_exec` (`:151,171–176`), y nada de eso está en `try`. Si lanzan, la excepción muere dentro de la tarea descartada (`:190`): la grabación queda parada con el indicador `_running = True` y nadie lo sabe. |
| TC4 | P058 | riteshbonthalakoti/HELPDESK.AI | U | U | U | sí (patrón presente; alcanzabilidad no demostrada) | **U** | No se demuestra que la aplicación use esta copia vendorizada en `.tmp-ci-venv` (`.tmp-ci-venv/Lib/site-packages/realtime/_async/channel.py:247`), así que tampoco se puede respaldar ningún fallo funcional. |
| TC4 | P066 | runvnc/mindroot | TP | TP | TP | sí | **sí** | `run_command` lanza `handle_cmds` y vuelve (`src/mindroot/coreplugins/agent/agent.py:929–936`). Antes de su `try`, `handle_cmds` guarda el mensaje en el chat log, que escribe en disco (`:268`; `src/mindroot/lib/chatlog.py`, `add_message_async` → `_save_log_async`). Si eso lanza, el comando pedido no se ejecuta y nadie se entera. Caso límite: depende de un fallo de E/S de disco. |
| TC4 | P087 | xianer235/115-media-hub | TP | TP | TP | sí | **sí** | `monitor_scheduler` es el planificador de las tareas de monitorización, y solo protege dos pasos (`app/startup.py:173–176,229–234`). `pending_offline_job_counts_by_monitor()`, que lista los trabajos de recursos de la base de datos (`app/services/resource.py:117–119,138–144`), está fuera de `try` (`app/startup.py:184–186`). Un fallo de la base de datos mata el bucle, y ninguna tarea programada vuelve a ejecutarse. Como la tarea no se conserva (`:393`), nadie lo nota. |
| TC4 | P096 | xianer235/115-media-hub | TP | TP | TP | sí | **sí** | `memory_housekeeper` no tiene `try` (`app/startup.py:379–385`), y `cleanup_completed_monitor_change_events` abre la base de datos y ejecuta un `DELETE` sin protección (`app/services/monitor_changes.py:2414–2425`). Un fallo de la base de datos mata el bucle: las cachés y los eventos dejan de podarse y la memoria crece, sin que nadie lo vea porque la tarea no se conserva (`app/startup.py:402`). |
| TC3 | P005 | apowerb/apowerb | TP | TP | TP | sí | **no** | `memory_retention_loop` contiene sus excepciones en cada pasada y sigue (`src/apowerb/memory/retention.py:24–31`); espera `asyncio.sleep`, referenciado por el loop. |
| TC3 | P020 | Deen-Bridge/dnb-ai | TP | TP | TP | sí | **no** | Todo el cuerpo está en `try/except Exception` con log (`main.py:2526,2540–2541`); solo espera E/S de `session_store`. |
| TC3 | P026 | hzy1522/tickflow-stock-panel | FP | TP | TP | sí | **no** | El cuerpo atrapa `Exception`, marca `job_store.fail` y libera el slot en `finally` (`backend/app/api/kline.py:957–1007`): el estado del trabajo queda coherente. |
| TC3 | P027 | hzy1522/tickflow-stock-panel | TP | TP | TP | sí | **no** | Igual: `job_store.fail` en `except` y `release_run_slot` en `finally` (`backend/app/api/kline.py:1143–1162`). |
| TC3 | P028 | hzy1522/tickflow-stock-panel | TP | TP | TP | sí | **no** | Igual: `job_store.fail` en `except` y `release_run_slot` en `finally` (`backend/app/api/kline.py:1233–1249`). |
| TC4 | P005 | AndrewCTF/velocity | TP | TP | TP | sí | **no** | Precalentamiento opcional: `_get_catalog` pasa por `cache.get_or_fetch` (`apps/api/app/routes/cams.py:170–182`) y la ruta lo vuelve a pedir bajo demanda; si falla, solo queda frío. |
| TC4 | P006 | AndrewCTF/velocity | TP | TP | TP | sí | **no** | `warm_basemap` atrapa el fallo de cada tesela (`apps/api/app/routes/tiles.py:243–246`); precalentamiento. |
| TC4 | P007 | AndrewCTF/velocity | TP | TP | TP | sí | **no** | Precalentamiento: si `apple_maps.session()` falla aquí, la sesión se vuelve a pedir bajo demanda con reintento (`apps/api/app/apple_maps.py:175,209`). |
| TC4 | P008 | AndrewCTF/velocity | TP | TP | TP | sí | **no** | `_prewarm` atrapa todo (`apps/api/app/mcp_server.py:282–286`); solo precalienta. |
| TC4 | P009 | AndrewCTF/velocity | TP | TP | TP | sí | **no** | `_pipeline` y `_pipeline_mapany` envuelven todo en `try/except Exception` y marcan `job["status"] = "error"` (`apps/api/app/routes/recon.py:419,511` y `:276,297–300`); la espera de `_GPU_LOCK` queda referenciada por el lock global. |
| TC4 | P012 | antiv/mate | TP | TP | TP | sí | **no** | `_cleanup_loop` espera `asyncio.sleep` y atrapa el fallo de cerrar cada sesión (`shared/utils/tools/browser_tools.py:235–251`); no hay una ruta normal que mate el bucle. |
| TC4 | P014 | asfaraguest/tatap | TP | TP | TP | sí | **no** | Prefetch de traducción de subtítulos: si falla, la petición real la hace bajo demanda (`android/app/src/main/python/backend/main.py:2343–2371`); el future interno queda en `_SUB_INFLIGHT`. |
| TC4 | P016 | asfaraguest/tatap | TP | TP | TP | sí | **no** | Mismo prefetch de traducción que P014 (`backend/main.py:2343–2371`): si falla, la petición real lo hace bajo demanda. |
| TC4 | P029 | crane-in-clear-sky/WorkWit-AI-Agent | TP | TP | TP | sí | **no** | `run_automation` atrapa `Exception`, registra la ejecución como `"error"` y libera `_RUNNING` en `finally` (`workwit/backend/automation_runner.py:86,129–133`). |
| TC4 | P030 | crane-in-clear-sky/WorkWit-AI-Agent | TP | TP | TP | sí | **no** | `scheduler_loop` atrapa cada pasada y espera `asyncio.sleep` (`workwit/backend/automation_runner.py:138–156`). |
| TC4 | P031 | crane-in-clear-sky/WorkWit-AI-Agent | TP | TP | TP | sí | **no** | La misma `run_automation` que P029: registra el error y libera `_RUNNING` (`workwit/backend/automation_runner.py:129–133`). |
| TC4 | P032 | dameng2026/xianyu-pilot | TP | TP | TP | sí | **no** | `_background_refresh_account` atrapa todo con log (`apps/api/app/services/rate_service.py:1476–1484`); solo recalibra datos que se vuelven a sincronizar. |
| TC4 | P033 | dameng2026/xianyu-pilot | TP | TP | TP | sí | **no** | `_bg_sync` atrapa todo con log (`apps/api/app/services/ws_client.py:876–880`). |
| TC4 | P034 | dameng2026/xianyu-pilot | TP | TP | TP | sí | **no** | `relist_sold_item` atrapa todo con log y su propia sesión hace `rollback` (`apps/api/app/services/relist_service.py:456–491`). |
| TC4 | P041 | foodpm/timecut | TP | TP | TP | sí | **no** | `run_diary_for_date` envuelve la generación en `try/except Exception` con log (`app/diary/generator.py:28–38`). |
| TC4 | P042 | foodpm/timecut | TP | TP | TP | sí | **no** | El callback registrado (`app/main.py:177–182`) llega a `_run_highlight`, que atrapa `Exception` y cierra el trabajo con `job.finish(False, …)` (`app/highlighter/scheduler.py:144–146`). |
| TC4 | P043 | HyxiaoGe/fusion | TP | TP | TP | sí | **no** | `_parse_file_with_llm` atrapa todo y marca el fichero como error con `_mark_file_error` (`backend/app/services/file_service.py:728,755–760`). |
| TC4 | P044 | HyxiaoGe/fusion | TP | TP | TP | sí | **no** | La misma `_parse_file_with_llm` que P043 (`backend/app/services/file_service.py:755–760`). |
| TC4 | P046 | jacebrowning/memegen | TP | TP | TP | sí | **no** | `track` solo envía analítica a un rastreador remoto (`app/utils/meta.py:109–140`); si falla, no cambia ninguna respuesta ni ningún estado funcional. |
| TC4 | P049 | liyupi/yu-ai-learn | TP | TP | TP | sí | **no** | `_process_document` atrapa `Exception` y marca el documento `"failed"` (`backend/app/services/knowledge_service.py:74,89–93`). |
| TC4 | P050 | liyupi/yu-ai-learn | TP | TP | TP | sí | **no** | `_run_quiz_task` atrapa `Exception` y marca la tarea `"failed"` (`backend/app/services/quiz_service.py:166,214–218`). |
| TC4 | P051 | ljxpython/ai-agent-platform | TP | TP | TP | sí | **no** | `_cleanup` atrapa los fallos de `_reap` y de `docker rm` (`apps/runtime-service/src/runtime_service/workspace/execution.py:28–38,105–108`) y devuelve el resultado. |
| TC4 | P053 | metalogico/issued | TP | TP | TP | sí | **no** | `_print_startup_messages` solo escribe mensajes de log (`server/opds/__init__.py:53–64`). |
| TC4 | P054 | phucnguyentvp1/frameweaver | TP | TP | TP | sí | **no** | `_sync_tier` atrapa `Exception` y libera `_sync_in_progress` en `finally` (`agent/services/flow_client.py:294–310`). |
| TC4 | P055 | phucnguyentvp1/frameweaver | TP | TP | TP | sí | **no** | La misma `_sync_tier` que P054 (`agent/services/flow_client.py:294–310`). |
| TC4 | P056 | phucnguyentvp1/frameweaver | TP | TP | TP | sí | **no** | Si `_refresh_media_urls` falla (`agent/services/flow_client.py:318–362`), solo se pierde una actualización oportunista de URLs firmadas. La extensión la reenvía cada vez que captura URLs nuevas (`extension/background.js:910–922`), así que no queda ningún estado bloqueado. |
| TC4 | P057 | phucnguyentvp1/frameweaver | TP | TP | TP | sí | **no** | `_run_one` libera el límite y `_active_ids` en `finally` (`agent/worker/processor.py:163–172`), y `_process_one` atrapa `Exception` y llama a `_handle_failure` (`:280,302–305`). |
| TC4 | P064 | runvnc/mindroot | TP | TP | TP | sí | **no** | `delayed_exit` duerme 0,5 s y hace `sys.exit(0)` (`src/mindroot/coreplugins/admin/server_router.py:36–38`); la espera está referenciada por el loop y no hay estado que quede a medias. |
| TC4 | P065 | runvnc/mindroot | TP | TP | TP | sí | **no** | La misma `delayed_exit` que P064 (`src/mindroot/coreplugins/admin/server_router.py:36–38`). |
| TC4 | P077 | runvnc/mindroot | TP | TP | TP | sí | **no** | `execute_scheduled_command` atrapa `Exception` y registra la ejecución como fallida (`src/mindroot/coreplugins/scheduler/mod.py:516,539–550`). |
| TC4 | P081 | SpillwaveSolutions/agent-brain | TP | TP | TP | sí | **no** | `_run_indexing_pipeline` atrapa `Exception`, marca el estado `FAILED` con el error y relanza (`agent-brain-server/agent_brain_server/services/indexing_service.py:837–842`), y libera `is_indexing` en `finally`. La excepción relanzada no la ve nadie, pero el estado queda coherente. |
| TC4 | P085 | TNT-Likely/BeeCount-Cloud | TP | TP | TP | sí | **no** | `_write_call_log` envuelve la escritura en `try/except Exception` con log (`src/mcp/server.py:91,113–114`); si falla, se pierde una línea del log de llamadas, no el resultado de la herramienta. |
| TC4 | P086 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | `_run_inbox_cron_import` atrapa todo con log (`app/startup.py:68–75`). |
| TC4 | P088 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | `offline_completion_watcher` atrapa cada pasada y espera `asyncio.sleep` (`app/services/resource.py:381–388`). |
| TC4 | P089 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | El watcher atrapa cada pasada y espera `asyncio.sleep` (`app/services/subscription_offline_cleanup.py:257–264`). |
| TC4 | P090 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | El watcher atrapa cada pasada (`app/services/cross_copy_staging_cleanup.py:381–389`). |
| TC4 | P091 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | El watcher atrapa cada pasada (`app/services/subscription_cross_copy_organize.py:559–567`). |
| TC4 | P092 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | El watcher atrapa cada pasada (`app/services/subscription_cross_copy_progress.py:622–630`). |
| TC4 | P093 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | El watcher atrapa cada pasada (`app/services/cross_copy_jobs.py:1265–1274`). |
| TC4 | P094 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | `subscription_scheduler` no tiene `try` (`app/startup.py:239–283`), pero solo calcula sobre la configuración normalizada. `get_config` lee bajo el mismo lock que la escritura, así que nunca ve un fichero a medias (`app/config_store.py:61–80`). No encuentro ninguna E/S fuera de `try` que falle en operación normal. |
| TC4 | P095 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | `sign115_scheduler` lee la configuración bajo lock (`app/config_store.py:61–70`), normaliza la hora antes de `int()` y delega en `submit_background` (`app/startup.py:362–377`). |
| TC4 | P097 | xianer235/115-media-hub | TP | TP | TP | sí | **no** | `resource_jobs_housekeeper` pasa por `_run_prune_step`, que atrapa `Exception` (`app/startup.py:60–65,387–391`). |
| TC4 | P098 | yujian0815/fnmedia-ext | TP | TP | TP | sí | **no** | `work` atrapa `Exception`, resuelve `fut` y limpia `_search_inflight` (`proxy/app.py:853–865`). Espera E/S de red, referenciada por el loop, así que la petición que espera `fut` no queda colgada. |
| TC4 | P099 | yujian0815/fnmedia-ext | TP | TP | TP | sí | **no** | `refresh_routes` restablece `_refreshing` en `finally` (`proxy/catalog.py:205–209,337`). Si falla, la siguiente petición con rutas caducadas lo vuelve a lanzar (`proxy/app.py:1389–1391`). |
| TC4 | P100 | yujian0815/fnmedia-ext | TP | TP | TP | sí | **no** | El mismo `refresh_routes` que P099, relanzado por la siguiente petición (`proxy/app.py:1426–1427`). |
| TC4 | P101 | yujian0815/fnmedia-ext | TP | TP | TP | sí | **no** | `chart_cache.refresh` atrapa `Exception`, conserva la caché anterior y restablece `_refreshing` (`proxy/charts.py:382–404`). |
| TC4 | P102 | yujian0815/fnmedia-ext | TP | TP | TP | sí | **no** | `produce` atrapa `Exception`, resuelve `fut` con `None` y limpia `_PLAYLIST_FUT` (`proxy/app.py:2989–3004`). |
| TC4 | P103 | yujian0815/fnmedia-ext | TP | TP | TP | sí | **no** | `warm_standalone` atrapa todo (`proxy/catalog.py:625–635`); solo precalienta. |
| TC4 | P104 | yujian0815/fnmedia-ext | TP | TP | TP | sí | **no** | `work` atrapa `Exception`, resuelve `fut` y limpia `_inflight` (`proxy/catalog.py:476–490`). |

### 2.2 Auxiliares (TC2, fuera de la selección)

| Corpus | ID | Repo | Original | v1 | v2 | (a) contrato | (b) fallo funcional | Razón de (b) |
|---|---|---|---|---|---|---|---|---|
| TC2 | P145 | OtoDock/oto-dock | TP | TP | TP | sí | **no** | `pty_resize` no tiene ningún `await` (`satellite/sessions/session_manager.py:1091–1094`): termina en el primer paso y no puede ser recolectada a medias; solo fallaría con un mensaje mal formado. |
| TC2 | P149 | OtoDock/oto-dock | TP | TP | TP | sí | **no** | `stop_turn` no tiene ningún `await` (`satellite/sessions/session_manager.py:837–844`). |
| TC2 | P161 | OtoDock/oto-dock | TP | TP | TP | sí | **no** | `file_stat` atrapa `ValueError`/`SafeFsError`/`OSError` y siempre responde con `enqueue_send` (`satellite/sessions/session_manager.py:1995–2016,2027–2055`), que no lanza (`satellite/transport/ws_client.py:552–564`). |
| TC2 | P116 | OtoDock/oto-dock | TP | TP | TP | sí | **no** | `_drain_stderr` atrapa todo (`proxy/core/layers/codex/app_server_client.py:380–401`) y espera la tubería del subproceso, referenciada por el loop. |
| TC2 | P153 | OtoDock/oto-dock | TP | TP | TP | sí | **no** | `check_session_resumable` atrapa `Exception` y luego responde con `enqueue_send`, que no lanza (`satellite/sessions/session_manager.py:1273–1311`). |

## 3. Otros casos corregidos el 2026-11-03 (reglas no candidatas)

Son ejemplos y casos que tus decisiones tocan. No entran en la selección: `blocking` (14) y PYVIBE-009 (12) no llegan a n ≥ 15 en TC3 + TC4, y `transactions` tiene WARNING como máximo.

| Corpus | ID | Regla | Repo | Original | v1 | v2 propuesta | Razón |
|---|---|---|---|---|---|---|---|
| TC3 | J001 | blocking | axelixlabs/axelix | TP | TP | **FP (context)** | `BookTestDataQueryRunner.java:22–24`: `Thread.sleep(10000)` en el único `@Scheduled` de la app. Un cron fija activaciones, no un SLA: Spring se salta las activaciones mientras la anterior sigue ocupada, y el repositorio no exige ningún plazo ni frescura a este runner de datos de prueba (v2 §1). |
| TC4 | J053 | transactions | VIJAYAPANDIANT/fixit-hub | U | U | **TP** | `ingestEvent` es `@Transactional` (`IngestionServiceImpl.java:46`) y llama a `diagnoseIssueAsync` solo para issues nuevos (`:155–156`). La rama local es rápida (`AIDiagnosticServiceImpl.java:124–130`), y el worker relee el issue en su propia transacción y descarta el resultado sin avisar si no lo encuentra (`:143–146`). Es lo que afirma el mensaje: el worker no ve los cambios sin confirmar del llamador. Confirmado por Joaquín (decisión 5 del 2026-11-03). |
| TC2 | J015 | blocking | quarkusio/quarkus | TP | TP | **FP (context)** | Fixture: `Thread.sleep(100)` en el job `increment()` con `cron = "*/1 * * * * ?"` (`integration-tests/opentelemetry-quartz/src/main/java/io/quarkus/it/opentelemetry/quartz/Counter.java:24–27`), igual que `FailedBasicScheduler.java:10–13`. La cadencia de un cron no es una propiedad (v2 §1), y el módulo no exige ningún plazo, así que no se incumple ninguna propiedad. |
| TC2 | J056 | blocking | terrakube-io/terrakube | FP | FP | **FP (context)** | El `join()` (`AzDevOpsPollingService.java:101–110`) tiene cota: HTTP con connect 5 s, respuesta 30 s y espera de pool 2 s (`WebhookHttpClientConfig.java:33–46`, usado en `WebhookServiceBase.java:125–128`) y token SP/MI con `block(30 s)` (`AzDevOpsTokenService.java:115`). Sí retrasa al otro job `fixedDelay` (`CliAuthSessionCleanupTask.java:19`), porque con `SimpleAsyncTaskScheduler` los `fixedDelay` comparten un hilo, pero la purga no tiene plazo exigido: las sesiones caducadas se rechazan al usarlas (`CliLoginService.java:228`). La etiqueta es la misma que la original, por otra razón (decisión 1 del 2026-11-03). |
| TC2 | J001 | blocking | bage2014/study | FP | TP | **FP (context)** | `SampleBackground.java:38–41`: sleep aleatorio < 1 s, con cota, en el único `@Async` del módulo (`study-spring-boot-zipkin`, sin `@Scheduled` ni configuración de executor); la ruta `/async` no espera el resultado (`SampleController.java:85–88`) y nada en el módulo exige un plazo, así que no se incumple ninguna propiedad. |
| TC2 | J052 | blocking | risesoft-y9/WorkFlow-Engine | TP | TP | **U** | `saveToEs` duerme 3 s por cada proceso que termina (`y9-module-processadmin/risenet-y9boot-support-processadmin/src/main/java/net/risesoft/service/impl/Process4CompleteUtilServiceImpl.java:283–299`, llamado en `TaskListener4ProcessCompleted.java:61`). La app activa `@EnableAsync` (`risenet-y9boot-server-processadmin/src/main/java/net/risesoft/ProcessAdminApplication.java:23`) sin executor propio ni `spring.task` en el módulo, así que el executor efectivo puede venir de los starters `risenet-y9boot-starter-*` (`risenet-y9boot-server-processadmin/pom.xml:37,49,66`), que están fuera del repositorio. Ningún código muestra la frecuencia o el volumen que llenarían un executor acotado. Falta configuración decisiva. |

Los demás casos de `blocking` y PYVIBE-009 de la primera propuesta no se han revisado con las decisiones del 2026-11-03, porque esas reglas no son candidatas. Si alguna vuelve a serlo, hay que revisarlos.

## Ficheros

- `propuesta.py`: genera `propuesta-v2.json` y este fichero.
- `pyvibe-012-campo-b.tsv`: el campo (b) de los 65 casos de PYVIBE-012, con su razón y sus `file:line`.
