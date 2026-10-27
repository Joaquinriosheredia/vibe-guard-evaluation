# FP analysis — test-corpus-3 (development data from here on)

test-corpus-3 is closed (`METRICS.md`, evaluation PR #16): criterion 1 is NOT MET in Java
(0.6667, n 24, below the 50 required) and Python (0.77), and the AI review was declared NOT
RELIABLE (Joaquín changed 5 of the 20 audited). Criterion 2 is MET in both. From here on its
findings, cards and verdicts are **development data**: they are used freely to fix the rules,
and nothing measured on them again is evidence for the criteria.

**Sources.**
- Verdict of each finding: the final one (version (a) of `METRICS.md`): Joaquín's where he
  reviewed (`audit-joaquin.json`), otherwise the agreeing verdict of A and B.
- Causes: the reasons in `audit-joaquin.json` and in reviews A and B (sealed, opened in phase 5),
  each checked against the TC3 checkouts at the pinned commits.
- Fixes: the private engine repos `pyvibe-pro` and `java-vibe-guard-pro` (branch
  `fix/tc3-fp-analysis` in both), each FP with a regression test from the reviewed code that
  fails without the fix, and a positive control.

## 1. False positives by rule and cause

### Python (23 FP of 100)

| Rule | n | TP | FP | Cause of the FP | IDs | # | Fix |
|---|---|---|---|---|---|---|---|
| PYVIBE-009 (`open()` in `async def`) | 56 | 47 | 9 | **Reachability.** One-shot operator CLI, `asyncio.run(_run())` reaching the coroutine through another coroutine. | P024 | 1 | **Rule demoted to WARNING** (§2). |
| | | | | **Reachability.** Handlers of one dispatcher (`code_tool.py`) that every runtime call rejects before dispatch. | P045–P049, P051–P053 | 8 | Same (WARNING). Not decidable in the AST; see §3 for P050. |
| PYVIBE-006 (`ContextVar.set()` without cleanup) | 6 | 1 | 5 | **Detection.** The token is stored on an attribute and reset in a `finally` of another method of the module (`__aenter__`/`__aexit__`, setup/teardown). | P043, P025 | 2 | An `<attribute> = var.set(...)` whose attribute a `finally` of the module passes to `var.reset()` is not counted. |
| | | | | **Detection.** `var.set(None)` with `default=None`: it clears the variable. | P099 | 1 | A `set()` of the declared constant default is not counted. |
| | | | | **Context.** Per-call marker with an explicit clearing point elsewhere in the module (`reset_authorized_vault()`, `_is_byok_call.set(False)`). | P023, P039 | 2 | **WARNING** when the module sets the variable back to its default elsewhere. Whether the clearing runs before reuse is not visible. |
| PYVIBE-017 (empty `except BaseException`) | 4 | 0 | 4 | **Context.** The `try` only reaps a task: `await task` after `task.cancel()` (P035 timeout branch, P063 `finally`), or `await asyncio.shield(task)` as the body of `while not task.done()` (P077, P078). | P035, P063, P077, P078 | 4 | **WARNING** for that shape; still CRITICAL inside a handler of the coroutine's own cancellation that does not re-raise (dev-labels DL-055, TP). |
| PYVIBE-008 (`sqlite3.connect` in `async def`) | 2 | 0 | 2 | **Reachability.** One-off manual script under `.scratch/`. | P094, P095 | 2 | `scratch/` and `.scratch/` join the non-production path segments (WARNING). |
| PYVIBE-012 (`create_task` orphan) | 19 | 18 | 1 | **Context** (Joaquín): the task body catches `Exception` and records the failure. | P026 | 1 | **None in this round** (not requested). See §3: P027 and P028 are the same pattern and TP. |
| PYVIBE-018 (`while True` without `await`) | 5 | 3 | 2 | **Context.** Inner drain loop that ends at `QueueEmpty`/`queue.Empty` (`get_nowait`). | P073, P097 | 2 | **None in this round** (not requested). Candidate: a `while True` whose only exit is a `get_nowait()` empty-queue handler. |

### Java (7 FP of 24)

| Rule | n | TP | FP | U | Cause of the FP | IDs | # | Fix |
|---|---|---|---|---|---|---|---|---|
| `blocking` | 10 | 5 | 5 | 0 | **Reachability.** Fixture apps of axelix under `playgrounds/` (deployed only to its test environment). | J002, J004, J005, J006 | 4 | A module directory (before `src/`) named playground/demo/example/sample → **WARNING**, with the directory in the message. |
| | | | | | **Context.** `@Async executeSync` is only self-invoked from `startSync`: the call bypasses the Spring proxy and never runs on the @Async executor. | J009 | 1 | A Spring `@Async` method called only from its own class (unqualified or `this.`) is not an anchor; any `<receiver>.name(` in the file or `.name(`/`::name` elsewhere keeps it. |
| `kafka-send-timeout` | 5 | 2 | 2 | 1 | **Reachability.** `hp-demo/hp-demo-kafka`, a reference demo outside the root build. | J014, J015 | 2 | The same non-production module rule (**WARNING**). |
| `transactions` | 9 | 9 | 0 | 0 | — | — | 0 | — |

### Summary

- Python: 20 of the 23 FPs are addressed (8 of them only by severity: PYVIBE-009 is no longer
  CRITICAL); P026 (012), P073 and P097 (018) are left for a later round.
- Java: all 7 are addressed (6 by WARNING, J009 removed).
- No rule was fixed by silencing a reachability FP: a path or module the engine cannot judge
  is demoted, never dropped.

## 2. Overstated messages

Joaquín marked 23 of his 25 verdicts as Overstated (`audit-joaquin.json`). By rule:

- **PYVIBE-009: 11 of 12 TPs Overstated.** A local `open()` and read/write blocks the loop for
  as long as the disk takes; rarely long enough to stall other coroutines the way a network
  call does. **Fix: PYVIBE-009 is WARNING** (BREAKING for CI gates). The 9 FPs above become
  WARNING too.
- `blocking` (Java): 3 of 3 TPs Overstated; `kafka-send-timeout`: 2 of 2. Not changed in this
  round (not requested). J003 and J001, his TP-Overstated playground findings, become WARNING
  through the non-production module rule, which matches his Overstated.
- PYVIBE-012: 3 of 4 TPs Overstated; PYVIBE-006: 1 of 1 (P044). Not changed.

## 3. Points that go against a verdict

The fixes follow the final verdicts. Three groups mix TP and FP on the same code; each fix
keeps the finding (WARNING) rather than removing it, so none of these TPs is lost.

- **`code_tool.py` (manor-ai):** Joaquín judged **P050** (`_handle_notebook_edit`, line 1312)
  **TP**; A and B agreed **FP** on P051 (line 1325 of the same function) and on P045–P049,
  P052, P053 (other handlers of the same dispatcher), by reachability. After the fix all of
  them are WARNING.
- **`playgrounds/` (axelix):** Joaquín judged **J003** (`SchedulerTestConfig.java:57`) and
  **J001** (`BookTestDataQueryRunner.java:24`) **TP, Overstated**; A and B agreed **FP** on
  J002, J004–J006 in the same playground classes, by reachability. After the fix all are
  WARNING.
- **`kline.py` (tickflow-stock-panel):** Joaquín judged **P026** (line 1009) **FP** and **P027**
  (1164) and **P028** (1251) **TP**; the three are `asyncio.create_task(task())` with a body
  that catches `Exception`. Not touched (PYVIBE-012 was not in this round); worth a decision
  before fixing PYVIBE-012.

## 4. After the fixes: control re-scan of test-corpus-2 and test-corpus-3 (not evidence)

Engines at `master` (pyvibe 0.15.0, java-vibe-guard 3.0.0) vs `fix/tc3-fp-analysis`, on the
frozen checkouts that still exist (Python: 13 of 20 TC2 repositories and 13 of 20 TC3, the
others are not in `~/vibe-guard-evaluation-work`; Java: 11 TC2 and 7 TC3). Every changed finding:

| Corpus | Rule | Change | TP | FP | not reviewed |
|---|---|---|---|---|---|
| TC2 | PYVIBE-009 | CRITICAL → WARNING (rule demoted) | 30 | 1 | 16 |
| TC2 | PYVIBE-006 | CRITICAL → WARNING (clearing point) | | | 1 (geolens `catalog_locks.py:246`, `set(False)` elsewhere) |
| TC3 | PYVIBE-009 | CRITICAL → WARNING (rule demoted) | 47 | 9 | 1 |
| TC3 | PYVIBE-006 | removed | | 3 (P025, P043, P099) | |
| TC3 | PYVIBE-006 | CRITICAL → WARNING | | 2 (P023, P039) | |
| TC3 | PYVIBE-017 | CRITICAL → WARNING | | 4 (P035, P063, P077, P078) | 1 (manor-ai `skill_runner.py:1315`, same shield helper) |
| TC3 | PYVIBE-008 | CRITICAL → WARNING (`.scratch/`) | | 2 (P094, P095) | |
| TC3 | `blocking` | CRITICAL → WARNING (`playgrounds/`) | 2 (J001, J003) | 4 (J002, J004–J006) | |
| TC3 | `blocking` | removed (self-invoked `@Async`) | | 1 (J009) | |
| TC3 | `kafka-send-timeout` | CRITICAL → WARNING (`hp-demo/`) | | 2 (J014, J015) | |

TC2 Java: no change. No TP is removed; the only TPs that change are demoted to WARNING by the
PYVIBE-009 decision (§2) or by the module rule on findings Joaquín judged Overstated. P044
(PYVIBE-006, TP) stays CRITICAL.
