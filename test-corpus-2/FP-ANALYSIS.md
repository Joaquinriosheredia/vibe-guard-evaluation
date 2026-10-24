# FP analysis — test-corpus-2 (development data from here on)

test-corpus-2 is closed (`main` `65f57e4`, `METRICS.md`): criterion 1 is NOT MET in Java (0.6724)
and Python (0.66), and criterion 2 is NOT MET in Python (13.43 FP/1000). From here on its
findings, cards and verdicts are **development data**: they are used freely to fix the rules,
and nothing measured on them again is evidence for the criteria. The measurement is
test-corpus-3 (`../test-corpus-3/PREREGISTRATION.md`).

**Sources.**
- Verdict of each finding: the final one, i.e. version (a) of `METRICS.md`: Joaquín's where he
  reviewed, otherwise the agreeing verdict of A and B.
- Causes: the reasons in `audit-joaquin.json` and in reviews A (`audit-claude.json`) and B
  (`audit-claude-B.json`), each with file:line, checked against the TC2 checkouts at the pinned
  commits.
- Counts are over the review set (Java: every CRITICAL, 58; Python: a sample of 100 of 168).

## 1. False positives by rule and cause

### Python (34 FP of 100)

| Rule | n | TP | FP | Cause of the FP | IDs | # | Proposed fix |
|---|---|---|---|---|---|---|---|
| PYVIBE-005 (Celery without time limit) | 13 | 0 | 13 | **Detection.** `@task_app.task` of a **Procrastinate** `App` is taken for Celery because the receiver's name contains `app`. The repository has no Celery at all. | P009, P023, P028, P030, P031, P035, P037, P041, P042, P044, P046, P048, P050 | 13 | Count a decorator as Celery's only with Celery provenance in the file: `shared_task` or the receiver imported from `celery`, a module named `celery`/`*celery*`, or a receiver bound to `Celery(...)`. **And demote the rule to WARNING:** with 0 TP in 13, and with the global `task_time_limit` it cannot see (its documented blind spot), a missing per-task limit is not a CRITICAL defect. |
| PYVIBE-013 (`gather` without `return_exceptions`) | 10 | 2 | 8 | **Context.** Every gathered awaitable already contains its exceptions in the callee (`try/except` returning a status, `None` or a dict). | P002, P003, P004, P010, P011, P015, P118 | 7 | Not decidable within a file: the containment is in other functions or modules. **Demote to WARNING.** |
| | | | | **Context.** An enclosing `gather(..., return_exceptions=True)` collects and inspects the inner gather's exception. | P065 | 1 | Same (demoted). |
| PYVIBE-009 (`open()` in `async def`) | 36 | 30 | 6 | **Reachability.** Start-up only: the config/logging file is read in the coroutine the module passes to `asyncio.run()`, before anything else runs. | P079, P080, P083, P084 | 4 | A blocking call in the module's `asyncio.run()` entry coroutine → **WARNING**, with the reason in the message (never silenced). Applies to every blocking rule. |
| | | | | **Reachability.** Manual smoke script, also run as `asyncio.run(main())`. | P099 | 1 | The same entry-coroutine rule. |
| | | | | **Reachability.** Unreachable branch: the only storage implementation returns early. | P067 | 1 | None. Needs inter-procedural analysis; stays as a known residual FP. |
| PYVIBE-008 (`sqlite3.connect` in `async def`) | 3 | 1 | 2 | **Reachability.** Demo script, `asyncio.run(main())` at the bottom. | P001 | 1 | The entry-coroutine rule. |
| | | | | **Reachability.** Start-up only: `migrate_db` is awaited from the FastAPI lifespan, in another module. | P005 | 1 | None (cross-module). Known residual FP. |
| PYVIBE-011 (`os.system/popen/waitpid`) | 2 | 0 | 2 | **Detection.** `os.waitpid(pid, os.WNOHANG)` does not block, and it is polled with `await asyncio.sleep`. | P119, P122 | 2 | `waitpid` with `WNOHANG` in its options is not reported. |
| PYVIBE-018 (`while True` without `await`) | 4 | 2 | 2 | **Context.** "First free name" search: a counter is incremented until `candidate not in <container>` returns or breaks. It ends after at most len(container)+1 pure in-memory iterations. | P014, P078 | 2 | A `while True` whose only exit is an `if <x> not in <container>:` that returns/breaks, plus a counter increment, is not reported. |
| PYVIBE-017 (empty `except BaseException`) | 1 | 0 | 1 | **Context.** The empty handler is inside an `except CancelledError:` handler whose last statement is a bare `raise`, so the original cancellation is always re-raised. | P043 | 1 | Not reported when an enclosing handler ends with a bare `raise`. |

The two Python FPs without a fix (P067, P005) remain in the expected residual.

### Java (19 FP of 58)

| Rule | n | TP | FP | Cause of the FP | IDs | # | Proposed fix |
|---|---|---|---|---|---|---|---|
| `transactions` (@Transactional + @Async) | 48 | 35 | 13 | **Detection.** `@Transactional`/`@Async` matched **inside string literals**: ArchUnit rule descriptions and violation messages (11), and an enum description string (1). No method carries the annotations. | J003–J013, J055 | 12 | Blank string, char and text-block literals (keeping lines) before matching either annotation. |
| | | | | **Detection.** The annotations sit on an `@interface` declaration: a composed annotation (Spring Modulith's `@ApplicationModuleListener`), not a proxied method. | J054 | 1 | Not reported when the annotated declaration is an `@interface`. |
| `blocking` | 8 | 2 | 6 | **Context.** `@Scheduled` is **Quarkus'** (`io.quarkus.scheduler.Scheduled`): it runs blocking methods on a worker pool and does not hold Spring's scheduler thread. All are integration-test fixture apps under `integration-tests/`. | J016, J017, J018 | 3 | `@Scheduled` counts only when it is Spring's (import `org.springframework.scheduling.annotation.Scheduled`/`.*`, or fully qualified), as `@Async` already does. **This also removes J015, a TP in Joaquín's verdict (§3 below).** |
| | | | | **Reachability.** Synchronous `@EventListener` for `ApplicationStartedEvent`: start-up only. The method also returns early before the `.block()`. | J053 | 1 | A synchronous `@EventListener` whose event is a start-up lifecycle event (`ApplicationStartedEvent`, `ApplicationReadyEvent`, `ContextRefreshedEvent`, …) → **WARNING** with the reason. |
| | | | | **Reachability.** Learning repository (`bage2014/study`): a demo that sleeps to simulate latency. | J001 | 1 | None (lexical repository-level signal only). Known residual FP. |
| | | | | **Context.** `.join()` in a `fixedDelay` `@Scheduled` method, with the work on a dedicated executor and `spring.threads.virtual.enabled=true`; deliberate design (Joaquín). | J056 | 1 | None: the virtual-thread downgrade is measured only for `@Async`, and extending it to `@Scheduled` without a measurement is not done here. Known residual FP. |

`kafka-send-timeout`: 2 TP, 0 FP.

### Summary

| Language | FP | With a proposed fix | Residual (no fix) |
|---|---|---|---|
| Python | 34 | 32 (13 by demoting PYVIBE-005, 8 by demoting PYVIBE-013, 11 by narrowing) | 2: P005, P067 |
| Java | 19 | 17 | 2: J001, J056 |

## 2. Overstated messages

Final flag (§3a: yes if A or B said yes, Joaquín's flag where he reviewed). A and B often
disagree on it: A only 33, B only 41, both 31 of 158. So the measure is noisy, and the
conservative rule pushes it up.

| Language | Rule (message) | n | Overstated |
|---|---|---|---|
| Java | `transactions` ("transaction will NOT propagate to async thread") | 48 | **48** |
| Java | `blocking` (`@Scheduled`, Quarkus fixtures) | 4 | 4 |
| Java | `blocking` (`@Async`) | 2 | 1 |
| Java | `kafka-send-timeout` (B only: the beans are opt-in) | 2 | 2 |
| Python | PYVIBE-012 ("task may be GC'd and silently cancelled") | 22 | **13** |
| Python | PYVIBE-009 ("blocks the event loop") | 36 | 11 |
| Python | PYVIBE-005 ("can hang forever") | 13 | 9 |
| Python | PYVIBE-018 ("event loop blocked indefinitely") | 4 | 3 |
| Python | PYVIBE-011, 013, 017, 008 | 16 | 6 |

**Common pattern.** The message states the **worst case as a certainty and without its
condition**: "will NOT propagate", "can hang forever", "blocked indefinitely", "silently
cancelled". The reviewers' reasons say the same thing in each rule: the mechanism is real,
but the impact is bounded or conditional. Examples:
- the method's own transaction still runs on the async thread, and what is lost is the
  caller's transaction (J002, J014, J019…);
- only the `open()` is on the loop, and the reads are offloaded or the file is a tiny lock
  file (P016, P024, P027, P033…);
- the scan ends when a batch is empty: it blocks for the scan, not indefinitely (P006);
- the GC risk is a possibility, and the callee logs its own errors (P055, P153).

**Proposed wording rule.** `<what the code does> — <mechanism>; <when it hurts>` with "can"
for what depends on runtime, and the bound when it is known. Never "forever", "indefinitely",
"silently" or "will", unless the code shows it.

| Rule | Current | Proposed |
|---|---|---|
| `transactions` | `@Transactional + @Async — transaction will NOT propagate to async thread` | `@Transactional + @Async on the same method — it runs in its own new transaction on the async executor thread, never in the caller's: a caller rollback does not undo it, and it cannot see the caller's uncommitted changes` |
| PYVIBE-012 | `asyncio.create_task() return value discarded — task may be GC'd and silently cancelled` | `asyncio.create_task() return value discarded — the event loop keeps only a weak reference to the task, so it can be garbage-collected before it finishes, and an exception it raises is never retrieved` |
| PYVIBE-009 | `open() performs synchronous file I/O — blocks the event loop` | `open() inside async def runs on the event loop — the open and every read/write on the handle block other coroutines for as long as the file I/O takes` |
| PYVIBE-005 | `Celery task defined without soft_time_limit or time_limit — can hang forever` | `Celery task without soft_time_limit or time_limit — if the work it wraps never returns, it holds a worker until a global task_time_limit (if one is set) stops it` |
| PYVIBE-018 | `while True loop inside async def has no await — event loop blocked indefinitely` | `while True loop inside async def has no await — it holds the event loop until the loop exits; no other coroutine runs meanwhile` |
| PYVIBE-011 | `os.<m>() blocks the OS thread — no direct async equivalent` | `os.<m>() inside async def blocks the event loop until the child process finishes` |
| PYVIBE-013 | `… gather re-raises it and the others keep running with nobody observing their results or later exceptions` | `… gather re-raises the first exception and the other awaitables keep running; their results and later exceptions are not observed by this call` |

**Not changed:**
- Java `blocking`: its overstated cases were the Quarkus fixtures, which the fix removes, and
  its messages are the baseline keys (`vibeguard-baseline.json`).
- `kafka-send-timeout`: already bounded (120 s / 60 s).
- PYVIBE-017 and PYVIBE-008.

A changed message changes the key of an existing baseline entry, so the release notes must say
so.

## 3. Points that go against a verdict

- **J015** (Quarkus `@Scheduled` with `Thread.sleep(100)` under `integration-tests/`):
  - Joaquín's verdict is **TP** ("bloquea el hilo del @Scheduled"); it is one of the 14
    assisted verdicts.
  - A and B said FP, and the three identical cases J016–J018 are FP (A = B).
  - The proposed `@Scheduled` provenance fix removes all four, so **one of Joaquín's TPs stops
    being CRITICAL**.
  - The reason is the framework's semantics, not the path: Quarkus runs blocking `@Scheduled`
    methods on a worker pool.
- **J056** stays CRITICAL although it is an FP (Joaquín). Closing it would need a measurement
  of `@Scheduled` under virtual threads, which does not exist.
