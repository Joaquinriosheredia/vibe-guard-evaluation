# REVIEW-CRITERIA v1 — TP / FP / U with explicit reachability

Version **v1** (2026-10-28). Decided by Joaquín on the open points of the draft in PR #18.
It applies to new reviews and to the next corpus's pre-registration. It does **not** change
any published verdict: `test-corpus-{1,2,3}/audit-joaquin.json`, their metrics and results
stay as published. How the published verdicts read under v1 is in §6, apart.

Source of the examples: the 15 cases where the 2026-10-27 calibration
(`calibration-2026-10-27/`) disagreed with Joaquín, plus P027/P028 (TC3) for PYVIBE-012.
Joaquín's verdicts and reasons come from `test-corpus-{2,3}/audit-joaquin.json`. The AI
reviewers' own reasons for these cases were lost with the raw outputs (see
`calibration-2026-10-27/README.md`); only their A/B verdicts survive.

The corpus-neutral instructions for AI reviewers that apply this file are
`REVIEW-AI-INSTRUCTIONS.md` (§7).

## 1. The three conditions

- **TP** when all three hold, each with `file:line` evidence opened at the pinned commit:
  1. **Detection:** the pattern the rule names is there.
  2. **Context:** the conditions the rule's impact needs hold there (§3 and §5).
  3. **Reachability:** the code runs in the normal operation of an application (§2).
- **FP** when the repository shows that one of 1–3 is false.
- **U** when the repository does not let 1–3 be decided (the caller, the thread or the
  configuration lives outside it).
- **Overstated** is recorded apart and is never a reason for FP. Of the 12 calibration
  failures that Joaquín judged TP, 7 are TP *and* Overstated.

## 2. Reachability

### 2.1 A production path inside the repository = reachable

If the callers, followed inside the repository, reach an entry point of normal operation
(an HTTP route, a message loop, a listener, `@Scheduled`/`@Async` with its anchor live, a
registered tool, a task runner), the code is reachable. A registration (tool table, listener
configuration, an `async for` consumer) counts as an entry point. How rarely the path runs
does not matter, nor that one branch of it returns early: an "unreachable" claim needs
evidence for **every** path that reaches the code.

| Case | Rule | Joaquín | A / B | The path Joaquín followed |
|---|---|---|---|---|
| TC2 P073 | PYVIBE-009 | TP | FP / FP | `open()` in async generator `open_read()` (`backend/storage/files.py:208–212`), consumed by `async for` in `backend/storage/__init__.py:76`. The AIs argued the only backend returns early. |
| TC2 P126 | PYVIBE-007 | TP | FP / FP | `subprocess.run(timeout=15)` in `_self_uninstall_and_exit` (`satellite/transport/lifecycle_update.py:165–169`), awaited from `ws_client.py:453,834` and `create_task` at `:1083`. |
| TC2 P127 | PYVIBE-007 | TP | FP / FP | Same coroutine, `lifecycle_update.py:188`, same callers. |
| TC3 P050 | PYVIBE-009 | TP | FP / FP | Sync `open()`/`json.load`/`json.dump` in async `_handle_notebook_edit` (`packages/core/ai/tools/code_tool.py:1301–1326`), registered as tool `notebook_edit` at `:1447`. |
| TC3 P075 | PYVIBE-009 | TP | FP / FP | Sync `open()`/`read()` in async `_ensure_public_url` (`packages/core/tasks/media_tasks.py:2859–2860`), on the video job path run through `_run_async`. |
| TC2 J052 | blocking | TP | invalid / invalid | `Thread.sleep(3000)` in `@Async saveToEs` (`Process4CompleteUtilServiceImpl.java:299`), `@EnableAsync` live, reached from a Flowable completion listener. |

### 2.2 Startup, shutdown and self-uninstall paths

- **TP** when the path is triggered by a message or event **on the live loop while the loop
  still serves other work** (P126/P127: `_self_uninstall_and_exit`, reached from the
  WebSocket message loop).
- **FP** only when the code runs at process **startup** (before serving) or at **final
  shutdown, with no other work left on the loop** (TC2 P083: `start_server.py:49`, `open()`
  before serving requests).

### 2.3 Demo, playground and fixture applications: reachable within their own app

Reachability is judged **inside the application the code belongs to.** A fixture app, a
playground app or a sample app is an application: if its own entry point (`@Scheduled`,
`main`, a route) runs the code, condition 3 holds, whether or not the app ships.

| Case | Where | Joaquín (published) | A / B | v1 |
|---|---|---|---|---|
| TC2 J001 | `bage2014/study` → `study-spring-boot-zipkin/…/SampleBackground.java:41` (`@Async background()`), called from route `/async` at `SampleController.java:85–88`; `@EnableAsync` at `SampleZipkinApplication.java:31` | FP | TP / TP | **TP** (§6) |
| TC2 J015 | `quarkus` → `integration-tests/opentelemetry-quartz/…/Counter.java:26` | TP | FP / FP | TP |
| TC3 J001 | `axelix` → `playgrounds/feature-service-maven-sb-3/…/BookTestDataQueryRunner.java:22–25` | TP (Overstated) | FP / FP | TP |
| TC3 J003 | `axelix` → `playgrounds/spring-petclinic-maven-sb-2/…/SchedulerTestConfig.java:49–57` | TP (Overstated) | FP / FP | TP |

- That a sleep is deliberate (it simulates latency or load) does not make it FP: the
  application still runs it on that thread.
- **Unchanged:** code reached only from test sources (`src/test/…`, `tests/…`), benchmarks,
  manual scripts or docs is FP by reachability (TC2 P099: `mcps/custom/tts-mcp/live_smoke.py`,
  a manual smoke-test script). `src/main` of a fixture app is not a test source (J015).

### 2.4 Study repositories: excluded at corpus triage, not judged

A repository whose purpose is study (one module per topic, notes, a learning path) is not
judged finding by finding: it is **excluded at triage**, before any scan, by a mechanical
rule. The rule below is to be copied verbatim into the next corpus's `PREREGISTRATION.md`
as an exclusion next to the toy filter (test-corpus-2/3 exclusion **c**), and implemented in
its `select.mjs`.

**Exclusion c2 — study repositories.** A candidate is excluded when any of these holds
(case-insensitive):

1. **Name:** the **last** token of the repository name, split on non-alphanumeric
   characters only (not on camelCase), is `study`, `studies`, `learning` or `notes`, and the
   token before it is not one of `machine deep reinforcement federated transfer meta active
   contrastive online incremental`.
2. **Description:** its tokens (split as in the toy filter) contain one of the consecutive
   pairs `study notes`, `learning notes`, `for learning`, `for study`, `learning purpose`,
   `learning purposes`, `learning project`, `study project`; or the description contains
   one of the substrings `学习笔记`, `学习记录`, `学习项目`, `练手`.
3. **Topics:** a topic is exactly `study`, `studies`, `study-notes`, `learning-notes` or
   `notes`.

Dry run on the descriptions and names of the test-corpus-2 and test-corpus-3 candidates
(1,252 and 1,271 unique repositories; their `candidates.json` has no topics, so 3 is not
tested): 5 hits in each, all study repositories — `zhisheng17/flink-learning`,
`moshowgame/spring-cloud-study`, `bage2014/study`, `zeroaihub/Java-Agent-Study`,
`kilerhg/Python-Studies`. Wider variants were rejected because they hit products: a bare
`learn`/`学习` token (`liyupi/yu-ai-learn`, `roncoo/roncoo-education`), `仅供学习使用` (a common
disclaimer on real products, `Yzw202011/OmniSpace`), camelCase splitting of the name
(`OpenStudy`, `StudyPilot`).

## 3. Context

### 3.1 A deliberate wait on the scheduler thread (J056 type)

When the blocking call is the **designed wait of a scheduled job whose work runs on another,
dedicated pool** (J056: `CompletableFuture.allOf(...).join()` over tasks on `pollExecutor`,
`AzDevOpsPollingService.java:101–110`, `@Scheduled(fixedDelay…)` at `:82`), the verdict depends on whether other
scheduled tasks can starve:

- **TP** when the application has other `@Scheduled` jobs **and** the scheduler is not
  configured with more than one thread (Spring's default scheduler has one).
- **FP** otherwise: no other scheduled job in the application, or a scheduler pool of more
  than one thread, or a scheduler that starts a new thread per run. Spring Boot ≥ 3.2 with
  `spring.threads.virtual.enabled=true` uses `SimpleAsyncTaskScheduler`, one virtual thread
  per run, so nothing waits behind the job.
- **U, never FP**, when the repository does not let you determine the scheduler pool, its
  configuration or whether other `@Scheduled` jobs exist (for example, the pool size or the
  virtual-thread switch comes from an environment variable or a profile outside the
  repository, or jobs are registered from a dependency).

Scope: this applies to designed waits. A blocking call that **is** the job's own work
(a `Thread.sleep` in the job, J015, TC3 J001/J003) stays under the rule criteria (§5): the
job's thread is blocked whatever the pool.

### 3.2 `kafka-send-timeout`

| Case | Joaquín | A / B | Joaquín's reason |
|---|---|---|---|
| TC3 J017 | TP (Overstated) | invalid / invalid | `AbstractKafkaDomainEventSender.java:84`: `op.send(rc).get()` with no timeout inside `executeInTransaction`, reached from handlers scheduled every 3 s |

An untimed `.get()` on a scheduled or request path is TP. The real bound depends on
`max.block.ms`/`delivery.timeout.ms`; a message that quotes those bounds without the
configuration in the repository is **Overstated**, not FP.

### 3.3 PYVIBE-006 (ContextVar without reset)

| Case | Joaquín | A / B | Joaquín's reason |
|---|---|---|---|
| TC3 P044 | TP (Overstated) | FP / FP | `tool_effect_intents.py:237` sets the ContextVar with no restore, called from the main tool-execution flow (`tool_execution.py:829,1091`) |

TP when later work **in the same context** (the rest of the task, the next step in the same
task) can see the value. FP only when the repository shows the context is discarded right
after the call (a `copy_context().run`, a fresh task per call). That a ContextVar does not
leak *between* tasks makes a cross-task message Overstated, not FP.

### 3.4 PYVIBE-012/014 (discarded task): any discarded reference is TP

The rule's message names two impacts: (i) the task can be garbage-collected before it
finishes; (ii) an exception it raises is never retrieved.

- **TP** when no reference to the task is kept anywhere (a set, a registry, a callback that
  retains it). Impact (i) alone suffices.
- A task body that catches its exceptions does **not** make it FP. It makes the finding
  **Overstated** when the message claims that exceptions are lost.

| Case | Location | Joaquín (published) | A / B | v1 |
|---|---|---|---|---|
| TC3 P026 | `backend/app/api/kline.py:1009` | FP | TP / TP | **TP, Overstated** (§6) |
| TC3 P027 | `kline.py:1164` | TP | — | TP |
| TC3 P028 | `kline.py:1251` | TP | — | TP |
| TC2 P153 | `satellite/transport/ws_client.py:1000–1002` | TP | TP / FP | TP |

## 4. Tooling: corpus-neutral instructions and repository-relative citations

TC2 J052 and TC3 J017 were invalid in both reviews for tooling reasons, not judgement ones:

- **J052:** the instructions used for both corpora (`test-corpus-3/REVIEW-AI-INSTRUCTIONS.md`)
  name `~/vibe-guard-evaluation-work/tc3/` and forbid reading `…/tc2/`, where the TC2
  checkout lived. **Fixed:** `REVIEW-AI-INSTRUCTIONS.md` at the root of this repository names
  no corpus and no path; the checkout is the reviewer's working directory, the card is in the
  prompt. `test-corpus-3/REVIEW-AI-INSTRUCTIONS.md` stays as it was frozen.
- **J017 (and J052's second attempt):** citations by bare file name
  (`AbstractKafkaDomainEventSender.java:17-30`) were rejected as "no such file in the
  repository", and the single re-ask got no hint. **Fixed in `vibe-guard-scan`**
  (`fix/review-citation-hint`): the contract stays strict (paths relative to the repository
  root), and the problem now names the matching repository-relative paths, so the re-ask can
  cite the full one.

## 5. Rule criteria v1 (condition 2)

The test-corpus-2/3 table, with the v1 changes in **bold**.

| Rule | TP context | FP context (examples, not exhaustive) |
|---|---|---|
| `blocking`, `blocking-kafka` | the blocking call runs on the anchored pool (an `@Async` executor with `@EnableAsync`, a scheduler, an event, a Kafka listener thread) on a normal path | the anchor is inert, or the call does not block (a completed future); **a designed wait on the scheduler thread with no starvation (§3.1)** |
| `kafka-send-timeout` | an untimed `.send(..).get()` on a normal path | the producer is configured so the call cannot wait beyond the message's bound |
| `transactions` (critical) | `@Transactional` and Spring's `@Async` on the same proxied method | not a Spring proxy, or not Spring's annotations |
| `reactor-block` (critical) | the call can run on a non-blocking Reactor thread (event loop, `parallel`, `single`) | it runs on a thread that may block (virtual, `@Async`, `boundedElastic`, startup, servlet worker) |
| PYVIBE-001/002/004/007/008/009/010/011/016/018 (blocking in `async def`) | the call runs on the event loop on a request or task path, **including a shutdown or self-uninstall path triggered while the loop serves other work** | the code runs only at **process startup or final shutdown with no other work on the loop**, in a thread (`to_thread`, executor), or in a `def` only called off the loop |
| PYVIBE-003/015 (nested loop) | reachable while a loop is running | only reachable with no running loop |
| PYVIBE-005 (Celery without a time limit) | the task can hang on external I/O and no global limit is set in the repository | a global `task_time_limit`/`task_soft_time_limit` covers it |
| PYVIBE-006 (ContextVar without reset) | the value can leak to later work sharing the context, **including later steps of the same task** | the context is discarded after the call |
| PYVIBE-012/014 (discarded task) | no reference to the task is kept anywhere, **whether or not the body catches its exceptions** | a reference is kept (a set, a registry, a callback attaching it) |
| PYVIBE-013 (gather) | some gathered awaitable can raise on a normal failure, and the others then run unobserved | every awaitable contains its exceptions |
| PYVIBE-017 (empty `except`) | it can swallow `KeyboardInterrupt`/`SystemExit`, or errors that matter on a normal path | — |

A rule not listed falls back to conditions 1–3.

## 6. Re-labelled under criterion v1

Informative only. The published `audit-joaquin.json` files, `metrics.json`, `METRICS.md`
and results are not changed; a corpus's numbers stay those of its own pre-registration.

| ID | Original (published) | New (v1) | Reason |
|---|---|---|---|
| TC2 J001 | FP | TP | §2.3: reachable within its own app (route `/async`, `SampleController.java:85–88`, calls the `@Async` `background()`; `@EnableAsync` at `SampleZipkinApplication.java:31`); a deliberate latency sleep is still a sleep on that thread. In a new corpus `bage2014/study` would be excluded at triage (§2.4, name token `study`). |
| TC3 P026 | FP | TP, Overstated | §3.4: the reference from `create_task` at `kline.py:1009` is discarded; the caught `Exception` only makes "never retrieved" Overstated. Now consistent with P027/P028. |

Checked under v1 and **unchanged**: every other non-TP verdict of both audits.

- TC2 J056 stays **FP** (§3.1): the API module has another `@Scheduled` job
  (`CliAuthSessionCleanupTask.java:19`) and no scheduler pool size, but
  `api/src/main/resources/application.properties:4` sets `spring.threads.virtual.enabled=true`
  on Spring Boot 4.1.1 (`pom.xml:9`), so each run gets its own virtual thread and nothing
  starves.
- TC2 P083 stays FP (startup only, §2.2); TC2 P099 stays FP (manual script, §2.3).
- TC2 P002, P065 (PYVIBE-013), P046 (PYVIBE-005 on a non-Celery app), TC3 P035
  (PYVIBE-017), P097 (PYVIBE-018): no v1 point touches them.

The calibration agreement under v1 (informative, same caveat): A and B both said TP on
TC2 J001 and TC3 P026, so A rises to 40/52 and B to 39/52.

## 7. Using this file

- AI reviews: `REVIEW-AI-INSTRUCTIONS.md` (root) embeds §1, §2, §3 and §5 as rules.
- Next corpus: its pre-registration copies §1, §5 and exclusion c2 (§2.4) word for word,
  and names this file's version (v1).
