# REVIEW-CRITERIA v2: TP / FP / U por propiedad incumplida

**Versión v2 (borrador, 2026-11-03).** Las decisiones son de Joaquín, del 2026-11-03.

- **Documento nuevo.** `REVIEW-CRITERIA.md` (v1) no se toca.
- **Resultados publicados intactos.** TC1–TC4 conservan sus veredictos, métricas y conclusiones: `audit-joaquin.json`, `metrics.json` y `METRICS.md` no cambian. Cada corpus se lee con el criterio de su propio pre-registro.
- **Aplicación:** v2 se aplica a la evaluación de desarrollo, que es asistida y se declara como tal (`criterio-v2-desarrollo/`), y al pre-registro de TC5.
- **Aviso:** si las cifras bajo v2 difieren de las publicadas bajo v1, la diferencia refleja también el cambio de definición, no solo un cambio en las reglas.

## 1. Veredicto

- **TP** cuando **existe una ruta alcanzable y una condición plausible**, ambas apoyadas en el repositorio, **bajo las cuales se incumple una propiedad explícita de corrección o funcionamiento**. No exige haber observado el incidente.
  - **Ruta alcanzable:** igual que en v1 §2, sin cambios. Un camino de producción dentro del repositorio llega desde un punto de entrada de la operación normal. Las apps demo, playground y fixture son alcanzables dentro de su propia app; los tests, scripts manuales, benchmarks y docs no. Los repositorios de estudio se excluyen en el triaje.
  - **Condición plausible:** un estado o una carga que el repositorio hace posible en esa ruta. Por ejemplo: otro trabajo que comparte el hilo o el pool, una dependencia de E/S sin cota, un llamador con transacción abierta. No basta con que la condición sea concebible en abstracto; tiene que poder señalarse con `file:line` (la configuración, los otros trabajos, el llamador).
  - **Propiedad explícita:** una de estas tres fuentes:
    - un contrato documentado de la plataforma o la API (asyncio: el event loop no debe bloquearse, y la referencia a una tarea hay que conservarla; Spring: semántica de `@Async`/`@Transactional`/`@Scheduled`);
    - lo que el propio repositorio declara (la cadencia de un `@Scheduled`, un timeout, una garantía transaccional);
    - el comportamiento que el código promete a su llamador.
- **FP** cuando el repositorio muestra lo contrario, con `file:line`:
  - **detección:** el patrón no está;
  - **alcanzabilidad:** no hay ruta alcanzable (v1 §2);
  - **contexto:** en esa ruta ninguna condición plausible incumple la propiedad. Por ejemplo, nada más espera al hilo bloqueado, o la transacción del llamador ya se confirmó.
- **U** cuando el repositorio no deja decidir la ruta o la condición. Ocurre, por ejemplo, cuando el llamador, el pool o la configuración están fuera del repositorio, o cuando el código es API pública de una biblioteca sin llamadores internos vivos.
- **Una pausa deliberada no decide nada por sí misma.** Un `sleep` que simula latencia, espacia peticiones o deja tiempo de margen es TP si el repositorio muestra trabajo que espera detrás de él, o una cadencia o un timeout que incumple. Si no muestra nada de eso, es FP por contexto. Esto sustituye la regla fija de v1 §3.1 (número de hilos del scheduler) por la misma pregunta hecha en general.

## 2. Aparte del veredicto: gravedad, utilidad de corregir y Overstated

Se registran por separado y **ninguno decide el veredicto**.

- **Gravedad:**
  - **CRITICAL:** solo para las reglas validadas con el procedimiento de selección (n ≥ 15, ≥ 5 repos, TP/n ≥ 0,90 con U como no-TP, e impacto grave justificado por escrito) y confirmadas después en el corpus pre-registrado.
  - **WARNING:** todo lo demás.
  - **Un TP puede ser WARNING.**
- **Utilidad de corregir:** si arreglarlo merece la pena en ese repositorio. Un TP de impacto mínimo sigue siendo TP.
- **Overstated:** el mensaje atribuye un impacto que el código no sostiene. Nunca es motivo de FP.

## 3. Por regla: propiedad y condición plausible

| Regla | Propiedad que se incumple | Condición plausible que hace TP | FP por contexto (ejemplos, no exhaustivo) |
|---|---|---|---|
| `blocking`, `blocking-kafka` | el hilo anclado (scheduler, executor de `@Async`, listener de Kafka, evento) atiende su trabajo y su cadencia | otro trabajo comparte ese hilo o pool y espera detrás de la llamada (otros `@Scheduled` con pool pequeño, otros `@Async` en el mismo executor), o la llamada no tiene cota y puede colgar el hilo | nada más usa el hilo y la pausa es el trabajo deliberado del propio job; el pool tiene hilos de sobra para la carga declarada; hilos virtuales por ejecución |
| `kafka-send-timeout` | el envío termina en un tiempo acotado en una ruta normal | `.send(..).get()` sin timeout en una ruta programada o de petición | el productor está configurado para que la espera no supere la cota del mensaje |
| `transactions` | la semántica transaccional que el llamador espera (rollback conjunto, visibilidad de lo que escribió) | **el llamador tiene una transacción abierta y el método asíncrono depende de ella**: relee datos que el llamador aún no ha confirmado, o el llamador cuenta con que su rollback lo deshaga. **Nunca por la mera combinación** `@Async` + `@Transactional` | ver la nota de abajo |
| `reactor-block` | los hilos no bloqueantes de Reactor no se bloquean | la llamada puede ejecutarse en un hilo de event loop, `parallel` o `single` | se ejecuta en un hilo que puede bloquear |
| PYVIBE-001/002/004/007/008/009/010/011/016/018 (bloqueo en `async def`) | el event loop no se bloquea (contrato de asyncio) | la llamada se ejecuta en el loop mientras este atiende otro trabajo (peticiones, otras tareas) | solo en el arranque antes de servir, o en el cierre final sin otro trabajo en el loop; en un hilo (`to_thread`, executor) |
| PYVIBE-003/015 (loop anidado) | no se arranca un loop dentro de otro | alcanzable con un loop en marcha | solo alcanzable sin loop en marcha |
| PYVIBE-005 (Celery sin límite de tiempo) | la tarea termina o se corta | puede colgar en E/S externa y no hay límite global en el repositorio | un `task_time_limit`/`task_soft_time_limit` global la cubre |
| PYVIBE-006 (ContextVar sin reset) | el valor no se filtra a trabajo posterior | trabajo posterior en el mismo contexto puede verlo | el contexto se descarta tras la llamada |
| PYVIBE-012/014 (tarea descartada) | contrato de `asyncio.create_task`: hay que conservar la referencia, o la tarea puede desaparecer antes de terminar; y una excepción no recogida se pierde | no se conserva ninguna referencia a la tarea en ninguna parte | se conserva una referencia (un set, un registro, un callback que la retiene) |
| PYVIBE-013 (gather) | los fallos de los awaitables se observan | algún awaitable puede lanzar en un fallo normal y los demás siguen sin observarse | todos los awaitables contienen sus excepciones |
| PYVIBE-017 (`except` vacío) | los errores que importan no se tragan | puede tragarse `KeyboardInterrupt`/`SystemExit`, o errores relevantes en una ruta normal | — |

**`transactions`: WARNING como máximo.**

- **Sin alerta:** la regla no alerta en ninguno de estos casos:
  - propagación `NOT_SUPPORTED`, `NEVER` o `SUPPORTS`;
  - listener `@TransactionalEventListener` en fase `AFTER_COMMIT`, la fase por defecto;
  - autoinvocación (`this.metodo()`, sin pasar por el proxy).
- **No son excepciones universales:** estos casos no son la lista completa de FP ni dan por resuelto el contexto en el resto. Cualquier otra combinación necesita la dependencia transaccional de la fila de la tabla para ser TP.
- **Si no puede aportar contexto:** cuando la regla no es capaz de aportar ese contexto adicional (el llamador con transacción abierta y la dependencia), **se desactiva**.

## 4. Ejemplos

Los ejemplos con ID salen de TC2–TC4. Sus etiquetas v2 son las **propuestas** de `criterio-v2-desarrollo/`, pendientes de la confirmación de Joaquín. Los marcados como *ilustrativos* no salen de ningún corpus.

### 4.1 Positivos (TP)

| Caso | Regla | Ruta | Condición plausible y propiedad |
|---|---|---|---|
| TC3 J010 (`Evvvvvvvan/XianYuSmart`) | `blocking` | `@Scheduled scheduledRefreshWebSocketToken()`, `TokenRefreshServiceImpl.java:486–509` | duerme 3–8 s por cuenta, en un scheduler de 2 hilos (`config/AsyncConfig.java:135–137`) que comparte con 14 `@Scheduled`: los demás jobs pierden su cadencia |
| TC4 J058 (`ysy0915/chat-system`) | `blocking` | `@Scheduled` de `ModelAutoChatService.java:59–94` | `Future.get()` sin timeout sobre una llamada LLM: el hilo del scheduler puede quedar colgado sin cota |
| TC3 J017 | `kafka-send-timeout` | handlers programados cada 3 s, `AbstractKafkaDomainEventSender.java:84` | `op.send(rc).get()` sin timeout en una ruta programada |
| TC3 P008 (`apowerb/apowerb`) | PYVIBE-009 | ruta HTTP `upload_complete`, `src/apowerb/routers/files.py:212–213,246–253` | `open()` y lecturas síncronas de fragmentos en el loop mientras el servidor atiende otras peticiones |
| TC3 P020 (`Deen-Bridge/dnb-ai`) | PYVIBE-012 | ruta `/chat`, `main.py:1988` | `create_task(_persist_chat_history(...))` sin conservar la referencia: se incumple el contrato de `create_task` |
| *ilustrativo* | `transactions` | un servicio `@Transactional` guarda una entidad y llama a un método `@Async @Transactional` que la relee por id | el worker puede ejecutarse antes del commit del llamador y no encontrarla: se pierde el resultado |

### 4.2 Negativos (FP)

| Caso | Regla | Condición que falla | Por qué |
|---|---|---|---|
| TC2 J015 (`quarkusio/quarkus`, fixture) | `blocking` | contexto | `Thread.sleep(100)` cada 1 s en el job `increment()` (`integration-tests/opentelemetry-quartz/.../Counter.java:24–27`). El planificador Quartz de Quarkus tiene 25 hilos por defecto y el módulo no lo cambia (`src/main/resources` no fija `thread-count`). Nada espera detrás. La pausa es el trabajo deliberado del fixture. |
| TC2 J056 (`terrakube-io/terrakube`) | `blocking` | contexto | espera de diseño con hilos virtuales (`application.properties:4`, Spring Boot 4.1.1): cada ejecución tiene su propio hilo |
| TC2 P083 (`not-sekiun/Consortium`) | PYVIBE-009 | contexto | `open()` solo en el arranque, antes de servir (`start_server.py:49`, servidor en `:154–155`) |
| TC2 P099 (`OtoDock/oto-dock`) | PYVIBE-009 | alcanzabilidad | script manual de humo (`mcps/custom/tts-mcp/live_smoke.py`) |
| TC4 J056/J057 (`wujun728/jun_java_plugin`) | `blocking` | alcanzabilidad | el único llamador es un test (`ApplicationTests.java:31,33`) |
| TC4 J001 (`Angular2Guy/AngularPortfolioMgr`) | `transactions` | contexto, sin alerta (§3) | `@TransactionalEventListener` con fase por defecto `AFTER_COMMIT` (`KafkaProducer.java:57–60`): cuando se ejecuta, la transacción del llamador ya se ha confirmado |

### 4.3 Indeterminados (U)

| Caso | Regla | Qué no deja decidir el repositorio |
|---|---|---|
| TC4 J032/J033 (`mrtylerzhou/AntFlow-activiti`) | `blocking` | la única cadena interna está muerta: `notifyCurrent` no tiene llamadores (`NotifyServiceImpl.java:168`) y la sobrecarga de 2 argumentos de `MessageUtils.sendMessageBatch` tampoco (`MessageUtils.java:44`). Pero son métodos públicos de un motor pensado para integrarse en otras aplicaciones, que pueden llamarlos desde fuera |
| TC4 P058 (`riteshbonthalakoti/HELPDESK.AI`) | PYVIBE-012 | el código está en un virtualenv de CI comiteado (`.tmp-ci-venv/.../realtime/_async/channel.py:247`), y no se demuestra que la aplicación use esa copia |
| TC4 J053 (`VIJAYAPANDIANT/fixit-hub`) | `transactions` | el worker relee el issue (`AIDiagnosticServiceImpl.java:143`) y se llama desde `ingestEvent`, que es `@Transactional` (`IngestionServiceImpl.java:46,156`). Decidir si el worker puede llegar antes del commit exige saber cuánto tarda la rama de diagnóstico; según la rama, puede ser TP |

## 5. Qué cambia respecto a v1

- **§1:** el TP se define por una propiedad incumplida en una condición plausible, no por "se cumplen detección, contexto y alcanzabilidad". La alcanzabilidad (v1 §2) y la exclusión c2 de repositorios de estudio no cambian.
- **Pausas deliberadas:** v1 §2.3 decía que una pausa deliberada no hace FP. v2 mantiene que tampoco hace TP por sí misma (§1): decide lo que espera detrás.
- **v1 §3.1** (número de hilos del scheduler) queda absorbido en la condición plausible de `blocking`.
- **`transactions`:** pasa a WARNING como máximo, deja de ser TP por la mera combinación de anotaciones, no alerta en los casos de §3 y se desactiva si no puede aportar contexto.
- **Gravedad, utilidad de corregir y Overstated** se registran aparte (§2).

## 6. Uso

- **Evaluación de desarrollo:** `criterio-v2-desarrollo/`, asistida y declarada como tal. Las etiquetas v2 las propone Claude y las confirma o corrige Joaquín.
- **TC5:** su pre-registro copia literalmente §1, §2 y §3 de este documento y cita su versión.
- **Instrucciones de IA:** las que apliquen v2 serán un documento nuevo; `REVIEW-AI-INSTRUCTIONS.md` (v1) no se toca.
