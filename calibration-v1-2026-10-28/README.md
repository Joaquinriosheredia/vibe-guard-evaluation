# Calibration v1 2026-10-28 — chain-v1 AI review vs Joaquín (TC3 + TC2, 52 cases)

What: `vibe-guard review --protocol chain-v1` re-judged the 25 TC3 + 27 TC2 cases of `test-corpus-{3,2}/audit-joaquin.json` under REVIEW-CRITERIA v1 (main bc0a3c6). `table.py` compares the verdicts with Joaquín's original labels and with the v1 labels (§6: TC2 J001 FP→TP, TC3 P026 FP→TP), Wilson 95 % intervals; an invalid answer counts as a disagreement.

## Code used

- **vibe-guard-scan `feat/review-chain-v1` @ `d1aa18abcfa17b1582b71747c09584ec31cfe1c7`**: all 52 cases (main run). Committed and pushed before the run.
- **vibe-guard-scan @ `123d440a0a1be5dfe1f573a0a84a6564dbada519`**: re-run of TC2 J001 and P116 only (see below). Committed and pushed before the re-run.
- vibe-guard-evaluation `calibration-v1-2026-10-28` @ `d6110de7e760393120fb6046937a43d1a67ba464`: instructions `../REVIEW-AI-INSTRUCTIONS.md` (v1), few-shot `examples-tc2.md`.
- claude 2.1.312 (Claude Code), CLI default model (claude-opus-5-5), logged-in Max subscription: `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN` are removed from the reviewer environment. pyvibe 0.15.0, node v22.22.1. TC3 first, then TC2; `--concurrency 3`.

## Protocol chain-v1 (per reviewer)

1. **Plan** with no tools, before reading code: entry points sought and the evidence needed for detection / context / reachability, v1 criterion numbers.
2. **Review** with Read/Grep/Glob plus a deterministic, name-based **callers tool** (MCP: `find_callers`, `find_definitions`, `enclosing_function`).
3. Answer: TP / FP / U, a **call chain** from an entry point (route, @Scheduled, listener, consumer, main, registration, task, hook…) with one `path:line` per hop, the v1 criteria applied and, for FP, the condition that fails.
4. **Verifier** (`chain.js`; standalone `scripts/verify-chains.mjs`): each hop exists and its line names the next hop's symbol; the last hop is the card's function. FP by reachability is checked by climbing callers by name. It states what it does **not** guarantee: name resolution (overloads, DI, reflection), that the call executes, the thread/loop, that the entry point is live, that no caller exists. Grep is not a complete proof.
5. **Rule e**: a TP chain or an FP-by-reachability claim that does not verify on the last attempt becomes **U**, never FP.

Configurations from one run: **A** = proposer only (`review-a.json`); **A+B** = proposer + refuter, B's final verdict (`review-b.json`).

## Result (`table-output.txt`)

| | TC3 — clean exam (**main figure**) | TC2 — contaminated by the examples (informative) |
|---|---|---|
| A vs original labels | 20/25 = 0.80 [0.61–0.91] | 24/27 = 0.89 [0.72–0.96] |
| A vs v1 labels | **21/25 = 0.84 [0.65–0.94]** | 24/27 = 0.89 [0.72–0.96] |
| A+B | identical to A in every cell | identical to A in every cell |
| TC2 with J001/P116 re-run, A and A+B vs v1 | — | 26/27 = 0.96 [0.82–0.99] |

- TC3 by language (A vs v1): Java 5/5, Python 16/20 = 0.80 [0.58–0.92].
- **The refuter never refuted**: B confirmed A in all 50 valid cases (52 after the re-run). Here the second reviewer added cost, not agreement.
- Compared with 2026-10-27 (legacy protocol, original labels): TC3 A 0.72 → 0.80; TC2+TC3 consensus 37/49 = 0.76 → 44/50 = 0.88 [0.76–0.94]. The intervals overlap; 2026-10-27 also used the TC3-specific instructions on TC2.
- Rule e coerced 0 answers to U. `verify-chains-*.txt`: no chain FAIL (82 pass, 18 n/a = FP by context/detection, which have no chain to verify; 4 invalid in the first run).
- Cost: $34.84 API-equivalent for the main run + $5.40 for the re-run, billed to the subscription. No usage-limit stop.

## Failures (vs v1 labels; chains and full reasons in `table-output.txt`)

- **TC3 P035** — Joaquín FP, model TP: `[route] delete_one_document` → `_invalidate_committed_document_cache` → `_detach_cache_invalidation` → `_finish_detached_cache_invalidation` (apps/api/routers/documents.py). It finds the `except BaseException: pass` swallow reachable from a DELETE route; it calls the impact overstated.
- **TC3 P097** — Joaquín FP, model TP: `[hook] _start_broadcaster` (scanner/api.py:198, startup) → `broadcast_loop` (scanner/feed_hub.py:300). It argues §2.2 does not apply because the task lives for the whole server; a short drain, overstated.
- **TC3 P050** — Joaquín TP, model FP (context): it argues `_code_handler` refuses the notebook-edit action whenever runtime context keys are present, which every registered-tool call adds.
- **TC3 P075** — Joaquín TP, model FP (context): it argues the blocking `open()` only runs with `allow_data_uri=True`, and every production caller passes False.
- **TC2 P073** — Joaquín TP, model FP (context): the remote-backend `open_read` branch is inert because `get_storage()` always returns the local backend. This case **is one of the few-shot examples** and the model still disagrees.
- **TC2 J001, P116** — invalid in the main run, see below; TP / TP after the re-run, matching v1.

All four TC3 failures are Python. P050, P075 and P073 are FP **by context**: neither the verifier nor rule e covers them, because they do not claim unreachability.

## J001 / P116: invalid in the main run, re-run

Prompts over 100 KB go to a file that the reviewer must Read. The plan phase had no tools, so it could not read that file. The two largest cards (J001 461 KB, P116 316 KB) timed out or answered without a plan, in the run and in a first retry with the same code (`out-tc2-retry-d1aa18a/` in the work dir). Fix `123d440`: such a plan runs with Read only, from the file's directory, so `--restricted` still denies the checkout (checked against the real CLI). The main tables keep the first run (invalid = disagreement); the re-run is a separate section of `table-output.txt`. TC3 had no card over the limit.

## Files

- `examples-tc2.md`: few-shot examples, TC2 only (J052, J015, P073, P126 TP; P083, P099, P065 FP), Joaquín's verdict and reason. TC3 was not used to develop anything.
- `table.py`: `python3 table.py ~/vibe-guard-evaluation-work/calib-v1-2026-10-28 ~/vibe-guard-evaluation` → `table-output.txt`.
- `verify-chains-tc3.txt`, `verify-chains-tc2.txt`, `verify-chains-tc2-retry.txt`: `node scripts/verify-chains.mjs <out-dir> test-corpus-$c/cards ~/vibe-guard-evaluation-work/tc$c/checkouts`.
- Raw outputs (review-a/b.json, review-sheet.md, logs, `RUN.md`) are in `~/vibe-guard-evaluation-work/calib-v1-2026-10-28/`, not in this repo.

Command per corpus `c`: `vibe-guard review test-corpus-$c/cards --instructions REVIEW-AI-INSTRUCTIONS.md --examples calibration-v1-2026-10-28/examples-tc2.md --checkouts ~/vibe-guard-evaluation-work/tc$c/checkouts --out <W>/out-tc$c --ids-file <W>/ids-tc$c.txt --protocol chain-v1 --concurrency 3`.
