# REVIEW-CRITERIA v2: TP / FP / U por propiedad incumplida

**Versión v2 (borrador).** Primera redacción del 2026-11-03; revisada el mismo día con las decisiones de Joaquín sobre las segundas opiniones de Codex (§7).

- **Documento nuevo.** `REVIEW-CRITERIA.md` (v1) solo recibe notas fechadas que corrigen hechos (§6 y §3.1 de v1). Sus reglas y los veredictos publicados no cambian.
- **Resultados publicados intactos.** TC1–TC4 conservan sus veredictos, métricas y conclusiones: `audit-joaquin.json`, `metrics.json` y `METRICS.md` no cambian. Cada corpus se lee con el criterio de su propio pre-registro.
- **Aplicación:** v2 se aplica a la evaluación de desarrollo, que es asistida y se declara como tal (`criterio-v2-desarrollo/`), y al pre-registro de TC5.
- **Aviso:** si las cifras bajo v2 difieren de las publicadas bajo v1, la diferencia refleja también el cambio de definición, no solo un cambio en las reglas.

## 1. Veredicto

- **TP** cuando **existe una ruta alcanzable y una condición plausible**, ambas apoyadas en el repositorio, **bajo las cuales se incumple una propiedad explícita de corrección o funcionamiento**. No exige haber observado el incidente.
  - **Ruta alcanzable:** igual que en v1 §2, sin cambios. Un camino de producción dentro del repositorio llega desde un punto de entrada de la operación normal. Las apps demo, playground y fixture son alcanzables dentro de su propia app; los tests, scripts manuales, benchmarks y docs no. Los repositorios de estudio se excluyen en el triaje (v1 §2.4); eso es una regla de triaje, nunca la razón de un veredicto.
  - **Condición plausible:** un estado o una carga que el repositorio hace posible en esa ruta. Por ejemplo: otro trabajo que comparte el hilo o el pool, una espera sin cota, un llamador con transacción abierta. No basta con que la condición sea concebible en abstracto; tiene que poder señalarse con `file:line` (la configuración, los otros trabajos, el llamador).
  - **Propiedad explícita:** una de estas tres fuentes:
    - un contrato documentado de la plataforma o la API (asyncio: el event loop no debe bloquearse; Spring: semántica de `@Async`/`@Transactional`);
    - lo que el propio repositorio exige: un timeout, un plazo, una frescura, una garantía transaccional;
    - el comportamiento que el código promete a su llamador.
  - **La cadencia de un job no es una propiedad.** Un `cron`, un `fixedRate` o un `fixedDelay` fija activaciones, no un SLA; Spring se salta una activación si la anterior sigue ocupada. Retrasar o saltarse activaciones, del propio job o de otro, solo incumple una propiedad si el repositorio exige un plazo o una frescura (por ejemplo, un dato que caduca y que otra parte del código necesita a tiempo). **Excepción decidida para `kafka-send-timeout`** (§3): en esa regla, la propiedad es la cadencia o el timeout de la ruta comparado con la cota efectiva del productor.
- **FP** solo cuando el repositorio **demuestra**, con `file:line`, que no se incumple nada:
  - **detección:** el patrón no está;
  - **alcanzabilidad:** no hay ruta alcanzable (v1 §2);
  - **contexto:** en esa ruta, ninguna condición plausible incumple la propiedad. Por ejemplo: la espera tiene cota y nada exige un plazo; nada más comparte el hilo; la transacción del llamador ya está confirmada.
- **U** cuando el repositorio no deja decidir, y en particular **cuando falta configuración decisiva**. Por ejemplo: el pool, el executor o la cota están fuera del repositorio; el llamador o el publicador están fuera; el código es API pública de una biblioteca sin llamadores internos vivos. La falta de evidencia nunca es FP.
- **Una pausa deliberada no decide nada por sí misma.** Un `sleep` que simula latencia, espacia peticiones o deja margen:
  - es **TP** si el repositorio muestra una espera sin cota, o un plazo o una frescura exigidos que el retraso incumple;
  - es **FP** si el repositorio demuestra que la espera tiene cota y que nada exige plazo;
  - es **U** si falta la configuración que lo decide.
  Esto sustituye la regla fija de v1 §3.1 (número de hilos del scheduler).

## 2. Aparte del veredicto: gravedad, utilidad de corregir y Overstated

Se registran por separado y **ninguno decide el veredicto**.

- **Gravedad:**
  - **CRITICAL:** solo para las reglas que pasan la selección de desarrollo (`criterio-v2-desarrollo/`: n ≥ 15, ≥ 5 repos, TP/n ≥ 0,90 con U como no-TP, e impacto grave justificado por escrito) **y** quedan validadas según el **pre-registro de TC5**, que fija la población, el muestreo, los umbrales por regla y por lenguaje, y qué pasa si falta evidencia. Ese pre-registro es el procedimiento de confirmación; este documento no lo sustituye.
  - **WARNING:** todo lo demás.
  - **Un TP puede ser WARNING.**
- **Utilidad de corregir:** si arreglarlo merece la pena en ese repositorio. Un TP de impacto mínimo sigue siendo TP.
- **Overstated:** el mensaje atribuye un impacto que el código no sostiene. Nunca es motivo de FP.

## 3. Por regla: propiedad y condición plausible

| Regla | Propiedad que se incumple | Condición plausible que hace TP | FP por contexto (ejemplos, no exhaustivo) |
|---|---|---|---|
| `blocking`, `blocking-kafka` | el hilo anclado (scheduler, executor de `@Async`, listener de Kafka, evento) no se queda bloqueado sin cota, y los trabajos que el repositorio obliga a cumplir un plazo lo cumplen | la espera no tiene cota, de modo que otro trabajo de ese hilo o pool, o el propio, puede no ejecutarse nunca; o tiene cota, pero el repositorio exige un plazo o una frescura que el retraso incumple | la espera tiene cota y nada exige plazo; nada más usa el hilo y la pausa es el trabajo deliberado del propio job |
| `kafka-send-timeout` | **la cadencia o el timeout de la ruta**, comparados con la **cota efectiva del productor** (`max.block.ms` + `delivery.timeout.ms`; por defecto, en Apache Kafka, 60 s y 120 s) | `.send(..).get()` sin timeout en una ruta programada o de petición, cuya cota efectiva supera la cadencia o el timeout de esa ruta | el productor está configurado, en el repositorio, con una cota dentro de la cadencia o el timeout de la ruta |
| `transactions` | **lo que afirma su mensaje**: el método se ejecuta en una transacción nueva en el hilo del executor, nunca en la del llamador, así que el rollback del llamador no lo deshace y el método no ve los cambios del llamador aún sin confirmar | una ruta alcanzable lo llama **con la transacción del llamador abierta**, y una de esas dos consecuencias rompe algo de lo que depende el código. Por ejemplo, relee datos que el llamador acaba de escribir y aún no ha confirmado (TC4 J053), o el llamador cuenta con que su rollback lo deshaga. **Nunca por la mera combinación** `@Async` + `@Transactional` | ver la nota de abajo |
| `reactor-block` | los hilos no bloqueantes de Reactor no se bloquean | la llamada puede ejecutarse en un hilo de event loop, `parallel` o `single` | se ejecuta en un hilo que puede bloquear |
| PYVIBE-001/002/004/007/008/009/010/011/016/018 (bloqueo en `async def`) | el event loop no se bloquea (contrato de asyncio) | la llamada se ejecuta en el loop mientras este atiende otro trabajo (peticiones, otras tareas) | solo en el arranque antes de servir, o en el cierre final sin otro trabajo en el loop; en un hilo (`to_thread`, executor) |
| PYVIBE-003/015 (loop anidado) | no se arranca un loop dentro de otro | alcanzable con un loop en marcha | solo alcanzable sin loop en marcha |
| PYVIBE-005 (Celery sin límite de tiempo) | la tarea termina o se corta | puede colgar en E/S externa y no hay un límite duro efectivo | **solo** un `task_time_limit` duro efectivo en el pool usado. Un `task_soft_time_limit` no basta: lanza una excepción que la tarea puede capturar (Celery, Workers Guide, «Time Limits») |
| PYVIBE-006 (ContextVar sin reset) | el valor no se filtra a trabajo posterior | trabajo posterior en el mismo contexto puede verlo | el contexto se descarta tras la llamada |
| PYVIBE-012/014 (tarea descartada) | dos campos separados, ver la nota de abajo | | |
| PYVIBE-013 (gather) | los fallos de los awaitables se observan | algún awaitable puede lanzar en un fallo normal y los demás siguen sin observarse | todos los awaitables contienen sus excepciones |
| PYVIBE-017 (`except` vacío) | los errores que importan no se tragan | puede tragarse `KeyboardInterrupt`/`SystemExit`, o errores relevantes en una ruta normal | — |

**`transactions`: WARNING como máximo, y la regla solo alerta de lo que afirma su mensaje.**

- **Sin alerta, porque ahí el mensaje es falso:**
  - propagación `NOT_SUPPORTED`, `NEVER` o `SUPPORTS`: no se abre ninguna transacción nueva;
  - `@TransactionalEventListener` en fase `AFTER_COMMIT`, la fase por defecto: el llamador ya ha confirmado;
  - autoinvocación (`this.metodo()`, sin pasar por el proxy): no se aplican las anotaciones.
- **No son excepciones universales:** no son la lista completa de FP ni dan por resuelto el contexto en el resto. Cualquier otra combinación necesita la dependencia de la fila de la tabla para ser TP.
- **Si no puede aportar contexto:** cuando la regla no es capaz de aportar el llamador con transacción abierta y la dependencia, **se desactiva**.
- **Trabajo futuro:** una regla distinta, «`@Async` llamado desde una transacción abierta», cubriría el riesgo de leer antes del commit en cualquier `@Async`, tenga o no `@Transactional`. Necesitará su propia validación.

**PYVIBE-012/014: dos campos separados por caso.**

- **(a) Contrato.** Se incumple la recomendación de retención de `asyncio.create_task` (documentación de Python, `asyncio.create_task`: «Save a reference to the result of this function, to avoid a task disappearing mid-execution»). Vale **sí** cuando no se conserva ninguna referencia a la tarea en ninguna parte.
- **(b) Escenario de fallo funcional respaldado por código: sí / no / U.**
  - **sí:** el código muestra un fallo funcional, más allá de una línea de log, si la tarea falla o desaparece. Por ejemplo:
    - una excepción no capturada dentro de la tarea deja un estado a medias (un registro en `processing` para siempre, un trabajo pedido por el usuario que no se hace sin que nadie lo sepa);
    - un bucle de fondo muere en el primer error y el servicio deja de hacer su trabajo;
    - la tarea espera un future que nada más referencia, de modo que puede ser recolectada antes de terminar.
  - **no:** el código muestra que no hay tal fallo. Por ejemplo:
    - el cuerpo contiene sus excepciones y deja un estado coherente;
    - la tarea solo hace trabajo no funcional (mensajes, precalentamiento opcional cuyo fallo no cambia el resultado).
  - **U:** depende de código o configuración que no está en el repositorio, o no se puede decidir.
- **Para la selección CRITICAL cuenta (b), no (a).** (a) se registra siempre.

## 4. Ejemplos

Los ejemplos con ID salen de TC2–TC4. Sus etiquetas v2 son las de `criterio-v2-desarrollo/PROPUESTA-v2.md` (propuestas por Claude; las confirmadas por Joaquín se indican). Los marcados como *ilustrativos* no salen de ningún corpus.

### 4.1 Positivos (TP)

| Caso | Regla | Ruta | Condición plausible y propiedad |
|---|---|---|---|
| TC4 J053 (`VIJAYAPANDIANT/fixit-hub`), **confirmado por Joaquín** | `transactions` | `ingestEvent`, `@Transactional` (`IngestionServiceImpl.java:46`), llama a `diagnoseIssueAsync` solo para issues nuevos (`:155–156`) | la rama local sin API es rápida (`AIDiagnosticServiceImpl.java:124–130`), y el worker relee el issue por id en su propia transacción y descarta el resultado sin avisar si no lo encuentra (`:143–146`). Si lee antes del commit del llamador, se pierde el diagnóstico: es la consecuencia «no ve los cambios sin confirmar» que afirma el mensaje |
| TC4 J058 (`ysy0915/chat-system`) | `blocking` | `@Scheduled` de `ModelAutoChatService.java:59–94` | `Future.get()` sin timeout sobre una llamada LLM: el hilo del scheduler puede quedar bloqueado sin cota |
| TC3 J017 (`ldcsaa/hp-soa`) | `kafka-send-timeout` | job `sendMqEvent` con `cron = "*/3 * * * * ?"` (`hp-demo/hp-demo-kafka/.../DomainEventSenderJobHandler.java:23`) → `op.send(rc).get()` (`AbstractKafkaDomainEventSender.java:84`) | el productor no fija `max.block.ms` ni `delivery.timeout.ms` (`misc/nacos/config/namespace-DEV/GLOBAL_GROUP/kafka.yml:5–26`), así que la cota efectiva es la de Kafka por defecto (60 s + 120 s), muy por encima de la cadencia de 3 s |
| TC3 P008 (`apowerb/apowerb`) | PYVIBE-009 | ruta HTTP `upload_complete`, `src/apowerb/routers/files.py:212–213,246–253` | `open()` y lecturas síncronas de fragmentos en el loop mientras el servidor atiende otras peticiones |

### 4.2 Negativos (FP)

| Caso | Regla | Condición que falla | Por qué |
|---|---|---|---|
| TC2 J056 (`terrakube-io/terrakube`) | `blocking` | contexto | `poll()` hace `join()` sobre tareas de un pool propio (`AzDevOpsPollingService.java:101–110`). Cada tarea solo hace llamadas con cota: HTTP con connect 5 s, respuesta 30 s y espera de pool 2 s (`WebhookHttpClientConfig.java:33–46`, usado en `WebhookServiceBase.java:125–128`) y token SP/MI con `block(30 s)` (`AzDevOpsTokenService.java:115`). El `join()` sí retrasa al otro job `fixedDelay` (`CliAuthSessionCleanupTask.java:19`), porque con `SimpleAsyncTaskScheduler` las tareas `fixedDelay` comparten un solo hilo (Spring, «TaskScheduler implementations»). Pero la purga no tiene plazo exigido: las sesiones caducadas se rechazan al usarlas (`CliLoginService.java:228`) |
| TC2 J015 (`quarkusio/quarkus`, fixture) | `blocking` | contexto | `Thread.sleep(100)` en el job `increment()` con `cron = "*/1 * * * * ?"` (`integration-tests/opentelemetry-quartz/.../Counter.java:24–27`), igual que `FailedBasicScheduler.java:10–13`. Es un fixture, y ni la cadencia del propio job ni la del otro son una propiedad (§1); el módulo no exige ningún plazo |
| TC2 P083 (`not-sekiun/Consortium`) | PYVIBE-009 | contexto | `open()` solo en el arranque, antes de servir (`start_server.py:49`, servidor en `:154–155`) |
| TC2 P099 (`OtoDock/oto-dock`) | PYVIBE-009 | alcanzabilidad | script manual de humo (`mcps/custom/tts-mcp/live_smoke.py`) |
| TC4 J056/J057 (`wujun728/jun_java_plugin`) | `blocking` | alcanzabilidad | el único llamador es un test (`ApplicationTests.java:31,33`) |
| TC4 J001 (`Angular2Guy/AngularPortfolioMgr`) | `transactions` | contexto, sin alerta (§3) | `@TransactionalEventListener` con fase por defecto `AFTER_COMMIT` (`KafkaProducer.java:57–60`): cuando se ejecuta, la transacción del llamador ya se ha confirmado, así que lo que afirma el mensaje no se cumple |

### 4.3 Indeterminados (U)

| Caso | Regla | Qué no deja decidir el repositorio |
|---|---|---|
| TC4 J032/J033 (`mrtylerzhou/AntFlow-activiti`) | `blocking` | la única cadena interna está muerta: `notifyCurrent` no tiene llamadores (`NotifyServiceImpl.java:168`) y la sobrecarga de 2 argumentos de `MessageUtils.sendMessageBatch` tampoco (`MessageUtils.java:44`). Pero son métodos públicos de un motor pensado para integrarse en otras aplicaciones, que pueden llamarlos desde fuera |
| TC2 J052 (`risesoft-y9/WorkFlow-Engine`) | `blocking` | `saveToEs` duerme 3 s por cada proceso que termina (`Process4CompleteUtilServiceImpl.java:283–299`, llamado en `TaskListener4ProcessCompleted.java:61`). La app activa `@EnableAsync` (`ProcessAdminApplication.java:23`) sin definir executor, así que el executor efectivo puede venir de los starters `risenet-y9boot-starter-*` (`risenet-y9boot-server-processadmin/pom.xml:37,49,66`), que están fuera del repositorio. Falta la configuración decisiva |
| TC4 P058 (`riteshbonthalakoti/HELPDESK.AI`) | PYVIBE-012 | el código está en un virtualenv de CI comiteado (`.tmp-ci-venv/.../realtime/_async/channel.py:247`), y no se demuestra que la aplicación use esa copia |

## 5. Qué cambia respecto a v1

- **§1:** el TP se define por una propiedad incumplida en una condición plausible, no por «se cumplen detección, contexto y alcanzabilidad». La alcanzabilidad (v1 §2) y la exclusión c2 de repositorios de estudio no cambian.
- **FP exige demostración.** Si falta la configuración decisiva, el caso es U.
- **Cadencias.** La cadencia de un job no es una propiedad salvo que el repositorio exija un plazo o una frescura. La excepción es `kafka-send-timeout`, que la compara con la cota del productor.
- **Pausas deliberadas.** v1 §2.3 decía que una pausa deliberada no hace FP. v2 mantiene que tampoco hace TP por sí misma: decide si la espera tiene cota y si hay un plazo exigido.
- **v1 §3.1** (número de hilos del scheduler) queda absorbido en la condición plausible de `blocking`. Su afirmación sobre los hilos virtuales era incorrecta para `fixedDelay` (nota del 2026-11-03 en v1).
- **`transactions`:** pasa a WARNING como máximo, solo alerta de lo que afirma su mensaje, no alerta en los casos de §3 y se desactiva si no puede aportar contexto.
- **PYVIBE-005:** solo un límite duro efectivo hace FP.
- **PYVIBE-012/014:** se separan (a), el contrato, y (b), el escenario de fallo funcional. Para CRITICAL cuenta (b).
- **Gravedad, utilidad de corregir y Overstated** se registran aparte (§2). La confirmación CRITICAL remite al pre-registro de TC5.

## 6. Uso

- **Evaluación de desarrollo:** `criterio-v2-desarrollo/`, asistida y declarada como tal. Las etiquetas v2 las propone Claude y las confirma o corrige Joaquín. La población de selección es solo TC3 + TC4; TC2 aporta ejemplos auxiliares.
- **TC5:** su pre-registro copia literalmente §1, §2 y §3 de este documento y cita su versión.
- **Instrucciones de IA:** las que apliquen v2 serán un documento nuevo; `REVIEW-AI-INSTRUCTIONS.md` (v1) no se toca.

## 7. Registro de cambios

- **2026-11-03 (primera redacción):** decisiones A de Joaquín.
- **2026-11-03 (revisión):** decisiones de Joaquín sobre las segundas opiniones de Codex (`~/vibe-guard-evaluation-work/second-opinions/2026-11-03-criterio-v2/` y `…/2026-11-03-review-criteria-v2/`):
  1. **J056:** comprobado que el `join()` tiene cota y que la purga no tiene plazo, así que es FP. Corregidos el ejemplo de v2 y la nota de v1 §6.
  2. **Frontera FP/U:** FP solo si el repositorio demuestra que no se incumple nada; U si falta configuración decisiva.
  3. **Cadencias:** la cadencia del propio job no es una propiedad salvo plazo o frescura exigidos.
  4. **`transactions`:** opción (a), la regla solo alerta de lo que afirma su mensaje. «`@Async` desde transacción abierta» queda como trabajo futuro.
  5. **J053:** pasa de U a TP y es el ejemplo positivo real de `transactions`.
  6. **`kafka-send-timeout`:** la propiedad es la cadencia o el timeout de la ruta frente a la cota efectiva del productor. Comprobado en TC3 J017.
  7. **Celery:** FP solo con `task_time_limit` duro efectivo.
  8. **§2:** la confirmación CRITICAL remite al pre-registro de TC5.
