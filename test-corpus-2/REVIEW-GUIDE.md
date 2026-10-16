# Review guide — test-corpus-2

The two sections below are copied **literally** from `PREREGISTRATION.md`. If anything here
differs from it, `PREREGISTRATION.md` decides.

---

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

---

## Reviewers, cards and blindness (excerpt)

**Assistance during the review:**
- **Who it covers:** any assistant, meaning any Claude session or other AI, including Joaquín's
  adviser.
- **What is allowed:** only factual navigation: where a file is, what a line contains, what a
  search returns.
- **What is never allowed:** a verdict, an assessment or an opinion on the case.
- **Logging:** every piece of help, from whoever gives it, is logged in `REVIEW-LOG.md` with
  its date, the question and the answer.
- **The cards do not change.**

---

## How to fill the sheet and the log

This is the format of the files named in `PREREGISTRATION.md`; it adds no rule.

- **`REVIEW-SHEET.md`:** it holds 27 IDs in a random order (`DEVIATIONS.md` §3a). For each ID,
  open its card (`cards/<ID>.md`) and fill in the three
  fields:
  - `Verdict`: `TP`, `FP` or `U`;
  - `Reason (file:line)`: one line with file:line evidence ("Each reason cites file:line
    evidence");
  - `Overstated`: `Sí` or `No` (message accuracy, recorded separately).
- **The repository at the pinned commit** may be consulted freely. Its link is at the top of
  each card.
- **When the sheet is complete:** `python3 scripts/review_sheet.py audit` writes
  `audit-joaquin.json`. It refuses if any verdict is missing or is not TP/FP/U, if a reason is
  missing, or if `Overstated` is not Sí/No.
- **`REVIEW-LOG.md`:** add one row for every piece of help received during the review, from
  whoever gives it: date, who, question and answer.
