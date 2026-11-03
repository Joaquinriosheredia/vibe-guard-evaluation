# Evaluación de desarrollo con REVIEW-CRITERIA v2: etiquetas y selección

**Evaluación asistida de desarrollo.** Claude propone la etiqueta v2 de cada caso y su razón; Joaquín la confirma o corrige. No es una revisión ciega ni sustituye a ningún resultado publicado: TC1–TC4 conservan sus veredictos, métricas y conclusiones. Criterio: `../REVIEW-CRITERIA-v2.md`. Las cifras de este fichero salen de `propuesta-v2.json`, y `comprobar.py` verifica que coinciden.

## Registro

- **2026-11-03, primera propuesta:** 101 casos de TC2–TC4.
- **2026-11-03, primeras correcciones de Joaquín:**
  - TC2 J015, TC3 J001 y TC2 J001: FP por contexto.
  - TC2 J052: U.
  - TC3 P026: TP por contrato.
  - PYVIBE-012: campos (a) y (b).
  - Decisiones sobre las segundas opiniones de Codex (J056 FP, frontera FP/U, cadencias, `transactions` opción (a), J053 TP, Kafka, Celery, confirmación CRITICAL).
- **2026-11-03, decisiones de Joaquín tras la segunda opinión de Codex sobre B** (`~/vibe-guard-evaluation-work/second-opinions/2026-11-03-criterio-v2-propuesta-b/`):
  1. **Población de selección:** solo TC4 (55 casos de PYVIBE-012, 18 repos). TC3 queda aparte, porque su revisión dependió del desacuerdo A/B y de un muestreo. P058 cuenta como U (no-TP).
  2. **Campos separados:** «categoría» y «gravedad» (WARNING/CRITICAL), sin ninguna escala de contrato.
  3. **PYVIBE-012:** (b) se separa en tres mecanismos: b1 pérdida por no retención, b2 excepción sin supervisión, b3 ausencia de recuperación. No se da por demostrado ningún recuento causal.
  4. **Una detección, una alerta.** Separar los mensajes no autoriza dos alertas basadas en la misma detección: `DISENO-PYVIBE-012.md` (propuesta, sin implementar).
  5–7. **Redacción.** «Ninguna regla evaluada reúne hoy los requisitos para CRITICAL automático». WARNING no tiene umbral, pero publica su evidencia y sus limitaciones. Se conservan los U y las cuestiones abiertas.
  8. **TC5:** borrador de pre-registro, `../tc5-borrador/PREREGISTRATION-BORRADOR.md`. No se ejecuta.
  9. **Proyecto:** TC5 se aparca y se pasa a pilotos de auditoría (`~/vibe-guard`, `DECISIONS.md`).
  - **Además:** P094 pasa a b2/b3 sí; «nadie lo nota» se sustituye por «sin observador ni recuperación en el código»; P087 se limita a las tareas de monitorización.
- **2026-11-03, debate con Codex aprobado por Joaquín** (`~/vibe-guard-evaluation-work/second-opinions/2026-11-03-criterio-v2-debate/final.md`):
  - **O1:** TC5 solo validaría R como WARNING.
  - **O2:** se reescribe la fila de PYVIBE-013 en v2.
  - **O3:** TC4 P046 pasa a b2 = sí y b3 = no; b2 sí en TC4 pasa de 12 a 13, y b2 y b3 sigue en 6.
  - **O4:** las modalidades de cadencia se describen por separado en v2.
  - **O5:** `comprobar.py` comprueba etiquetas y campos por caso, distribuciones por repo y árboles de TC1–TC4.
  - **Puntos 2 y 3 de la consulta `…/2026-11-03-criterio-v2-cierre/`:** manejador global y análisis de propietarios y alias, en `DISENO-PYVIBE-012.md`.

## 1. Población de selección (declarada)

Todos los casos con tu veredicto en **TC4**, que tuvo revisión humana completa. **TC3 queda aparte:** sus 25 casos son los 5 desacuerdos A/B y una muestra de 20 acuerdos, así que su inclusión depende de las IAs y del muestreo. TC2 solo aporta ejemplos auxiliares. Las cifras de TC3 y TC2 no se suman a las de TC4.

| Regla | n | Repos | Máx. por repo | ¿Candidata? (n ≥ 15 y ≥ 5 repos) |
|---|---|---|---|---|
| PYVIBE-012 | 55 | 18 | 12 | **sí** |
| transactions | 39 | 16 | 10 | no: WARNING como máximo (v2 §3) |
| PYVIBE-002 | 11 | 2 | 10 | no |
| PYVIBE-007 | 11 | 2 | 10 | no |
| blocking | 11 | 6 | 2 | no |
| PYVIBE-018 | 9 | 5 | 3 | no |
| kafka-send-timeout | 6 | 1 | 6 | no |
| PYVIBE-010 | 3 | 2 | 2 | no |
| PYVIBE-016 | 3 | 3 | 1 | no |
| PYVIBE-017 | 3 | 2 | 2 | no |
| reactor-block | 3 | 1 | 3 | no |
| PYVIBE-006 | 2 | 2 | 1 | no |
| PYVIBE-014 | 2 | 2 | 1 | no |
| PYVIBE-008 | 1 | 1 | 1 | no |
| blocking-kafka | 1 | 1 | 1 | no |

**La única regla candidata es PYVIBE-012.** n por repo:

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
| HyxiaoGe/fusion | 2 |
| asfaraguest/tatap | 2 |
| liyupi/yu-ai-learn | 2 |
| SpillwaveSolutions/agent-brain | 1 |
| TNT-Likely/BeeCount-Cloud | 1 |
| antiv/mate | 1 |
| jacebrowning/memegen | 1 |
| ljxpython/ai-agent-platform | 1 |
| metalogico/issued | 1 |
| riteshbonthalakoti/HELPDESK.AI | 1 |

## 2. Selección (C): PYVIBE-012 en TC4

n = 55, 18 repos. Umbral CRITICAL: n ≥ 15, ≥ 5 repos y TP/n ≥ 0.90, con U como no-TP. Wilson 95 %.

| Campo | Casos | ¿Pasa el umbral CRITICAL? |
|---|---|---|
| (a) contrato: TP v2 (incumple la recomendación de retención) | 54/55 = 0.98 [0.90–1.00] | no aplica: es la categoría «incumplimiento de recomendación documentada de uso seguro», con gravedad WARNING |
| b1 pérdida por no retención | 0/55 = 0.00 [0.00–0.07] | no |
| b2 excepción sin supervisión | 13/55 = 0.24 [0.14–0.36] | no |
| b2 y b3 (excepción sin supervisión y sin recuperación) | 6/55 = 0.11 [0.05–0.22] | no |
| U (P058) | 1/55 = 0.02 [0.00–0.10] | cuenta como no-TP |

- **Ninguna regla evaluada reúne hoy los requisitos para CRITICAL automático.** PYVIBE-012 queda en WARNING, con categoría «incumplimiento de recomendación documentada de uso seguro».
- **Sin causalidad.** Los tres mecanismos se cuentan por separado, y ningún recuento atribuye un fallo a la falta de retención. b2 y b3 describen fallos del manejo de errores del cuerpo de la tarea; conservar la referencia no los evita por sí solo, si nadie supervisa la tarea.
- **Cómo se lee b1, b2 y b3:**
  - **sí:** el código muestra la condición;
  - **no:** he leído el cuerpo de la corrutina, y lo que llama donde hacía falta, y no la muestra; eso no afirma que sea imposible;
  - **U:** no se puede decidir;
  - **—:** no aplica (b3 solo se evalúa si b2 es sí).
- **Límite de b1:** solo se miró a qué espera la tarea en su propio cuerpo. Ningún caso espera un future que solo referencie la propia tarea.

## 3. PYVIBE-012 caso por caso

Categoría: «incumplimiento de recomendación documentada de uso seguro». Gravedad: WARNING. Veredicto v2: TP por contrato salvo P058 (U).

### 3.1 Población (TC4), primero los que tienen b2 = sí o U

| Corpus | ID | Repo | Original | v2 | (a) | b1 | b2 | b3 | Razón |
|---|---|---|---|---|---|---|---|---|---|
| TC4 | P004 | AndrewCTF/velocity | TP | TP | sí | no | **sí** | **sí** | b2: `_run_job` no protege `_verify_sha256`, el cálculo de tamaño ni `_write_metadata` (`apps/api/app/localllm/manager.py:531,551–558`); un `OSError` ahí escapa de la tarea. b3: `job.status` queda en `"verifying"` para siempre: nada en el código lo corrige ni lo reintenta. |
| TC4 | P040 | foodpm/timecut | TP | TP | sí | no | **sí** | **sí** | b2: En el reinicio, `start()` no protege `_ensure_dirs()` ni `create_subprocess_exec` (`app/recorder/manager.py:151,171–176`), que se llaman desde `_monitor_process` (`:255,261`). b3: `start()` ya ha puesto `self._running = True`: la grabación queda parada con el indicador diciendo que corre, y nada la reinicia. |
| TC4 | P066 | runvnc/mindroot | TP | TP | sí | no | **sí** | **sí** | b2: Antes de su `try`, `handle_cmds` escribe el chat log en disco (`src/mindroot/coreplugins/agent/agent.py:268`; `src/mindroot/lib/chatlog.py`, `add_message_async` → `_save_log_async`). Caso límite: depende de un fallo de E/S de disco. b3: `run_command` no espera la tarea (`agent.py:929–936`): el comando pedido no se ejecuta y nada lo reintenta. |
| TC4 | P087 | xianer235/115-media-hub | TP | TP | sí | no | **sí** | **sí** | b2: `pending_offline_job_counts_by_monitor()`, que lista los trabajos de recursos de la base de datos (`app/services/resource.py:117–119,138–144`), está fuera de `try` en el bucle (`app/startup.py:184–186`). b3: El bucle muere y las tareas de monitorización con `cron_minutes` dejan de dispararse; nada lo reinicia. Los demás bucles (suscripciones, firma, mantenimiento) son independientes (`app/startup.py:393–403`). |
| TC4 | P094 | xianer235/115-media-hub | TP | TP | sí | no | **sí** | **sí** | b2: `load_subscription_task_state` ejecuta un `SELECT` sin protección (`app/services/subscription_state.py:630–634`) y se llama fuera de `try` en el bucle (`app/startup.py:291`). Corregido el 2026-11-03 tras la segunda opinión de Codex (antes: no). b3: `subscription_scheduler` muere y las suscripciones programadas dejan de dispararse; nada lo reinicia. |
| TC4 | P096 | xianer235/115-media-hub | TP | TP | sí | no | **sí** | **sí** | b2: `memory_housekeeper` no tiene `try` (`app/startup.py:379–385`), y `cleanup_completed_monitor_change_events` ejecuta un `DELETE` en la base de datos sin protección (`app/services/monitor_changes.py:2414–2425`). b3: El bucle muere: las cachés y los eventos dejan de podarse y la memoria crece; nada lo reinicia. |
| TC4 | P005 | AndrewCTF/velocity | TP | TP | sí | no | **sí** | **no** | b2: `_get_catalog` → `cache.get_or_fetch` → `load()` hace llamadas de red con `gather` sin `return_exceptions` (`apps/api/app/routes/cams.py:170–182`); un fallo de red escapa. b3: Es un precalentamiento: la ruta vuelve a llamar a `_get_catalog` bajo demanda. |
| TC4 | P007 | AndrewCTF/velocity | TP | TP | sí | no | **sí** | **no** | b2: `_warm_apple` no tiene `try` (`apps/api/app/main.py:500–502`), y `apple_maps.session()` hace una petición HTTP con `raise_for_status()` (`apps/api/app/apple_maps.py:175–184`). b3: La sesión se vuelve a pedir bajo demanda, con reintento (`apps/api/app/apple_maps.py:209`). |
| TC4 | P014 | asfaraguest/tatap | TP | TP | sí | no | **sí** | **no** | b2: `_prewarm_sub_translation` espera `_get_validated_subtitle_cache` fuera de `try` (`android/app/src/main/python/backend/main.py:2354`), y esa función lee la caché de la base de datos (`get_subtitle_cache`). b3: Es un prefetch: la petición real traduce bajo demanda. |
| TC4 | P016 | asfaraguest/tatap | TP | TP | sí | no | **sí** | **no** | b2: La misma lectura de caché fuera de `try` que P014 (`backend/main.py:2354`; `backend/database/__init__.py:466`). b3: Es un prefetch: la petición real traduce bajo demanda. |
| TC4 | P046 | jacebrowning/memegen | TP | TP | sí | no | **sí** | **no** | b2: `track` no tiene `try` (`app/utils/meta.py:109–140`), y `http.fetch` solo atrapa `EXCEPTIONS`, que son errores de conexión, URL y redirección (`app/utils/http.py:9–13,32–35`); un `json.JSONDecodeError` de `response.json()` (`:26`) escapa de la tarea. b3: no; es analítica, y la petición siguiente vuelve a enviar su seguimiento. Corregido el 2026-11-03 (debate O3; antes: no, por falta de impacto, que no es la definición de b2). |
| TC4 | P056 | phucnguyentvp1/frameweaver | TP | TP | sí | no | **sí** | **no** | b2: `_refresh_media_urls` no tiene `try` y hace consultas y actualizaciones de base de datos (`agent/services/flow_client.py:318–362`). b3: La extensión reenvía `media_urls_refresh` cada vez que captura URLs nuevas (`extension/background.js:910–922`). |
| TC4 | P081 | SpillwaveSolutions/agent-brain | TP | TP | sí | no | **sí** | **no** | b2: `_run_indexing_pipeline` relanza tras marcar el fallo (`agent-brain-server/agent_brain_server/services/indexing_service.py:837–842`). b3: El estado queda `FAILED` con el error y se libera `is_indexing`: es coherente y se puede reintentar. |
| TC4 | P058 | riteshbonthalakoti/HELPDESK.AI | U | U | sí (patrón presente; alcanzabilidad no demostrada) | U | **U** | **—** | No se demuestra que la aplicación use esta copia vendorizada en `.tmp-ci-venv` (`.tmp-ci-venv/Lib/site-packages/realtime/_async/channel.py:247`), así que tampoco se puede respaldar ningún fallo funcional. |
| TC4 | P006 | AndrewCTF/velocity | TP | TP | sí | no | **no** | **—** | `warm_basemap` atrapa el fallo de cada tesela (`apps/api/app/routes/tiles.py:243–246`); precalentamiento. |
| TC4 | P008 | AndrewCTF/velocity | TP | TP | sí | no | **no** | **—** | `_prewarm` atrapa todo (`apps/api/app/mcp_server.py:282–286`); solo precalienta. |
| TC4 | P009 | AndrewCTF/velocity | TP | TP | sí | no | **no** | **—** | `_pipeline` y `_pipeline_mapany` envuelven todo en `try/except Exception` y marcan `job["status"] = "error"` (`apps/api/app/routes/recon.py:419,511` y `:276,297–300`); la espera de `_GPU_LOCK` queda referenciada por el lock global. |
| TC4 | P012 | antiv/mate | TP | TP | sí | no | **no** | **—** | `_cleanup_loop` espera `asyncio.sleep` y atrapa el fallo de cerrar cada sesión (`shared/utils/tools/browser_tools.py:235–251`); no hay una ruta normal que mate el bucle. |
| TC4 | P029 | crane-in-clear-sky/WorkWit-AI-Agent | TP | TP | sí | no | **no** | **—** | `run_automation` atrapa `Exception`, registra la ejecución como `"error"` y libera `_RUNNING` en `finally` (`workwit/backend/automation_runner.py:86,129–133`). |
| TC4 | P030 | crane-in-clear-sky/WorkWit-AI-Agent | TP | TP | sí | no | **no** | **—** | `scheduler_loop` atrapa cada pasada y espera `asyncio.sleep` (`workwit/backend/automation_runner.py:138–156`). |
| TC4 | P031 | crane-in-clear-sky/WorkWit-AI-Agent | TP | TP | sí | no | **no** | **—** | La misma `run_automation` que P029: registra el error y libera `_RUNNING` (`workwit/backend/automation_runner.py:129–133`). |
| TC4 | P032 | dameng2026/xianyu-pilot | TP | TP | sí | no | **no** | **—** | `_background_refresh_account` atrapa todo con log (`apps/api/app/services/rate_service.py:1476–1484`); solo recalibra datos que se vuelven a sincronizar. |
| TC4 | P033 | dameng2026/xianyu-pilot | TP | TP | sí | no | **no** | **—** | `_bg_sync` atrapa todo con log (`apps/api/app/services/ws_client.py:876–880`). |
| TC4 | P034 | dameng2026/xianyu-pilot | TP | TP | sí | no | **no** | **—** | `relist_sold_item` atrapa todo con log y su propia sesión hace `rollback` (`apps/api/app/services/relist_service.py:456–491`). |
| TC4 | P041 | foodpm/timecut | TP | TP | sí | no | **no** | **—** | `run_diary_for_date` envuelve la generación en `try/except Exception` con log (`app/diary/generator.py:28–38`). |
| TC4 | P042 | foodpm/timecut | TP | TP | sí | no | **no** | **—** | El callback registrado (`app/main.py:177–182`) llega a `_run_highlight`, que atrapa `Exception` y cierra el trabajo con `job.finish(False, …)` (`app/highlighter/scheduler.py:144–146`). |
| TC4 | P043 | HyxiaoGe/fusion | TP | TP | sí | no | **no** | **—** | `_parse_file_with_llm` atrapa todo y marca el fichero como error con `_mark_file_error` (`backend/app/services/file_service.py:728,755–760`). |
| TC4 | P044 | HyxiaoGe/fusion | TP | TP | sí | no | **no** | **—** | La misma `_parse_file_with_llm` que P043 (`backend/app/services/file_service.py:755–760`). |
| TC4 | P049 | liyupi/yu-ai-learn | TP | TP | sí | no | **no** | **—** | `_process_document` atrapa `Exception` y marca el documento `"failed"` (`backend/app/services/knowledge_service.py:74,89–93`). |
| TC4 | P050 | liyupi/yu-ai-learn | TP | TP | sí | no | **no** | **—** | `_run_quiz_task` atrapa `Exception` y marca la tarea `"failed"` (`backend/app/services/quiz_service.py:166,214–218`). |
| TC4 | P051 | ljxpython/ai-agent-platform | TP | TP | sí | no | **no** | **—** | `_cleanup` atrapa los fallos de `_reap` y de `docker rm` (`apps/runtime-service/src/runtime_service/workspace/execution.py:28–38,105–108`) y devuelve el resultado. |
| TC4 | P053 | metalogico/issued | TP | TP | sí | no | **no** | **—** | `_print_startup_messages` solo escribe mensajes de log (`server/opds/__init__.py:53–64`). |
| TC4 | P054 | phucnguyentvp1/frameweaver | TP | TP | sí | no | **no** | **—** | `_sync_tier` atrapa `Exception` y libera `_sync_in_progress` en `finally` (`agent/services/flow_client.py:294–310`). |
| TC4 | P055 | phucnguyentvp1/frameweaver | TP | TP | sí | no | **no** | **—** | La misma `_sync_tier` que P054 (`agent/services/flow_client.py:294–310`). |
| TC4 | P057 | phucnguyentvp1/frameweaver | TP | TP | sí | no | **no** | **—** | `_run_one` libera el límite y `_active_ids` en `finally` (`agent/worker/processor.py:163–172`), y `_process_one` atrapa `Exception` y llama a `_handle_failure` (`:280,302–305`). |
| TC4 | P064 | runvnc/mindroot | TP | TP | sí | no | **no** | **—** | `delayed_exit` duerme 0,5 s y hace `sys.exit(0)` (`src/mindroot/coreplugins/admin/server_router.py:36–38`); la espera está referenciada por el loop y no hay estado que quede a medias. |
| TC4 | P065 | runvnc/mindroot | TP | TP | sí | no | **no** | **—** | La misma `delayed_exit` que P064 (`src/mindroot/coreplugins/admin/server_router.py:36–38`). |
| TC4 | P077 | runvnc/mindroot | TP | TP | sí | no | **no** | **—** | `execute_scheduled_command` atrapa `Exception` y registra la ejecución como fallida (`src/mindroot/coreplugins/scheduler/mod.py:516,539–550`). |
| TC4 | P085 | TNT-Likely/BeeCount-Cloud | TP | TP | sí | no | **no** | **—** | `_write_call_log` envuelve la escritura en `try/except Exception` con log (`src/mcp/server.py:91,113–114`); si falla, se pierde una línea del log de llamadas, no el resultado de la herramienta. |
| TC4 | P086 | xianer235/115-media-hub | TP | TP | sí | no | **no** | **—** | `_run_inbox_cron_import` atrapa todo con log (`app/startup.py:68–75`). |
| TC4 | P088 | xianer235/115-media-hub | TP | TP | sí | no | **no** | **—** | `offline_completion_watcher` atrapa cada pasada y espera `asyncio.sleep` (`app/services/resource.py:381–388`). |
| TC4 | P089 | xianer235/115-media-hub | TP | TP | sí | no | **no** | **—** | El watcher atrapa cada pasada y espera `asyncio.sleep` (`app/services/subscription_offline_cleanup.py:257–264`). |
| TC4 | P090 | xianer235/115-media-hub | TP | TP | sí | no | **no** | **—** | El watcher atrapa cada pasada (`app/services/cross_copy_staging_cleanup.py:381–389`). |
| TC4 | P091 | xianer235/115-media-hub | TP | TP | sí | no | **no** | **—** | El watcher atrapa cada pasada (`app/services/subscription_cross_copy_organize.py:559–567`). |
| TC4 | P092 | xianer235/115-media-hub | TP | TP | sí | no | **no** | **—** | El watcher atrapa cada pasada (`app/services/subscription_cross_copy_progress.py:622–630`). |
| TC4 | P093 | xianer235/115-media-hub | TP | TP | sí | no | **no** | **—** | El watcher atrapa cada pasada (`app/services/cross_copy_jobs.py:1265–1274`). |
| TC4 | P095 | xianer235/115-media-hub | TP | TP | sí | no | **no** | **—** | `sign115_scheduler` lee la configuración bajo lock (`app/config_store.py:61–70`), normaliza la hora antes de `int()` y delega en `submit_background` (`app/startup.py:362–377`). |
| TC4 | P097 | xianer235/115-media-hub | TP | TP | sí | no | **no** | **—** | `resource_jobs_housekeeper` pasa por `_run_prune_step`, que atrapa `Exception` (`app/startup.py:60–65,387–391`). |
| TC4 | P098 | yujian0815/fnmedia-ext | TP | TP | sí | no | **no** | **—** | `work` atrapa `Exception`, resuelve `fut` y limpia `_search_inflight` (`proxy/app.py:853–865`). Espera E/S de red, referenciada por el loop, así que la petición que espera `fut` no queda colgada. |
| TC4 | P099 | yujian0815/fnmedia-ext | TP | TP | sí | no | **no** | **—** | `refresh_routes` restablece `_refreshing` en `finally` (`proxy/catalog.py:205–209,337`). Si falla, la siguiente petición con rutas caducadas lo vuelve a lanzar (`proxy/app.py:1389–1391`). |
| TC4 | P100 | yujian0815/fnmedia-ext | TP | TP | sí | no | **no** | **—** | El mismo `refresh_routes` que P099, relanzado por la siguiente petición (`proxy/app.py:1426–1427`). |
| TC4 | P101 | yujian0815/fnmedia-ext | TP | TP | sí | no | **no** | **—** | `chart_cache.refresh` atrapa `Exception`, conserva la caché anterior y restablece `_refreshing` (`proxy/charts.py:382–404`). |
| TC4 | P102 | yujian0815/fnmedia-ext | TP | TP | sí | no | **no** | **—** | `produce` atrapa `Exception`, resuelve `fut` con `None` y limpia `_PLAYLIST_FUT` (`proxy/app.py:2989–3004`). |
| TC4 | P103 | yujian0815/fnmedia-ext | TP | TP | sí | no | **no** | **—** | `warm_standalone` atrapa todo (`proxy/catalog.py:625–635`); solo precalienta. |
| TC4 | P104 | yujian0815/fnmedia-ext | TP | TP | sí | no | **no** | **—** | `work` atrapa `Exception`, resuelve `fut` y limpia `_inflight` (`proxy/catalog.py:476–490`). |

### 3.2 Aparte (TC3) y auxiliares (TC2), fuera de la selección

| Corpus | ID | Repo | Original | v2 | (a) | b1 | b2 | b3 | Razón |
|---|---|---|---|---|---|---|---|---|---|
| TC3 | P026 | hzy1522/tickflow-stock-panel | FP | TP | sí | no | **no** | **—** | El cuerpo atrapa `Exception`, marca `job_store.fail` y libera el slot en `finally` (`backend/app/api/kline.py:957–1007`): el estado del trabajo queda coherente. |
| TC3 | P020 | Deen-Bridge/dnb-ai | TP | TP | sí | no | **no** | **—** | Todo el cuerpo está en `try/except Exception` con log (`main.py:2526,2540–2541`); solo espera E/S de `session_store`. |
| TC3 | P028 | hzy1522/tickflow-stock-panel | TP | TP | sí | no | **no** | **—** | Igual: `job_store.fail` en `except` y `release_run_slot` en `finally` (`backend/app/api/kline.py:1233–1249`). |
| TC3 | P027 | hzy1522/tickflow-stock-panel | TP | TP | sí | no | **no** | **—** | Igual: `job_store.fail` en `except` y `release_run_slot` en `finally` (`backend/app/api/kline.py:1143–1162`). |
| TC3 | P005 | apowerb/apowerb | TP | TP | sí | no | **no** | **—** | `memory_retention_loop` contiene sus excepciones en cada pasada y sigue (`src/apowerb/memory/retention.py:24–31`); espera `asyncio.sleep`, referenciado por el loop. |
| TC2 | P145 | OtoDock/oto-dock | TP | TP | sí | no | **no** | **—** | `pty_resize` no tiene ningún `await` (`satellite/sessions/session_manager.py:1091–1094`): termina en el primer paso y no puede ser recolectada a medias; solo fallaría con un mensaje mal formado. |
| TC2 | P149 | OtoDock/oto-dock | TP | TP | sí | no | **no** | **—** | `stop_turn` no tiene ningún `await` (`satellite/sessions/session_manager.py:837–844`). |
| TC2 | P161 | OtoDock/oto-dock | TP | TP | sí | no | **no** | **—** | `file_stat` atrapa `ValueError`/`SafeFsError`/`OSError` y siempre responde con `enqueue_send` (`satellite/sessions/session_manager.py:1995–2016,2027–2055`), que no lanza (`satellite/transport/ws_client.py:552–564`). |
| TC2 | P116 | OtoDock/oto-dock | TP | TP | sí | no | **no** | **—** | `_drain_stderr` atrapa todo (`proxy/core/layers/codex/app_server_client.py:380–401`) y espera la tubería del subproceso, referenciada por el loop. |
| TC2 | P153 | OtoDock/oto-dock | TP | TP | sí | no | **no** | **—** | `check_session_resumable` atrapa `Exception` y luego responde con `enqueue_send`, que no lanza (`satellite/sessions/session_manager.py:1273–1311`). |

## 4. Otros casos corregidos el 2026-11-03 (reglas no candidatas)

Son ejemplos y casos que tocan tus decisiones; no entran en la selección.

| Corpus | ID | Regla | Repo | Original | v1 | v2 | Razón |
|---|---|---|---|---|---|---|---|
| TC4 | J053 | transactions | VIJAYAPANDIANT/fixit-hub | U | U | **TP** | `ingestEvent` es `@Transactional` (`IngestionServiceImpl.java:46`) y llama a `diagnoseIssueAsync` solo para issues nuevos (`:155–156`). La rama local es rápida (`AIDiagnosticServiceImpl.java:124–130`), y el worker relee el issue en su propia transacción y descarta el resultado sin avisar si no lo encuentra (`:143–146`). Es lo que afirma el mensaje: el worker no ve los cambios sin confirmar del llamador. Confirmado por Joaquín (decisión 5 del 2026-11-03). |
| TC3 | J001 | blocking | axelixlabs/axelix | TP | TP | **FP (context)** | `BookTestDataQueryRunner.java:22–24`: `Thread.sleep(10000)` en el único `@Scheduled` de la app. Un cron fija activaciones, no un SLA: Spring se salta las activaciones mientras la anterior sigue ocupada, y el repositorio no exige ningún plazo ni frescura a este runner de datos de prueba (v2 §1). |
| TC2 | J015 | blocking | quarkusio/quarkus | TP | TP | **FP (context)** | Fixture: `Thread.sleep(100)` en el job `increment()` con `cron = "*/1 * * * * ?"` (`integration-tests/opentelemetry-quartz/src/main/java/io/quarkus/it/opentelemetry/quartz/Counter.java:24–27`), igual que `FailedBasicScheduler.java:10–13`. La cadencia de un cron no es una propiedad (v2 §1), y el módulo no exige ningún plazo, así que no se incumple ninguna propiedad. |
| TC2 | J056 | blocking | terrakube-io/terrakube | FP | FP | **FP (context)** | El `join()` (`AzDevOpsPollingService.java:101–110`) tiene cota: HTTP con connect 5 s, respuesta 30 s y espera de pool 2 s (`WebhookHttpClientConfig.java:33–46`, usado en `WebhookServiceBase.java:125–128`) y token SP/MI con `block(30 s)` (`AzDevOpsTokenService.java:115`). Sí retrasa al otro job `fixedDelay` (`CliAuthSessionCleanupTask.java:19`), porque con `SimpleAsyncTaskScheduler` los `fixedDelay` comparten un hilo, pero la purga no tiene plazo exigido: las sesiones caducadas se rechazan al usarlas (`CliLoginService.java:228`). La etiqueta es la misma que la original, por otra razón (decisión 1 del 2026-11-03). |
| TC2 | J001 | blocking | bage2014/study | FP | TP | **FP (context)** | `SampleBackground.java:38–41`: sleep aleatorio < 1 s, con cota, en el único `@Async` del módulo (`study-spring-boot-zipkin`, sin `@Scheduled` ni configuración de executor); la ruta `/async` no espera el resultado (`SampleController.java:85–88`) y nada en el módulo exige un plazo, así que no se incumple ninguna propiedad. |
| TC2 | J052 | blocking | risesoft-y9/WorkFlow-Engine | TP | TP | **U** | `saveToEs` duerme 3 s por cada proceso que termina (`y9-module-processadmin/risenet-y9boot-support-processadmin/src/main/java/net/risesoft/service/impl/Process4CompleteUtilServiceImpl.java:283–299`, llamado en `TaskListener4ProcessCompleted.java:61`). La app activa `@EnableAsync` (`risenet-y9boot-server-processadmin/src/main/java/net/risesoft/ProcessAdminApplication.java:23`) sin executor propio ni `spring.task` en el módulo, así que el executor efectivo puede venir de los starters `risenet-y9boot-starter-*` (`risenet-y9boot-server-processadmin/pom.xml:37,49,66`), que están fuera del repositorio. Ningún código muestra la frecuencia o el volumen que llenarían un executor acotado. Falta configuración decisiva. |

Los demás casos de `blocking` y PYVIBE-009 de la primera propuesta no se han revisado con las decisiones del 2026-11-03, porque esas reglas no son candidatas.

## 5. Cuestiones abiertas (se conservan)

- **U de la población:** TC4 P058 (copia vendorizada en `.tmp-ci-venv`). Cerrar v2 no lo resuelve.
- **U auxiliares y de ejemplos:** TC2 J052 (executor de starters externos) y TC4 J032/J033 (API pública de un motor integrable).
- **Límite de b1:** no se ha seguido el árbol completo de awaits de cada tarea.
- **Caso límite:** P066 (b2 depende de un fallo de E/S de disco).
- **TC3:** sus casos de PYVIBE-012 se conservan aparte, sin sumarlos a ninguna tasa.
- **`blocking` y PYVIBE-009:** sin revisar con las reglas nuevas de cadencia y de frontera FP/U.
- **Analizadores:** sin cambios. El diseño de la separación de PYVIBE-012 está en `DISENO-PYVIBE-012.md` y no está implementado.

## Ficheros

- `propuesta.py`: genera `propuesta-v2.json` y este fichero.
- `pyvibe-012-mecanismos.tsv`: (a), b1, b2 y b3 de los 65 casos de PYVIBE-012, con su razón y sus `file:line`.
- `comprobar.py`: recalcula las cifras desde el TSV y las fichas, y comprueba que el JSON, este fichero, `REVIEW-CRITERIA-v2.md` y el borrador de TC5 dicen lo mismo.
- `DISENO-PYVIBE-012.md`: propuesta de separar retención y supervisión, sin implementar.
