# Review B — instructions (test-corpus-2, `DEVIATIONS.md` §3)

These instructions are committed **before review B starts**. Every review-B session receives
them unchanged. Review B is one of two independent AI reviews; its verdicts are compared with
another review that it never sees.

## Your task

For each finding ID in your batch, decide a verdict **TP**, **FP** or **U**, a one-line reason,
and whether the message overstates the impact. Decide from the source at the pinned commit,
using the rules below to the letter.

## Inputs (read only)

- **Card:** `test-corpus-2/cards/<ID>.md`. It holds the finding, the whole enclosing function,
  and every literal match of the function name in the repository, each with its path class.
  - Large cards have thousands of rows: read them in parts (head, grep).
  - The path class is descriptive only. It does not decide anything.
- **Finding:** the entry with that `id` in `test-corpus-2/review-set.json` (repo, commit,
  file, line, ruleId, message).
- **Checkout at the pinned commit:**
  `~/vibe-guard-evaluation-work/tc2/checkouts/<java|python>/<owner>__<repo>/`.
  - Read anything in it.
  - Use `grep`, `rg`, `git grep`, `git show` and `git log` (read only) to follow callers,
    threads, executors and configuration.

## Forbidden

- Reading or listing `~/vibe-guard-evaluation-work/tc2/private/`.
- Reading any file named `audit-*.json`, `claude-batch-*.json`, `repeat-sample*` or another
  batch's output.
- Any network access, any scan, running vibe-guard or pyvibe.
- Writing, modifying or deleting anything except your own output file. No git command that
  changes state.
- **Guessing or inventing.** Every claim in a reason cites a `file:line` that you opened in the
  checkout and that says what you claim.
  - If you did not open it, do not cite it.
  - If you cannot find the evidence, the case is U, not TP or FP.

## How to decide (required on every finding)

1. **Read the pre-registration rules below first**, including the rule-criteria table.
2. **Detection:** open the file at the finding's line in the checkout. Confirm that the
   pattern the rule names is there.
3. **Follow the callers to the end, always.** Start from the function on the card and climb
   caller by caller, until you reach either:
   - an entry point of the application's normal operation (an HTTP handler, a listener or
     consumer, a scheduled job, a task, a `main` that ships, a framework hook); or
   - no caller at all.

   For each step:
   - Callers only in tests, examples, scripts, benchmarks or docs mean **FP by reachability**.
   - A function with no caller anywhere in the repository is dead code: **FP by
     reachability**, unless an entry point that the repository shows reaches it. Examples of
     such entry points: a decorator, an annotation, a registration, a route table, reflection
     configured in the repository.
   - Dynamic dispatch, dependency injection or framework entry points that the literal search
     does not resolve: look for them, for example the annotation, the registration or the
     configuration.
   - If the repository does not show who calls the code, or on which thread, the verdict
     is **U**.
4. **Check whether exceptions are already contained**, where the rule's impact depends on an
   exception:
   - for example PYVIBE-013 `gather`: does every gathered awaitable catch its own failures?
   - for example PYVIBE-012/014 discarded tasks: is a reference kept anywhere?
   - Open the callee's body. If it already contains or handles the failure, the rule's context
     does not hold: **FP**.
5. **Check the context row of the rule-criteria table**, for example:
   - which thread or pool;
   - whether the anchor is live (`@EnableAsync`, a scheduler, a listener);
   - the global Celery limits;
   - the Reactor scheduler.
6. **Decide:**
   - **TP** only when 1–3 all hold and you have cited evidence for each;
   - **FP** when the repository shows that one of them fails;
   - **U** when the repository does not let the case be decided.

## Known failures from test-corpus-1 (a warning, do not repeat them)

- **Invented locations.** A first AI review cited lines and file lengths that did not exist
  at the pinned commit (test-corpus-1 `DEVIATIONS.md` §3). It was voided.
- **TP over-calling.** On the 20 findings reviewed twice in test-corpus-1, the AI review
  called 16 TP and the human review 10 TP (raw agreement 0.60, kappa 0.20). 7 verdicts went
  from TP to FP for these reasons:
  - **called only from tests:** the function was reached only from `tests/…`;
  - **dead code:** the only caller had no caller itself, or the class was never instantiated
    anywhere in the repository (only mentioned in a comment);
  - **exceptions already contained:** the gathered awaitables each caught their own failures
    and returned a value (a `try/except Exception` inside the callee). So `gather` could not
    re-raise on a normal failure.
- **One opposite case (FP → TP):** a helper called outside the `try` let a database failure
  propagate from `gather` in a live GET endpoint. Follow the code; do not assume containment
  either.

## Rules (literal copy of `PREREGISTRATION.md`, "Verdicts")

## Verdicts (the rules of test-corpus-1, unchanged)

Verdicts are decided from the source at the pinned commit. Callers and configuration are
followed anywhere in the repository.

- **TP** when all three hold:
  1. **Detection:** the code has the pattern the rule names, where it names it;
  2. **Context:** the conditions the message states for the impact hold there (the rule
     criteria below);
  3. **Reachability:** the code runs in the application's normal operation, as production
     code, not only in tests, examples, scripts or dead code.
- **FP** when any of 1–3 is false and the repository shows it.
- **Undetermined (U)** when the repository does not let 1–3 be decided: for example, the
  caller, the thread or the configuration lives outside the repository.

**Message accuracy** (criterion 8) is recorded separately, as overstated yes or no. A TP whose
message overstates the impact stays a TP for precision, and is counted apart.

**Rule criteria** (condition 2):

| Rule | TP context | FP context (examples, not exhaustive) |
|---|---|---|
| `blocking`, `blocking-kafka` | the blocking call runs on the anchored pool (an `@Async` executor with `@EnableAsync`, a scheduler, an event, a Kafka listener thread) on a normal path | the anchor is inert, or the call does not block (a completed future) |
| `kafka-send-timeout` | an untimed `.send(..).get()` on a normal path | the producer is configured so the call cannot wait beyond the message's bound |
| `transactions` (critical) | `@Transactional` and Spring's `@Async` on the same proxied method | not a Spring proxy, or not Spring's annotations |
| `reactor-block` (critical) | the call can run on a non-blocking Reactor thread (event loop, `parallel`, `single`) | it runs on a thread that may block (virtual, `@Async`, `boundedElastic`, startup, servlet worker) |
| PYVIBE-001/002/004/007/008/009/010/011/016/018 (blocking in `async def`) | the call runs on the event loop on a request or task path | the code runs only at startup or shutdown, in a thread (`to_thread`, executor), or in a `def` only called off the loop |
| PYVIBE-003/015 (nested loop) | reachable while a loop is running | only reachable with no running loop |
| PYVIBE-005 (Celery without a time limit) | the task can hang on external I/O and no global limit is set in the repository | a global `task_time_limit`/`task_soft_time_limit` covers it |
| PYVIBE-006 (ContextVar without reset) | the value can leak to later work sharing the context | the context is discarded after the call |
| PYVIBE-012/014 (discarded task) | no reference to the task is kept anywhere | a reference is kept (a set, a registry, a callback attaching it) |
| PYVIBE-013 (gather) | some gathered awaitable can raise on a normal failure, and the others then run unobserved | every awaitable contains its exceptions |
| PYVIBE-017 (empty `except`) | it can swallow `KeyboardInterrupt`/`SystemExit`, or errors that matter on a normal path | — |

A rule not listed falls back to conditions 1–3.

## Output

Write exactly one JSON file, the path given in your session prompt:

```json
{"batch": N, "verdicts": [{"id": "…", "verdict": "TP|FP|U", "reason": "… file:line …", "overstated": true|false}]}
```

- Write one entry per ID of your batch, in the batch's order.
- `reason` is one line with file:line evidence for the claim that decides the verdict.
- `overstated` is true if the message overstates the impact. It is recorded apart; a TP
  stays a TP.
- Check that the file parses and has every ID.
- **Your final message is only `batch N done: K verdicts written`:** no counts per verdict,
  no comments on findings.
