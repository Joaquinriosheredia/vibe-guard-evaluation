# AI review instructions — corpus-neutral, criterion v1

These instructions apply `REVIEW-CRITERIA.md` v1 to one finding at a time. They name **no
corpus and no path**: the same file is used for any corpus. They replace
`test-corpus-3/REVIEW-AI-INSTRUCTIONS.md` for new reviews; that file stays frozen with its
corpus.

## Your task

Decide one finding: a verdict **TP**, **FP** or **U**, a one-line reason with `path:line`
evidence, and whether the message overstates the impact. Decide from the source at the
pinned commit, using the rules below to the letter.

## Inputs (read only)

- **The card** is given in your prompt. It holds the finding (repository, commit, file,
  line, rule, message), the whole enclosing function, and every literal match of the
  function name in the repository, each with its path class. The path class is descriptive
  only; it does not decide anything.
- **The checkout** of that repository at the pinned commit is your working directory. Read
  anything in it; follow callers, threads, executors and configuration inside it.

## Forbidden

- Reading anything outside your working directory.
- Reading any verdict, audit, metric or analysis of any corpus (`audit-*.json`,
  `metrics.json`, `METRICS.md`, `REVIEW-*.md`, `FP-ANALYSIS.md`, `DEVIATIONS.md`, batch
  outputs), if one is reachable.
- Network access, scans, running vibe-guard or pyvibe.
- Writing, modifying or deleting anything. No git command that changes state.
- **Guessing or inventing.** Every claim cites a `path:line` that you opened and that says
  what you claim. If you did not open it, do not cite it. If you cannot find the evidence,
  the case is U, not TP or FP.

## Citations

- Every location is `path:line` or `path:start-end`, with the path **relative to the
  repository root** (your working directory), for example
  `src/main/java/com/acme/OrderService.java:42`.
- Not a bare file name (`OrderService.java:42`), not an absolute path, not a URL.
- Each citation is checked: the file must exist at that path and the lines must be in it.

## How to decide (every finding)

1. **Detection:** open the file at the finding's line. Confirm that the pattern the rule
   names is there.
2. **Follow the callers to the end, always.** Climb caller by caller until you reach either
   an entry point of normal operation (an HTTP route, a message loop, a listener or consumer,
   a scheduled job, a task, a `main` that ships, a framework hook, a registration such as a
   tool table or an `async for` consumer) or no caller at all.
   - Callers only in test sources, benchmarks, manual scripts or docs: **FP by
     reachability**.
   - No caller anywhere, and no decorator, annotation, registration, route table or
     configured reflection that reaches it: dead code, **FP by reachability**.
   - **Demo, playground, sample and fixture applications are applications.** If the app's
     own entry point runs the code, it is reachable, whether or not the app ships. Say which
     application the code belongs to and cite its entry point. `src/main` of a fixture app
     is not a test source.
   - **Startup and shutdown:** FP only when the code runs at process startup, before
     serving, or at final shutdown with no other work left. A shutdown or self-uninstall path
     triggered by a message while the loop still serves other work is reachable.
   - A path that runs rarely, or that one branch skips, is still reachable. An
     "unreachable" claim needs evidence for every path that reaches the code.
   - If the repository does not show who calls the code, or on which thread: **U**.
3. **Check the context row of the rule-criteria table below** (the thread or pool, whether
   the anchor is live, the configuration).
4. **Decide:** TP only when 1–3 hold, each with cited evidence; FP when the repository shows
   that one fails; U when it does not let the case be decided.

**Overstatement is never a reason for FP:** record it in `overstated`, true only when the
message states an impact the code does not support (say which part in the reason).

## Context rules that are easy to get wrong

- **Deliberate wait on a scheduler thread** (`join()`/`get()` over work submitted to another,
  dedicated pool): TP when the application has other `@Scheduled` jobs and the scheduler has
  one thread (Spring's default); FP when there is no other scheduled job, the scheduler pool
  has more than one thread, or each run gets its own thread (Spring Boot ≥ 3.2 with
  `spring.threads.virtual.enabled=true`). A `Thread.sleep` that is the job's own work is not
  a designed wait: it blocks the job's thread whatever the pool.
- **Discarded task (PYVIBE-012/014):** TP when no reference to the task is kept anywhere.
  A body that catches its exceptions does not make it FP; it makes the finding Overstated if
  the message says exceptions are lost.
- **ContextVar without reset (PYVIBE-006):** TP when later work in the same context (the
  rest of the task) can see the value; FP only when the context is discarded right after
  the call. "Leaks between tasks" without evidence is Overstated, not FP.
- **Untimed Kafka `.send(..).get()`:** TP on a normal path; bounds quoted from producer
  defaults that the repository does not set make the message Overstated, not FP.
- **Inner `gather()` without `return_exceptions`:** follow the raised exception up to where
  it is caught or observed; an enclosing `gather(…, return_exceptions=True)` that inspects it
  contains it.

## Rule criteria v1 (condition 2)

| Rule | TP context | FP context (examples, not exhaustive) |
|---|---|---|
| `blocking`, `blocking-kafka` | the blocking call runs on the anchored pool (an `@Async` executor with `@EnableAsync`, a scheduler, an event, a Kafka listener thread) on a normal path | the anchor is inert, or the call does not block (a completed future); a designed wait on the scheduler thread with no starvation |
| `kafka-send-timeout` | an untimed `.send(..).get()` on a normal path | the producer is configured so the call cannot wait beyond the message's bound |
| `transactions` (critical) | `@Transactional` and Spring's `@Async` on the same proxied method | not a Spring proxy, or not Spring's annotations |
| `reactor-block` (critical) | the call can run on a non-blocking Reactor thread (event loop, `parallel`, `single`) | it runs on a thread that may block (virtual, `@Async`, `boundedElastic`, startup, servlet worker) |
| PYVIBE-001/002/004/007/008/009/010/011/016/018 (blocking in `async def`) | the call runs on the event loop on a request or task path, including a shutdown or self-uninstall path triggered while the loop serves other work | the code runs only at process startup or final shutdown with no other work on the loop, in a thread (`to_thread`, executor), or in a `def` only called off the loop |
| PYVIBE-003/015 (nested loop) | reachable while a loop is running | only reachable with no running loop |
| PYVIBE-005 (Celery without a time limit) | the task can hang on external I/O and no global limit is set in the repository | a global `task_time_limit`/`task_soft_time_limit` covers it |
| PYVIBE-006 (ContextVar without reset) | the value can leak to later work sharing the context, including later steps of the same task | the context is discarded after the call |
| PYVIBE-012/014 (discarded task) | no reference to the task is kept anywhere, whether or not the body catches its exceptions | a reference is kept (a set, a registry, a callback attaching it) |
| PYVIBE-013 (gather) | some gathered awaitable can raise on a normal failure, and the others then run unobserved | every awaitable contains its exceptions |
| PYVIBE-017 (empty `except`) | it can swallow `KeyboardInterrupt`/`SystemExit`, or errors that matter on a normal path | — |

A rule not listed falls back to conditions 1–3.

## Output

The JSON contract in your prompt. If you are run without one: a single JSON object
`{"verdict": "TP|FP|U", "reason": "… path:line …", "citations": ["path:line", …], "overstated": true|false}`.
