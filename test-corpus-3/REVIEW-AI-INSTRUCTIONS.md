# Reviews A and B — instructions (test-corpus-3, `PREREGISTRATION.md`, "Review method")

These instructions are committed **before review A starts**. Every session of review A
(Claude Opus 5.5, `claude-opus-5-5`) and of review B (Claude Sonnet 5.5, `claude-sonnet-5-5`)
receives them unchanged.
- They are test-corpus-2's `REVIEW-B-INSTRUCTIONS.md` with only the paths changed and
  test-corpus-2's known reviewer failures added to the warning.
- Each review is one of two independent AI reviews, and its verdicts are compared with the
  other, which it never sees.
- The session prompt says which review (A or B) and which batch.

## Your task

For each finding ID in your batch, decide a verdict **TP**, **FP** or **U**, a one-line reason,
and whether the message overstates the impact. Decide from the source at the pinned commit,
using the rules below to the letter.

## Inputs (read only)

- **Card:** `test-corpus-3/cards/<ID>.md`. It holds the finding, the whole enclosing function,
  and every literal match of the function name in the repository, each with its path class.
  - Large cards have thousands of rows: read them in parts (head, grep).
  - The path class is descriptive only. It does not decide anything.
- **Finding:** the entry with that `id` in `test-corpus-3/review-set.json` (repo, commit,
  file, line, ruleId, message).
- **Checkout at the pinned commit:**
  `~/vibe-guard-evaluation-work/tc3/checkouts/<java|python>/<owner>__<repo>/`.
  - Read anything in it.
  - Use `grep`, `rg`, `git grep`, `git show` and `git log` (read only) to follow callers,
    threads, executors and configuration.

## Forbidden

- Reading or listing `~/vibe-guard-evaluation-work/tc3/private-a/` or
  `~/vibe-guard-evaluation-work/tc3/private-b/`, except writing your own output file where
  your session prompt says.
- Reading any file named `audit-*.json`, `a-batch-*.json`, `b-batch-*.json`,
  `claude-batch-*.json` or another batch's output.
- **Reading any test-corpus-2 verdict or analysis:**
  - anything under `~/vibe-guard-evaluation-work/tc2/`;
  - in `test-corpus-2/`: `audit-*`, `metrics.json`, `METRICS.md`, `REVIEW-*.md`,
    `FP-ANALYSIS.md` and `DEVIATIONS.md`;
  - `test-corpus-1`'s verdicts and dev labels.

  The known failures below are all you are given of them.
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

## Known failures from test-corpus-2 (a warning, not a rule)

- **The two AI reviews agreed with each other far more than with the author.**
  - A–B agreement was 151 of 158 (kappa 0.90).
  - Yet in the audit of 20 agreeing cases the author changed 3, which made the AI review
    NOT RELIABLE.
  - Two reviews agreeing is not evidence that they are right. Each claim needs its own
    `file:line`.
- **The three changed cases** show reasoning steps that were judged differently. They are
  examples, not precedents; decide each case from its own code:
  - **An app under `integration-tests/…/src/main/java`** (a framework's fixture application)
    was FP by reachability in both AI reviews and TP for the author, who held that the
    blocking call runs on the scheduler thread of that application. State which application
    the code belongs to and whether it ships, with `file:line`.
  - **An inner `gather()` without `return_exceptions`** was TP in both AI reviews. The author
    called it FP: the enclosing `gather(…, return_exceptions=True)` of the caller collects and
    inspects that exception. Follow the raised exception up to where it is caught or
    observed.
  - **A blocking `open()` inside an async generator** was FP in both AI reviews: they
    reasoned that the only storage backend returns early, so the code is unreachable. The
    author called it TP: it is consumed by `async for` in production code. An "unreachable"
    claim needs evidence for every path that reaches the code.
- **Disagreements between A and B** (7):
  - whether a learning repository's demo is production;
  - a deliberate `join()` with virtual threads;
  - whether a shutdown-only path counts as normal operation (2);
  - whether a discarded task whose coroutine never suspends can be lost (2);
  - a bounded `while True`, where one review judged the message ("indefinitely") instead of
    the verdict.

  **Overstatement is never a reason for FP:** record it in `overstated`.
- **`overstated` was very noisy:** A and B disagreed on it in 74 of 158 cases. Mark it only
  when the message states an impact that the code does not support, and say which part.

## Rules (literal copy of `PREREGISTRATION.md`, "Verdicts")

test-corpus-3's pre-registration applies test-corpus-2's verdict rules unchanged. Its section
follows word for word. PYVIBE-005 and PYVIBE-013 are WARNING rules now and are not in the
review set.

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

Write exactly one JSON file, at the path given in your session prompt: `~/vibe-guard-evaluation-work/tc3/private-a/a-batch-<N>.json` (review A) or `…/private-b/b-batch-<N>.json` (review B), which `scripts/review_ab.py seal` merges:

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
