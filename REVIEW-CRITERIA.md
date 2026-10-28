# REVIEW-CRITERIA — TP / FP / U with explicit reachability (DRAFT)

Status: **draft**, not yet a pre-registration. Points marked **[DECIDE JOAQUÍN]** cannot be
settled from Joaquín's existing verdicts; they need a decision before this file is used to
write AI review instructions or a new corpus's pre-registration.

Source of the examples: the 15 cases where the 2026-10-27 calibration
(`calibration-2026-10-27/`) disagreed with Joaquín. Joaquín's verdicts and reasons come from
`test-corpus-{2,3}/audit-joaquin.json`. The AI reviewers' own reasons for these cases were
lost with the raw outputs (see `calibration-2026-10-27/README.md`); only the A/B verdicts
survive, so "why the AI failed" below is inferred from the verdict and from
`test-corpus-{2,3}/FP-ANALYSIS.md`, not quoted.

## 1. The three conditions (unchanged from test-corpus-1/2/3)

- **TP** when all three hold, each with `file:line` evidence opened at the pinned commit:
  1. **Detection:** the pattern the rule names is there.
  2. **Context:** the conditions the rule's message needs for its impact hold there (the
     rule-criteria table of `test-corpus-3/PREREGISTRATION.md`).
  3. **Reachability:** the code runs in the normal operation of an application (§2).
- **FP** when the repository shows that one of 1–3 is false.
- **U** when the repository does not let 1–3 be decided (the caller, the thread or the
  configuration lives outside it).
- **Overstated** is recorded apart and is never a reason for FP. Of the 12 cases below that
  Joaquín judged TP, 7 are TP *and* Overstated: an exaggerated message does not make the finding false.

## 2. Reachability

### 2.1 A production path inside the repository = reachable

If the callers, followed inside the repository, reach an entry point of normal operation
(an HTTP route, a message loop, a listener, `@Scheduled`/`@Async` with its anchor live, a
registered tool, a task runner), the code is reachable. It does not matter how rarely the
path runs, or that one branch of it returns early: an "unreachable" claim needs evidence for
**every** path that reaches the code.

| Case | Rule | Joaquín | A / B | The path Joaquín followed |
|---|---|---|---|---|
| TC2 P073 | PYVIBE-009 | TP | FP / FP | `open()` in async generator `open_read()` (`backend/storage/files.py:208–212`), consumed by `async for` in `backend/storage/__init__.py:76`. The AIs argued the only backend returns early. |
| TC2 P126 | PYVIBE-007 | TP | FP / FP | `subprocess.run(timeout=15)` in `_self_uninstall_and_exit` (`satellite/transport/lifecycle_update.py:165–169`), awaited from `ws_client.py:453,834` and `create_task` at `:1083`. |
| TC2 P127 | PYVIBE-007 | TP | FP / FP | Same coroutine, `lifecycle_update.py:188`, same callers. |
| TC3 P050 | PYVIBE-009 | TP | FP / FP | Sync `open()`/`json.load`/`json.dump` in async `_handle_notebook_edit` (`packages/core/ai/tools/code_tool.py:1301–1326`), registered as tool `notebook_edit` at `:1447`. |
| TC3 P075 | PYVIBE-009 | TP | FP / FP | Sync `open()`/`read()` in async `_ensure_public_url` (`packages/core/tasks/media_tasks.py:2859–2860`), on the video job path run through `_run_async`. |
| TC2 J052 | blocking | TP | invalid / invalid | `Thread.sleep(3000)` in `@Async saveToEs` (`Process4CompleteUtilServiceImpl.java:299`), `@EnableAsync` live, reached from a Flowable completion listener. |

Criterion: **follow every caller to an entry point; a registration (tool table, listener
config, `async for` consumer) counts as an entry point.** Do not downgrade to FP because a
path is uncommon or because one of several branches exits early.

- **[DECIDE JOAQUÍN] Shutdown / self-uninstall paths.** P126/P127 run inside
  `_self_uninstall_and_exit`. The pre-registration's FP context for blocking rules says "the
  code runs only at startup or shutdown". Joaquín's TP implies that a shutdown path
  *triggered by a message on the live loop, while the loop still serves other work*, is
  normal operation. Confirm that reading, and whether the table row should say "only at
  process startup or final shutdown, with no other work on the loop".

### 2.2 Demo, playground, study and fixture code

These are the cases where the verdicts do not yet form one rule:

| Case | Where | Joaquín | A / B | Joaquín's reason |
|---|---|---|---|---|
| TC2 J001 | `bage2014/study` → `study-spring-boot-zipkin/…/SampleBackground.java:41` | **FP** | TP / TP | random sleep that simulates latency for Zipkin traces; didactic project |
| TC2 J015 | `quarkus` → `integration-tests/opentelemetry-quartz/…/Counter.java:26` | **TP** | FP / FP | `Thread.sleep(100)` blocks the `@Scheduled` thread |
| TC3 J001 | `axelix` → `playgrounds/feature-service-maven-sb-3/…/BookTestDataQueryRunner.java:22–25` | **TP** (Overstated) | FP / FP | `@Scheduled(cron="*/2 …")` sleeps 10 s, longer than its period |
| TC3 J003 | `axelix` → `playgrounds/spring-petclinic-maven-sb-2/…/SchedulerTestConfig.java:49–57` | **TP** (Overstated) | FP / FP | `@Scheduled` sleeps 120 s holding `reentrantLock` |

In TC3 the AIs also called J002, J004–J006 (same playground classes) FP by reachability
(`test-corpus-3/FP-ANALYSIS.md` §3).

Three of four say: **reachability is judged inside the application the code belongs to.** A
fixture app, a playground app or a sample app is an application; if its own entry point
(`@Scheduled`, `main`) runs the code, condition 3 holds, whether or not the app ships.
TC2 J001 is the exception, and its reason ("simulates latency") reads more like a context
argument (the sleep *is* the demo's purpose) than a reachability one.

- **[DECIDE JOAQUÍN] Rule for demo/playground/fixture apps.** Pick one:
  - (a) *Reachable within its own app* (J015, TC3 J001/J003 stand; TC2 J001 is re-judged
    or re-labelled as FP by context, with that context written down);
  - (b) *Not production unless the repository ships it* (TC3 J001/J003 and J015 become FP;
    then the AI reviews were right on 3 of these 4);
  - (c) keep the distinction by intent: "a deliberate sleep whose purpose is to simulate
    load is FP by context" — needs a definition an AI can apply from the code alone.
- **[DECIDE JOAQUÍN] Learning repositories.** The TC2 A/B disagreement list already had
  "whether a learning repository's demo is production". Decide whether a repository whose
  purpose is study (one module per topic) is treated like (a)/(b) above, or excluded from
  corpora at triage instead of being judged (the java-vibe-guard "Found in the Wild" triage
  already drops demo/tutorial/simulation before the audit).
- **Tests stay FP.** Code reached only from `src/test/…`, `tests/…`, benchmarks, scripts
  or docs is FP by reachability (unchanged). Note that J015 sits under
  `integration-tests/…/src/main/java`: `src/main` of a fixture app is not a test source.

## 3. Context

### 3.1 Blocking on a scheduler thread

| Case | Rule | Joaquín | A / B | Joaquín's reason |
|---|---|---|---|---|
| TC2 J056 | blocking | **FP** | TP / TP | `AzDevOpsPollingService.java:110`: deliberate `join()` with `fixedDelay`; the work runs on `pollExecutor` |

Criterion derived: a blocking call on the scheduler thread is FP by context when it is the
designed wait of a `fixedDelay` job whose work runs on another, dedicated pool (no other
scheduled work is starved by it). Contrast J015, TC3 J001/J003: the sleep itself occupies
the scheduler thread → TP.

- **[DECIDE JOAQUÍN]** Does J056 still hold when the application has other `@Scheduled`
  jobs sharing a single-thread default scheduler? (Spring's default is one thread.) If yes,
  "deliberate" is the deciding factor; if no, the criterion must check the scheduler pool
  size in the repository.

### 3.2 `kafka-send-timeout`

| Case | Joaquín | A / B | Joaquín's reason |
|---|---|---|---|
| TC3 J017 | TP (Overstated) | invalid / invalid | `AbstractKafkaDomainEventSender.java:84`: `op.send(rc).get()` with no timeout inside `executeInTransaction`, reached from handlers scheduled every 3 s |

Criterion: an untimed `.get()` on a scheduled or request path is TP; the real bound depends
on `max.block.ms`/`delivery.timeout.ms`, so a message that quotes those bounds without the
configuration in the repository is **Overstated**, not FP. Both AI answers were invalid for
a tooling reason (citation path), not a judgement one.

### 3.3 PYVIBE-006 (ContextVar without reset)

| Case | Joaquín | A / B | Joaquín's reason |
|---|---|---|---|
| TC3 P044 | TP (Overstated) | FP / FP | `tool_effect_intents.py:237` sets the ContextVar with no restore, called from the main tool-execution flow (`tool_execution.py:829,1091`); does not by itself prove a cross-task leak |

Criterion: TP when later work **in the same context** (the rest of the task, the next tool
call in the same task) can see the value; FP only when the repository shows the context is
discarded right after the call (a `copy_context().run`, a fresh task per call). That a
ContextVar does not leak *between* tasks is an Overstated message, not an FP.

### 3.4 PYVIBE-012 with exceptions captured

| Case | Location | Joaquín | A / B | Joaquín's reason |
|---|---|---|---|---|
| TC3 P026 | `backend/app/api/kline.py:1009` | **FP** | TP / TP | `task()` catches `Exception` and records the failure via `job_store.fail`; the unretrieved-exception risk does not hold |
| TC3 P027 | `kline.py:1164` (not a calibration failure) | **TP** | — | same `create_task(task())`, body catches `Exception`; no reference kept, lifecycle not guaranteed |
| TC3 P028 | `kline.py:1251` (not a calibration failure) | **TP** | — | same as P027 |
| TC2 P153 | `satellite/transport/ws_client.py:1000–1002` | **TP** | TP / FP | reference discarded and no callback retains it; GC/cancellation is a potential risk |

The rule's message names two impacts: (i) the task can be garbage-collected before it
finishes; (ii) an exception it raises is never retrieved. A body that catches `Exception`
removes (ii) but not (i). P026 is FP on (ii); P027/P028/P153 are TP on (i). The
pre-registration row says "TP: no reference to the task is kept anywhere", which supports
P027/P028/P153; the AI instructions' step 4 ("if the callee already handles the failure, the
context does not hold: FP") supports P026.

- **[DECIDE JOAQUÍN] PYVIBE-012 when the body catches `Exception`.** Pick one and re-judge
  the other cases:
  - (a) *Any discarded reference is TP* (impact (i) alone suffices; caught exceptions only
    make it Overstated if the message claims (ii)) → P026 becomes TP;
  - (b) *Caught exceptions make it FP* → P027, P028, and probably P153 (callee logs its own
    errors, `test-corpus-2/FP-ANALYSIS.md`) become FP, and the rule should demand evidence
    of an uncaught raise.
  `test-corpus-3/FP-ANALYSIS.md` §3 already flags this as needed before fixing PYVIBE-012.

## 4. Not a criterion: tooling failures

TC2 J052 and TC3 J017 were invalid in both reviews: J052 because the TC3 instructions forbid
`~/vibe-guard-evaluation-work/tc2/` while the checkout lived there; J017 because the citation
checker resolved a short file name against the wrong root. They count as failures in the
table, but they say nothing about the criteria. Fix: corpus-neutral instructions and
repo-relative citations before the next calibration.

## 5. Summary of the 15 failures by cause

| Cause | Cases | AI direction |
|---|---|---|
| Production path not followed to the end (§2.1) | TC2 P073, P126, P127; TC3 P050, P075 | FP where TP |
| Demo / playground / fixture app (§2.2) | TC2 J001, J015; TC3 J001, J003 | both ways |
| Context: deliberate scheduler wait (§3.1) | TC2 J056 | TP where FP |
| Context: ContextVar in the same task (§3.3) | TC3 P044 | FP where TP |
| PYVIBE-012 with exceptions caught (§3.4) | TC3 P026; TC2 P153 (B only) | both ways |
| Tooling, not judgement (§4) | TC2 J052; TC3 J017 | invalid |
